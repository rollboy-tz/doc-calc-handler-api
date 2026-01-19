"""
Student Report Generator using fpdf2
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
    """Generate student academic reports"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.validator = StudentReportValidator()
    
    def generate(self, 
                 student_data: Dict[str, Any],
                 class_info: Dict[str, Any],
                 school_info: Dict[str, Any]) -> str:
        """Generate student report PDF and return filepath"""
        try:
            # Validate data
            is_valid, message = self.validator.validate_student_data(student_data)
            if not is_valid:
                return self._create_error_pdf(message)
            
            # Generate filename
            student = student_data['student']
            filename = generate_filename(
                "student_report",
                f"{student['admission']}_{student['name']}"
            )
            filepath = get_temp_path(filename)
            
            # Build PDF
            self._build_header(school_info)
            self._build_title(class_info)
            self._build_student_info(student_data['student'])
            self._build_summary(student_data['summary'])
            
            # Add subjects if available
            if 'subjects' in student_data:
                subjects = student_data['subjects']
                is_valid, msg = self.validator.validate_subjects(subjects)
                if is_valid:
                    self._build_subjects_table(subjects)
            
            # Add comments if available
            if 'comments' in student_data:
                self._build_comments(student_data['comments'])
            
            # Add footer section
            self._build_footer(class_info)
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_header(self, school_info: Dict[str, Any]):
        """Build school header section"""
        # School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 14)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 10, school_info.get('name', 'SCHOOL NAME'), 0, 1, 'C')
        
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
        
        title = f"{exam_name} - TERM {term} {year}"
        self.add_title(title, 16)
    
    def _build_student_info(self, student: Dict[str, Any]):
        """Build student information section"""
        self.add_subtitle("STUDENT INFORMATION", 12)
        
        info_text = StudentReportTemplates.student_info(student)
        self.add_paragraph(info_text)
        self.ln(5)
    
    def _build_summary(self, summary: Dict[str, Any]):
        """Build academic summary section"""
        self.add_subtitle("ACADEMIC SUMMARY", 12)
        
        # Create summary table
        summary_data = StudentReportTemplates.summary_table(summary)
        
        # Draw table
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
        col_widths = [60, 60]
        
        for i, (label, value) in enumerate(summary_data):
            # Alternate row colors
            if i % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Draw cells
            self.cell(col_widths[0], 8, label, 'LR', 0, 'L', 1)
            self.cell(col_widths[1], 8, value, 'LR', 1, 'C', 1)
        
        # Close table borders
        self.cell(sum(col_widths), 0, '', 'T', 1)
        self.ln(10)
    
    def _build_subjects_table(self, subjects: list):
        """Build subjects performance table"""
        self.add_subtitle("SUBJECT PERFORMANCE", 12)
        
        headers, data, col_widths = StudentReportTemplates.subjects_table(subjects)
        
        # Table header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for row_idx, row in enumerate(data):
            # Alternate row colors
            if row_idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Draw row
            for col_idx, cell in enumerate(row):
                align = 'C' if col_idx in [0, 2, 3] else 'L'
                self.cell(col_widths[col_idx], 7, str(cell), 1, 0, align, 1)
            self.ln()
        
        self.ln(10)
    
    def _build_comments(self, comments: Dict[str, Any]):
        """Build comments section"""
        self.add_subtitle("COMMENTS", 12)
        
        if 'class_teacher' in comments:
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
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
        
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        footer_text = [
            f"Printed on: {date_printed}",
            f"Class: {class_info.get('class_name', 'N/A')}",
            f"Term: {class_info.get('term', 'N/A')}"
        ]
        
        for text in footer_text:
            self.cell(0, 5, text, 0, 1, 'C')
    
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