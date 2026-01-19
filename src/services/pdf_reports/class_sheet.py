"""
class_sheet.py - UPGRADED VERSION
Same logic, professional presentation
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, PageBreak
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
    """Enhanced class sheet with professional design"""
    
    def generate(self, class_data, school_info=None):
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            class_id = class_data['metadata']['class_id']
            
            doc = self.create_document(
                filepath=filepath,
                title=f"Class Result Sheet - {class_id}",
                subject=f"Class Results for {class_id}",
                author=self.system_config['author']
            )
            
            story = self._build_content(class_data, school_info)
            
            def build_canvas(canvas, doc):
                school_name = school_info.get('name') if school_info else None
                self.add_professional_header(canvas, doc, school_name)
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=build_canvas, onLaterPages=build_canvas)
            
            logger.info(f"Generated enhanced class sheet: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_content(self, class_data, school_info):
        """Build enhanced class sheet content"""
        story = []
        
        metadata = class_data['metadata']
        students = class_data['students']
        
        # Title
        story.append(Paragraph(
            f"CLASS RESULT SHEET - {metadata['class_id']}",
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 10))
        
        # Class info box
        info_text = f"""
        <b>Exam:</b> {metadata.get('exam_id', 'N/A')} | 
        <b>Class:</b> {metadata.get('class_id', 'N/A')} | 
        <b>Students:</b> {metadata.get('students', len(students))} |
        <b>Academic Year:</b> {datetime.now().year}
        """
        story.append(Paragraph(info_text, self.styles['StudentInfo']))
        story.append(Spacer(1, 20))
        
        # Summary statistics
        if len(students) > 0:
            totals = [s['summary']['total'] for s in students]
            averages = [s['summary']['average'] for s in students]
            
            stats_data = [
                ["STATISTICS", "VALUE"],
                ["Class Average", f"{sum(averages)/len(averages):.1f}%"],
                ["Highest Score", f"{max(totals)}"],
                ["Lowest Score", f"{min(totals)}"],
                ["Total Students", f"{len(students)}"],
                ["Date Generated", datetime.now().strftime('%Y-%m-%d')]
            ]
            
            stats_table = Table(stats_data, colWidths=[120, 100])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
                ('ROWBACKGROUNDS', (1,1), (-1,-1), [self.colors['row_even'], self.colors['row_odd']]),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # Students table - enhanced
        story.append(Paragraph("STUDENT PERFORMANCE LIST", self.styles['SectionHeader']))
        
        # Prepare table data
        data = [["RANK", "NAME", "ADM NO", "TOTAL", "AVG%", "GRADE", "REMARKS"]]
        
        for idx, student in enumerate(students):
            stu = student['student']
            summary = student['summary']
            
            # Alternate row colors
            row_color = self.colors['row_even'] if idx % 2 == 0 else self.colors['row_odd']
            
            data.append([
                f"<b>{summary['rank']}</b>",
                stu['name'][:25],  # Limit name length
                stu['admission'],
                f"<font size='10'><b>{summary['total']}</b></font>",
                self._get_average_with_color(summary['average']),
                self._get_grade_with_color(summary['grade']),
                summary.get('remark', 'N/A')[:15]  # Limit remarks
            ])
        
        table = Table(data, colWidths=[40, 150, 80, 60, 60, 50, 80])
        
        # Enhanced table styling
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['header']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('ALIGN', (2,0), (2,-1), 'CENTER'),  # ADM NO center
            ('ALIGN', (0,0), (0,-1), 'CENTER'),  # RANK center
            ('ALIGN', (3,0), (4,-1), 'CENTER'),  # TOTAL & AVG% center
            ('ALIGN', (5,0), (5,-1), 'CENTER'),  # GRADE center
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
        
        # Add alternating row colors
        for i in range(1, len(data)):
            bg_color = self.colors['row_even'] if i % 2 == 1 else self.colors['row_odd']
            table_style.add('BACKGROUND', (0,i), (-1,i), bg_color)
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Grading key
        story.append(Paragraph("GRADING KEY", self.styles['SectionHeader']))
        
        grade_key = [
            ["GRADE", "RANGE", "INTERPRETATION"],
            ["A", "80-100%", "Excellent - Outstanding performance"],
            ["B", "70-79%", "Good - Above average"],
            ["C", "60-69%", "Average - Meets requirements"],
            ["D", "50-59%", "Below Average - Needs improvement"],
            ["E", "40-49%", "Poor - Requires intervention"],
            ["F", "Below 40%", "Fail - Does not meet minimum"]
        ]
        
        grade_table = Table(grade_key, colWidths=[50, 80, 250])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['secondary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
            ('ROWBACKGROUNDS', (1,1), (-1,-1), [self.colors['row_even'], self.colors['row_odd']]),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        
        story.append(grade_table)
        story.append(Spacer(1, 20))
        
        # Footer note
        footer_note = f"""
        <font size='8' color='gray'>
        <i>
        This is an official class result sheet generated by {self.system_config['system_name']}.<br/>
        Report ID: {metadata['class_id']}_{datetime.now().strftime('%Y%m%d')}<br/>
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        For official use only. Unauthorized distribution is prohibited.
        </i>
        </font>
        """
        story.append(Paragraph(footer_note, self.styles['Normal']))
        
        return story
    
    def _get_average_with_color(self, average):
        """Color code averages"""
        if average >= 80:
            color = '#27AE60'  # Green
        elif average >= 70:
            color = '#2ECC71'  # Light Green
        elif average >= 60:
            color = '#F39C12'  # Orange
        elif average >= 50:
            color = '#E67E22'  # Dark Orange
        elif average >= 40:
            color = '#E74C3C'  # Red
        else:
            color = '#C0392B'  # Dark Red
        
        return f"<font color='{color}'><b>{average:.1f}</b></font>"
    
    def _get_grade_with_color(self, grade):
        """Color code grades"""
        color_map = {
            'A': '#27AE60',
            'B': '#2ECC71', 
            'C': '#F39C12',
            'D': '#E67E22',
            'E': '#E74C3C',
            'F': '#C0392B'
        }
        color = color_map.get(grade.upper(), '#000000')
        return f"<font color='{color}'><b>{grade}</b></font>"
    
    def _create_filename(self, class_data, school_info):
        """Create filename - SAME LOGIC"""
        class_id = class_data['metadata']['class_id']
        clean_class = re.sub(r'[^\w\-]', '_', class_id)[:20]
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_ClassResult_{clean_class}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Enhanced error PDF for class sheet"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        
        c.setTitle("Class Sheet Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("System Error Report")
        c.setCreator(self.system_config['system_name'])
        c.setProducer(f"{self.system_config['system_name']} v{self.system_config['version']}")
        
        # Professional error display
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.colors['danger'])
        c.drawString(100, 800, "CLASS SHEET GENERATION ERROR")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors['dark'])
        c.drawString(100, 770, "The system was unable to generate the class result sheet.")
        
        # Error box
        c.setFillColor(colors.HexColor('#FFF3CD'))  # Warning background
        c.setStrokeColor(colors.HexColor('#FFEEBA'))  # Warning border
        c.rect(100, 700, 400, 60, fill=1, stroke=1)
        
        c.setFillColor(colors.HexColor('#856404'))  # Warning text
        c.setFont("Helvetica-Bold", 11)
        c.drawString(110, 740, "Technical Details:")
        
        c.setFont("Courier", 9)
        c.drawString(110, 720, error_msg[:70])
        
        # Recovery instructions
        c.setFillColor(self.colors['dark'])
        c.setFont("Helvetica", 9)
        c.drawString(100, 650, "Suggested Actions:")
        c.drawString(110, 630, "1. Verify the class data is complete and valid")
        c.drawString(110, 610, "2. Check student records for inconsistencies")
        c.drawString(110, 590, "3. Contact system administrator if error persists")
        
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawString(100, 550, f"System: {self.system_config['system_name']}")
        c.drawString(100, 535, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        return temp_file.name