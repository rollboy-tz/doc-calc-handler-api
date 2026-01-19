"""
Student Report Generator - All systems in one file
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


# ========== BASE GENERATOR ==========

class StudentReportGenerator(BasePDFTemplate):
    """Base student report generator - detects system automatically"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_rule = self.config.get('system_rule', '').lower()
        self.system_name = self.config.get('system_name', '')
        
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
                f"report_{self.system_rule or 'generic'}",
                f"{admission}_{student_name}"
            )
            filepath = get_temp_path(filename)
            
            # Build PDF based on system
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
        # Detect system from class_info if not in config
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # Build based on system
        if self.system_rule in ['acsee', 'advanced', 'a-level']:
            self._build_acsee_document(student_data, class_info, school_info)
        elif self.system_rule in ['csee', 'certificate', 'o-level']:
            self._build_csee_document(student_data, class_info, school_info)
        elif self.system_rule in ['plse', 'primary', 'standard']:
            self._build_plse_document(student_data, class_info, school_info)
        else:
            self._build_generic_document(student_data, class_info, school_info)
    
    # ========== ACSEE (A-Level) ==========
    
    def _build_acsee_document(self, student_data, class_info, school_info):
        """Build ACSEE (Advanced Level) report"""
        # Header
        self._build_system_header(school_info, "ADVANCED LEVEL (ACSEE)")
        
        # Title
        self._build_exam_title(class_info, "ACSEE")
        
        # Student Info
        self._build_student_info(student_data.get('student', {}))
        
        # Summary with ACSEE specific fields
        summary = student_data.get('summary', {})
        self.add_subtitle("ACADEMIC SUMMARY - ADVANCED LEVEL", 12)
        
        acsee_summary = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average Score", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Division", summary.get('division', 'N/A')),
            ("Points", str(summary.get('points', 'N/A'))),
            ("Principals", str(summary.get('principals', 'N/A'))),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'PASS'))
        ]
        
        self._draw_summary_table(acsee_summary)
        
        # Subjects
        if 'subjects' in student_data:
            self._build_acsee_subjects_table(student_data['subjects'])
        
        # Footer
        self._build_footer(class_info, "ACSEE - Advanced Certificate of Secondary Education")
    
    # ========== CSEE (O-Level) ==========
    
    def _build_csee_document(self, student_data, class_info, school_info):
        """Build CSEE (Ordinary Level) report"""
        # Header
        self._build_system_header(school_info, "ORDINARY LEVEL (CSEE)")
        
        # Title
        self._build_exam_title(class_info, "CSEE")
        
        # Student Info
        self._build_student_info(student_data.get('student', {}))
        
        # Summary with CSEE specific fields
        summary = student_data.get('summary', {})
        self.add_subtitle("ACADEMIC SUMMARY - ORDINARY LEVEL", 12)
        
        csee_summary = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average Score", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Division", summary.get('division', 'N/A')),
            ("Points", str(summary.get('points', 'N/A'))),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'PASS')),
            ("Subjects Passed", f"{summary.get('subjects_passed', 0)}/{summary.get('subjects_total', 0)}")
        ]
        
        self._draw_summary_table(csee_summary)
        
        # Subjects
        if 'subjects' in student_data:
            self._build_csee_subjects_table(student_data['subjects'])
        
        # Footer
        self._build_footer(class_info, "CSEE - Certificate of Secondary Education")
    
    # ========== PLSE (Primary) ==========
    
    def _build_plse_document(self, student_data, class_info, school_info):
        """Build PLSE (Primary Level) report"""
        # Header
        self._build_system_header(school_info, "PRIMARY LEVEL (PLSE)")
        
        # Title
        self._build_exam_title(class_info, "PLSE")
        
        # Student Info
        self._build_student_info(student_data.get('student', {}))
        
        # Summary without divisions/points
        summary = student_data.get('summary', {})
        self.add_subtitle("ACADEMIC SUMMARY - PRIMARY LEVEL", 12)
        
        plse_summary = [
            ("Total Marks", f"{summary.get('total', 0):.0f}"),
            ("Average Score", f"{summary.get('average', 0):.1f}%"),
            ("Grade", summary.get('grade', 'N/A')),
            ("Rank", str(summary.get('rank', 'N/A'))),
            ("Status", summary.get('status', 'PASS')),
            ("Subjects Passed", f"{summary.get('subjects_passed', 0)}/{summary.get('subjects_total', 0)}")
        ]
        
        self._draw_summary_table(plse_summary)
        
        # Note about PLSE system
        self.ln(5)
        self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.multi_cell(0, 4, "Note: PLSE uses letter grades (A-E) without divisions or points system.")
        self.reset_styles()
        
        # Subjects
        if 'subjects' in student_data:
            self._build_plse_subjects_table(student_data['subjects'])
        
        # Footer
        self._build_footer(class_info, "PLSE - Primary School Leaving Examination")
    
    # ========== GENERIC ==========
    
    def _build_generic_document(self, student_data, class_info, school_info):
        """Build generic report for unknown systems"""
        # Header
        self._build_system_header(school_info, "ACADEMIC REPORT")
        
        # Title
        self._build_exam_title(class_info, "EXAMINATION")
        
        # Student Info
        self._build_student_info(student_data.get('student', {}))
        
        # Generic Summary
        summary = student_data.get('summary', {})
        self.add_subtitle("ACADEMIC SUMMARY", 12)
        
        generic_summary = []
        
        # Dynamically add available fields
        if 'total' in summary:
            generic_summary.append(("Total Marks", f"{summary['total']:.0f}"))
        if 'average' in summary:
            generic_summary.append(("Average", f"{summary['average']:.1f}%"))
        if 'grade' in summary:
            generic_summary.append(("Grade", summary['grade']))
        if 'division' in summary:
            generic_summary.append(("Division", summary['division']))
        if 'points' in summary:
            generic_summary.append(("Points", str(summary['points'])))
        if 'rank' in summary:
            generic_summary.append(("Rank", str(summary['rank'])))
        if 'status' in summary:
            generic_summary.append(("Status", summary['status']))
        
        if generic_summary:
            self._draw_summary_table(generic_summary)
        
        # Subjects
        if 'subjects' in student_data:
            self._build_generic_subjects_table(student_data['subjects'])
        
        # System note if available
        if 'system' in class_info:
            self.ln(5)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.cell(0, 5, f"System: {class_info['system']}", 0, 1, 'R')
        
        # Footer
        self._build_footer(class_info, "Academic Performance Report")
    
    # ========== COMMON BUILDING METHODS ==========
    
    def _build_system_header(self, school_info: Dict[str, Any], system_label: str):
        """Build system-specific header"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        self.cell(0, 10, school_name, 0, 1, 'C')
        
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, system_label, 0, 1, 'C')
        
        if 'motto' in school_info:
            self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
            self.cell(0, 8, school_info['motto'], 0, 1, 'C')
        
        self.ln(5)
        self.add_separator()
    
    def _build_exam_title(self, class_info: Dict[str, Any], default_exam: str):
        """Build exam title"""
        exam_name = class_info.get('exam_name', default_exam)
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        title_parts = []
        if exam_name:
            title_parts.append(exam_name)
        if class_name:
            title_parts.append(class_name)
        
        title = " - ".join(title_parts) if title_parts else "STUDENT REPORT"
        
        self.add_title(title, 14)
        
        # Subtitle
        subtitle = f"TERM {term} - {year}"
        self.set_font(PDFConstants.DEFAULT_FONT, "I", 11)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 8, subtitle, 0, 1, 'C')
        self.ln(5)
    
    def _build_student_info(self, student: Dict[str, Any]):
        """Build student information section"""
        self.add_subtitle("STUDENT INFORMATION", 12)
        
        info_lines = []
        
        if 'name' in student:
            info_lines.append(f"Name: {student['name']}")
        if 'admission' in student:
            info_lines.append(f"Admission No: {student['admission']}")
        if 'gender' in student:
            gender = student['gender']
            if gender == 'M':
                info_lines.append("Gender: Male")
            elif gender == 'F':
                info_lines.append("Gender: Female")
            else:
                info_lines.append(f"Gender: {gender}")
        if 'class' in student:
            info_lines.append(f"Class: {student['class']}")
        if 'stream' in student:
            info_lines.append(f"Stream: {student['stream']}")
        if 'year' in student:
            info_lines.append(f"Year: {student['year']}")
        
        if info_lines:
            self.add_paragraph("\n".join(info_lines))
            self.ln(5)
    
    def _draw_summary_table(self, summary_items: list):
        """Draw summary table"""
        if not summary_items:
            return
        
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
    
    def _build_acsee_subjects_table(self, subjects):
        """Build ACSEE subjects table"""
        self._build_subjects_table_common(subjects, system='acsee')
    
    def _build_csee_subjects_table(self, subjects):
        """Build CSEE subjects table"""
        self._build_subjects_table_common(subjects, system='csee')
    
    def _build_plse_subjects_table(self, subjects):
        """Build PLSE subjects table"""
        self._build_subjects_table_common(subjects, system='plse')
    
    def _build_generic_subjects_table(self, subjects):
        """Build generic subjects table"""
        self._build_subjects_table_common(subjects, system='generic')
    
    def _build_subjects_table_common(self, subjects, system='generic'):
        """Common method to build subjects table"""
        if not subjects:
            return
        
        self.add_subtitle("SUBJECT PERFORMANCE", 12)
        
        # Determine headers based on system
        if system == 'acsee':
            headers = ["No.", "Subject", "Marks", "Grade", "Points", "Status"]
            col_widths = [10, 70, 30, 25, 30, 35]
        elif system == 'csee':
            headers = ["No.", "Subject", "Marks", "Grade", "Points", "Rank"]
            col_widths = [10, 70, 30, 25, 30, 25]
        elif system == 'plse':
            headers = ["No.", "Subject", "Marks", "Grade", "Status", "Rank"]
            col_widths = [10, 70, 30, 25, 30, 25]
        else:
            headers = ["No.", "Subject", "Marks", "Grade", "Status"]
            col_widths = [10, 80, 40, 30, 40]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Prepare subjects list
        subjects_list = []
        if isinstance(subjects, dict):
            for subject_name, subject_data in subjects.items():
                if isinstance(subject_data, dict):
                    subject_item = subject_data.copy()
                    subject_item['name'] = subject_name.title().replace('_', ' ')
                    subjects_list.append(subject_item)
        elif isinstance(subjects, list):
            subjects_list = subjects
        
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
            
            # Get common data
            name = subject.get('name', 'N/A')[:25]
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            rank = subject.get('subject_rank', '')
            attended = subject.get('attended', True)
            passed = subject.get('pass', subject.get('pass', True))
            
            # System-specific handling
            if system == 'acsee':
                # ACSEE: Show status based on attendance/pass
                if not attended:
                    status = "ABSENT"
                    marks_text = "N/A"
                    points_text = "N/A"
                elif not passed:
                    status = "FAIL"
                    marks_text = f"{marks:.1f}" if marks else "N/A"
                    points_text = str(points) if points else "N/A"
                else:
                    status = "PASS"
                    marks_text = f"{marks:.1f}" if marks else "N/A"
                    points_text = str(points) if points else "N/A"
                
                # Draw ACSEE row
                self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
                self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                self.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
                
                # Color code status
                if status == "ABSENT":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                elif status == "FAIL":
                    self.set_text_color(*PDFConstants.WARNING_COLOR)
                
                self.cell(col_widths[5], 7, status, 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
            
            elif system == 'csee':
                # CSEE: Show ABS for absent, rank for present
                if not attended:
                    marks_text = "ABS"
                    grade = "ABS"
                    points_text = "ABS"
                    rank_text = "N/A"
                else:
                    marks_text = f"{marks:.1f}" if marks else "N/A"
                    points_text = str(points) if points else "N/A"
                    rank_text = str(rank) if rank else ''
                
                # Draw CSEE row
                self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
                self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                self.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
                self.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
            
            elif system == 'plse':
                # PLSE: Simple PASS/FAIL
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.1f}" if marks else "N/A"
                rank_text = str(rank) if rank else ''
                
                # Draw PLSE row
                self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
                self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                
                # Color code status
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[4], 7, status, 1, 0, 'C', 1)
                self.set_text_color(0, 0, 0)
                self.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
            
            else:
                # Generic: Simple display
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.1f}" if marks else "N/A"
                
                self.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                self.cell(col_widths[1], 7, name, 1, 0, 'L', 1)
                self.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[4], 7, status, 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
        
        self.ln(10)
    
    def _build_footer(self, class_info: Dict[str, Any], system_label: str):
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
        
        # System label
        footer_lines.append(f"System: {system_label}")
        
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
        
        pdf.output(filepath)
        return filepath


# ========== ALIAS CLASSES FOR FACTORY ==========

# These are just aliases for the factory to use
# All use the same StudentReportGenerator but with different configs

class ACSEEReportGenerator(StudentReportGenerator):
    """ACSEE Report Generator (alias)"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'acsee'
        config['system_name'] = config.get('system_name', 'ADVANCED LEVEL (ACSEE)')
        super().__init__(config)

class CSEEReportGenerator(StudentReportGenerator):
    """CSEE Report Generator (alias)"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'csee'
        config['system_name'] = config.get('system_name', 'ORDINARY LEVEL (CSEE)')
        super().__init__(config)

class PLSEReportGenerator(StudentReportGenerator):
    """PLSE Report Generator (alias)"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'plse'
        config['system_name'] = config.get('system_name', 'PRIMARY LEVEL (PLSE)')
        super().__init__(config)

class GenericReportGenerator(StudentReportGenerator):
    """Generic Report Generator (alias)"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = config.get('system_rule', 'generic')
        config['system_name'] = config.get('system_name', 'ACADEMIC REPORT')
        super().__init__(config)