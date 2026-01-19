"""
Individual Student Report
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.lib import colors
import tempfile
import os

class StudentReport(BasePDFTemplate):
    """Generate student report PDF"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method"""
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
            
            # Build with footer
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _create_filename(self, student_data, school_info):
        """Professional filename"""
        import re
        student_name = re.sub(r'[^\w\-]', '_', student_data['student']['name'])[:30]
        admission = student_data['student']['admission']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        return f"{school_code}_REPORT_{admission}_{student_name}_{timestamp}.pdf"
    
    def _create_header(self, student_data, class_data, school_info):
        """Create report header"""
        elements = []
        
        # School name if available
        if school_info and school_info.get('name'):
            elements.append(Paragraph(school_info['name'], self.styles['Heading1']))
        
        # Report title
        exam_name = class_data.get('metadata', {}).get('exam_id', 'EXAMINATION')
        elements.append(Paragraph(f"{exam_name} - STUDENT REPORT", self.styles['Heading2']))
        
        return elements
    
    def _create_student_table(self, student_data):
        """Student information table"""
        student = student_data['student']
        
        data = [
            ["STUDENT INFORMATION", "", "", ""],
            ["Full Name:", student['name'], "Admission:", student['admission']],
            ["Gender:", student['gender'], "Student ID:", student['id']],
        ]
        
        table = Table(data, colWidths=[100, 150, 100, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
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