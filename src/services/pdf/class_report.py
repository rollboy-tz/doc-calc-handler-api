"""
CLASS REPORT GENERATOR
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class ClassReportGenerator:
    """Generate PDF for class results"""
    
    def generate(self, class_data, school_info=None):
        """Generate class report PDF - with error handling"""
        try:
            html_content = self._create_html(class_data, school_info)
            pdf_bytes = self._html_to_pdf(html_content)
            return pdf_bytes
        except Exception as e:
            # Return simple error PDF instead of crashing
            print(f"Class report error: {e}")
            return self._generate_error_pdf(f"Class Report Error: {str(e)[:100]}")
    
    def _create_html(self, class_data, school_info):
        """Create HTML content for class report"""
        metadata = class_data.get('metadata', {})
        students = class_data.get('students', [])
        
        # Get top students
        top_students = []
        try:
            top_students = sorted(
                students,
                key=lambda x: x.get('summary', {}).get('average', 0),
                reverse=True
            )[:10]
        except:
            top_students = students[:10] if len(students) > 10 else students
        
        # Top students table rows
        top_students_rows = ""
        for i, student in enumerate(top_students, 1):
            student_info = student.get('student', {})
            summary = student.get('summary', {})
            
            top_students_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{student_info.get('name', 'N/A')}</td>
                    <td>{student_info.get('admission', 'N/A')}</td>
                    <td>{summary.get('average', 0)}</td>
                    <td>{summary.get('grade', 'N/A')}</td>
                    <td>{summary.get('division', 'N/A')}</td>
                </tr>
            """
        
        # School info
        school = school_info or {}
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Class Report - {metadata.get('class_id', 'Class')}</title>
            <style>
                {self._get_css()}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{school.get('name', 'CLASS REPORT')}</h1>
                <p>Class: {metadata.get('class_id', 'N/A')} | Students: {len(students)}</p>
            </div>
            
            <div class="top-students">
                <h2>TOP PERFORMERS</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Admission No</th>
                        <th>Average</th>
                        <th>Grade</th>
                        <th>Division</th>
                    </tr>
                    {top_students_rows}
                </table>
            </div>
            
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p>Report ID: CLS-{metadata.get('class_id', 'CLASS')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _html_to_pdf(self, html_content):
        """Convert HTML to PDF bytes"""
        font_config = FontConfiguration()
        css = CSS(string=self._get_css(), font_config=font_config)
        html_obj = HTML(string=html_content)
        return html_obj.write_pdf(stylesheets=[css], font_config=font_config)
    
    def _generate_error_pdf(self, error_message):
        """Generate error PDF when main generation fails"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><style>body {{ font-family: Arial; padding: 20px; }}</style></head>
        <body>
            <h1>⚠️ Class Report Error</h1>
            <p>{error_message}</p>
            <p>Please try again or contact support.</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </body>
        </html>
        """
        html = HTML(string=html_content)
        return html.write_pdf()
    
    def _get_css(self):
        """Get CSS styles"""
        return """
        @page { size: A4 landscape; margin: 15mm; }
        body { font-family: Arial, sans-serif; font-size: 11px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: #2c3e50; }
        .top-students h2 { 
            color: #3498db; 
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th { background-color: #2c3e50; color: white; padding: 8px; }
        td { border: 1px solid #ddd; padding: 6px; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .footer { margin-top: 30px; text-align: center; color: #666; }
        """