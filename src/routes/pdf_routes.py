"""
PDF ROUTES - CLEAN & RELIABLE
Separate endpoints with proper validation
"""
from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import sys
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Import PDF generators
try:
    from services.pdf.student_report import StudentReportGenerator
    from services.pdf.class_report import ClassReportGenerator
    
    student_gen = StudentReportGenerator()
    class_gen = ClassReportGenerator()
    IMPORT_SUCCESS = True
    
except ImportError as e:
    # If import fails, service is unavailable
    student_gen = None
    class_gen = None
    IMPORT_SUCCESS = False


@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    """
    Generate student report PDF
    Returns: PDF if successful, JSON error if failed
    """
    # Check if service is available
    if not IMPORT_SUCCESS or student_gen is None:
        return jsonify({
            'success': False,
            'error': 'PDF service unavailable',
            'message': 'Student report service is currently unavailable'
        }), 503
    
    # Validate request
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Invalid content type',
            'message': 'Content-Type must be application/json'
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'message': 'Request body is empty'
        }), 400
    
    if 'student_data' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required field',
            'message': 'student_data field is required'
        }), 400
    
    # Generate PDF
    success, result = student_gen.generate(
        student_data=data['student_data'],
        school_info=data.get('school_info')
    )
    
    if not success:
        # Return JSON error - no PDF
        return jsonify({
            'success': False,
            'error': 'PDF generation failed',
            'details': result,
            'message': 'Cannot generate PDF with provided data'
        }), 400
    
    # Success - return PDF
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        # Generate filename
        student_name = data['student_data'].get('student', {}).get('name', 'student')
        safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)[:50]
        filename = f"student_report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
            'success': False,
            'error': 'File creation failed',
            'message': str(e)
        }), 500


@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    """
    Generate class report PDF
    Returns: PDF if successful, JSON error if failed
    """
    # Check if service is available
    if not IMPORT_SUCCESS or class_gen is None:
        return jsonify({
            'success': False,
            'error': 'PDF service unavailable',
            'message': 'Class report service is currently unavailable'
        }), 503
    
    # Validate request
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Invalid content type',
            'message': 'Content-Type must be application/json'
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'message': 'Request body is empty'
        }), 400
    
    if 'class_data' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required field',
            'message': 'class_data field is required'
        }), 400
    
    # Generate PDF
    success, result = class_gen.generate(
        class_data=data['class_data'],
        school_info=data.get('school_info')
    )
    
    if not success:
        # Return JSON error - no PDF
        return jsonify({
            'success': False,
            'error': 'PDF generation failed',
            'details': result,
            'message': 'Cannot generate PDF with provided data'
        }), 400
    
    # Success - return PDF
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        # Generate filename
        class_id = data['class_data'].get('metadata', {}).get('class_id', 'class')
        safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)[:50]
        filename = f"class_report_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
            'success': False,
            'error': 'File creation failed',
            'message': str(e)
        }), 500


@pdf_routes.route('/api/pdf/status', methods=['GET'])
def service_status():
    """Get PDF service status"""
    return jsonify({
        'success': True,
        'service': 'pdf_generation',
        'status': 'available' if IMPORT_SUCCESS else 'unavailable',
        'student_report': 'available' if student_gen else 'unavailable',
        'class_report': 'available' if class_gen else 'unavailable',
        'timestamp': datetime.now().isoformat()
    })