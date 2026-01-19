"""
CLASS REPORT GENERATOR - FIXED PDF OUTPUT
"""
from datetime import datetime


class ClassReportGenerator:
    
    def __init__(self):
        pass
    
    def validate_data(self, class_data):
        """Validate class data"""
        errors = []
        
        if not class_data:
            errors.append("No class data")
            return False, errors
        
        if 'metadata' not in class_data:
            errors.append("Missing 'metadata'")
            return False, errors
        
        metadata = class_data['metadata']
        if not metadata.get('class_id'):
            errors.append("Missing class_id")
        
        return len(errors) == 0, errors
    
    def generate(self, class_data, school_info=None):
        """Generate proper PDF"""
        try:
            # Validate
            is_valid, errors = self.validate_data(class_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Generate clean HTML
            html = self._create_clean_html(class_data, school_info)
            
            # Generate PDF
            from weasyprint import HTML
            html_obj = HTML(string=html, encoding='utf-8')
            pdf_bytes = html_obj.write_pdf()
            
            return True, pdf_bytes
            
        except Exception as e:
            import traceback
            return False, {"error": str(e), "traceback": traceback.format_exc()}
    
    def _create_clean_html(self, class_data, school_info):
        """Create clean HTML"""
        metadata = class_data['metadata']
        students = class_data.get('students', [])
        school = school_info or {}
        
        # Students table
        students_rows = ""
        if students:
            for i, student in enumerate(students[:15], 1):
                stu_info = student.get('student', {})
                summary = student.get('summary', {})
                
                students_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{stu_info.get('name', '')}</td>
                    <td>{stu_info.get('admission', '')}</td>
                    <td>{summary.get('average', 0)}</td>
                    <td>{summary.get('grade', 'N/A')}</td>
                    <td>{summary.get('division', 'N/A')}</td>
                </tr>
                """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Class Report - {metadata.get('class_id', '')}</title>
    <style>
        body {{
            font-family: Arial;
            font-size: 11px;
            margin: 15px;
        }}
        h1 {{ color: #2c3e50; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #2c3e50; color: white; padding: 8px; }}
        td {{ border: 1px solid #ddd; padding: 6px; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <h1>{school.get('name', 'CLASS REPORT')}</h1>
    <p style="text-align: center;">Class: {metadata.get('class_id', '')}</p>
    
    <h2>Top Students</h2>
    <table>
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Admission</th>
            <th>Average</th>
            <th>Grade</th>
            <th>Division</th>
        </tr>
        {students_rows if students_rows else '<tr><td colspan="6">No students</td></tr>'}
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>"""
        
        return html