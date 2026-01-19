"""
STUDENT REPORT GENERATOR - FIXED
"""
from datetime import datetime


class StudentReportGenerator:
    """Generate professional student report PDF"""
    
    def __init__(self):
        """Initialize generator - EMPTY"""
        pass
    
    def validate_data(self, student_data):
        """Validate student data before generating PDF"""
        errors = []
        
        if not student_data or not isinstance(student_data, dict):
            errors.append("Invalid student data format")
            return False, errors
        
        if 'student' not in student_data:
            errors.append("Missing 'student' object")
            return False, errors
        
        student = student_data['student']
        if not isinstance(student, dict):
            errors.append("Invalid student object")
            return False, errors
        
        required_fields = ['name', 'admission']
        for field in required_fields:
            if field not in student or not student[field]:
                errors.append(f"Missing required field: student.{field}")
        
        if 'subjects' not in student_data:
            errors.append("Missing 'subjects'")
        elif not student_data['subjects']:
            errors.append("Subjects data is empty")
        
        if 'summary' not in student_data:
            errors.append("Missing 'summary'")
        
        return len(errors) == 0, errors
    
    def generate(self, student_data, school_info=None):
        """Generate PDF - returns (success, pdf_bytes_or_error)"""
        try:
            # Validate data first
            is_valid, errors = self.validate_data(student_data)
            if not is_valid:
                return False, {"errors": errors, "message": "Invalid student data"}
            
            # Generate HTML
            html_content = self._create_html(student_data, school_info)
            
            # Generate PDF
            pdf_bytes = self._html_to_pdf(html_content)
            
            return True, pdf_bytes
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Student PDF Error: {error_details}")
            return False, {"error": str(e), "traceback": error_details}
    
    def _create_html(self, student_data, school_info):
        """Create HTML content"""
        student = student_data['student']
        subjects = student_data['subjects']
        summary = student_data['summary']
        
        # School info
        school = school_info or {}
        
        # Subjects table
        subjects_rows = ""
        if subjects and isinstance(subjects, dict):
            for subj_name, subj_data in subjects.items():
                if isinstance(subj_data, dict):
                    subjects_rows += f"""
                    <tr>
                        <td>{subj_name}</td>
                        <td>{subj_data.get('marks', 'N/A')}</td>
                        <td>{subj_data.get('grade', 'N/A')}</td>
                        <td>{subj_data.get('points', '-')}</td>
                        <td>{"PASS" if subj_data.get('pass') else "FAIL"}</td>
                    </tr>
                    """
        
        if not subjects_rows:
            subjects_rows = "<tr><td colspan='5' style='text-align: center;'>No subjects data</td></tr>"
        
        # Create HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Student Report - {student.get('name', 'Student')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 12px; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background-color: #2c3e50; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        .subject-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .footer {{ margin-top: 40px; text-align: center; color: #666; font-size: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{school.get('name', 'STUDENT REPORT')}</h1>
        <p>{school.get('address', '')}</p>
    </div>
    
    <h2>Student Information</h2>
    <table>
        <tr><td><strong>Name:</strong></td><td>{student.get('name', 'N/A')}</td></tr>
        <tr><td><strong>Admission No:</strong></td><td>{student.get('admission', 'N/A')}</td></tr>
        <tr><td><strong>Class:</strong></td><td>{student.get('class', 'N/A')}</td></tr>
        <tr><td><strong>Gender:</strong></td><td>{student.get('gender', 'N/A')}</td></tr>
    </table>
    
    <h2>Academic Performance</h2>
    <table class="subject-table">
        <tr>
            <th>Subject</th>
            <th>Marks</th>
            <th>Grade</th>
            <th>Points</th>
            <th>Status</th>
        </tr>
        {subjects_rows}
    </table>
    
    <h2>Summary</h2>
    <table>
        <tr><td><strong>Average Score:</strong></td><td>{summary.get('average', 'N/A')}%</td></tr>
        <tr><td><strong>Overall Grade:</strong></td><td>{summary.get('grade', 'N/A')}</td></tr>
        <tr><td><strong>Division:</strong></td><td>{summary.get('division', 'N/A')}</td></tr>
        <tr><td><strong>Class Rank:</strong></td><td>{summary.get('rank', 'N/A')}</td></tr>
        <tr><td><strong>Status:</strong></td><td>{summary.get('status', 'PENDING')}</td></tr>
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Report ID: {student.get('admission', 'N/A')}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _html_to_pdf(self, html_content):
        """Convert HTML to PDF using WeasyPrint"""
        try:
            from weasyprint import HTML
            
            # Simple PDF generation - NO extra arguments
            html_obj = HTML(string=html_content)
            pdf_bytes = html_obj.write_pdf()
            
            return pdf_bytes
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"WeasyPrint Error: {error_details}")
            raise Exception(f"WeasyPrint failed: {str(e)}")