"""
student_report.py - FIXED SIMPLE VERSION
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
import tempfile
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StudentReport(BasePDFTemplate):
    """Simple student report - WORKING VERSION"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Simple generation method"""
        try:
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            student = student_data['student']
            summary = student_data['summary']
            
            doc = self.create_document(
                filepath=filepath,
                title=f"Student Report - {student['name']}",
                subject=f"Academic Report",
                author=self.system_config['author']
            )
            
            story = self._build_simple_content(student_data, class_data, school_info)
            
            def build_canvas(canvas, doc):
                school_name = school_info.get('name') if school_info else None
                self.add_professional_header(canvas, doc, school_name, "STUDENT REPORT")
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=build_canvas, onLaterPages=build_canvas)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_simple_content(self, student_data, class_data, school_info):
        """Build simple content"""
        story = []
        
        student = student_data['student']
        summary = student_data['summary']
        
        # Title
        exam_id = class_data.get('metadata', {}).get('exam_id', 'Examination')
        story.append(Paragraph(
            f"{exam_id} - STUDENT REPORT",
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 15))
        
        # Student info
        info_text = f"""
        <b>Student Name:</b> {student['name']}<br/>
        <b>Admission No:</b> {student['admission']}<br/>
        <b>Gender:</b> {student['gender']}<br/>
        <b>Class:</b> {class_data.get('metadata', {}).get('class_id', 'N/A')}
        """
        story.append(Paragraph(info_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Performance summary
        story.append(Paragraph("PERFORMANCE SUMMARY", self.styles['Heading3']))
        
        perf_data = [
            ["Total Marks", str(summary['total'])],
            ["Average", f"{summary['average']:.1f}%"],
            ["Grade", summary['grade']],
            ["Division", summary.get('division', 'N/A')],
            ["Remark", summary.get('remark', 'N/A')],
            ["Rank", str(summary.get('rank', 'N/A'))]
        ]
        
        table = Table(perf_data, colWidths=[100, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Italic']
        ))
        
        return story
    
    def _create_filename(self, student_data, school_info):
        """Create filename"""
        student_name = student_data['student']['name']
        clean_name = re.sub(r'[^\w\-]', '_', student_name)[:15]
        admission = student_data['student']['admission']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"Report_{admission}_{clean_name}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        
        c.setTitle("Report Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("Error Report")
        
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor('#E74C3C'))
        c.drawString(50, 800, "⚠️ REPORT ERROR")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(50, 770, f"Error: {error_msg[:80]}")
        
        c.save()
        return temp_file.name