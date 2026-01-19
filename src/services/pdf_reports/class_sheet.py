"""
services/pdf_reports/class_sheet.py - SIMPLE & WORKING
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
import tempfile
import os
from datetime import datetime

class ClassSheet(BasePDFTemplate):
    """Generate class result sheet - SIMPLE WORKING VERSION"""
    
    def generate(self, class_data, school_info=None):
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Landscape for class sheet
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4),
                title=f"Class Sheet - {class_data['metadata']['class_id']}",
                author=self.system_config['author']
            )
            
            story = []
            
            # Header
            story.append(Paragraph(
                f"CLASS RESULTS SHEET - {class_data['metadata']['class_id']}",
                self.styles['Heading1']
            ))
            
            story.append(Spacer(1, 10))
            
            # Simple students table
            story.append(self._create_simple_students_table(class_data))
            
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _create_simple_students_table(self, class_data):
        """Simple working students table"""
        metadata = class_data['metadata']
        students = class_data['students']
        
        # Header
        data = [["RANK", "NAME", "ADM NO", "TOTAL", "AVG%", "GRADE", "REMARK"]]
        
        # Add students
        for student in students:
            summary = student['summary']
            data.append([
                str(summary['rank']),
                student['student']['name'],
                student['student']['admission'],
                str(summary['total']),
                f"{summary['average']:.1f}",
                summary['grade'],
                summary['remark']
            ])
        
        # Create table
        table = Table(data, colWidths=[40, 150, 80, 60, 60, 50, 120])
        
        # Simple styling that works
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        
        # Color code grades
        for i in range(1, len(data)):
            grade = data[i][5]  # Grade column
            if grade == 'A':
                table.setStyle(TableStyle([('TEXTCOLOR', (5,i), (5,i), colors.green)]))
            elif grade == 'B':
                table.setStyle(TableStyle([('TEXTCOLOR', (5,i), (5,i), colors.blue)]))
            elif grade == 'C':
                table.setStyle(TableStyle([('TEXTCOLOR', (5,i), (5,i), colors.orange)]))
            elif grade in ['D', 'E']:
                table.setStyle(TableStyle([('TEXTCOLOR', (5,i), (5,i), colors.darkorange)]))
            elif grade == 'F':
                table.setStyle(TableStyle([('TEXTCOLOR', (5,i), (5,i), colors.red)]))
        
        return table
    
    def _create_error_pdf(self, error_msg):
        """Create error PDF"""
        import tempfile
        from reportlab.pdfgen import canvas
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        c = canvas.Canvas(temp_file.name)
        
        c.drawString(100, 800, "⚠️ CLASS SHEET ERROR")
        c.drawString(100, 780, f"Error: {error_msg[:100]}")
        c.drawString(100, 760, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        c.save()
        return temp_file.name