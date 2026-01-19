"""
STUDENT REPORT GENERATOR
"""
from datetime import datetime


class StudentReportGenerator:
    """Generate student report PDF"""
    
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
        """Generate PDF"""
        try:
            # Validate
            is_valid, errors = self.validate_data(student_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Create HTML
            html_content = self._create_html(student_data, school_info)
            
            # Generate PDF
            pdf_bytes = self._generate_pdf(html_content)
            
            return True, pdf_bytes
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def _create_html(self, student_data, school_info):
        """Create HTML content"""
        student = student_data['student']
        subjects = student_data.get('subjects', {})
        summary = student_data.get('summary', {})
        school = school_info or {}
        
        # Subjects table
        subjects_rows = ""
        if subjects:
            for subj_name, subj_data in subjects.items():
                status = "PASS" if subj_data.get('pass') else "FAIL"
                subjects_rows += f"""
                <tr>
                    <td>{subj_name}</td>
                    <td>{subj_data.get('marks', 'N/A')}</td>
                    <td>{subj_data.get('grade', 'N/A')}</td>
                    <td>{subj_data.get('points', '-')}</td>
                    <td>{status}</td>
                </tr>
                """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Student Report</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
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
        <tr><td><strong>Gender:</strong></td><td>{student.get('gender', 'N/A')}</td></tr>
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
        {subjects_rows if subjects_rows else '<tr><td colspan="5">No subjects</td></tr>'}
    </table>
    
    <h2>Summary</h2>
    <table>
        <tr><td><strong>Average:</strong></td><td>{summary.get('average', 'N/A')}</td></tr>
        <tr><td><strong>Grade:</strong></td><td>{summary.get('grade', 'N/A')}</td></tr>
        <tr><td><strong>Division:</strong></td><td>{summary.get('division', 'N/A')}</td></tr>
        <tr><td><strong>Rank:</strong></td><td>{summary.get('rank', 'N/A')}</td></tr>
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_pdf(self, html_content):
        """Convert HTML to PDF using WeasyPrint"""
        from weasyprint import HTML
        html_obj = HTML(string=html_content)
        return html_obj.write_pdf()