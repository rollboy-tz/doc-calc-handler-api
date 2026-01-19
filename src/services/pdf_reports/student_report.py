"""
student_report.py - SIMPLE WORKING VERSION
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StudentReport(BasePDFTemplate):
    """Generate student report PDF"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method"""
        try:
            # Create filename
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Prepare metadata
            student_name = student_data['student']['name']
            school_name = school_info.get('name', 'School') if school_info else 'School'
            exam_name = class_data.get('metadata', {}).get('exam_id', 'Examination')
            
            # Create document
            doc = self.create_document(
                filepath=filepath,
                title=f"Student Report - {student_name}",
                subject=f"Academic Report for {student_name}",
                author=f"{self.system_config['system_name']}"
            )
            
            # Build content
            story = self._build_content(student_data, class_data, school_info)
            
            # Build PDF
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            logger.info(f"Generated report: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_content(self, student_data, class_data, school_info):
        """Build PDF content"""
        story = []
        styles = getSampleStyleSheet()
        
        # School header
        if school_info and school_info.get('name'):
            story.append(Paragraph(school_info['name'], styles['Heading2']))
        
        # Report title
        exam_info = class_data.get('metadata', {})
        exam_title = exam_info.get('exam_id', 'Examination')
        story.append(Paragraph(f"{exam_title} - STUDENT REPORT", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Student info
        student = student_data['student']
        info_text = f"""
        <b>Name:</b> {student['name']}<br/>
        <b>Admission No:</b> {student['admission']}<br/>
        <b>Gender:</b> {student['gender']}<br/>
        <b>Class:</b> {exam_info.get('class_id', 'N/A')}<br/>
        """
        
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Performance summary
        story.append(Paragraph("PERFORMANCE SUMMARY", styles['Heading2']))
        summary = student_data['summary']
        
        data = [
            ["Total Marks", f"{summary['total']}"],
            ["Average Score", f"{summary['average']:.1f}%"],
            ["Grade", summary['grade']],
            ["Division", summary.get('division', 'N/A')],
            ["Status", summary['status']],
        ]
        
        table = Table(data, colWidths=[120, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Subjects (if available)
        if 'subjects' in student_data and student_data['subjects']:
            story.append(Paragraph("SUBJECTS PERFORMANCE", styles['Heading2']))
            
            subjects = student_data['subjects']
            subj_data = [["SUBJECT", "MARKS", "GRADE"]]
            
            for subj_name, subj_info in subjects.items():
                subj_data.append([
                    subj_name.upper(),
                    str(subj_info.get('marks', 'ABS')),
                    subj_info.get('grade', 'ABS')
                ])
            
            subj_table = Table(subj_data, colWidths=[150, 80, 80])
            subj_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            
            story.append(subj_table)
            story.append(Spacer(1, 20))
        
        # Footer note
        story.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}",
            styles['Italic']
        ))
        
        return story
    
    def _create_filename(self, student_data, school_info):
        """Create filename"""
        student_name = student_data['student']['name']
        clean_name = re.sub(r'[^\w\-]', '_', student_name)[:20]
        admission = student_data['student']['admission']
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_Report_{admission}_{clean_name}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(temp_file.name)
        
        # Set metadata
        c.setTitle("Report Generation Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("Error Report")
        
        # Content
        c.drawString(100, 800, "⚠️ REPORT ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:80]}")
        c.drawString(100, 760, f"System: {self.system_config['system_name']}")
        c.drawString(100, 740, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        c.save()
        return temp_file.name