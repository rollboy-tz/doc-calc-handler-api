"""
STUDENT REPORT GENERATOR
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class StudentReportGenerator:
    def generate(self, student_data, school_info=None):
        """Generate student report PDF"""
        html_content = self._create_html(student_data, school_info)
        pdf_bytes = self._html_to_pdf(html_content)
        return pdf_bytes
    
    def _create_html(self, student_data, school_info):
        """Create HTML content"""
        student = student_data['student']
        subjects = student_data['subjects']
        summary = student_data['summary']
        
        # Format subjects table
        subjects_rows = ""
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
        
        # School info
        school = school_info or {}
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Student Report - {student['name']}</title>
            <style>
                {self._get_css()}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{school.get('name', 'SCHOOL REPORT')}</h1>
                <p class="school-info">
                    {school.get('address', '')} | 
                    Tel: {school.get('phone', '')}
                </p>
            </div>
            
            <div class="student-info">
                <h2>STUDENT INFORMATION</h2>
                <table>
                    <tr><td><strong>Name:</strong></td><td>{student['name']}</td></tr>
                    <tr><td><strong>Admission No:</strong></td><td>{student['admission']}</td></tr>
                    <tr><td><strong>Gender:</strong></td><td>{student['gender']}</td></tr>
                    <tr><td><strong>Class:</strong></td><td>{student.get('class', 'N/A')}</td></tr>
                </table>
            </div>
            
            <div class="academic-section">
                <h3>ACADEMIC PERFORMANCE</h3>
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
            </div>
            
            <div class="summary-section">
                <h3>PERFORMANCE SUMMARY</h3>
                <table class="summary-table">
                    <tr><td><strong>Total Marks:</strong></td><td>{summary.get('total', 0)}</td></tr>
                    <tr><td><strong>Average Score:</strong></td><td>{summary.get('average', 0)}%</td></tr>
                    <tr><td><strong>Overall Grade:</strong></td><td>{summary.get('grade', 'N/A')}</td></tr>
                    <tr><td><strong>Division:</strong></td><td>{summary.get('division', 'N/A')}</td></tr>
                    <tr><td><strong>Class Rank:</strong></td><td>{summary.get('rank', 'N/A')}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>{summary.get('status', 'PENDING')}</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _html_to_pdf(self, html_content):
        """Convert HTML to PDF"""
        font_config = FontConfiguration()
        css = CSS(string=self._get_css(), font_config=font_config)
        html_obj = HTML(string=html_content)
        return html_obj.write_pdf(stylesheets=[css], font_config=font_config)
    
    def _get_css(self):
        """Get CSS styles"""
        return """
        @page { size: A4; margin: 20mm; }
        body { font-family: Arial, sans-serif; font-size: 12px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: #2c3e50; }
        .student-info h2 { color: #3498db; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th { background-color: #2c3e50; color: white; padding: 8px; }
        td { border: 1px solid #ddd; padding: 8px; }
        .subject-table tr:nth-child(even) { background-color: #f2f2f2; }
        .summary-table td { background-color: #f8f9fa; }
        .footer { margin-top: 30px; text-align: center; color: #666; }
        """