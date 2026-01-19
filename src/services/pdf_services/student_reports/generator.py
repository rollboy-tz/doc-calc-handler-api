"""
services/pdf_services/student_reports/generator.py
"""
import os
import tempfile
from datetime import datetime
from ..base.template import PDFBaseTemplate
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

class StudentReportGenerator(PDFBaseTemplate):
    """Generate student academic reports"""
    
    def generate(self, student_data, class_info=None, school_info=None):
        """
        Generate student report PDF
        
        Args:
            student_data: Student information and performance
            class_info: Class information
            school_info: School information
        
        Returns:
            Path to generated PDF file
        """
        try:
            # Prepare data
            student = student_data.get('student', {})
            summary = student_data.get('summary', {})
            
            # Create filename
            filename = self._create_filename(student)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Create document
            doc = self.create_document(
                filepath=filepath,
                title=f"Student Report - {student.get('name', 'Unknown')}",
                subject=f"Academic Report for {student.get('name', 'Student')}",
                author=self.system_config['system_name']
            )
            
            # Build content
            story = self._build_content(student_data, class_info, school_info)
            
            # Build PDF with headers and footers
            def on_each_page(canvas, doc):
                # Add header
                school_name = school_info.get('name') if school_info else None
                report_title = f"STUDENT ACADEMIC REPORT - {class_info.get('exam_name', 'TERM EXAMINATION')}" if class_info else "STUDENT REPORT"
                self.add_header(canvas, doc, school_name, report_title)
                
                # Add footer
                self.add_footer(canvas, doc)
            
            # Build the PDF
            doc.build(story, onFirstPage=on_each_page, onLaterPages=on_each_page)
            
            logger.info(f"Generated student report: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_content(self, student_data, class_info, school_info):
        """Build the report content"""
        from reportlab.platypus import KeepTogether
        
        story = []
        
        student = student_data.get('student', {})
        summary = student_data.get('summary', {})
        
        # Add space below header
        story.append(Spacer(1, 40))
        
        # Student information section
        story.append(Paragraph("STUDENT INFORMATION", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        info_text = f"""
        <b>Full Name:</b> {student.get('name', 'Not Provided')}<br/>
        <b>Admission Number:</b> {student.get('admission', 'N/A')}<br/>
        <b>Gender:</b> {student.get('gender', 'N/A')}<br/>
        <b>Class:</b> {class_info.get('class_name', 'N/A') if class_info else 'N/A'}<br/>
        <b>Academic Year:</b> {datetime.now().year}
        """
        
        story.append(Paragraph(info_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Academic performance section
        story.append(Paragraph("ACADEMIC PERFORMANCE", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Performance table
        perf_data = [
            ["Total Marks", f"{summary.get('total', 0):,}"],
            ["Average Score", f"{summary.get('average', 0):.1f}%"],
            ["Grade", f"{summary.get('grade', 'N/A')}"],
            ["Class Position", f"{summary.get('position', 'N/A')}"],
            ["Division", f"{summary.get('division', 'N/A')}"],
            ["Remarks", f"{summary.get('remark', 'N/A')}"]
        ]
        
        table = Table(perf_data, colWidths=[150, 150])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
        
        # Grading key
        story.append(Paragraph("GRADING KEY", self.styles['Heading3']))
        story.append(Spacer(1, 5))
        
        grade_info = """
        <b>A (80-100%):</b> Excellent &nbsp; | &nbsp;
        <b>B (70-79%):</b> Very Good &nbsp; | &nbsp;
        <b>C (60-69%):</b> Good &nbsp; | &nbsp;
        <b>D (50-59%):</b> Satisfactory &nbsp; | &nbsp;
        <b>E (40-49%):</b> Fair &nbsp; | &nbsp;
        <b>F (Below 40%):</b> Fail
        """
        
        story.append(Paragraph(grade_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Generation info
        gen_info = f"""
        <font size='9' color='gray'>
        <i>
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        System: {self.system_config['system_name']} v{self.system_config['version']}<br/>
        This is an official academic document.
        </i>
        </font>
        """
        
        story.append(Paragraph(gen_info, self.styles['Normal']))
        
        return story
    
    def _create_filename(self, student):
        """Create filename for the report"""
        student_name = student.get('name', 'Unknown')
        admission = student.get('admission', 'NONE')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Clean filename
        clean_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')[:20]
        
        return f"Student_Report_{admission}_{clean_name}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_message):
        """Create error PDF when generation fails"""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            c = canvas.Canvas(temp_file.name, pagesize=A4)
            
            # Set document properties
            c.setTitle("Report Generation Error")
            c.setAuthor(self.system_config['system_name'])
            c.setSubject("System Error Report")
            
            # Error message
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(colors.HexColor('#E74C3C'))
            c.drawString(50, 800, "REPORT GENERATION ERROR")
            
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(50, 770, "The system encountered an error while generating the report.")
            
            # Error details
            c.setFont("Helvetica", 9)
            c.drawString(50, 740, "Error Details:")
            
            c.setFont("Courier", 8)
            c.drawString(50, 720, error_message[:100])
            
            # Contact information in footer
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(50, 50, f"System: {self.system_config['system_name']}")
            c.drawString(50, 35, f"Support: {self.system_config['support_email']}")
            c.drawRightString(550, 50, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            c.showPage()
            c.save()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating error PDF: {e}")
            # Fallback: create empty file
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            return temp_file.name