"""
CLASS REPORT GENERATOR - STABLE VERSION
"""
from datetime import datetime


class ClassReportGenerator:
    
    def __init__(self):
        pass
    
    def validate_data(self, class_data):
        """Validate class data"""
        if not class_data:
            return False, ["No class data"]
        
        if 'metadata' not in class_data:
            return False, ["Missing 'metadata' object"]
        
        metadata = class_data['metadata']
        errors = []
        
        if not metadata.get('class_id'):
            errors.append("Missing class_id in metadata")
        
        return len(errors) == 0, errors
    
    def generate(self, class_data, school_info=None):
        """Generate PDF - STABLE VERSION"""
        try:
            # Validate
            is_valid, errors = self.validate_data(class_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Create HTML
            html_content = self._create_simple_html(class_data, school_info)
            
            # Generate PDF
            from weasyprint import HTML
            html_obj = HTML(string=html_content)
            pdf_bytes = html_obj.write_pdf()
            
            return True, pdf_bytes
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def _create_simple_html(self, class_data, school_info):
        """Create SIMPLE HTML"""
        metadata = class_data['metadata']
        students = class_data.get('students', [])
        school = school_info or {}
        
        # Students table - SIMPLE
        students_rows = ""
        if students:
            for i, student in enumerate(students[:15], 1):
                stu_info = student.get('student', {})
                summary = student.get('summary', {})
                
                students_rows += f"""
                <tr>
                    <td align="center">{i}</td>
                    <td>{stu_info.get('name', '')}</td>
                    <td>{stu_info.get('admission', '')}</td>
                    <td align="center">{summary.get('average', 0)}</td>
                    <td align="center">{summary.get('grade', 'N/A')}</td>
                    <td align="center">{summary.get('division', 'N/A')}</td>
                </tr>
                """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Class Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 11px;
            margin: 15px;
        }}
        h1 {{
            color: #000000;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background-color: #333333;
            color: #FFFFFF;
            padding: 8px;
            border: 1px solid #000000;
        }}
        td {{
            padding: 6px;
            border: 1px solid #CCCCCC;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666666;
        }}
    </style>
</head>
<body>
    <h1>{school.get('name', 'CLASS REPORT')}</h1>
    <p style="text-align: center;">{metadata.get('class_id', '')}</p>
    
    <h2>Students Performance</h2>
    <table>
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Admission</th>
            <th>Average</th>
            <th>Grade</th>
            <th>Division</th>
        </tr>
        {students_rows if students_rows else '<tr><td colspan="6" align="center">No students data</td></tr>'}
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
        
        return html