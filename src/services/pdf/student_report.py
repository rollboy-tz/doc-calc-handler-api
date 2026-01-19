"""
STUDENT REPORT GENERATOR
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class StudentReportGenerator:
    """Generate PDF for individual student"""
    
    def generate(self, student_data, school_info=None):
        """Generate student report PDF - with error handling"""
        try:
            html_content = self._create_html(student_data, school_info)
            pdf_bytes = self._html_to_pdf(html_content)
            return pdf_bytes
        except Exception as e:
            # Return simple error PDF instead of crashing
            print(f"Student report error: {e}")
            return self._generate_error_pdf(f"Student Report Error: {str(e)[:100]}")
    
    def _create_html(self, student_data, school_info):
        """Create HTML content for student report"""
        student = student_data.get('student', {})
        subjects = student_data.get('subjects', {})
        summary = student_data.get('summary', {})
        
        # School info
        school = school_info or {}
        
        # Subjects table rows
        subjects_rows = ""
        for subj_name, subj_data in subjects.items():
            marks = subj_data.get('marks', 'N/A')
            grade = subj_data.get('grade', 'N/A')
            points = subj_data.get('points', '-')
            status = "PASS" if subj_data.get('pass') else "FAIL"
            
            subjects_rows += f"""
                <tr>
                    <td>{subj_name}</td>
                    <td>{marks}</td>
                    <td>{grade}</td>
                    <td>{points}</td>
                    <td>{status}</td>
                </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Student Report - {student.get('name', 'Unknown')}</title>
            <style>
                {self._get_css()}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{school.get('name', 'STUDENT REPORT')}</h1>
                <p class="school-info">
                    {school.get('address', '')} | 
                    Tel: {school.get('phone', '')}
                </p>
            </div>
            
            <div class="student-info">
                <h2>STUDENT INFORMATION</h2>
                <table>
                    <tr><td><strong>Name:</strong></td><td>{student.get('name', 'N/A')}</td></tr>
                    <tr><td><strong>Admission No:</strong></td><td>{student.get('admission', 'N/A')}</td></tr>
                    <tr><td><strong>Gender:</strong></td><td>{student.get('gender', 'N/A')}</td></tr>
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
            <h1>⚠️ Report Generation Error</h1>
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
        @page { size: A4; margin: 20mm; }
        body { font-family: Arial, sans-serif; font-size: 12px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: #2c3e50; }
        .student-info h2, .academic-section h3, .summary-section h3 { 
            color: #3498db; 
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th { background-color: #2c3e50; color: white; padding: 8px; }
        td { border: 1px solid #ddd; padding: 8px; }
        .subject-table tr:nth-child(even) { background-color: #f2f2f2; }
        .summary-table td { background-color: #f8f9fa; }
        .footer { margin-top: 30px; text-align: center; color: #666; }
        """