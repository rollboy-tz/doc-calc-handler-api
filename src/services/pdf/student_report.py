"""
STUDENT REPORT GENERATOR - PROFESSIONAL
Validates data and generates PDF only if data is complete
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class StudentReportGenerator:
    """Generate professional student report PDF"""
    
    def validate_data(self, student_data):
        """Validate student data before generating PDF"""
        errors = []
        
        # Check required fields
        if 'student' not in student_data:
            errors.append("Missing 'student' object")
            return False, errors
        
        student = student_data['student']
        required_fields = ['name', 'admission']
        for field in required_fields:
            if field not in student or not student[field]:
                errors.append(f"Missing required field: student.{field}")
        
        # Check subjects
        if 'subjects' not in student_data:
            errors.append("Missing 'subjects' object")
        elif not student_data['subjects']:
            errors.append("Subjects data is empty")
        
        # Check summary
        if 'summary' not in student_data:
            errors.append("Missing 'summary' object")
        
        return len(errors) == 0, errors
    
    def generate(self, student_data, school_info=None):
        """Generate PDF - returns (success, pdf_bytes_or_error)"""
        # Validate data first
        is_valid, errors = self.validate_data(student_data)
        if not is_valid:
            return False, {"errors": errors, "message": "Invalid student data"}
        
        try:
            html_content = self._create_html(student_data, school_info)
            pdf_bytes = self._html_to_pdf(html_content)
            return True, pdf_bytes
        except Exception as e:
            return False, {"error": str(e), "message": "PDF generation failed"}
    
    def _create_html(self, student_data, school_info):
        """Create HTML content"""
        student = student_data['student']
        subjects = student_data['subjects']
        summary = student_data['summary']
        
        # School info
        school = school_info or {}
        
        # Subjects table
        subjects_html = ""
        if subjects:
            for subj_name, subj_data in subjects.items():
                subjects_html += f"""
                <tr>
                    <td>{subj_name}</td>
                    <td>{subj_data.get('marks', 'N/A')}</td>
                    <td>{subj_data.get('grade', 'N/A')}</td>
                    <td>{subj_data.get('points', '-')}</td>
                    <td>{"PASS" if subj_data.get('pass') else "FAIL"}</td>
                </tr>
                """
        else:
            subjects_html = "<tr><td colspan='5' style='text-align: center;'>No subjects data</td></tr>"
        
        # Generate HTML
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
                <h1>{school.get('name', 'STUDENT REPORT')}</h1>
                <p class="info">{school.get('address', '')}</p>
            </div>
            
            <div class="content">
                <h2>Student Information</h2>
                <table class="info-table">
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
                    {subjects_html}
                </table>
                
                <h2>Summary</h2>
                <table class="summary-table">
                    <tr><td><strong>Average:</strong></td><td>{summary.get('average', 'N/A')}%</td></tr>
                    <tr><td><strong>Overall Grade:</strong></td><td>{summary.get('grade', 'N/A')}</td></tr>
                    <tr><td><strong>Division:</strong></td><td>{summary.get('division', 'N/A')}</td></tr>
                    <tr><td><strong>Class Rank:</strong></td><td>{summary.get('rank', 'N/A')}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>{summary.get('status', 'PENDING')}</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Report ID: {student.get('admission', 'N/A')}-{datetime.now().strftime('%Y%m%d%H%M%S')}</p>
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
        """Professional CSS styling"""
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
            margin: 0 0 5px 0;
        }
        .header .info {
            color: #666;
            font-size: 10pt;
            margin: 0;
        }
        .content {
            margin: 0 10px;
        }
        h2 {
            color: #3498db;
            font-size: 14pt;
            border-bottom: 1px solid #3498db;
            padding-bottom: 5px;
            margin: 25px 0 15px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .info-table td {
            padding: 8px;
            border: 1px solid #ddd;
        }
        .subject-table th {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            text-align: left;
        }
        .subject-table td {
            padding: 8px;
            border: 1px solid #ddd;
        }
        .subject-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .summary-table {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
        }
        .summary-table td {
            padding: 10px;
            border: 1px solid #ddd;
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