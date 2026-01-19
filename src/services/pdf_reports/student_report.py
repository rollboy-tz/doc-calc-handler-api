"""
student_report.py - WITH PROPER METADATA
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StudentReport(BasePDFTemplate):
    """Generate student report PDF with proper metadata"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method with metadata"""
        try:
            # Create filename
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Prepare metadata
            student_name = student_data['student']['name']
            school_name = school_info.get('name', 'School') if school_info else 'School'
            exam_name = class_data.get('metadata', {}).get('exam_id', 'Examination')
            
            # Create title and subject
            title = f"Student Report - {student_name}"
            subject = f"Academic Report for {student_name} - {school_name} - {exam_name}"
            
            # Create document WITH METADATA
            doc = self.create_document(
                filepath=filepath,
                title=title,
                subject=subject,
                author=f"{self.system_config['system_name']} for {school_name}"
            )
            
            # Build content
            story = self._build_content(student_data, class_data, school_info)
            
            # Build PDF
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            logger.info(f"Generated report with metadata: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e), student_data, school_info)
    
    def _build_content(self, student_data, class_data, school_info):
        """Build PDF content"""
        story = []
        styles = getSampleStyleSheet()
        
        # School header
        if school_info and school_info.get('name'):
            story.append(Paragraph(school_info['name'], styles['Heading2']))
            if school_info.get('address'):
                story.append(Paragraph(school_info['address'], styles['Normal']))
        
        # Report title
        exam_info = class_data.get('metadata', {})
        exam_title = exam_info.get('exam_id', 'Examination')
        story.append(Paragraph(f"{exam_title} - STUDENT REPORT", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Student info
        student = student_data['student']
        info_data = [
            ["Full Name:", student['name']],
            ["Admission No:", student['admission']],
            ["Student ID:", student.get('id', 'N/A')],
            ["Gender:", student['gender']],
            ["Class:", exam_info.get('class_id', 'N/A')],
        ]
        
        # Create student info table
        from reportlab.platypus import Table
        info_table = Table(info_data, colWidths=[100, 200])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Performance summary
        story.append(Paragraph("PERFORMANCE SUMMARY", styles['Heading2']))
        summary = student_data['summary']
        
        perf_data = [
            ["Total Marks", f"{summary['total']}"],
            ["Average Score", f"{summary['average']:.1f}%"],
            ["Grade", summary['grade']],
            ["Division", summary.get('division', 'N/A')],
            ["Class Rank", f"{summary.get('rank', 'N/A')}"],
            ["Status", summary['status']],
            ["Remark", summary['remark']],
        ]
        
        perf_table = Table(perf_data, colWidths=[120, 100])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Subjects (if available)
        if 'subjects' in student_data and student_data['subjects']:
            story.append(Paragraph("SUBJECTS PERFORMANCE", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            subjects = student_data['subjects']
            subj_data = [["SUBJECT", "MARKS", "GRADE", "POINTS", "REMARK"]]
            
            for subj_name, subj_info in subjects.items():
                subj_data.append([
                    subj_name.upper(),
                    str(subj_info.get('marks', 'ABS')),
                    subj_info.get('grade', 'ABS'),
                    str(subj_info.get('points', '-')),
                    subj_info.get('remark', 'N/A')
                ])
            
            subj_table = Table(subj_data, colWidths=[120, 60, 60, 60, 120])
            subj_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('ALIGN', (1,1), (3,-1), 'CENTER'),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
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
        clean_name = re.sub(r'[^\w\-]', '_', student_name)[:30]
        admission = student_data['student']['admission']
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_Report_{admission}_{clean_name}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg, student_data=None, school_info=None):
        """Create error PDF with metadata"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(temp_file.name)
        
        # Set metadata even for error PDF
        c.setTitle("Report Generation Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("Error Report")
        c.setKeywords("error, report, system")
        c.setCreator(self.system_config['system_name'])
        
        # Content
        c.drawString(100, 800, "⚠️ REPORT GENERATION ERROR")
        c.drawString(100, 780, "The system encountered an error while generating your report.")
        c.drawString(100, 760, f"Error: {error_msg[:80]}")
        
        if student_data:
            student = student_data.get('student', {})
            c.drawString(100, 740, f"Student: {student.get('name', 'N/A')}")
            c.drawString(100, 720, f"Admission: {student.get('admission', 'N/A')}")
        
        c.drawString(100, 700, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(100, 680, f"System: {self.system_config['system_name']}")
        c.drawString(100, 660, "Please try again or contact system administrator.")
        
        if school_info and school_info.get('support_contact'):
            c.drawString(100, 640, f"Contact: {school_info['support_contact']}")
        
        c.save()
        return temp_file.name