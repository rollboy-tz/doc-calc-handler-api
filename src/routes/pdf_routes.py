"""
PDF ROUTES - WITH ERROR HANDLING
"""
from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import sys
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Fix imports - handle gracefully
try:
    # Try to import PDF generators
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from services.pdf import StudentReportGenerator, ClassReportGenerator
    
    # Create instances
    student_gen = StudentReportGenerator()
    class_gen = ClassReportGenerator()
    
    IMPORT_SUCCESS = True
    print("✓ PDF generators loaded successfully")
    
except ImportError as e:
    # If import fails, create simple fallback generators
    print(f"⚠️ PDF import failed, using fallback: {e}")
    
    class FallbackPDFGenerator:
        def generate(self, data, school_info=None):
            from weasyprint import HTML
            html_content = """
            <!DOCTYPE html>
            <html>
            <head><style>body { font-family: Arial; padding: 40px; text-align: center; }</style></head>
            <body>
                <h1>📚 School Report</h1>
                <p>PDF service is currently in fallback mode.</p>
                <p>Full service will be restored shortly.</p>
                <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """</p>
            </body>
            </html>
            """
            return HTML(string=html_content).write_pdf()
    
    student_gen = FallbackPDFGenerator()
    class_gen = FallbackPDFGenerator()
    IMPORT_SUCCESS = False


def safe_pdf_generation(route_func):
    """Decorator to ensure PDF generation never crashes the service"""
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except Exception as e:
            # Log error but don't crash
            print(f"PDF Route Error (service continues): {e}")
            
            # Generate error PDF
            try:
                from weasyprint import HTML
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><style>
                    body {{ font-family: Arial; padding: 40px; text-align: center; }}
                    .error {{ color: #e74c3c; }}
                </style></head>
                <body>
                    <h1>⚠️ Service Error</h1>
                    <p class="error">PDF generation failed but service is still running.</p>
                    <p>Error: {str(e)[:200]}</p>
                    <p>Please try again in a moment.</p>
                    <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
                </html>
                """
                
                html = HTML(string=html_content)
                pdf_bytes = html.write_pdf()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(pdf_bytes)
                    tmp_path = tmp.name
                
                return send_file(
                    tmp_path,
                    as_attachment=True,
                    download_name='error_report.pdf',
                    mimetype='application/pdf'
                )
                
            except Exception as inner_e:
                # If even error PDF fails, return JSON error
                print(f"Critical PDF error: {inner_e}")
                return jsonify({
                    'success': False,
                    'error': 'PDF service error',
                    'service_status': 'still_running',
                    'timestamp': datetime.now().isoformat()
                }), 500
    
    # Preserve original function name
    wrapper.__name__ = route_func.__name__
    return wrapper


@pdf_routes.route('/api/pdf/student', methods=['POST'])
@safe_pdf_generation
def generate_student_pdf():
    """Generate student report PDF"""
    # Get request data
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'student_data' not in data:
        return jsonify({'error': 'Missing student_data field'}), 400
    
    # Generate PDF
    pdf_bytes = student_gen.generate(
        student_data=data['student_data'],
        school_info=data.get('school_info', {})
    )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    
    # Create filename
    student_name = data['student_data'].get('student', {}).get('name', 'student')
    safe_name = ''.join(c if c.isalnum() else '_' for c in student_name)[:50]
    filename = f"student_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Return PDF
    response = send_file(
        tmp_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
    
    # Clean up (optional)
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return response


@pdf_routes.route('/api/pdf/class', methods=['POST'])
@safe_pdf_generation
def generate_class_pdf():
    """Generate class report PDF"""
    # Get request data
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'class_data' not in data:
        return jsonify({'error': 'Missing class_data field'}), 400
    
    # Generate PDF
    pdf_bytes = class_gen.generate(
        class_data=data['class_data'],
        school_info=data.get('school_info', {})
    )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    
    # Create filename
    class_id = data['class_data'].get('metadata', {}).get('class_id', 'class')
    safe_id = ''.join(c if c.isalnum() else '_' for c in class_id)[:50]
    filename = f"class_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Return PDF
    response = send_file(
        tmp_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
    
    # Clean up (optional)
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return response


@pdf_routes.route('/api/pdf/test', methods=['GET'])
@safe_pdf_generation
def test_pdf():
    """Test endpoint with sample data"""
    # Sample data
    sample_data = {
        'student': {
            'name': 'Test Student',
            'admission': 'STD001',
            'gender': 'M',
            'class': 'Form 4A'
        },
        'subjects': {
            'Mathematics': {'marks': 85, 'grade': 'A', 'pass': True},
            'English': {'marks': 78, 'grade': 'B', 'pass': True},
            'Physics': {'marks': 65, 'grade': 'C', 'pass': True}
        },
        'summary': {
            'average': 76,
            'grade': 'B',
            'division': 'I',
            'rank': 5,
            'status': 'PASS'
        }
    }
    
    pdf_bytes = student_gen.generate(sample_data)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    
    return send_file(
        tmp_path,
        as_attachment=True,
        download_name='test_report.pdf',
        mimetype='application/pdf'
    )


@pdf_routes.route('/api/pdf/status', methods=['GET'])
def status():
    """Check PDF service status"""
    return jsonify({
        'success': True,
        'status': 'active',
        'pdf_service': 'operational' if IMPORT_SUCCESS else 'fallback_mode',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            'POST /api/pdf/student - Generate student report',
            'POST /api/pdf/class - Generate class report',
            'GET /api/pdf/test - Test endpoint',
            'GET /api/pdf/status - Service status'
        ]
    })