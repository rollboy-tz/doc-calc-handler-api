"""
class_sheet.py - FIX LOGGER ERROR
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
from datetime import datetime
import logging  # ✨ ADD THIS LINE

# ✨ DEFINE LOGGER
logger = logging.getLogger(__name__)

class ClassSheet(BasePDFTemplate):
    """Generate class result sheet - FIXED"""
    
    def generate(self, class_data, school_info=None):
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4),
                title=f"Class Sheet - {class_data['metadata']['class_id']}",
                author=self.system_config['author']
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Header
            story.append(Paragraph(f"CLASS SHEET - {class_data['metadata']['class_id']}", styles['Heading1']))
            story.append(Spacer(1, 10))
            
            # Students table
            students = class_data['students']
            data = [["Rank", "Name", "Admission", "Total", "Avg%", "Grade"]]
            
            for student in students:
                summary = student['summary']
                data.append([
                    str(summary['rank']),
                    student['student']['name'],
                    student['student']['admission'],
                    str(summary['total']),
                    f"{summary['average']:.1f}",
                    summary['grade']
                ])
            
            table = Table(data, colWidths=[50, 150, 80, 60, 60, 50])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            
            story.append(table)
            
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")  # ✨ NOW LOGGER IS DEFINED
            return self._create_error_pdf(str(e))
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        import tempfile
        from reportlab.pdfgen import canvas
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        c = canvas.Canvas(temp_file.name)
        
        c.drawString(100, 800, "⚠️ CLASS SHEET ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:100]}")
        
        c.save()
        return temp_file.name