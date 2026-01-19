"""
PDF GENERATION ROUTES - SIMPLE TEST
"""
from flask import Blueprint, request, jsonify, send_file, render_template_string
import tempfile
import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io

pdf_routes = Blueprint('pdf', __name__, url_prefix='/api/pdf')

# Simple HTML template for testing
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .content {
            line-height: 1.6;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }
        .test-box {
            border: 1px solid #ddd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>Test PDF - {{ title }}</h1>
    
    <div class="content">
        <p>Generated on: {{ timestamp }}</p>
        <p>This is a test PDF generated with WeasyPrint.</p>
        
        <div class="test-box">
            <h3>Test Box</h3>
            <p>If you can see this box with borders and background color, 
            then CSS is working correctly.</p>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
                <li>List item 3</li>
            </ul>
        </div>
        
        <p>If everything works, you should be able to download this as a PDF file.</p>
    </div>
    
    <div class="footer">
        Page <span class="pageNumber"></span> of <span class="totalPages"></span>
    </div>
</body>
</html>
"""

@pdf_routes.route('/test', methods=['GET'])
def test_pdf():
    """Simple test endpoint to generate PDF"""
    try:
        # Create simple HTML content
        html_content = SIMPLE_HTML
        
        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        
        # Generate PDF bytes
        pdf_bytes = html.write_pdf()
        
        # Save to BytesIO
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        # Return as file
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='test.pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'PDF generation failed. Check WeasyPrint installation.'
        }), 500

@pdf_routes.route('/custom', methods=['POST'])
def generate_custom_pdf():
    """Generate PDF from custom HTML"""
    try:
        data = request.json or {}
        
        # Get HTML content from request
        html_content = data.get('html', '<h1>No HTML provided</h1><p>Test PDF</p>')
        
        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        
        # Generate PDF bytes
        pdf_bytes = html.write_pdf()
        
        # Save to BytesIO
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        # Return as file
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@pdf_routes.route('/health', methods=['GET'])
def pdf_health():
    """Check if PDF generation is working"""
    try:
        # Try to import WeasyPrint
        from weasyprint import HTML
        import weasyprint
        
        # Simple test HTML
        test_html = "<h1>Health Check</h1><p>WeasyPrint version: " + weasyprint.__version__ + "</p>"
        
        # Try to generate a tiny PDF
        html = HTML(string=test_html)
        pdf_bytes = html.write_pdf()
        
        return jsonify({
            'success': True,
            'message': 'PDF generation is working',
            'weasyprint_version': weasyprint.__version__,
            'test_pdf_size': len(pdf_bytes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'PDF generation is not working properly'
        }), 500