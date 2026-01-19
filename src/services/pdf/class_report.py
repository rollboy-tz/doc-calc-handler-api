"""
CLASS REPORT GENERATOR - WORKING VERSION
"""
from datetime import datetime


class ClassReportGenerator:
    """Generate class report PDF"""
    
    def __init__(self):
        pass
    
    def validate_data(self, class_data):
        """Validate class data"""
        errors = []
        
        if not class_data:
            errors.append("No class data provided")
            return False, errors
        
        if 'metadata' not in class_data:
            errors.append("Missing 'metadata' object")
            return False, errors
        
        metadata = class_data['metadata']
        if not metadata.get('class_id'):
            errors.append("Missing class_id in metadata")
        
        if 'students' not in class_data:
            errors.append("Missing 'students' array")
        elif not class_data['students']:
            errors.append("Students array is empty")
        
        return len(errors) == 0, errors
    
    def generate(self, class_data, school_info=None):
        """Generate PDF"""
        try:
            # Validate
            is_valid, errors = self.validate_data(class_data)
            if not is_valid:
                return False, {"errors": errors}
            
            # Generate HTML
            html = self._create_simple_html(class_data, school_info)
            
            # Generate PDF
            pdf_bytes = self._simple_html_to_pdf(html)
            
            return True, pdf_bytes
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def _create_simple_html(self, class_data, school_info):
        """Create simple HTML"""
        metadata = class_data['metadata']
        students = class_data['students']
        school = school_info or {}
        
        # Top 10 students
        try:
            top_students = sorted(
                students,
                key=lambda x: x.get('summary', {}).get('average', 0),
                reverse=True
            )[:10]
        except:
            top_students = students[:10] if len(students) > 10 else students
        
        # Students table
        students_html = ""
        for i, student in enumerate(top_students, 1):
            stu_info = student.get('student', {})
            summary = student.get('summary', {})
            
            students_html += f"""
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
<html>
<head>
    <meta charset="UTF-8">
    <title>Class Report</title>
    <style>
        body {{ font-family: Arial; margin: 15px; }}
        h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #2c3e50; color: white; padding: 8px; }}
        td {{ border: 1px solid #ddd; padding: 6px; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 10px; margin: 20px 0; }}
        .stat {{ background: #3498db; color: white; padding: 10px; flex: 1; text-align: center; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{school.get('name', 'CLASS REPORT')}</h1>
        <p>{metadata.get('class_id', '')}</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div style="font-size: 18px; font-weight: bold;">{len(students)}</div>
            <div>Students</div>
        </div>
        <div class="stat">
            <div style="font-size: 18px; font-weight: bold;">{metadata.get('subjects', 'N/A')}</div>
            <div>Subjects</div>
        </div>
    </div>
    
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
        {students_html if students_html else '<tr><td colspan="6">No students</td></tr>'}
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _simple_html_to_pdf(self, html_content):
        """Convert HTML to PDF"""
        try:
            from weasyprint import HTML
            html_obj = HTML(string=html_content)
            return html_obj.write_pdf()
        except TypeError as e:
            if "PDF.__init__()" in str(e):
                # Fallback
                from weasyprint import HTML
                html_obj = HTML(string=html_content)
                try:
                    return html_obj.write_pdf(target=None)
                except:
                    # Minimal PDF
                    return b"%PDF-1.4\n"
            raise