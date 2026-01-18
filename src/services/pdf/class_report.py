# services/pdf/class_report.py

"""
CLASS REPORT GENERATOR
Generates class summary report PDF
"""
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime


class ClassReportGenerator:
    """Generate PDF for class results"""
    
    def generate(self, class_data, school_info=None):
        """Generate class report PDF"""
        html_content = self._create_html(class_data, school_info)
        pdf_bytes = self._html_to_pdf(html_content)
        return pdf_bytes
    
    def _create_html(self, class_data, school_info):
        """Create HTML content"""
        metadata = class_data['metadata']
        students = class_data['students']
        analytics = class_data.get('analytics', {})
        
        # Get top 10 students
        top_students = sorted(
            students,
            key=lambda x: x['summary'].get('average', 0),
            reverse=True
        )[:10]
        
        # Top students table
        top_students_rows = ""
        for i, student in enumerate(top_students, 1):
            top_students_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{student['student']['name']}</td>
                <td>{student['student']['admission']}</td>
                <td>{student['summary'].get('average', 0)}</td>
                <td>{student['summary'].get('grade', 'N/A')}</td>
                <td>{student['summary'].get('division', 'N/A')}</td>
            </tr>
            """
        
        # Class analytics
        class_stats = analytics.get('class', {})
        
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
                <h1>{school.get('name', 'SCHOOL MANAGEMENT SYSTEM')}</h1>
                <p class="school-info">
                    {school.get('address', '')} | 
                    Tel: {school.get('phone', '')}
                </p>
            </div>
            
            <div class="report-title">
                <h2>CLASS PERFORMANCE REPORT</h2>
                <p>Exam: {metadata.get('exam_id', 'N/A')} | Term: {datetime.now().year}</p>
            </div>
            
            <div class="class-info">
                <table>
                    <tr>
                        <td><strong>Class:</strong> {metadata.get('class_id', 'N/A')}</td>
                        <td><strong>Stream:</strong> {metadata.get('stream_id', 'N/A')}</td>
                        <td><strong>Grading System:</strong> {metadata.get('system', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Students:</strong> {len(students)}</td>
                        <td><strong>Subjects:</strong> {metadata.get('subjects', 0)}</td>
                        <td><strong>Processed:</strong> {metadata.get('processed', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="statistics-section">
                <h3>CLASS STATISTICS</h3>
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
                        <div class="stat-value">{class_stats.get('division_iii', 0)}</div>
                        <div class="stat-label">Division III</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{class_stats.get('division_iv', 0)}</div>
                        <div class="stat-label">Division IV</div>
                    </div>
                    <div class="stat-box fail">
                        <div class="stat-value">{class_stats.get('failed', 0)}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                </div>
            </div>
            
            <div class="top-students-section">
                <h3>TOP 10 PERFORMERS</h3>
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Student Name</th>
                            <th>Admission No</th>
                            <th>Average</th>
                            <th>Grade</th>
                            <th>Division</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_students_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="subject-performance">
                <h3>SUBJECT PERFORMANCE</h3>
                <table class="subject-stats-table">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Average</th>
                            <th>Pass Rate</th>
                            <th>Top Score</th>
                            <th>Lowest</th>
                            <th>A Grades</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add subject statistics
        subject_analytics = analytics.get('subjects', {})
        for subject_name, stats in subject_analytics.items():
            html += f"""
                    <tr>
                        <td>{subject_name}</td>
                        <td>{stats.get('average', 0)}%</td>
                        <td>{stats.get('pass_rate', 0)}%</td>
                        <td>{stats.get('top_score', 0)}</td>
                        <td>{stats.get('lowest_score', 0)}</td>
                        <td>{stats.get('a_count', 0)}</td>
                    </tr>
            """
        
        html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="summary-section">
                <h3>SUMMARY</h3>
                <div class="summary-content">
                    <p><strong>Top Student:</strong> {class_stats.get('top_student', 'N/A')} 
                    with {class_stats.get('top_score', 0)}% average</p>
                    <p><strong>Performance Analysis:</strong> The class has shown 
                    {self._get_performance_level(class_stats.get('average', 0))} 
                    performance overall.</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Report ID: CLS-{metadata.get('class_id', 'CLASS')}-{datetime.now().strftime('%Y%m%d%H%M')}</p>
                <p>Generated on: {datetime.now().strftime('%d %B, %Y %H:%M')}</p>
                <p>This report is computer generated for internal use.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_performance_level(self, average):
        """Get performance level description"""
        if average >= 75:
            return "EXCELLENT"
        elif average >= 60:
            return "GOOD"
        elif average >= 50:
            return "SATISFACTORY"
        elif average >= 40:
            return "FAIR"
        else:
            return "NEEDS IMPROVEMENT"
    
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
            size: A4 landscape;
            margin: 15mm;
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10pt;
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
            margin: 0 0 8px 0;
        }
        
        .school-info {
            color: #666;
            font-size: 9pt;
            margin: 0;
        }
        
        .report-title {
            text-align: center;
            margin: 20px 0;
        }
        
        .report-title h2 {
            color: #3498db;
            font-size: 14pt;
            margin: 0 0 5px 0;
        }
        
        .class-info table {
            width: 100%;
            margin-bottom: 20px;
            border-collapse: collapse;
        }
        
        .class-info td {
            padding: 8px;
            border: 1px solid #ddd;
            background-color: #f8f9fa;
        }
        
        .statistics-section {
            margin: 20px 0;
        }
        
        .statistics-section h3 {
            background-color: #f8f9fa;
            padding: 8px;
            border-left: 4px solid #9b59b6;
            margin-bottom: 15px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background-color: #3498db;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 6px;
        }
        
        .stat-box.fail {
            background-color: #e74c3c;
        }
        
        .stat-value {
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 9pt;
            opacity: 0.9;
        }
        
        .top-students-section, .subject-performance {
            margin: 25px 0;
        }
        
        .top-students-section h3, .subject-performance h3 {
            background-color: #f8f9fa;
            padding: 8px;
            border-left: 4px solid #27ae60;
            margin-bottom: 15px;
        }
        
        .ranking-table, .subject-stats-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        
        .ranking-table th, .subject-stats-table th {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }
        
        .ranking-table td, .subject-stats-table td {
            padding: 8px;
            border: 1px solid #ddd;
        }
        
        .ranking-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .summary-section {
            margin: 25px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
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