"""
class_sheet.py - LANDSCAPE MULTI-PAGE VERSION
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib import colors
import tempfile
import os
import re
from datetime import datetime
import logging
from reportlab.platypus.flowables import KeepTogether

logger = logging.getLogger(__name__)

class ClassSheet(BasePDFTemplate):
    """Professional class sheet with landscape orientation and multiple pages"""
    
    def generate(self, class_data, school_info=None):
        """Generate multi-page class sheet"""
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            class_id = class_data['metadata']['class_id']
            
            # Create document with LANDSCAPE orientation
            doc = self.create_document(
                filepath=filepath,
                title=f"Class Result Sheet - {class_id}",
                subject=f"Class Analysis Report for {class_id}",
                author=self.system_config['author'],
                orientation='landscape'  # LANDSCAPE MODE
            )
            
            # Build multi-page content
            story = self._build_multi_page_content(class_data, school_info)
            
            def build_canvas(canvas, doc):
                school_name = school_info.get('name') if school_info else None
                page_num = canvas.getPageNumber()
                
                # Different titles for different pages
                if page_num == 1:
                    page_title = "CLASS PERFORMANCE OVERVIEW"
                elif page_num == 2:
                    page_title = "DETAILED SUBJECT ANALYSIS"
                else:
                    page_title = f"CLASS REPORT - Page {page_num}"
                
                self.add_professional_header(canvas, doc, school_name, page_title)
                self.add_footer(canvas, doc)
            
            doc.build(story, onFirstPage=build_canvas, onLaterPages=build_canvas)
            
            logger.info(f"Generated professional class sheet: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _build_multi_page_content(self, class_data, school_info):
        """Build multi-page content with different sections"""
        story = []
        
        metadata = class_data['metadata']
        analytics = class_data.get('analytics', {})
        students = class_data['students']
        
        # PAGE 1: CLASS OVERVIEW AND STUDENT RANKING
        story.append(self._build_class_overview_page(metadata, analytics, school_info))
        story.append(Spacer(1, 10))
        
        # Student ranking table
        story.append(self._build_student_ranking_table(students))
        story.append(Spacer(1, 15))
        
        # Class statistics
        story.append(self._build_class_statistics(analytics))
        
        # PAGE BREAK
        story.append(PageBreak())
        
        # PAGE 2: SUBJECT ANALYSIS
        story.append(self._build_subject_analysis_page(analytics))
        
        # If there are many subjects, add more pages
        if analytics.get('subjects'):
            subjects = list(analytics['subjects'].keys())
            # We could split subjects across pages if needed
            
        return story
    
    def _build_class_overview_page(self, metadata, analytics, school_info):
        """Build class overview section"""
        from reportlab.platypus import Paragraph
        
        content = []
        
        # Main title
        content.append(Paragraph(
            f"CLASS RESULT SHEET - {metadata['class_id']}",
            self.styles['ReportTitle']
        ))
        content.append(Spacer(1, 5))
        
        # Exam info
        exam_info = f"""
        <b>Exam:</b> {metadata.get('exam_id', 'N/A')} | 
        <b>Academic Year:</b> {datetime.now().year} | 
        <b>Grading System:</b> {metadata.get('system_name', 'Standard')}
        """
        content.append(Paragraph(exam_info, self.styles['DataLabel']))
        content.append(Spacer(1, 15))
        
        return content
    
    def _build_student_ranking_table(self, students):
        """Build professional student ranking table"""
        from reportlab.platypus import Table
        
        # Prepare table data
        data = []
        
        # Header row
        header = ["RANK", "NAME", "ADM NO", "GENDER", "TOTAL", "AVG%", "GRADE", "DIVISION", "REMARKS"]
        data.append(header)
        
        # Student rows
        for idx, student in enumerate(students):
            stu = student['student']
            summary = student['summary']
            
            # Format values
            avg_text = f"{summary['average']:.1f}"
            grade_text = summary['grade']
            division_text = summary.get('division', '-')
            remark_text = summary.get('remark', '-')
            
            if len(remark_text) > 15:
                remark_text = remark_text[:15] + "..."
            
            row = [
                str(summary['rank']),
                stu['name'],
                stu['admission'],
                stu['gender'],
                str(summary['total']),
                avg_text,
                grade_text,
                division_text,
                remark_text
            ]
            data.append(row)
        
        # Calculate column widths for landscape
        col_widths = [35, 140, 70, 45, 50, 45, 45, 50, 80]
        
        # Create table
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Apply styling
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0,0), (-1,0), self.colors['header']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            
            # Column alignments
            ('ALIGN', (0,1), (0,-1), 'CENTER'),  # Rank
            ('ALIGN', (3,1), (3,-1), 'CENTER'),  # Gender
            ('ALIGN', (4,1), (5,-1), 'CENTER'),  # Total & Avg
            ('ALIGN', (6,1), (7,-1), 'CENTER'),  # Grade & Division
            
            # Grid and borders
            ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Row height
            ('ROWBACKGROUNDS', (0,1), (-1,-1), 
             [self.colors['row_even'], self.colors['row_odd']]),
        ])
        
        # Add conditional formatting for grades
        for i in range(1, len(data)):
            grade = data[i][6]  # Grade column
            
            # Color coding based on grade
            if grade == 'A':
                table_style.add('TEXTCOLOR', (6,i), (6,i), colors.HexColor('#27AE60'))
                table_style.add('FONTNAME', (6,i), (6,i), 'Helvetica-Bold')
            elif grade == 'B':
                table_style.add('TEXTCOLOR', (6,i), (6,i), colors.HexColor('#2ECC71'))
            elif grade == 'C':
                table_style.add('TEXTCOLOR', (6,i), (6,i), colors.HexColor('#F39C12'))
            elif grade == 'D':
                table_style.add('TEXTCOLOR', (6,i), (6,i), colors.HexColor('#E67E22'))
            elif grade == 'E' or grade == 'F':
                table_style.add('TEXTCOLOR', (6,i), (6,i), colors.HexColor('#E74C3C'))
        
        table.setStyle(table_style)
        return table
    
    def _build_class_statistics(self, analytics):
        """Build class statistics section"""
        from reportlab.platypus import Table, Paragraph
        
        content = []
        
        content.append(Paragraph("CLASS STATISTICS", self.styles['SectionTitle']))
        content.append(Spacer(1, 5))
        
        class_stats = analytics.get('class', {})
        overview = class_stats.get('overview', {})
        gender_stats = class_stats.get('gender', {})
        grade_stats = class_stats.get('grades', {}).get('counts', {})
        
        # Statistics table
        stats_data = []
        
        # Row 1: Overview
        stats_data.append(["CLASS OVERVIEW", ""])
        stats_data.append(["Total Students", str(overview.get('students', 0))])
        stats_data.append(["Class Average", f"{overview.get('average', 0):.1f}%"])
        stats_data.append(["Highest Score", str(overview.get('range', {}).get('high', 0))])
        stats_data.append(["Lowest Score", str(overview.get('range', {}).get('low', 0))])
        stats_data.append(["", ""])
        
        # Row 2: Gender Distribution
        stats_data.append(["GENDER DISTRIBUTION", ""])
        if gender_stats.get('F'):
            stats_data.append(["Female Students", f"{gender_stats['F'].get('count', 0)} ({gender_stats['F'].get('percentage', 0):.1f}%)"])
        if gender_stats.get('M'):
            stats_data.append(["Male Students", f"{gender_stats['M'].get('count', 0)} ({gender_stats['M'].get('percentage', 0):.1f}%)"])
        stats_data.append(["", ""])
        
        # Row 3: Grade Distribution
        stats_data.append(["GRADE DISTRIBUTION", ""])
        for grade, count in grade_stats.items():
            percentage = class_stats.get('grades', {}).get('percentages', {}).get(grade, 0)
            stats_data.append([f"Grade {grade}", f"{count} ({percentage:.1f}%)"])
        
        stats_table = Table(stats_data, colWidths=[120, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
            ('ROWBACKGROUNDS', (1,1), (-1,-1), 
             [self.colors['row_even'], self.colors['row_odd']]),
            ('SPAN', (0,0), (1,0)),  # Span title row
            ('SPAN', (0,6), (1,6)),  # Span gender title
            ('SPAN', (0,12), (1,12)), # Span grade title
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        
        content.append(stats_table)
        return content
    
    def _build_subject_analysis_page(self, analytics):
        """Build subject analysis page"""
        from reportlab.platypus import Paragraph, Table
        
        content = []
        
        # Page title
        content.append(Paragraph("SUBJECT PERFORMANCE ANALYSIS", self.styles['ReportTitle']))
        content.append(Spacer(1, 10))
        
        subjects = analytics.get('subjects', {})
        
        if not subjects:
            content.append(Paragraph("No subject data available.", self.styles['DataLabel']))
            return content
        
        # Create a summary table of all subjects
        summary_data = [["SUBJECT", "AVERAGE", "HIGHEST", "LOWEST", "PASS RATE", "TOP GRADE"]]
        
        for subject_name, subject_data in subjects.items():
            perf = subject_data.get('performance', {})
            grades = subject_data.get('grades', {}).get('counts', {})
            
            # Find top grade
            top_grade = '-'
            if grades:
                # Find grade with highest count
                top_grade = max(grades.items(), key=lambda x: x[1])[0] if grades else '-'
            
            summary_data.append([
                subject_name.upper(),
                f"{perf.get('average', 0):.1f}%",
                str(perf.get('high', 0)),
                str(perf.get('low', 0)),
                f"{perf.get('pass_rate', 0):.1f}%",
                top_grade
            ])
        
        # Subject summary table
        summary_table = Table(summary_data, colWidths=[90, 60, 55, 55, 60, 60])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.colors['secondary']),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
            ('ROWBACKGROUNDS', (1,1), (-1,-1), 
             [self.colors['row_even'], self.colors['row_odd']]),
            ('ALIGN', (1,1), (4,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        
        content.append(summary_table)
        content.append(Spacer(1, 15))
        
        # Add detailed subject tables in groups of 3
        subject_list = list(subjects.items())
        
        for i in range(0, len(subject_list), 3):
            subject_group = subject_list[i:i+3]
            content.append(self._build_subject_detail_tables(subject_group))
            if i + 3 < len(subject_list):
                content.append(Spacer(1, 10))
        
        return content
    
    def _build_subject_detail_tables(self, subject_group):
        """Build detailed tables for a group of subjects"""
        from reportlab.platypus import Table, Paragraph
        
        content = []
        
        for subject_name, subject_data in subject_group:
            # Subject header
            content.append(Paragraph(
                f"{subject_name.upper()} ANALYSIS",
                self.styles['SectionTitle']
            ))
            
            # Create three-column layout for subject details
            perf = subject_data.get('performance', {})
            gender = subject_data.get('gender', {})
            grades = subject_data.get('grades', {})
            
            # Performance table
            perf_data = [
                ["PERFORMANCE", ""],
                ["Class Average", f"{perf.get('average', 0):.1f}%"],
                ["Highest Score", str(perf.get('high', 0))],
                ["Lowest Score", str(perf.get('low', 0))],
                ["Pass Rate", f"{perf.get('pass_rate', 0):.1f}%"],
                ["", ""],
                ["GENDER ANALYSIS", ""],
                ["Female Average", f"{gender.get('averages', {}).get('F', 0):.1f}%"],
                ["Male Average", f"{gender.get('averages', {}).get('M', 0):.1f}%"],
            ]
            
            perf_table = Table(perf_data, colWidths=[80, 60])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), self.colors['accent']),
                ('BACKGROUND', (0,6), (1,6), self.colors['accent']),
                ('TEXTCOLOR', (0,0), (1,0), colors.white),
                ('TEXTCOLOR', (0,6), (1,6), colors.white),
                ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,6), (1,6), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
                ('SPAN', (0,0), (1,0)),
                ('SPAN', (0,6), (1,6)),
                ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ]))
            
            # Grade distribution table
            grade_counts = grades.get('counts', {})
            grade_percentages = grades.get('percentages', {})
            
            grade_data = [["GRADE", "COUNT", "%"]]
            for grade in sorted(grade_counts.keys()):
                count = grade_counts[grade]
                percentage = grade_percentages.get(grade, 0)
                grade_data.append([grade, str(count), f"{percentage:.1f}%"])
            
            grade_table = Table(grade_data, colWidths=[40, 40, 40])
            grade_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.colors['primary']),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, self.colors['border']),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            
            # Combine tables side by side
            from reportlab.platypus import KeepTogether
            
            combined = Table([[perf_table, grade_table]], colWidths=[140, 120])
            combined.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (0,0), 0),
                ('RIGHTPADDING', (1,0), (1,0), 0),
            ]))
            
            content.append(combined)
            content.append(Spacer(1, 10))
        
        return KeepTogether(content)
    
    def _create_filename(self, class_data, school_info):
        """Create filename"""
        class_id = class_data['metadata']['class_id']
        clean_class = re.sub(r'[^\w\-]', '_', class_id)[:30]
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{school_code}_ClassReport_{clean_class}_{timestamp}.pdf"
    
    def _create_error_pdf(self, error_msg):
        """Enhanced error PDF"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        
        # Set metadata
        c.setTitle("Class Report Error")
        c.setAuthor(self.system_config['author'])
        c.setSubject("System Error Report")
        c.setCreator(self.system_config['system_name'])
        c.setProducer(f"{self.system_config['system_name']} v{self.system_config['version']}")
        
        # Professional error display
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.colors['danger'])
        c.drawString(50, 800, "CLASS REPORT GENERATION ERROR")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors['dark'])
        c.drawString(50, 770, "The system encountered an error while generating the class report.")
        
        # Error box
        c.setFillColor(colors.HexColor('#FFF3CD'))
        c.setStrokeColor(colors.HexColor('#FFEEBA'))
        c.roundRect(50, 700, 500, 60, 5, fill=1, stroke=1)
        
        c.setFillColor(colors.HexColor('#856404'))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, 740, "Error Details:")
        
        c.setFont("Courier", 9)
        c.drawString(60, 720, error_msg[:70] if len(error_msg) > 70 else error_msg)
        
        c.save()
        return temp_file.name