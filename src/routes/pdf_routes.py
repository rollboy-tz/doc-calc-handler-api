"""
PDF ROUTES - FIXED VERSION
"""
from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import sys
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Fix import - add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from services.pdf import StudentReportGenerator, ClassReportGenerator
    student_gen = StudentReportGenerator()
    class_gen = ClassReportGenerator()
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"PDF Import Error: {e}")
    # Create dummy generators for fallback
    class DummyGenerator:
        def generate(self, data, school_info=None):
            from weasyprint import HTML
            html = HTML(string="<h1>PDF Service Error</h1><p>Import failed</p>")
            return html.write_pdf()
    
    student_gen = DummyGenerator()
    class_gen = DummyGenerator()
    IMPORT_SUCCESS = False


@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    """Generate student report PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        if 'student_data' not in data:
            return jsonify({'error': 'Missing student_data', 'success': False}), 400
        
        # Generate PDF
        pdf_bytes = student_gen.generate(
            student_data=data['student_data'],
            school_info=data.get('school_info')
        )
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Filename
        student_name = data['student_data']['student']['name']
        safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)
        filename = f"student_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return file
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500


@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    """Generate class report PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        if 'class_data' not in data:
            return jsonify({'error': 'Missing class_data', 'success': False}), 400
        
        # Generate PDF
        pdf_bytes = class_gen.generate(
            class_data=data['class_data'],
            school_info=data.get('school_info')
        )
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Filename
        class_id = data['class_data']['metadata'].get('class_id', 'class')
        safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)
        filename = f"class_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return file
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500


@pdf_routes.route('/api/pdf/status', methods=['GET'])
def status():
    """Check PDF service status"""
    return jsonify({
        'status': 'active',
        'service': 'pdf_generation',
        'import_success': IMPORT_SUCCESS,
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'student_report': 'POST /api/pdf/student',
            'class_report': 'POST /api/pdf/class'
        }
    })