"""
student_report.py - UPGRADED VERSION
Same generation logic, better presentation
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib import colors
import tempfile
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StudentReport(BasePDFTemplate):
    """Enhanced student report with professional design"""
    
    def generate(self, student_data, class_data, school_info=None):
        """Main generation method - SAME LOGIC, BETTER OUTPUT"""
        try:
            filename = self._create_filename(student_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            student = student_data['student']
            summary = student_data['summary']
            school_name = school_info.get('name', 'School') if school_info else 'School'
            
            doc = self.create_document(
                filepath=filepath,
                title=f"Student Report - {student['name']}",
                subject=f"Academic Report - {school_name}",
                author=self.system_config['author']
            )
            
            story = self._build_content(student_data, class_data, school_info)
            
            def build_canvas(canvas, doc):
                self.add_professional_header(canvas, doc, school_name)
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=build_canvas, onLaterPages=build_canvas)
            
            logger.info(f"Generated enhanced student report: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Student report error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_content(self, student_data, class_data, school_info):
        """Build enhanced content"""
        story = []
        
        student = student_data['student']
        summary = student_data['summary']
        
        # School header (already in canvas)
        
        # Report title
        exam_id = class_data.get('metadata', {}).get('exam_id', 'Examination')
        story.append(Paragraph(
            f"{exam_id} - STUDENT PERFORMANCE REPORT",
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 15))
        
        # Student information box
        info_box = [
            ["STUDENT INFORMATION", ""],
            ["Full Name:", f"<b>{student['name']}</b>"],
            ["Admission No:", f"<b>{student['admission']}</b>"],
            ["Gender:", student['gender']],
            ["Class:", class_data.get('metadata', {}).get('class_id', 'N/A')],
            ["Exam:", exam_id]
        ]
        
        info_table = Table(info_box, colWidths=[120, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Performance summary - enhanced
        story.append(Paragraph("PERFORMANCE SUMMARY", self.styles['SectionHeader']))
        
        perf_data = [
            ["METRIC", "VALUE", "CATEGORY"],
            ["Total Marks", f"<font size='12'><b>{summary['total']}</b></font>", "Score"],
            ["Average", f"<font size='12'><b>{summary['average']:.1f}%</b></font>", "Percentage"],
            ["Grade", self._get_grade_with_color(summary['grade']), "Grade"],
            ["Division", summary.get('division', 'N/A'), "Division"],
            ["Remark", f"<i>{summary.get('remark', 'N/A')}</i>", "Remark"]
        ]
        
        perf_table = Table(perf_data, colWidths=[100, 100, 80])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['secondary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
            ('ROWBACKGROUNDS', (1,1), (-1,-1), [self.colors['row_even'], self.colors['row_odd']]),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(perf_table)
        story.append(Spacer(1, 25))
        
        # Grade interpretation
        story.append(Paragraph("GRADE INTERPRETATION", self.styles['SectionHeader']))
        
        grade_info = self._get_grade_interpretation(summary['grade'])
        story.append(Paragraph(grade_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Generation info
        gen_info = f"""
        <font size='8' color='gray'>
        Report ID: {student['admission']}_{datetime.now().strftime('%Y%m%d')}<br/>
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        System: {self.system_config['system_name']} v{self.system_config['version']}<br/>
        Valid for academic purposes only.
        </font>
        """
        story.append(Paragraph(gen_info, self.styles['Normal']))
        
        return story
    
    def _get_grade_with_color(self, grade):
        """Get grade with color coding"""
        color_map = {
            'A': '#27AE60',  # Green
            'B': '#2ECC71',  # Light Green
            'C': '#F39C12',  # Orange
            'D': '#E67E22',  # Dark Orange
            'E': '#E74C3C',  # Red
            'F': '#C0392B'   # Dark Red
        }
        
        color = color_map.get(grade.upper(), '#000000')
        return f"<font color='{color}' size='12'><b>{grade}</b></font>"
    
    def _get_grade_interpretation(self, grade):
        """Get grade interpretation"""
        interpretations = {
            'A': "Excellent performance. Student has demonstrated outstanding understanding and mastery of the subject matter.",
            'B': "Good performance. Above average understanding with room for improvement in some areas.",
            'C': "Average performance. Meets basic requirements but needs improvement.",
            'D': "Below average. Requires significant improvement and additional support.",
            'E': "Poor performance. Immediate intervention and remedial work required.",
            'F': "Fail. Does not meet minimum requirements for passing."
        }
        return interpretations.get(grade.upper(), "Grade interpretation not available.")
    
    def _create_filename(self, student_data, school_info):
        """Create filename - SAME LOGIC"""
        student_name = student_data['student']['name']
        clean_name = re.sub(r'[^\w\-]', '_', student_name)[:20]
        admission = student_data['student']['admission']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"StudentReport_{admission}_{clean_name}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Enhanced error PDF"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        
        # Set metadata
        c.setTitle("Report Generation Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("System Error Report")
        c.setCreator(self.system_config['system_name'])
        c.setProducer(f"{self.system_config['system_name']} v{self.system_config['version']}")
        
        # Professional error page
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.colors['danger'])
        c.drawString(100, 800, "⚠️ REPORT GENERATION ERROR")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors['dark'])
        c.drawString(100, 770, "The system encountered an error while generating your report.")
        
        # Error details box
        c.setFillColor(self.colors['light'])
        c.rect(100, 700, 400, 50, fill=1, stroke=0)
        
        c.setFillColor(self.colors['danger'])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(110, 730, "Error Details:")
        
        c.setFillColor(self.colors['dark'])
        c.setFont("Courier", 9)
        c.drawString(110, 710, error_msg[:80])
        
        # Contact info
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawString(100, 650, f"System: {self.system_config['system_name']}")
        c.drawString(100, 635, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 620, "Please contact system administrator for assistance.")
        
        c.save()
        return temp_file.name