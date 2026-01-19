"""
student_report.py - FIX LOGGER ERROR
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
from datetime import datetime
import logging  # ✨ ADD THIS LINE

# ✨ DEFINE LOGGER
logger = logging.getLogger(__name__)

class StudentReport(BasePDFTemplate):
    """Generate student report PDF - FIXED"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method"""
        try:
            # Create filename
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Create document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                title=f"Report - {student_data['student']['name']}",
                author=self.system_config['author']
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Add content
            story.append(Paragraph("STUDENT REPORT", styles['Heading1']))
            story.append(Spacer(1, 20))
            
            # Student info
            student = student_data['student']
            story.append(Paragraph(f"Name: {student['name']}", styles['Normal']))
            story.append(Paragraph(f"Admission: {student['admission']}", styles['Normal']))
            
            # Summary
            summary = student_data['summary']
            data = [
                ["Total Marks:", str(summary['total'])],
                ["Average:", f"{summary['average']:.1f}%"],
                ["Grade:", summary['grade']],
                ["Remark:", summary['remark']]
            ]
            
            table = Table(data, colWidths=[100, 100])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Build
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")  # ✨ NOW LOGGER IS DEFINED
            return self._create_error_pdf(str(e))
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        import tempfile
        from reportlab.pdfgen import canvas
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        c = canvas.Canvas(temp_file.name)
        
        c.drawString(100, 800, "⚠️ REPORT ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:100]}")
        c.drawString(100, 760, f"System: {self.system_config['system_name']}")
        
        c.save()
        return temp_file.name