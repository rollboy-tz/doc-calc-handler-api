"""
Student Report Generator using fpdf2 - COMPATIBLE WITH YOUR DATA STRUCTURE
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from .validator import StudentReportValidator
from .templates import StudentReportTemplates
from ..base.constants import PDFConstants

class StudentReportGenerator(BasePDFTemplate):
    """Generate student academic reports - Compatible with your API data"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.validator = StudentReportValidator()
    
    def generate(self, 
                 student_data: Dict[str, Any],
                 class_info: Dict[str, Any] = None,
                 school_info: Dict[str, Any] = None) -> str:
        """Generate student report PDF from your API response"""
        try:
            # Generate filename
            student_name = "unknown"
            admission = "unknown"
            
            # Extract student info from your data structure
            if isinstance(student_data, dict):
                if 'student' in student_data:
                    student = student_data['student']
                    student_name = student.get('name', 'unknown')
                    admission = student.get('admission', 'unknown')
                elif 'students' in student_data and len(student_data['students']) > 0:
                    # Handle array of students (first student)
                    student = student_data['students'][0]['student']
                    student_name = student.get('name', 'unknown')
                    admission = student.get('admission', 'unknown')
            
            filename = generate_filename(
                "student_report",
                f"{admission}_{student_name}"
            )
            filepath = get_temp_path(filename)
            
            # Build PDF based on data structure
            self._build_header(school_info or {})
            self._build_title(class_info or {})
            
            # Handle different data structures
            if isinstance(student_data, dict):
                if 'student' in student_data and 'summary' in student_data:
                    # Single student format
                    self._build_student_info(student_data['student'])
                    self._build_summary(student_data['summary'])
                    
                    # Add subjects if available
                    if 'subjects' in student_data:
                        self._build_subjects_table(student_data['subjects'])
                    
                    # Add comments if available
                    if 'comments' in student_data:
                        self._build_comments(student_data['comments'])
                
                elif 'students' in student_data and len(student_data['students']) > 0:
                    # Multiple students format - use first student
                    student_item = student_data['students'][0]
                    self._build_student_info(student_item['student'])
                    
                    if 'summary' in student_item:
                        self._build_summary(student_item['summary'])
                    
                    if 'subjects' in student_item:
                        self._build_subjects_table_from_dict(student_item['subjects'])
            
            # Add footer section
            self._build_footer(class_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_header(self, school_info: Dict[str, Any]):
        """Build school header section"""
        # School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        self.cell(0, 10, school_name, 0, 1, 'C')
        
        # School motto/address
        if 'motto' in school_info:
            self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.cell(0, 8, school_info['motto'], 0, 1, 'C')
        elif 'address' in school_info:
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.cell(0, 8, school_info['address'], 0, 1, 'C')
        
        self.ln(5)
        self.add_separator()
    
    def _build_title(self, class_info: Dict[str, Any]):
        """Build report title"""
        exam_name = class_info.get('exam_name', 'ACADEMIC REPORT')
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        class_name = class_info.get('class_name', '')
        
        title_parts = []
        if exam_name:
            title_parts.append(exam_name)
        if class_name:
            title_parts.append(f"CLASS: {class_name}")
        
        title = " - ".join(title_parts) if title_parts else "STUDENT ACADEMIC REPORT"
        
        self.add_title(title, 14)
        
        # Subtitle with term and year
        subtitle = f"TERM {term} - {year}"
        self.set_font(PDFConstants.DEFAULT_FONT, "I", 11)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, subtitle, 0, 1, 'C')
        self.ln(5)
    
    def _build_student_info(self, student: Dict[str, Any]):
        """Build student information section"""
        self.add_subtitle("STUDENT INFORMATION", 12)
        
        info_lines = []
        
        # Name
        if 'name' in student:
            info_lines.append(f"Name: {student['name']}")
        
        # Admission
        if 'admission' in student:
            info_lines.append(f"Admission No: {student['admission']}")
        
        # Gender
        if 'gender' in student:
            gender_display = "Male" if student['gender'] == 'M' else "Female" if student['gender'] == 'F' else student['gender']
            info_lines.append(f"Gender: {gender_display}")
        
        # Class/Stream
        if 'class' in student:
            info_lines.append(f"Class: {student['class']}")
        elif 'stream' in student:
            info_lines.append(f"Stream: {student['stream']}")
        
        # Year
        if 'year' in student:
            info_lines.append(f"Year: {student['year']}")
        
        # Join all lines
        info_text = "\n".join(info_lines)
        self.add_paragraph(info_text)
        self.ln(5)
    
    def _build_summary(self, summary: Dict[str, Any]):
        """Build academic summary section"""
        self.add_subtitle("ACADEMIC SUMMARY", 12)
        
        summary_data = []
        
        # Total Marks
        if 'total' in summary:
            summary_data.append(("Total Marks", f"{summary['total']:.0f}"))
        
        # Average
        if 'average' in summary:
            summary_data.append(("Average Score", f"{summary['average']:.2f}%"))
        
        # Grade
        if 'grade' in summary:
            summary_data.append(("Grade", summary['grade']))
        
        # Position/Rank
        if 'position' in summary:
            summary_data.append(("Position", str(summary['position'])))
        elif 'rank' in summary:
            summary_data.append(("Rank", str(summary['rank'])))
        
        # Division
        if 'division' in summary and summary['division']:
            summary_data.append(("Division", summary['division']))
        
        # Points (if available)
        if 'points' in summary and summary['points'] is not None:
            summary_data.append(("Points", str(summary['points'])))
        
        # Remark
        if 'remark' in summary:
            summary_data.append(("Remarks", summary['remark']))
        
        # Status
        if 'status' in summary:
            summary_data.append(("Status", summary['status']))
        
        # Create table
        if summary_data:
            col_widths = [70, 70]
            
            for i, (label, value) in enumerate(summary_data):
                # Alternate row colors
                if i % 2 == 0:
                    self.set_fill_color(*PDFConstants.LIGHT_COLOR)
                else:
                    self.set_fill_color(255, 255, 255)
                
                # Set font based on importance
                if label in ["Grade", "Position", "Rank"]:
                    self.set_font(PDFConstants.BOLD_FONT, "B", 10)
                else:
                    self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
                
                # Draw cells
                self.cell(col_widths[0], 8, label, 'LR', 0, 'L', 1)
                self.cell(col_widths[1], 8, value, 'LR', 1, 'C', 1)
            
            # Close table borders
            self.cell(sum(col_widths), 0, '', 'T', 1)
            self.ln(10)
    
    def _build_subjects_table(self, subjects: list):
        """Build subjects performance table from list format"""
        if not subjects:
            return
        
        self.add_subtitle("SUBJECT PERFORMANCE", 12)
        
        # Table header
        headers = ["No.", "Subject", "Score", "Grade", "Remarks", "Rank"]
        col_widths = [10, 60, 30, 25, 45, 20]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects, 1):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get subject data
            name = subject.get('name', 'N/A')
            score = subject.get('score', subject.get('marks', 0))
            grade = subject.get('grade', 'N/A')
            remarks = subject.get('remarks', subject.get('remark', ''))
            rank = subject.get('subject_rank', '')
            
            # Truncate long text
            name = name[:25] + '...' if len(name) > 25 else name
            remarks = remarks[:20] + '...' if len(remarks) > 20 else remarks
            
            # Draw row
            self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
            self.cell(col_widths[2], 7, f"{score:.1f}", 1, 0, 'C', 1)
            self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
            self.cell(col_widths[4], 7, remarks, 1, 0, 'L', 1)
            self.cell(col_widths[5], 7, str(rank) if rank else '', 1, 1, 'C', 1)
        
        self.ln(10)
    
    def _build_subjects_table_from_dict(self, subjects_dict: Dict[str, Any]):
        """Build subjects table from dictionary format (your API format)"""
        if not subjects_dict:
            return
        
        self.add_subtitle("SUBJECT PERFORMANCE", 12)
        
        # Convert dict to list
        subjects_list = []
        for subject_name, subject_data in subjects_dict.items():
            if isinstance(subject_data, dict):
                subject_data['name'] = subject_name.title()
                subjects_list.append(subject_data)
        
        # Sort by subject name
        subjects_list.sort(key=lambda x: x.get('name', ''))
        
        # Table header
        headers = ["No.", "Subject", "Marks", "Grade", "Points", "Rank"]
        col_widths = [10, 60, 30, 25, 30, 25]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get subject data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', 0)
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            rank = subject.get('subject_rank', '')
            remark = subject.get('remark', '')
            
            # Truncate long text
            name = name[:25] + '...' if len(name) > 25 else name
            
            # Draw row
            self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
            self.cell(col_widths[2], 7, f"{marks:.1f}", 1, 0, 'C', 1)
            self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
            
            # Points cell (may be empty for some systems)
            points_text = str(points) if points is not None else ''
            self.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
            
            # Rank cell
            rank_text = str(rank) if rank else ''
            self.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
            
            # Add remark as a small note if available
            if remark and idx % 3 == 0:  # Add remark every 3 rows to save space
                self.set_font(PDFConstants.ITALIC_FONT, "I", 8)
                self.set_text_color(*PDFConstants.SECONDARY_COLOR)
                self.cell(sum(col_widths), 4, f"   Remarks: {remark[:50]}", 0, 1, 'L')
                self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
                self.set_text_color(0, 0, 0)
        
        self.ln(10)
    
    def _build_comments(self, comments: Dict[str, Any]):
        """Build comments section"""
        self.add_subtitle("TEACHER'S COMMENTS", 12)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        
        if 'class_teacher' in comments:
            self.cell(0, 6, f"Class Teacher: {comments['class_teacher']}", 0, 1)
        
        if 'principal' in comments:
            self.cell(0, 6, f"Principal: {comments['principal']}", 0, 1)
        
        if 'remarks' in comments:
            self.ln(3)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
            self.multi_cell(0, 5, f"Remarks: {comments['remarks']}")
        
        self.ln(10)
    
    def _build_footer(self, class_info: Dict[str, Any]):
        """Build report footer"""
        self.add_separator()
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        
        footer_lines = []
        
        # Date printed
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        footer_lines.append(f"Printed on: {date_printed}")
        
        # Class info
        if 'class_name' in class_info:
            footer_lines.append(f"Class: {class_info['class_name']}")
        
        if 'term' in class_info:
            footer_lines.append(f"Term: {class_info['term']}")
        
        if 'exam_date' in class_info:
            footer_lines.append(f"Exam Date: {class_info['exam_date']}")
        
        # Print footer lines
        for line in footer_lines:
            self.cell(0, 5, line, 0, 1, 'C')
    
    def _create_error_pdf(self, error_message: str) -> str:
        """Create error PDF file"""
        from fpdf import FPDF
        
        filename = generate_filename("error", "student_report")
        filepath = get_temp_path(filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*PDFConstants.DANGER_COLOR)
        pdf.cell(0, 10, "Error Generating Report", 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, f"Error details: {error_message[:200]}")
        
        pdf.ln(10)
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 8, "Please contact support if this error persists.", 0, 1)
        
        pdf.output(filepath)
        return filepath