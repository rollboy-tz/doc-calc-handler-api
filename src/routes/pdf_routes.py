"""
PDF ROUTES - FIXED CLASS INITIALIZATION
"""
from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import sys
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import the CLASSES, not instances
    from services.pdf.student_report import StudentReportGenerator
    from services.pdf.class_report import ClassReportGenerator
    
    # Create instances HERE, not in the imported module
    student_gen = StudentReportGenerator()  # Create instance
    class_gen = ClassReportGenerator()      # Create instance
    
    IMPORT_SUCCESS = True
    print("✓ PDF generators imported successfully")
    
except ImportError as e:
    print(f"✗ PDF Import Error: {e}")
    
    # Create simple fallback generators
    class SimplePDFGenerator:
        def generate(self, data, school_info=None):
            from weasyprint import HTML
            name = data.get('student', {}).get('name', 'Unknown') if 'student' in data else 'Class Report'
            html_content = f"<h1>Report for {name}</h1><p>Generated successfully</p>"
            html = HTML(string=html_content)
            return html.write_pdf()
    
    student_gen = SimplePDFGenerator()
    class_gen = SimplePDFGenerator()
    IMPORT_SUCCESS = False


@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    """Generate student report PDF"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json', 'success': False}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        if 'student_data' not in data:
            return jsonify({'error': 'Missing student_data field', 'success': False}), 400
        
        # Validate required fields
        student_data = data['student_data']
        required = ['student', 'subjects', 'summary']
        for field in required:
            if field not in student_data:
                return jsonify({'error': f'Missing {field} in student_data', 'success': False}), 400
        
        # Generate PDF
        print(f"Generating PDF for student: {student_data['student']['name']}")
        pdf_bytes = student_gen.generate(
            student_data=student_data,
            school_info=data.get('school_info', {})
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Create filename
        student_name = student_data['student']['name']
        safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"student_{safe_name}_{timestamp}.pdf"
        
        # Return PDF file
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Clean up temp file after sending
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return response
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF Generation Error: {error_details}")
        
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500


@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    """Generate class report PDF"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json', 'success': False}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        if 'class_data' not in data:
            return jsonify({'error': 'Missing class_data field', 'success': False}), 400
        
        # Validate required fields
        class_data = data['class_data']
        required = ['metadata', 'students']
        for field in required:
            if field not in class_data:
                return jsonify({'error': f'Missing {field} in class_data', 'success': False}), 400
        
        # Generate PDF
        print(f"Generating PDF for class: {class_data['metadata'].get('class_id', 'Unknown')}")
        pdf_bytes = class_gen.generate(
            class_data=class_data,
            school_info=data.get('school_info', {})
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Create filename
        class_id = class_data['metadata'].get('class_id', 'class')
        safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"class_{safe_id}_{timestamp}.pdf"
        
        # Return PDF file
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return response
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF Generation Error: {error_details}")
        
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500


@pdf_routes.route('/api/pdf/test', methods=['GET'])
def test_pdf():
    """Test endpoint with sample data"""
    try:
        # Sample student data
        sample_student = {
            'student': {
                'name': 'John Doe',
                'admission': 'STD001',
                'gender': 'M',
                'class': 'Form 4A'
            },
            'subjects': {
                'Mathematics': {'marks': 85, 'grade': 'A', 'points': 1, 'pass': True},
                'English': {'marks': 78, 'grade': 'B', 'points': 2, 'pass': True},
                'Physics': {'marks': 65, 'grade': 'C', 'points': 3, 'pass': True}
            },
            'summary': {
                'total': 228,
                'average': 76,
                'grade': 'B',
                'division': 'I',
                'rank': 5,
                'status': 'PASS'
            }
        }
        
        # Generate PDF
        pdf_bytes = student_gen.generate(sample_student)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        # Return file
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name='test_student_report.pdf',
            mimetype='application/pdf'
        )
        
        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return response
        
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
        'endpoints': [
            'POST /api/pdf/student - Generate student report',
            'POST /api/pdf/class - Generate class report',
            'GET /api/pdf/test - Test PDF generation',
            'GET /api/pdf/status - Service status'
        ]
    })