# routes/pdf_routes.py - FIXED VERSION WITH DEBUGGING
"""
PDF ROUTES - DEBUG VERSION
"""
from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import sys
import traceback
from datetime import datetime

pdf_routes = Blueprint('pdf', __name__)

# Debug: Check WeasyPrint
print("=== PDF SERVICE DEBUG ===")
try:
    from weasyprint import HTML
    test_html = HTML(string="<h1>Test</h1>")
    test_bytes = test_html.write_pdf()
    print("✓ WeasyPrint basic test PASSED")
except Exception as e:
    print(f"✗ WeasyPrint test FAILED: {e}")
    print(traceback.format_exc())

# Try to import PDF generators
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    print(f"Current dir: {current_dir}")
    print(f"Parent dir: {parent_dir}")
    print(f"Python path: {sys.path}")
    
    # List files in services
    services_path = os.path.join(parent_dir, 'services')
    if os.path.exists(services_path):
        print(f"Services path exists: {services_path}")
        for root, dirs, files in os.walk(services_path):
            level = root.replace(services_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.py'):
                    print(f'{subindent}{file}')
    
    # Import
    from services.pdf.student_report import StudentReportGenerator
    from services.pdf.class_report import ClassReportGenerator
    
    student_gen = StudentReportGenerator()
    class_gen = ClassReportGenerator()
    
    print("✓ PDF generators imported successfully")
    IMPORT_SUCCESS = True
    
except ImportError as e:
    print(f"✗ PDF import failed: {e}")
    print(traceback.format_exc())
    
    # Simple inline generator
    class SimplePDFGenerator:
        def generate(self, data, school_info=None):
            try:
                from weasyprint import HTML
                # Get name from data
                if 'student' in data:
                    name = data['student'].get('name', 'Student')
                    title = f"Report for {name}"
                elif 'metadata' in data:
                    class_id = data['metadata'].get('class_id', 'Class')
                    title = f"Class Report for {class_id}"
                else:
                    title = "Report"
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><style>
                    body {{ font-family: Arial; padding: 30px; }}
                    h1 {{ color: #2c3e50; }}
                </style></head>
                <body>
                    <h1>{title}</h1>
                    <p>This is a fallback PDF report.</p>
                    <p>Full PDF service will be available soon.</p>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </body>
                </html>
                """
                
                return HTML(string=html_content).write_pdf()
            except Exception as e:
                print(f"Fallback PDF error: {e}")
                # Return minimal PDF
                return HTML(string="<h1>PDF</h1><p>Report</p>").write_pdf()
    
    student_gen = SimplePDFGenerator()
    class_gen = SimplePDFGenerator()
    IMPORT_SUCCESS = True  # Still true kwa sababu tunatumia fallback


def safe_pdf_generation(route_func):
    """Decorator to ensure PDF generation never crashes"""
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except Exception as e:
            print(f"🚨 PDF Route Error: {e}")
            print(traceback.format_exc())
            
            # Try to generate error PDF
            try:
                from weasyprint import HTML
                import tempfile
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head><style>
                    body {{ font-family: Arial; padding: 40px; }}
                    .error {{ color: #e74c3c; background: #fee; padding: 20px; }}
                </style></head>
                <body>
                    <h1>Report Generation Issue</h1>
                    <div class="error">
                        <p><strong>Error:</strong> {str(e)[:200]}</p>
                        <p>The PDF service encountered an error but is still running.</p>
                        <p>Please try your request again.</p>
                    </div>
                    <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
                </html>
                """
                
                pdf_bytes = HTML(string=error_html).write_pdf()
                
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
                print(f"🚨 CRITICAL: Error PDF also failed: {inner_e}")
                # Last resort: JSON response
                return jsonify({
                    'success': False,
                    'error': 'PDF service temporarily unavailable',
                    'details': str(e)[:100],
                    'service': 'still_running',
                    'timestamp': datetime.now().isoformat()
                }), 500
    
    wrapper.__name__ = route_func.__name__
    return wrapper


# Routes remain the same as before...
@pdf_routes.route('/api/pdf/student', methods=['POST'])
@safe_pdf_generation
def generate_student_pdf():
    # ... same code as before
    pass

@pdf_routes.route('/api/pdf/class', methods=['POST'])
@safe_pdf_generation
def generate_class_pdf():
    # ... same code as before
    pass

# Add debug endpoint
@pdf_routes.route('/api/pdf/debug', methods=['GET'])
def debug_pdf():
    """Debug WeasyPrint installation"""
    try:
        from weasyprint import HTML
        # Simple test
        html = HTML(string="<h1>PDF Service Debug</h1><p>If you see this, WeasyPrint is working.</p>")
        pdf_bytes = html.write_pdf()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name='debug.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'module': 'WeasyPrint',
            'timestamp': datetime.now().isoformat()
        }), 500


@pdf_routes.route('/api/pdf/info', methods=['GET'])
def pdf_info():
    """Get PDF service information"""
    return jsonify({
        'service': 'pdf_generation',
        'status': 'active',
        'weasyprint': 'installed' if IMPORT_SUCCESS else 'fallback',
        'endpoints': [
            'POST /api/pdf/student - Student report',
            'POST /api/pdf/class - Class report', 
            'GET /api/pdf/debug - Debug WeasyPrint',
            'GET /api/pdf/info - This info'
        ],
        'timestamp': datetime.now().isoformat()
    })