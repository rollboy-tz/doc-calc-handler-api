"""
Basic PDF Generation Tests
"""
import pytest
import io
from weasyprint import HTML

def test_weasyprint_import():
    """Test if WeasyPrint can be imported"""
    import weasyprint
    assert weasyprint.__version__ is not None
    print(f"✅ WeasyPrint version: {weasyprint.__version__}")

def test_simple_pdf_generation():
    """Test basic PDF generation"""
    html = HTML(string='<h1>Test PDF</h1><p>Hello World</p>')
    pdf_bytes = html.write_pdf()
    
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 100  # PDF should be more than 100 bytes
    print(f"✅ Generated PDF: {len(pdf_bytes)} bytes")

def test_pdf_with_css():
    """Test PDF with CSS styling"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; margin: 40px; }
            h1 { color: #3498db; }
            .test { border: 1px solid #ddd; padding: 20px; }
        </style>
    </head>
    <body>
        <h1>CSS Test</h1>
        <div class="test">Styled content</div>
    </body>
    </html>
    """
    
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    
    assert len(pdf_bytes) > 100
    print(f"✅ PDF with CSS: {len(pdf_bytes)} bytes")

def test_pdf_with_table():
    """Test PDF with table"""
    html_content = """
    <h1>Student Marks</h1>
    <table border="1" style="width:100%">
        <tr>
            <th>Name</th>
            <th>Subject</th>
            <th>Score</th>
        </tr>
        <tr>
            <td>John Doe</td>
            <td>Math</td>
            <td>85</td>
        </tr>
        <tr>
            <td>Jane Smith</td>
            <td>Science</td>
            <td>92</td>
        </tr>
    </table>
    """
    
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    
    assert len(pdf_bytes) > 100
    print(f"✅ PDF with table: {len(pdf_bytes)} bytes")

@pytest.mark.skipif(not weasyprint_available, reason="WeasyPrint not installed")
class TestFlaskPDFEndpoints:
    """Test Flask PDF endpoints"""
    
    def test_pdf_health_endpoint(self, client):
        """Test /api/test/health endpoint"""
        response = client.get('/api/test/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'weasyprint_version' in data
        print(f"✅ Health endpoint: {data['weasyprint_version']}")
    
    def test_pdf_generation_endpoint(self, client):
        """Test /api/test/pdf endpoint"""
        response = client.get('/api/test/pdf')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'
        assert len(response.data) > 1000  # PDF should be substantial
        
        # Save for manual verification
        with open('/tmp/test_flask_output.pdf', 'wb') as f:
            f.write(response.data)
        print(f"✅ Flask PDF endpoint: {len(response.data)} bytes")
    
    def test_pdf_debug_endpoint(self, client):
        """Test /api/test/debug endpoint"""
        response = client.get('/api/test/debug')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'python_version' in data['debug_info']
        print(f"✅ Debug endpoint works")

if __name__ == '__main__':
    # Run tests manually
    print("🧪 Running PDF tests...")
    
    try:
        test_weasyprint_import()
        test_simple_pdf_generation()
        test_pdf_with_css()
        test_pdf_with_table()
        print("\n🎉 All basic tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()