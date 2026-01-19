"""
class_sheet.py - FIXED VERSION (Using available styles)
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

class ClassSheet(BasePDFTemplate):
    """Fixed class sheet using available styles"""
    
    def generate(self, class_data, school_info=None):
        """Generate class sheet - SIMPLIFIED VERSION"""
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            class_id = class_data['metadata']['class_id']
            
            # Create document
            doc = self.create_document(
                filepath=filepath,
                title=f"Class Result Sheet - {class_id}",
                subject=f"Class Results for {class_id}",
                author=self.system_config['author'],
                orientation='landscape'
            )
            
            # Build content
            story = self._build_simple_content(class_data, school_info)
            
            def build_canvas(canvas, doc):
                school_name = school_info.get('name') if school_info else None
                self.add_professional_header(canvas, doc, school_name, "CLASS RESULT SHEET")
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=build_canvas, onLaterPages=build_canvas)
            
            logger.info(f"Generated class sheet: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_simple_content(self, class_data, school_info):
        """Build simple but clean content"""
        story = []
        
        metadata = class_data['metadata']
        students = class_data['students']
        
        # School header
        if school_info and school_info.get('name'):
            story.append(Paragraph(school_info['name'], self.styles['SchoolHeader']))
        
        # Title
        story.append(Paragraph(
            f"CLASS RESULT SHEET - {metadata['class_id']}", 
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 10))
        
        # Exam info
        exam_info = f"""
        <b>Exam:</b> {metadata.get('exam_id', 'N/A')} | 
        <b>Academic Year:</b> {datetime.now().year} | 
        <b>Total Students:</b> {len(students)}
        """
        story.append(Paragraph(exam_info, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Students table
        story.append(self._build_simple_student_table(students))
        story.append(Spacer(1, 20))
        
        # Statistics if available
        if 'analytics' in class_data:
            story.append(self._build_simple_statistics(class_data['analytics']))
        
        # Footer
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Italic']
        ))
        story.append(Paragraph(
            f"System: {self.system_config['system_name']} v{self.system_config['version']}",
            self.styles['Italic']
        ))
        
        return story
    
    def _build_simple_student_table(self, students):
        """Build simple student table"""
        # Header
        data = [["RANK", "NAME", "ADM NO", "GENDER", "TOTAL", "AVG%", "GRADE", "REMARKS"]]
        
        # Add student rows
        for idx, student in enumerate(students):
            stu = student['student']
            summary = student['summary']
            
            # Truncate long names
            name = stu['name']
            if len(name) > 25:
                name = name[:22] + "..."
            
            # Truncate remarks
            remark = summary.get('remark', '-')
            if len(remark) > 15:
                remark = remark[:12] + "..."
            
            data.append([
                str(summary['rank']),
                name,
                stu['admission'],
                stu['gender'],
                str(summary['total']),
                f"{summary['average']:.1f}",
                summary['grade'],
                remark
            ])
        
        # Column widths for landscape
        col_widths = [40, 150, 80, 50, 60, 50, 50, 80]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Simple table styling
        table_style = TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), self.colors['header']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            
            # Grid
            ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Column alignments
            ('ALIGN', (0,1), (0,-1), 'CENTER'),  # Rank
            ('ALIGN', (3,1), (3,-1), 'CENTER'),  # Gender
            ('ALIGN', (4,1), (5,-1), 'CENTER'),  # Total & Avg
            ('ALIGN', (6,1), (6,-1), 'CENTER'),  # Grade
            
            # Row colors
            ('ROWBACKGROUNDS', (1,1), (-1,-1), 
             [self.colors['row_even'], self.colors['row_odd']]),
        ])
        
        table.setStyle(table_style)
        return table
    
    def _build_simple_statistics(self, analytics):
        """Build simple statistics section"""
        from reportlab.platypus import Table, Paragraph
        
        story = []
        
        story.append(Paragraph("CLASS STATISTICS", self.styles['Heading3']))
        story.append(Spacer(1, 5))
        
        class_stats = analytics.get('class', {})
        overview = class_stats.get('overview', {})
        
        # Simple statistics table
        stats_data = [
            ["STATISTIC", "VALUE"],
            ["Class Average", f"{overview.get('average', 0):.1f}%"],
            ["Highest Score", str(overview.get('range', {}).get('high', 0))],
            ["Lowest Score", str(overview.get('range', {}).get('low', 0))],
            ["Total Students", str(overview.get('students', 0))],
            ["Subjects", str(overview.get('subjects', 0))],
        ]
        
        # Add gender stats if available
        gender_stats = class_stats.get('gender', {})
        if gender_stats:
            stats_data.append(["", ""])
            stats_data.append(["GENDER BREAKDOWN", ""])
            for gender, data in gender_stats.items():
                gender_name = "Female" if gender == 'F' else "Male"
                stats_data.append([
                    gender_name,
                    f"{data.get('count', 0)} ({data.get('percentage', 0):.1f}%)"
                ])
        
        stats_table = Table(stats_data, colWidths=[120, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
            ('ROWBACKGROUNDS', (1,1), (-1,-1), 
             [self.colors['row_even'], self.colors['row_odd']]),
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ]))
        
        story.append(stats_table)
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
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        
        # Set metadata
        c.setTitle("Class Sheet Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("System Error Report")
        c.setCreator(self.system_config['system_name'])
        c.setProducer(f"{self.system_config['system_name']} v{self.system_config['version']}")
        
        # Error content
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor('#E74C3C'))
        c.drawString(50, 800, "⚠️ CLASS SHEET ERROR")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(50, 770, "The system encountered an error while generating the class sheet.")
        
        # Error message
        c.setFont("Helvetica", 9)
        c.drawString(50, 740, f"Error: {error_msg[:100]}")
        
        # System info
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawString(50, 710, f"System: {self.system_config['system_name']}")
        c.drawString(50, 695, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        return temp_file.name