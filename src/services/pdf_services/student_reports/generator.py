"""
Student Report Generators for different education systems
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from .templates import (
    ACSEEReportTemplates,
    CSEEReportTemplates,
    PLSEReportTemplates,
    GenericReportTemplates
)
from ..base.constants import PDFConstants

# ========== BASE REPORT GENERATOR ==========

class BaseReportGenerator(BasePDFTemplate):
    """Base class for all report generators"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_name = self.config.get('system_name', '')
        self.system_rule = self.config.get('system_rule', '').lower()
        self.templates = self._get_templates()
    
    def _get_templates(self):
        """Get templates based on system rule"""
        return GenericReportTemplates()
    
    def generate(self, 
                 student_data: Dict[str, Any],
                 class_info: Dict[str, Any] = None,
                 school_info: Dict[str, Any] = None) -> str:
        """Generate student report PDF"""
        try:
            # Generate filename
            student = student_data.get('student', {})
            student_name = student.get('name', 'unknown')
            admission = student.get('admission', 'unknown')
            
            filename = generate_filename(
                f"report_{self.system_rule}",
                f"{admission}_{student_name}"
            )
            filepath = get_temp_path(filename)
            
            # Build PDF
            self._build_document(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_document(self, student_data: Dict[str, Any], 
                        class_info: Dict[str, Any], 
                        school_info: Dict[str, Any]):
        """Build complete document"""
        self._build_header(school_info)
        self._build_title(class_info)
        self._build_student_info(student_data.get('student', {}))
        self._build_summary(student_data.get('summary', {}))
        
        # Build subjects based on format
        if 'subjects' in student_data:
            subjects = student_data['subjects']
            if isinstance(subjects, dict):
                self._build_subjects_table_from_dict(subjects)
            elif isinstance(subjects, list):
                self._build_subjects_table_from_list(subjects)
        
        self._build_footer(class_info)
    
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
        
        pdf.output(filepath)
        return filepath

# ========== ACSEE REPORT GENERATOR (A-Level) ==========

class ACSEEReportGenerator(BaseReportGenerator):
    """Generate ACSEE (Advanced Level) reports"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.templates = ACSEEReportTemplates()
    
    def _build_header(self, school_info: Dict[str, Any]):
        """Build ACSEE-specific header"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        # School name with ACSEE label
        school_name = school_info.get('name', 'ADVANCED SECONDARY SCHOOL')
        self.cell(0, 10, f"{school_name} - ADVANCED LEVEL", 0, 1, 'C')
        
        # Add system info
        self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, "NATIONAL EXAMINATIONS COUNCIL OF TANZANIA", 0, 1, 'C')
        
        self.ln(5)
        self.add_separator()
    
    def _build_summary(self, summary: Dict[str, Any]):
        """Build ACSEE-specific summary"""
        self.add_subtitle("ACADEMIC SUMMARY - ADVANCED LEVEL", 12)
        
        # ACSEE specific summary items
        summary_items = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Division", summary.get('division', 'N/A')),
            ("Points", str(summary.get('points', 'N/A'))),
            ("Principals", str(summary.get('principals', 'N/A'))),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'N/A'))
        ]
        
        self._draw_summary_table(summary_items)
        
        # Remarks
        if 'remark' in summary:
            self.ln(5)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.multi_cell(0, 5, f"Remarks: {summary['remark']}")
    
    def _build_subjects_table_from_dict(self, subjects_dict: Dict[str, Any]):
        """Build ACSEE subjects table"""
        self.add_subtitle("SUBJECT PERFORMANCE - ADVANCED LEVEL", 12)
        
        # ACSEE table headers
        headers = ["No.", "Subject", "Marks", "Grade", "Points", "Status"]
        col_widths = [10, 70, 30, 25, 30, 35]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Process subjects
        subjects_list = []
        for subject_name, subject_data in subjects_dict.items():
            if isinstance(subject_data, dict):
                subject_item = subject_data.copy()
                subject_item['name'] = subject_name.title()
                subjects_list.append(subject_item)
        
        # Sort by subject name
        subjects_list.sort(key=lambda x: x.get('name', ''))
        
        # Draw table
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', 0)
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            attended = subject.get('attended', False)
            passed = subject.get('pass', False)
            
            # Status based on attendance and pass
            if not attended:
                status = "ABSENT"
            elif not passed:
                status = "FAIL"
            else:
                status = "PASS"
            
            # Draw row
            self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 7, name[:25], 1, 0, 'L', 1)
            
            # Marks (show N/A if absent)
            marks_text = f"{marks:.1f}" if marks is not None else "N/A"
            self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
            
            self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
            
            # Points (show N/A if absent)
            points_text = str(points) if points is not None else "N/A"
            self.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
            
            # Status with color coding
            if status == "ABSENT":
                self.set_text_color(*PDFConstants.DANGER_COLOR)
            elif status == "FAIL":
                self.set_text_color(*PDFConstants.WARNING_COLOR)
            
            self.cell(col_widths[5], 7, status, 1, 1, 'C', 1)
            
            # Reset color
            self.set_text_color(0, 0, 0)
        
        self.ln(10)

# ========== CSEE REPORT GENERATOR (O-Level) ==========

class CSEEReportGenerator(BaseReportGenerator):
    """Generate CSEE (Certificate Level) reports"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.templates = CSEEReportTemplates()
    
    def _build_header(self, school_info: Dict[str, Any]):
        """Build CSEE-specific header"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        # School name with CSEE label
        school_name = school_info.get('name', 'SECONDARY SCHOOL')
        self.cell(0, 10, f"{school_name} - ORDINARY LEVEL", 0, 1, 'C')
        
        # Add system info
        self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, "CERTIFICATE OF SECONDARY EDUCATION EXAMINATION", 0, 1, 'C')
        
        self.ln(5)
        self.add_separator()
    
    def _build_summary(self, summary: Dict[str, Any]):
        """Build CSEE-specific summary"""
        self.add_subtitle("ACADEMIC SUMMARY - ORDINARY LEVEL", 12)
        
        # CSEE specific summary items
        summary_items = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Division", summary.get('division', 'N/A')),
            ("Points", str(summary.get('points', 'N/A'))),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'N/A')),
            ("Subjects Passed", f"{summary.get('subjects_passed', 0)}/{summary.get('subjects_total', 0)}")
        ]
        
        self._draw_summary_table(summary_items)
    
    def _build_subjects_table_from_dict(self, subjects_dict: Dict[str, Any]):
        """Build CSEE subjects table"""
        self.add_subtitle("SUBJECT PERFORMANCE - ORDINARY LEVEL", 12)
        
        # CSEE table headers
        headers = ["No.", "Subject", "Marks", "Grade", "Points", "Rank"]
        col_widths = [10, 70, 30, 25, 30, 25]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Process subjects
        subjects_list = []
        for subject_name, subject_data in subjects_dict.items():
            if isinstance(subject_data, dict):
                subject_item = subject_data.copy()
                subject_item['name'] = subject_name.title()
                subjects_list.append(subject_item)
        
        # Sort by subject name
        subjects_list.sort(key=lambda x: x.get('name', ''))
        
        # Draw table
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', 0)
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            rank = subject.get('subject_rank', '')
            attended = subject.get('attended', False)
            
            # Draw row
            self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 7, name[:25], 1, 0, 'L', 1)
            
            # Marks (show ABS if absent)
            if not attended:
                marks_text = "ABS"
                grade = "ABS"
                points_text = "ABS"
            else:
                marks_text = f"{marks:.1f}" if marks is not None else "N/A"
                points_text = str(points) if points is not None else "N/A"
            
            self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
            self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
            self.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
            
            # Rank (show N/A if absent)
            rank_text = str(rank) if rank and attended else "N/A"
            self.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
        
        self.ln(10)

# ========== PLSE REPORT GENERATOR (Primary Level) ==========

class PLSEReportGenerator(BaseReportGenerator):
    """Generate PLSE (Primary Level) reports"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.templates = PLSEReportTemplates()
    
    def _build_header(self, school_info: Dict[str, Any]):
        """Build PLSE-specific header"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        # School name with PLSE label
        school_name = school_info.get('name', 'PRIMARY SCHOOL')
        self.cell(0, 10, f"{school_name} - PRIMARY LEVEL", 0, 1, 'C')
        
        # Add system info
        self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, "PRIMARY SCHOOL LEAVING EXAMINATION", 0, 1, 'C')
        
        self.ln(5)
        self.add_separator()
    
    def _build_summary(self, summary: Dict[str, Any]):
        """Build PLSE-specific summary (no divisions/points)"""
        self.add_subtitle("ACADEMIC SUMMARY - PRIMARY LEVEL", 12)
        
        # PLSE specific summary items (no divisions/points)
        summary_items = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'N/A')),
            ("Subjects Passed", f"{summary.get('subjects_passed', 0)}/{summary.get('subjects_total', 0)}")
        ]
        
        self._draw_summary_table(summary_items)
        
        # PLSE specific note
        self.ln(5)
        self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.multi_cell(0, 4, "Note: PLSE uses letter grades (A-E) without divisions or points system.")
    
    def _build_subjects_table_from_dict(self, subjects_dict: Dict[str, Any]):
        """Build PLSE subjects table (simple, no points)"""
        self.add_subtitle("SUBJECT PERFORMANCE - PRIMARY LEVEL", 12)
        
        # PLSE table headers (no points)
        headers = ["No.", "Subject", "Marks", "Grade", "Status", "Rank"]
        col_widths = [10, 70, 30, 25, 30, 25]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Process subjects
        subjects_list = []
        for subject_name, subject_data in subjects_dict.items():
            if isinstance(subject_data, dict):
                subject_item = subject_data.copy()
                subject_item['name'] = subject_name.replace('_', ' ').title()
                subjects_list.append(subject_item)
        
        # Sort by subject name
        subjects_list.sort(key=lambda x: x.get('name', ''))
        
        # Draw table
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', 0)
            grade = subject.get('grade', 'N/A')
            passed = subject.get('pass', False)
            rank = subject.get('subject_rank', '')
            
            # Status
            status = "PASS" if passed else "FAIL"
            
            # Draw row
            self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 7, name[:25], 1, 0, 'L', 1)
            self.cell(col_widths[2], 7, f"{marks:.1f}", 1, 0, 'C', 1)
            self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
            
            # Status color coding
            if status == "FAIL":
                self.set_text_color(*PDFConstants.DANGER_COLOR)
            
            self.cell(col_widths[4], 7, status, 1, 0, 'C', 1)
            
            # Reset color
            self.set_text_color(0, 0, 0)
            
            # Rank
            self.cell(col_widths[5], 7, str(rank) if rank else '', 1, 1, 'C', 1)
        
        self.ln(10)

# ========== GENERIC REPORT GENERATOR ==========

class GenericReportGenerator(BaseReportGenerator):
    """Generic report generator for unknown systems"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.templates = GenericReportTemplates()
    
    def _build_document(self, student_data: Dict[str, Any], 
                        class_info: Dict[str, Any], 
                        school_info: Dict[str, Any]):
        """Build generic document that adapts to data"""
        super()._build_document(student_data, class_info, school_info)
        
        # Add system-specific note if available
        system_name = class_info.get('system', '')
        if system_name:
            self.ln(5)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.cell(0, 5, f"System: {system_name}", 0, 1, 'R')

# ========== HELPER METHOD ==========

def _draw_summary_table(self, summary_items: list):
    """Draw summary table (common method for all generators)"""
    col_widths = [70, 70]
    
    for i, (label, value) in enumerate(summary_items):
        # Alternate row colors
        if i % 2 == 0:
            self.set_fill_color(*PDFConstants.LIGHT_COLOR)
        else:
            self.set_fill_color(255, 255, 255)
        
        # Set font
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        
        # Highlight important items
        if label in ["Grade", "Division", "Status"]:
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        # Draw cells
        self.cell(col_widths[0], 8, label, 'LR', 0, 'L', 1)
        self.cell(col_widths[1], 8, value, 'LR', 1, 'C', 1)
    
    # Close table borders
    self.cell(sum(col_widths), 0, '', 'T', 1)
    self.ln(10)

# Add method to BaseReportGenerator
BaseReportGenerator._draw_summary_table = _draw_summary_table