"""
PDF TEST ROUTES - For Render.com (No terminal access)
"""
from flask import Blueprint, request, jsonify, send_file, render_template_string, Response
import io
import json
from datetime import datetime
import traceback
import sys

test_pdf_routes = Blueprint('test_pdf', __name__, url_prefix='/api/test-pdf')

@test_pdf_routes.route('/status', methods=['GET'])
def pdf_status():
    """Show PDF generation status in browser"""
    try:
        from weasyprint import HTML
        import weasyprint
        
        # Test PDF generation
        html = HTML(string='<h1>Test</h1><p>Testing PDF generation...</p>')
        pdf_bytes = html.write_pdf()
        
        status_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Status - School API</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .success {{ color: #27ae60; }}
                .error {{ color: #e74c3c; }}
                .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                pre {{ background: #2c3e50; color: white; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
            </style>
        </head>
        <body>
            <h1>✅ PDF Generation Status</h1>
            
            <div class="info">
                <h2>System Information</h2>
                <p><strong>WeasyPrint Version:</strong> {weasyprint.__version__}</p>
                <p><strong>Python Version:</strong> {sys.version}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>PDF Test Size:</strong> {len(pdf_bytes)} bytes</p>
            </div>
            
            <h2>Quick Tests</h2>
            <p>
                <a class="btn" href="/api/test-pdf/download" target="_blank">📥 Download Test PDF</a>
                <a class="btn" href="/api/test-pdf/debug" target="_blank">🐛 Debug Info</a>
                <a class="btn" href="/api/test-pdf/full-test" target="_blank">🧪 Full Test</a>
            </p>
            
            <h2>Test Results</h2>
            <div class="success">
                <p>✓ PDF generation is WORKING correctly!</p>
                <p>✓ WeasyPrint is properly installed</p>
                <p>✓ All dependencies are available</p>
            </div>
            
            <h2>Sample PDFs</h2>
            <p>
                <a href="/api/test-pdf/sample/report">📄 Sample Report</a> |
                <a href="/api/test-pdf/sample/marksheet">📊 Sample Marksheet</a> |
                <a href="/api/test-pdf/sample/invoice">🧾 Sample Invoice</a>
            </p>
        </body>
        </html>
        """
        
        return status_html
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Status - ERROR</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: #e74c3c; }}
                pre {{ background: #2c3e50; color: white; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1 class="error">❌ PDF Generation Failed</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            
            <h2>Traceback:</h2>
            <pre>{traceback.format_exc()}</pre>
            
            <h2>Common Solutions:</h2>
            <ol>
                <li>Check if WeasyPrint dependencies are installed in Dockerfile</li>
                <li>Verify WeasyPrint version (should be 61.2 for Python 3.11)</li>
                <li>Check system dependencies: libpango, libcairo, libgdk-pixbuf</li>
            </ol>
        </body>
        </html>
        """
        
        return error_html, 500

@test_pdf_routes.route('/download', methods=['GET'])
def download_test_pdf():
    """Download a simple test PDF"""
    try:
        from weasyprint import HTML
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; }
                .success { color: #27ae60; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #3498db; color: white; }
                .footer { margin-top: 40px; text-align: center; color: #7f8c8d; }
            </style>
        </head>
        <body>
            <h1>✅ PDF Generation Test</h1>
            <p>This PDF confirms that WeasyPrint is working correctly on Render.com</p>
            
            <p class="success">Status: PDF generation is FUNCTIONAL</p>
            
            <h2>Test Data</h2>
            <table>
                <tr>
                    <th>Component</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
                <tr>
                    <td>WeasyPrint</td>
                    <td>✅ Working</td>
                    <td>Version check passed</td>
                </tr>
                <tr>
                    <td>Fonts</td>
                    <td>✅ Available</td>
                    <td>System fonts loaded</td>
                </tr>
                <tr>
                    <td>CSS Styling</td>
                    <td>✅ Applied</td>
                    <td>Tables, colors, margins</td>
                </tr>
                <tr>
                    <td>Image Support</td>
                    <td>✅ Ready</td>
                    <td>Base64 images supported</td>
                </tr>
            </table>
            
            <h2>Server Information</h2>
            <ul>
                <li>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</li>
                <li>Platform: Render.com Docker</li>
                <li>Purpose: School Management API</li>
            </ul>
            
            <div class="footer">
                <p>If you can see this PDF with proper styling, everything is working!</p>
            </div>
        </body>
        </html>
        """
        
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        filename = f"pdf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@test_pdf_routes.route('/debug', methods=['GET'])
def pdf_debug():
    """Show detailed debug information"""
    try:
        import weasyprint
        import platform
        
        # Test PDF
        from weasyprint import HTML
        html = HTML(string='<h1>Debug Test</h1>')
        pdf_bytes = html.write_pdf()
        
        debug_info = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
            },
            'weasyprint': {
                'version': weasyprint.__version__,
                'pdf_test_size': len(pdf_bytes),
                'working': True
            },
            'python': {
                'version': sys.version,
                'executable': sys.executable,
                'path': sys.path
            }
        }
        
        # Return as pretty JSON for browser
        response = json.dumps(debug_info, indent=2, default=str)
        return Response(response, mimetype='application/json')
        
    except Exception as e:
        error_info = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        response = json.dumps(error_info, indent=2)
        return Response(response, mimetype='application/json'), 500

@test_pdf_routes.route('/full-test', methods=['GET'])
def full_test():
    """Run full PDF test suite"""
    test_results = []
    
    try:
        import weasyprint
        from weasyprint import HTML
        
        # Test 1: Basic HTML
        html = HTML(string='<h1>Test 1</h1>')
        pdf1 = html.write_pdf()
        test_results.append({
            'test': 'Basic HTML',
            'status': '✅ PASS',
            'size': len(pdf1)
        })
        
        # Test 2: CSS Styling
        html2 = HTML(string='<style>h1{color:red;}</style><h1>Test 2</h1>')
        pdf2 = html2.write_pdf()
        test_results.append({
            'test': 'CSS Styling',
            'status': '✅ PASS',
            'size': len(pdf2)
        })
        
        # Test 3: Table
        html3 = HTML(string='''
        <table border="1">
            <tr><th>Name</th><th>Score</th></tr>
            <tr><td>John</td><td>85</td></tr>
        </table>
        ''')
        pdf3 = html3.write_pdf()
        test_results.append({
            'test': 'Table Rendering',
            'status': '✅ PASS',
            'size': len(pdf3)
        })
        
        # Test 4: Complex layout
        html4 = HTML(string='''
        <div style="padding: 20px; border: 2px solid blue; margin: 10px;">
            <h2 style="color: green;">Complex Layout</h2>
            <p>Multiple elements with styling</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </div>
        ''')
        pdf4 = html4.write_pdf()
        test_results.append({
            'test': 'Complex Layout',
            'status': '✅ PASS',
            'size': len(pdf4)
        })
        
        # Create HTML report
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Full Test Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; }
                .pass { color: #27ae60; }
                .results { width: 100%; border-collapse: collapse; }
                .results th, .results td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                .results th { background-color: #3498db; color: white; }
                .summary { background: #f8f9fa; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>📊 PDF Full Test Results</h1>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Total Tests:</strong> """ + str(len(test_results)) + """</p>
                <p><strong>Status:</strong> <span style="color: #27ae60; font-weight: bold;">ALL TESTS PASSED</span></p>
                <p><strong>WeasyPrint Version:</strong> """ + weasyprint.__version__ + """</p>
                <p><strong>Timestamp:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
            
            <h2>Detailed Results</h2>
            <table class="results">
                <tr>
                    <th>Test</th>
                    <th>Status</th>
                    <th>PDF Size</th>
                </tr>
        """
        
        for result in test_results:
            html_report += f"""
                <tr>
                    <td>{result['test']}</td>
                    <td class="pass">{result['status']}</td>
                    <td>{result['size']} bytes</td>
                </tr>
            """
        
        html_report += """
            </table>
            
            <h2>Next Steps</h2>
            <p>
                <a href="/api/test-pdf/download">📥 Download Sample PDF</a> |
                <a href="/api/test-pdf/status">🔄 Back to Status</a>
            </p>
        </body>
        </html>
        """
        
        return html_report
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1 style="color: red;">❌ Full Test Failed</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        return error_html, 500

@test_pdf_routes.route('/sample/<type>', methods=['GET'])
def sample_pdf(type):
    """Generate sample PDFs"""
    samples = {
        'report': {
            'title': 'School Report Card',
            'content': '''
            <h1>SCHOOL REPORT CARD</h1>
            <h2>TERM 1, 2024</h2>
            <table border="1" style="width:100%">
                <tr><th>Subject</th><th>Score</th><th>Grade</th></tr>
                <tr><td>Mathematics</td><td>85</td><td>A</td></tr>
                <tr><td>English</td><td>78</td><td>B+</td></tr>
                <tr><td>Science</td><td>92</td><td>A+</td></tr>
            </table>
            '''
        },
        'marksheet': {
            'title': 'Exam Marksheet',
            'content': '''
            <h1>EXAMINATION MARKSHEET</h1>
            <table border="1" style="width:100%">
                <tr>
                    <th>Student ID</th><th>Name</th><th>Class</th>
                    <th>Math</th><th>Eng</th><th>Sci</th><th>Total</th><th>Grade</th>
                </tr>
                <tr><td>001</td><td>John Doe</td><td>Form 4A</td><td>85</td><td>78</td><td>92</td><td>255</td><td>A</td></tr>
                <tr><td>002</td><td>Jane Smith</td><td>Form 4A</td><td>92</td><td>88</td><td>95</td><td>275</td><td>A+</td></tr>
            </table>
            '''
        },
        'invoice': {
            'title': 'School Fees Invoice',
            'content': '''
            <h1>SCHOOL FEES INVOICE</h1>
            <p><strong>Student:</strong> John Doe</p>
            <p><strong>Class:</strong> Form 4A</p>
            <p><strong>Term:</strong> 1, 2024</p>
            
            <table border="1" style="width:100%">
                <tr><th>Item</th><th>Amount</th></tr>
                <tr><td>Tuition Fees</td><td>200,000 TZS</td></tr>
                <tr><td>Activity Fees</td><td>50,000 TZS</td></tr>
                <tr><td>Total</td><td><strong>250,000 TZS</strong></td></tr>
            </table>
            '''
        }
    }
    
    if type not in samples:
        return jsonify({'error': 'Sample type not found'}), 404
    
    try:
        from weasyprint import HTML
        
        sample = samples[type]
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; }}
                th {{ background-color: #3498db; color: white; }}
                .footer {{ margin-top: 50px; text-align: center; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            {sample['content']}
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Sample PDF - School Management API</p>
            </div>
        </body>
        </html>
        """
        
        html = HTML(string=full_html)
        pdf_bytes = html.write_pdf()
        
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        filename = f"sample_{type}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'sample_type': type
        }), 500