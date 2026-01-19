"""
PDF ROUTES
"""
from flask import Blueprint, request, send_file, jsonify
from services.pdf import StudentReportGenerator, ClassReportGenerator
import tempfile
import os
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Initialize generators
student_gen = StudentReportGenerator()
class_gen = ClassReportGenerator()


@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    """Generate student report PDF"""
    try:
        # Get request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'student_data' not in data:
            return jsonify({'error': 'Missing student_data field'}), 400
        
        # Generate PDF
        success, result = student_gen.generate(
            student_data=data['student_data'],
            school_info=data.get('school_info')
        )
        
        if not success:
            return jsonify({
                'error': 'PDF generation failed',
                'details': result
            }), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        # Create filename
        student_name = data['student_data']['student']['name']
        safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)
        filename = f"student_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return PDF
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    """Generate class report PDF"""
    try:
        # Get request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'class_data' not in data:
            return jsonify({'error': 'Missing class_data field'}), 400
        
        # Generate PDF
        success, result = class_gen.generate(
            class_data=data['class_data'],
            school_info=data.get('school_info')
        )
        
        if not success:
            return jsonify({
                'error': 'PDF generation failed',
                'details': result
            }), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        # Create filename
        class_id = data['class_data']['metadata'].get('class_id', 'class')
        safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)
        filename = f"class_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return PDF
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@pdf_routes.route('/api/pdf/status', methods=['GET'])
def status():
    """Check PDF service status"""
    return jsonify({
        'success': True,
        'service': 'pdf_generation',
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })