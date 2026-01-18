"""
PDF ROUTES
Simple endpoints for PDF generation
"""
from flask import Blueprint, request, send_file
from services.pdf import StudentReportGenerator, ClassReportGenerator
from datetime import datetime
import tempfile

pdf_routes = Blueprint('pdf', __name__)

# Initialize generators
student_gen = StudentReportGenerator()
class_gen = ClassReportGenerator()


@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    """Generate student report PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return {'error': 'No data provided'}, 400
        
        if 'student_data' not in data:
            return {'error': 'Missing student_data field'}, 400
        
        # Generate PDF
        pdf_bytes = student_gen.generate(
            student_data=data['student_data'],
            school_info=data.get('school_info')
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Get student name for filename
        student_name = data['student_data']['student']['name']
        safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)
        filename = f"student_report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return PDF file
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return {'error': str(e)}, 500


@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    """Generate class report PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return {'error': 'No data provided'}, 400
        
        if 'class_data' not in data:
            return {'error': 'Missing class_data field'}, 400
        
        # Generate PDF
        pdf_bytes = class_gen.generate(
            class_data=data['class_data'],
            school_info=data.get('school_info')
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Get class ID for filename
        class_id = data['class_data']['metadata'].get('class_id', 'class')
        safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)
        filename = f"class_report_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return PDF file
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return {'error': str(e)}, 500


@pdf_routes.route('/api/pdf/status', methods=['GET'])
def status():
    """Check PDF service status"""
    return {
        'status': 'active',
        'service': 'pdf_generation',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'student_report': 'POST /api/pdf/student',
            'class_report': 'POST /api/pdf/class'
        }
    }