"""
CLASS REPORT GENERATOR - FIXED
"""
from datetime import datetime


class ClassReportGenerator:
    """Generate professional class report PDF"""
    
    def __init__(self):
        """Initialize generator - EMPTY"""
        pass
    
    def validate_data(self, class_data):
        """Validate class data before generating PDF"""
        errors = []
        
        if not class_data or not isinstance(class_data, dict):
            errors.append("Invalid class data format")
            return False, errors
        
        if 'metadata' not in class_data:
            errors.append("Missing 'metadata' object")
            return False, errors
        
        metadata = class_data['metadata']
        if not isinstance(metadata, dict):
            errors.append("Invalid metadata object")
            return False, errors
        
        if 'class_id' not in metadata or not metadata['class_id']:
            errors.append("Missing required field: metadata.class_id")
        
        if 'students' not in class_data:
            errors.append("Missing 'students' array")
        elif not isinstance(class_data['students'], list):
            errors.append("Students must be an array")
        elif not class_data['students']:
            errors.append("Students array is empty")
        
        return len(errors) == 0, errors
    
    def generate(self, class_data, school_info=None):
        """Generate PDF - returns (success, pdf_bytes_or_error)"""
        try:
            # Validate data first
            is_valid, errors = self.validate_data(class_data)
            if not is_valid:
                return False, {"errors": errors, "message": "Invalid class data"}
            
            # Generate HTML
            html_content = self._create_html(class_data, school_info)
            
            # Generate PDF
            pdf_bytes = self._html_to_pdf(html_content)
            
            return True, pdf_bytes
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Class PDF Error: {error_details}")
            return False, {"error": str(e), "traceback": error_details}
    
    def _create_html(self, class_data, school_info):
        """Create HTML content"""
        metadata = class_data['metadata']
        students = class_data['students']
        
        # Sort students
        try:
            sorted_students = sorted(
                students,
                key=lambda x: x.get('summary', {}).get('average', 0),
                reverse=True
            )[:15]
        except:
            sorted_students = students[:15] if len(students) > 15 else students
        
        # Top students table
        students_rows = ""
        for i, student in enumerate(sorted_students, 1):
            student_info = student.get('student', {})
            summary = student.get('summary', {})
            
            students_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{student_info.get('name', 'N/A')}</td>
                <td>{student_info.get('admission', 'N/A')}</td>
                <td>{summary.get('average', 0)}</td>
                <td>{summary.get('grade', 'N/A')}</td>
                <td>{summary.get('division', 'N/A')}</td>
            </tr>
            """
        
        if not students_rows:
            students_rows = "<tr><td colspan='6' style='text-align: center;'>No student data</td></tr>"
        
        # School info
        school = school_info or {}
        
        # Create HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Class Report - {metadata.get('class_id', 'Class')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 11px; margin: 15px; }}
        .header {{ text-align: center; margin-bottom: 25px; }}
        .header h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background-color: #2c3e50; color: white; padding: 8px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 6px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .stats {{ display: flex; justify-content: space-between; margin: 20px 0; }}
        .stat-box {{ background-color: #3498db; color: white; padding: 10px; border-radius: 5px; text-align: center; flex: 1; margin: 0 5px; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 9px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{school.get('name', 'CLASS REPORT')}</h1>
        <p>Class: {metadata.get('class_id', 'N/A')} | Students: {len(students)}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div style="font-size: 18px; font-weight: bold;">{len(students)}</div>
            <div>Total Students</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 18px; font-weight: bold;">{metadata.get('subjects', 'N/A')}</div>
            <div>Subjects</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 18px; font-weight: bold;">{metadata.get('system', 'N/A')}</div>
            <div>Grading System</div>
        </div>
    </div>
    
    <h2>Top Performers</h2>
    <table>
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Admission No</th>
            <th>Average</th>
            <th>Grade</th>
            <th>Division</th>
        </tr>
        {students_rows}
    </table>
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Report ID: CLS-{metadata.get('class_id', 'CLASS')}</p>
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