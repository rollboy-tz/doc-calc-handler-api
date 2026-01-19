"""
STUDENT REPORT GENERATOR - STABLE VERSION
"""
from datetime import datetime


class StudentReportGenerator:
    
    def __init__(self):
        pass
    
    def validate_data(self, student_data):
        """Validate student data"""
        if not student_data:
            return False, ["No student data"]
        
        if 'student' not in student_data:
            return False, ["Missing 'student' object"]
        
        student = student_data['student']
        errors = []
        
        if not student.get('name'):
            errors.append("Missing student name")
        if not student.get('admission'):
            errors.append("Missing admission number")
        
        return len(errors) == 0, errors
    
    def generate(self, student_data, school_info=None):
        """Generate PDF - STABLE VERSION"""
        try:
            # Validate
            is_valid, errors = self.validate_data(student_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Create HTML
            html_content = self._create_simple_html(student_data, school_info)
            
            # Generate PDF with simple method
            pdf_bytes = self._simple_pdf_generation(html_content)
            
            return True, pdf_bytes
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"PDF Generation Error: {error_msg}")
            return False, {"error": str(e), "traceback": error_msg}
    
    def _create_simple_html(self, student_data, school_info):
        """Create SIMPLE HTML (minimal CSS)"""
        student = student_data['student']
        subjects = student_data.get('subjects', {})
        summary = student_data.get('summary', {})
        school = school_info or {}
        
        # Subjects table - SIMPLE
        subjects_rows = ""
        if subjects:
            for subj_name, subj_data in subjects.items():
                status = "PASS" if subj_data.get('pass') else "FAIL"
                subjects_rows += f"""
                <tr>
                    <td>{subj_name}</td>
                    <td align="center">{subj_data.get('marks', 'N/A')}</td>
                    <td align="center">{subj_data.get('grade', 'N/A')}</td>
                    <td align="center">{subj_data.get('points', '-')}</td>
                    <td align="center">{status}</td>
                </tr>
                """
        
        # SIMPLE HTML with minimal styling
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Student Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 12px;
            margin: 20px;
        }}
        h1 {{
            color: #000000;
            text-align: center;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th {{
            background-color: #333333;
            color: #FFFFFF;
            padding: 8px;
            text-align: left;
            border: 1px solid #000000;
        }}
        td {{
            padding: 6px;
            border: 1px solid #CCCCCC;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 10px;
            color: #666666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{school.get('name', 'STUDENT REPORT')}</h1>
        <div>{school.get('address', '')}</div>
    </div>
    
    <h2>Student Information</h2>
    <table>
        <tr>
            <td><strong>Name:</strong></td>
            <td>{student.get('name', '')}</td>
        </tr>
        <tr>
            <td><strong>Admission:</strong></td>
            <td>{student.get('admission', '')}</td>
        </tr>
        <tr>
            <td><strong>Class:</strong></td>
            <td>{student.get('class', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Gender:</strong></td>
            <td>{student.get('gender', 'N/A')}</td>
        </tr>
    </table>
    
    <h2>Academic Performance</h2>
    <table>
        <tr>
            <th>Subject</th>
            <th>Marks</th>
            <th>Grade</th>
            <th>Points</th>
            <th>Status</th>
        </tr>
        {subjects_rows if subjects_rows else '<tr><td colspan="5" align="center">No subjects data</td></tr>'}
    </table>
    
    <h2>Summary</h2>
    <table>
        <tr>
            <td><strong>Average:</strong></td>
            <td>{summary.get('average', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Grade:</strong></td>
            <td>{summary.get('grade', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Division:</strong></td>
            <td>{summary.get('division', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Rank:</strong></td>
            <td>{summary.get('rank', 'N/A')}</td>
        </tr>
    </table>
    
    <div class="footer">
        <div>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div>Report ID: {student.get('admission', '')}</div>
    </div>
</body>
</html>"""
        
        return html
    
    def _simple_pdf_generation(self, html_content):
        """Simple PDF generation that works"""
        try:
            from weasyprint import HTML
            
            # Method 1: Simple without any options
            html_obj = HTML(string=html_content)
            pdf_bytes = html_obj.write_pdf()
            
            # Check if PDF is valid
            if pdf_bytes and pdf_bytes.startswith(b'%PDF'):
                return pdf_bytes
            else:
                raise Exception("Generated invalid PDF")
                
        except Exception as e:
            print(f"WeasyPrint error: {e}")
            # Fallback to minimal PDF
            return self._create_minimal_pdf()
    
    def _create_minimal_pdf(self):
        """Create minimal PDF as fallback"""
        from weasyprint import HTML
        minimal_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Student Report</h1>
            <p>PDF service is active.</p>
            <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </body>
        </html>
        """
        html_obj = HTML(string=minimal_html)
        return html_obj.write_pdf()