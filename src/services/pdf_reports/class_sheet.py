"""
class_sheet.py - WITH METADATA
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ClassSheet(BasePDFTemplate):
    """Generate class result sheet with metadata"""
    
    def generate(self, class_data, school_info=None):
        try:
            # Create filename
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Prepare metadata
            class_id = class_data['metadata']['class_id']
            exam_id = class_data['metadata'].get('exam_id', 'Examination')
            school_name = school_info.get('name', 'School') if school_info else 'School'
            
            title = f"Class Result Sheet - {class_id}"
            subject = f"Class Results for {class_id} - {school_name} - {exam_id}"
            author = f"{self.system_config['system_name']} for {school_name}"
            
            # Create document with metadata
            doc = self.create_document(
                filepath=filepath,
                title=title,
                subject=subject,
                author=author
            )
            
            # Build content
            story = self._build_content(class_data, school_info)
            
            # Build PDF
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            logger.info(f"Generated class sheet with metadata: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e), class_data, school_info)
    
    def _build_content(self, class_data, school_info):
        """Build class sheet content"""
        story = []
        styles = getSampleStyleSheet()
        
        # School header
        if school_info and school_info.get('name'):
            story.append(Paragraph(school_info['name'], styles['Heading2']))
        
        # Class sheet title
        metadata = class_data['metadata']
        title = f"CLASS RESULT SHEET - {metadata['class_id']}"
        if metadata.get('exam_id'):
            title += f" - {metadata['exam_id']}"
        
        story.append(Paragraph(title, styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Class info
        info_text = f"Academic Year: {metadata.get('academic_year', 'N/A')}"
        if metadata.get('term'):
            info_text += f" | Term: {metadata['term']}"
        if metadata.get('stream'):
            info_text += f" | Stream: {metadata['stream']}"
        
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Paragraph(f"Total Students: {metadata.get('students', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Students table
        students = class_data['students']
        data = [["RANK", "NAME", "ADM NO", "TOTAL", "AVG%", "GRADE", "DIV", "REMARK"]]
        
        for student in students:
            stu = student['student']
            summary = student['summary']
            data.append([
                str(summary['rank']),
                stu['name'],
                stu['admission'],
                str(summary['total']),
                f"{summary['average']:.1f}",
                summary['grade'],
                summary.get('division', ''),
                summary['remark'][:15]  # Shorten remark
            ])
        
        table = Table(data, colWidths=[40, 120, 70, 50, 50, 40, 40, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,1), (7,-1), 'CENTER'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,i), (-1,i), colors.HexColor('#f8f9fa'))
                ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Generation info
        story.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}",
            styles['Italic']
        ))
        
        return story
    
    def _create_filename(self, class_data, school_info):
        """Create filename"""
        class_id = class_data['metadata']['class_id']
        clean_class = re.sub(r'[^\w\-]', '_', class_id)[:30]
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_ClassSheet_{clean_class}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg, class_data=None, school_info=None):
        """Create error PDF with metadata"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(temp_file.name)
        
        # Set metadata
        c.setTitle("Class Sheet Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("Error Report")
        c.setKeywords("error, class, sheet, system")
        c.setCreator(self.system_config['system_name'])
        
        # Content
        c.drawString(100, 800, "⚠️ CLASS SHEET GENERATION ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:80]}")
        
        if class_data:
            metadata = class_data.get('metadata', {})
            c.drawString(100, 760, f"Class: {metadata.get('class_id', 'N/A')}")
            c.drawString(100, 740, f"Exam: {metadata.get('exam_id', 'N/A')}")
        
        c.drawString(100, 720, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(100, 700, f"System: {self.system_config['system_name']}")
        
        c.save()
        return temp_file.name