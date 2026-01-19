"""
student_report.py - SIMPLE WORKING
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
    """Generate student report PDF"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method - SIMPLE VERSION"""
        try:
            # Create filename
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Get student info
            student = student_data['student']
            student_name = student['name']
            school_name = school_info.get('name', 'School') if school_info else 'School'
            
            # Create document WITH CORRECT METADATA
            doc = self.create_document(
                filepath=filepath,
                title=f"Student Report - {student_name}",
                subject=f"Academic Report - {school_name}",
                author=f"{self.system_config['author']}"
            )
            
            # Build simple story
            story = []
            
            # School name
            if school_info and school_info.get('name'):
                from reportlab.lib.styles import ParagraphStyle
                story.append(Paragraph(school_info['name'], self.styles['Heading2']))
            
            # Report title
            exam_id = class_data.get('metadata', {}).get('exam_id', 'Examination')
            story.append(Paragraph(f"{exam_id} - STUDENT REPORT", self.styles['Heading1']))
            story.append(Spacer(1, 20))
            
            # Student info
            info_text = f"""
            <b>Student Name:</b> {student['name']}<br/>
            <b>Admission No:</b> {student['admission']}<br/>
            <b>Gender:</b> {student['gender']}<br/>
            """
            story.append(Paragraph(info_text, self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Performance
            summary = student_data['summary']
            story.append(Paragraph("PERFORMANCE SUMMARY", self.styles['Heading2']))
            
            perf_data = [
                ["Total Marks", str(summary['total'])],
                ["Average", f"{summary['average']:.1f}%"],
                ["Grade", summary['grade']],
                ["Division", summary.get('division', 'N/A')],
                ["Remark", summary.get('remark', 'N/A')]
            ]
            
            table = Table(perf_data, colWidths=[100, 100])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Italic']
            ))
            story.append(Paragraph(
                f"System: {self.system_config['system_name']}",
                self.styles['Italic']
            ))
            
            # Build PDF with custom onFirstPage
            def add_metadata_and_footer(canvas, doc):
                self._add_metadata_to_canvas(canvas, doc)
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=add_metadata_and_footer, onLaterPages=add_metadata_and_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
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
        
        c = canvas.Canvas(temp_file.name)
        
        # Set metadata correctly
        c.setTitle("Report Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("Error Report")
        c.setCreator(self.system_config['system_name'])
        c.setProducer(f"{self.system_config['system_name']} v{self.system_config['version']}")
        
        # Content
        c.drawString(100, 800, "⚠️ REPORT GENERATION ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:60]}")
        c.drawString(100, 760, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        c.save()
        return temp_file.name