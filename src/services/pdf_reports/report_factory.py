"""
services/pdf_reports/student_report.py - FIXED
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.lib import colors
import tempfile
import os
from datetime import datetime

class StudentReport(BasePDFTemplate):
    """Generate student report PDF - FIXED VERSION"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method - FIXED"""
        try:
            # Create filename with metadata
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Create document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                title=f"Report - {student_data['student']['name']}",
                author=self.system_config['author'],
                creator=self.system_config['generator']
            )
            
            # Build content
            story = []
            
            # 1. Header
            story.extend(self._create_header(student_data, class_data, school_info))
            story.append(Spacer(1, 20))
            
            # 2. Student Info
            story.append(self._create_student_table(student_data))
            story.append(Spacer(1, 15))
            
            # 3. Performance
            story.append(self._create_performance_table(student_data))
            story.append(Spacer(1, 15))
            
            # 4. Subjects
            story.append(self._create_subjects_table(student_data))
            
            # Build with footer (no watermark for now to avoid errors)
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _create_student_table(self, student_data):
        """Student information table - FIXED"""
        from reportlab.platypus import Table, TableStyle
        
        student = student_data['student']
        
        data = [
            ["STUDENT INFORMATION", "", "", ""],
            ["Full Name:", student['name'], "Admission:", student['admission']],
            ["Gender:", student['gender'], "Student ID:", student['id']],
        ]
        
        table = Table(data, colWidths=[100, 150, 100, 150])
        
        # FIXED: Use colors.blue instead of HexColor
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        
        return table
    
    def _create_performance_table(self, student_data):
        """Performance summary table - FIXED"""
        from reportlab.platypus import Table, TableStyle
        
        summary = student_data['summary']
        
        data = [
            ["PERFORMANCE SUMMARY", "", ""],
            ["Total Marks:", str(summary['total']), ""],
            ["Average Score:", f"{summary['average']:.1f}%", ""],
            ["Grade:", summary['grade'], "Division:", summary.get('division', 'N/A')],
            ["Class Rank:", f"{summary['rank']}", "Status:", summary['status']],
        ]
        
        table = Table(data, colWidths=[120, 80, 120, 80])
        
        # FIXED: Use predefined colors
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        
        return table
    
    def _create_subjects_table(self, student_data):
        """Subjects table - FIXED"""
        from reportlab.platypus import Table, TableStyle
        
        subjects = student_data['subjects']
        
        # Header
        data = [["SUBJECT", "MARKS", "GRADE", "POINTS", "REMARK"]]
        
        # Add subjects
        for subject_name, subject_info in subjects.items():
            data.append([
                subject_name.upper(),
                str(subject_info.get('marks', 'ABS')),
                subject_info.get('grade', 'ABS'),
                str(subject_info.get('points', '-')),
                subject_info.get('remark', 'N/A')
            ])
        
        # Add total row
        summary = student_data['summary']
        data.append([
            "TOTAL",
            str(summary['total']),
            summary['grade'],
            str(summary.get('points', '')),
            summary['remark']
        ])
        
        table = Table(data, colWidths=[120, 60, 60, 60, 120])
        
        # FIXED: Simple color scheme
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
            ('GRID', (0,-1), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightblue),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        
        return table
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF if generation fails"""
        import tempfile
        from reportlab.pdfgen import canvas
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        c = canvas.Canvas(temp_file.name)
        
        c.drawString(100, 800, "⚠️ REPORT GENERATION ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:100]}")
        c.drawString(100, 760, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(100, 740, f"System: {self.system_config['system_name']}")
        
        c.save()
        return temp_file.name