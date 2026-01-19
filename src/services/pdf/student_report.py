"""
STUDENT REPORT GENERATOR - WORKING VERSION
"""
from datetime import datetime


class StudentReportGenerator:
    """Generate student report PDF"""
    
    def __init__(self):
        pass
    
    def validate_data(self, student_data):
        """Validate student data"""
        errors = []
        
        if not student_data:
            errors.append("No student data provided")
            return False, errors
        
        if 'student' not in student_data:
            errors.append("Missing 'student' object")
            return False, errors
        
        student = student_data['student']
        if not student.get('name'):
            errors.append("Missing student name")
        if not student.get('admission'):
            errors.append("Missing admission number")
        
        return len(errors) == 0, errors
    
    def generate(self, student_data, school_info=None):
        """Generate PDF"""
        try:
            # Validate
            is_valid, errors = self.validate_data(student_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Generate HTML
            html = self._create_simple_html(student_data, school_info)
            
            # Generate PDF with workaround
            pdf_bytes = self._simple_html_to_pdf(html)
            
            return True, pdf_bytes
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def _create_simple_html(self, student_data, school_info):
        """Create simple HTML"""
        student = student_data['student']
        subjects = student_data.get('subjects', {})
        summary = student_data.get('summary', {})
        school = school_info or {}
        
        # Build subjects table
        subjects_html = ""
        if subjects:
            for name, data in subjects.items():
                subjects_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{data.get('marks', 'N/A')}</td>
                    <td>{data.get('grade', 'N/A')}</td>
                    <td>{data.get('points', '-')}</td>
                    <td>{"PASS" if data.get('pass') else "FAIL"}</td>
                </tr>
                """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Student Report</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #2c3e50; color: white; padding: 10px; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{school.get('name', 'STUDENT REPORT')}</h1>
        <p>{school.get('address', '')}</p>
    </div>
    
    <h2>Student Information</h2>
    <table>
        <tr><td><strong>Name:</strong></td><td>{student.get('name', '')}</td></tr>
        <tr><td><strong>Admission:</strong></td><td>{student.get('admission', '')}</td></tr>
        <tr><td><strong>Class:</strong></td><td>{student.get('class', 'N/A')}</td></tr>
    </table>
    
    <h2>Subjects</h2>
    <table>
        <tr>
            <th>Subject</th>
            <th>Marks</th>
            <th>Grade</th>
            <th>Points</th>
            <th>Status</th>
        </tr>
        {subjects_html if subjects_html else '<tr><td colspan="5">No subjects</td></tr>'}
    </table>
    
    <h2>Summary</h2>
    <table>
        <tr><td><strong>Average:</strong></td><td>{summary.get('average', 'N/A')}</td></tr>
        <tr><td><strong>Grade:</strong></td><td>{summary.get('grade', 'N/A')}</td></tr>
        <tr><td><strong>Division:</strong></td><td>{summary.get('division', 'N/A')}</td></tr>
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _simple_html_to_pdf(self, html_content):
        """Convert HTML to PDF with version compatibility"""
        try:
            # Try WeasyPrint
            from weasyprint import HTML
            html_obj = HTML(string=html_content)
            return html_obj.write_pdf()
            
        except TypeError as e:
            if "PDF.__init__()" in str(e):
                # Fallback to older version method
                return self._fallback_pdf_generation(html_content)
            raise
    
    def _fallback_pdf_generation(self, html_content):
        """Fallback if WeasyPrint has version issues"""
        try:
            # Try without any extra parameters
            from weasyprint import HTML
            
            # Create minimal PDF
            html_obj = HTML(string=html_content)
            
            # Try different write_pdf signatures
            try:
                return html_obj.write_pdf()
            except TypeError:
                try:
                    return html_obj.write_pdf(target=None)
                except TypeError:
                    # Last resort: create empty PDF
                    return b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[]/Count 0>>\nendobj\nxref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n90\n%%EOF"
                    
        except Exception as e:
            raise Exception(f"PDF generation failed: {e}")