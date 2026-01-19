"""
CLASS REPORT GENERATOR - PROFESSIONAL
Validates data and generates PDF only if data is complete
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class ClassReportGenerator:
    """Generate professional class report PDF"""
    
    def validate_data(self, class_data):
        """Validate class data before generating PDF"""
        errors = []
        
        # Check required fields
        if 'metadata' not in class_data:
            errors.append("Missing 'metadata' object")
            return False, errors
        
        metadata = class_data['metadata']
        if 'class_id' not in metadata or not metadata['class_id']:
            errors.append("Missing required field: metadata.class_id")
        
        # Check students
        if 'students' not in class_data:
            errors.append("Missing 'students' array")
        elif not class_data['students']:
            errors.append("Students array is empty")
        
        return len(errors) == 0, errors
    
    def generate(self, class_data, school_info=None):
        """Generate PDF - returns (success, pdf_bytes_or_error)"""
        # Validate data first
        is_valid, errors = self.validate_data(class_data)
        if not is_valid:
            return False, {"errors": errors, "message": "Invalid class data"}
        
        try:
            html_content = self._create_html(class_data, school_info)
            pdf_bytes = self._html_to_pdf(html_content)
            return True, pdf_bytes
        except Exception as e:
            return False, {"error": str(e), "message": "PDF generation failed"}
    
    def _create_html(self, class_data, school_info):
        """Create HTML content"""
        metadata = class_data['metadata']
        students = class_data['students']
        analytics = class_data.get('analytics', {})
        
        # Sort students by average
        sorted_students = sorted(
            students,
            key=lambda x: x.get('summary', {}).get('average', 0),
            reverse=True
        )
        
        # Top students table
        top_students_html = ""
        for i, student in enumerate(sorted_students[:15], 1):
            student_info = student.get('student', {})
            summary = student.get('summary', {})
            
            top_students_html += f"""
            <tr>
                <td>{i}</td>
                <td>{student_info.get('name', 'N/A')}</td>
                <td>{student_info.get('admission', 'N/A')}</td>
                <td>{summary.get('average', 0)}</td>
                <td>{summary.get('grade', 'N/A')}</td>
                <td>{summary.get('division', 'N/A')}</td>
                <td>{summary.get('status', 'N/A')}</td>
            </tr>
            """
        
        # School info
        school = school_info or {}
        
        # Class statistics
        class_stats = analytics.get('class', {})
        
        # Generate HTML
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
                <p class="info">Class Performance Analysis</p>
            </div>
            
            <div class="content">
                <h2>Class Information</h2>
                <table class="info-table">
                    <tr><td><strong>Class:</strong></td><td>{metadata.get('class_id', 'N/A')}</td></tr>
                    <tr><td><strong>Stream:</strong></td><td>{metadata.get('stream_id', 'N/A')}</td></tr>
                    <tr><td><strong>Total Students:</strong></td><td>{len(students)}</td></tr>
                    <tr><td><strong>Grading System:</strong></td><td>{metadata.get('system', 'N/A')}</td></tr>
                    <tr><td><strong>Exam:</strong></td><td>{metadata.get('exam_id', 'N/A')}</td></tr>
                </table>
                
                <h2>Class Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('average', 0)}%</div>
                        <div class="stat-label">Class Average</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('pass_rate', 0)}%</div>
                        <div class="stat-label">Pass Rate</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('division_i', 0)}</div>
                        <div class="stat-label">Division I</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('division_ii', 0)}</div>
                        <div class="stat-label">Division II</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('failed', 0)}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                </div>
                
                <h2>Top Performers</h2>
                <table class="ranking-table">
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Admission No</th>
                        <th>Average</th>
                        <th>Grade</th>
                        <th>Division</th>
                        <th>Status</th>
                    </tr>
                    {top_students_html}
                </table>
            </div>
            
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Report ID: CLS-{metadata.get('class_id', 'CLASS')}-{datetime.now().strftime('%Y%m%d%H%M%S')}</p>
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
            size: A4 landscape;
            margin: 15mm;
            @bottom-right {
                content: "Page " counter(page);
                font-size: 9pt;
                color: #666;
            }
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 10pt;
            line-height: 1.3;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #2c3e50;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 18pt;
            margin: 0 0 5px 0;
        }
        .header .info {
            color: #666;
            font-size: 11pt;
            margin: 0;
        }
        .content {
            margin: 0 5px;
        }
        h2 {
            color: #3498db;
            font-size: 12pt;
            border-bottom: 1px solid #3498db;
            padding-bottom: 3px;
            margin: 20px 0 10px 0;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        .info-table td {
            padding: 8px;
            border: 1px solid #ddd;
            width: 50%;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .stat-box {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: center;
            border-radius: 5px;
        }
        .stat-box:nth-child(5) {
            background-color: #e74c3c;
        }
        .stat-value {
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 3px;
        }
        .stat-label {
            font-size: 9pt;
            opacity: 0.9;
        }
        .ranking-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        .ranking-table th {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            text-align: left;
            font-weight: bold;
        }
        .ranking-table td {
            padding: 6px;
            border: 1px solid #ddd;
        }
        .ranking-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .footer {
            margin-top: 30px;
            padding-top: 12px;
            border-top: 1px solid #ddd;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }
        """