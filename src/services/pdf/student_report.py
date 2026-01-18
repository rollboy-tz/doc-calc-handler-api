# services/pdf/student_report.py

"""
STUDENT REPORT GENERATOR
Generates individual student report PDF
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class StudentReportGenerator:
    """Generate PDF for single student"""
    
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
        
        # Format subjects table rows
        subjects_rows = ""
        for subj_name, subj_data in subjects.items():
            subjects_rows += f"""
            <tr>
                <td>{subj_name}</td>
                <td>{subj_data.get('marks', 'N/A')}</td>
                <td>{subj_data.get('grade', 'N/A')}</td>
                <td>{subj_data.get('points', '-')}</td>
                <td>{"PASS" if subj_data.get('pass') else "FAIL"}</td>
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
                <h1>{school.get('name', 'SCHOOL MANAGEMENT SYSTEM')}</h1>
                <p class="school-info">
                    {school.get('address', '')} | 
                    Tel: {school.get('phone', '')} | 
                    Email: {school.get('email', '')}
                </p>
            </div>
            
            <div class="report-title">
                <h2>STUDENT PERFORMANCE REPORT</h2>
                <p>Academic Year: {datetime.now().year}</p>
            </div>
            
            <div class="student-info">
                <table>
                    <tr>
                        <td><strong>Student Name:</strong> {student['name']}</td>
                        <td><strong>Admission No:</strong> {student['admission']}</td>
                    </tr>
                    <tr>
                        <td><strong>Class:</strong> {student.get('class', 'N/A')}</td>
                        <td><strong>Gender:</strong> {student['gender']}</td>
                    </tr>
                </table>
            </div>
            
            <div class="academic-section">
                <h3>ACADEMIC PERFORMANCE</h3>
                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Marks</th>
                            <th>Grade</th>
                            <th>Points</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {subjects_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="summary-section">
                <h3>PERFORMANCE SUMMARY</h3>
                <table class="summary-table">
                    <tr>
                        <td><strong>Total Marks:</strong> {summary.get('total', 0)}</td>
                        <td><strong>Average Score:</strong> {summary.get('average', 0)}%</td>
                        <td><strong>Overall Grade:</strong> {summary.get('grade', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Division:</strong> {summary.get('division', 'N/A')}</td>
                        <td><strong>Total Points:</strong> {summary.get('points', 0)}</td>
                        <td><strong>Class Rank:</strong> {summary.get('rank', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Subjects Total:</strong> {summary.get('subjects_total', 0)}</td>
                        <td><strong>Subjects Passed:</strong> {summary.get('subjects_passed', 0)}</td>
                        <td><strong>Status:</strong> {summary.get('status', 'PENDING')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="remarks-section">
                <h3>REMARKS</h3>
                <p>{summary.get('remark', 'No remarks')}</p>
            </div>
            
            <div class="signature-section">
                <table>
                    <tr>
                        <td class="signature-box">
                            <p>_________________________</p>
                            <p><strong>Class Teacher</strong></p>
                        </td>
                        <td class="signature-box">
                            <p>_________________________</p>
                            <p><strong>Head Teacher</strong></p>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Report ID: {student['admission']}-{datetime.now().strftime('%Y%m%d%H%M')}</p>
                <p>Generated on: {datetime.now().strftime('%d %B, %Y %H:%M')}</p>
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
        pdf_bytes = html_obj.write_pdf(stylesheets=[css], font_config=font_config)
        
        return pdf_bytes
    
    def _get_css(self):
        """Get CSS styles"""
        return """
        @page {
            size: A4;
            margin: 20mm;
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #2c3e50;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 20pt;
            margin: 0 0 10px 0;
        }
        
        .school-info {
            color: #666;
            font-size: 10pt;
            margin: 0;
        }
        
        .report-title {
            text-align: center;
            margin: 25px 0;
        }
        
        .report-title h2 {
            color: #3498db;
            font-size: 16pt;
            margin: 0 0 5px 0;
        }
        
        .student-info table {
            width: 100%;
            margin-bottom: 25px;
            border-collapse: collapse;
        }
        
        .student-info td {
            padding: 10px;
            border: 1px solid #ddd;
            width: 50%;
        }
        
        .academic-section {
            margin: 25px 0;
        }
        
        .academic-section h3 {
            background-color: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #3498db;
            margin-bottom: 15px;
        }
        
        .subject-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .subject-table th {
            background-color: #2c3e50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        .subject-table td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        
        .subject-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .summary-section {
            margin: 25px 0;
        }
        
        .summary-section h3 {
            background-color: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #27ae60;
            margin-bottom: 15px;
        }
        
        .summary-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .summary-table td {
            padding: 12px;
            border: 1px solid #ddd;
            background-color: #f8f9fa;
        }
        
        .remarks-section {
            margin: 25px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
        }
        
        .signature-section {
            margin-top: 50px;
        }
        
        .signature-section table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .signature-box {
            width: 50%;
            text-align: center;
            padding: 30px;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }
        """