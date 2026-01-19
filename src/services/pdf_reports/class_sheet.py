"""
class_sheet.py - SIMPLE WORKING VERSION
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate
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
    """Generate class result sheet"""
    
    def generate(self, class_data, school_info=None):
        try:
            # Create filename
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Prepare metadata
            class_id = class_data['metadata']['class_id']
            
            # Create document
            doc = self.create_document(
                filepath=filepath,
                title=f"Class Sheet - {class_id}",
                subject=f"Class Results for {class_id}",
                author=self.system_config['author']
            )
            
            # Build content
            story = self._build_content(class_data, school_info)
            
            # Build PDF
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            logger.info(f"Generated class sheet: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_content(self, class_data, school_info):
        """Build content"""
        story = []
        styles = getSampleStyleSheet()
        
        # School header
        if school_info and school_info.get('name'):
            story.append(Paragraph(school_info['name'], styles['Heading2']))
        
        # Title
        metadata = class_data['metadata']
        story.append(Paragraph(f"CLASS RESULT SHEET - {metadata['class_id']}", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Class info
        story.append(Paragraph(f"Exam: {metadata.get('exam_id', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Students: {metadata.get('students', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Students table
        students = class_data['students']
        data = [["RANK", "NAME", "ADM NO", "TOTAL", "AVG%", "GRADE"]]
        
        for student in students:
            stu = student['student']
            summary = student['summary']
            data.append([
                str(summary['rank']),
                stu['name'][:20],  # Limit name length
                stu['admission'],
                str(summary['total']),
                f"{summary['average']:.1f}",
                summary['grade']
            ])
        
        table = Table(data, colWidths=[50, 150, 80, 60, 60, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Italic']
        ))
        
        return story
    
    def _create_filename(self, class_data, school_info):
        """Create filename"""
        class_id = class_data['metadata']['class_id']
        clean_class = re.sub(r'[^\w\-]', '_', class_id)[:20]
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_Class_{clean_class}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(temp_file.name)
        
        # Set metadata
        c.setTitle("Class Sheet Error")
        c.setAuthor(self.system_config['author'])
        
        # Content
        c.drawString(100, 800, "⚠️ CLASS SHEET ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:80]}")
        
        c.save()
        return temp_file.name