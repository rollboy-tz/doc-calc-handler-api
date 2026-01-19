"""
Student Report Generator - COMPACT VERSION
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


class StudentReportGenerator(BasePDFTemplate):
    """Base student report generator - COMPACT DESIGN"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_rule = self.config.get('system_rule', '').lower()
        self.system_name = self.config.get('system_name', '')
        
    def generate(self, 
                 student_data: Dict[str, Any],
                 class_info: Dict[str, Any] = None,
                 school_info: Dict[str, Any] = None) -> str:
        """Generate student report PDF - COMPACT"""
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
            self._build_compact_document(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_compact_document(self, student_data: Dict[str, Any], 
                                class_info: Dict[str, Any], 
                                school_info: Dict[str, Any]):
        """Build COMPACT document"""
        # Detect system from class_info if not in config
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # ===== HEADER SECTION =====
        self._build_compact_header(school_info, class_info)
        
        # ===== STUDENT INFO (HORIZONTAL) =====
        self._build_horizontal_student_info(student_data.get('student', {}))
        
        # ===== ACADEMIC SUMMARY (COMPACT TABLE) =====
        summary = student_data.get('summary', {})
        self._build_compact_summary(summary)
        
        # ===== SUBJECTS TABLE =====
        if 'subjects' in student_data:
            self._build_compact_subjects_table(student_data['subjects'])
        
        # ===== FOOTER =====
        self._build_compact_footer(class_info)
    
    def _build_compact_header(self, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Build COMPACT header"""
        # School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        self.cell(0, 5, school_name, 0, 1, 'C')
        
        # System and exam
        system_label = self._get_system_label()
        exam_name = class_info.get('exam_name', 'EXAMINATION')
        
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 9)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 4, f"{system_label} - {exam_name}", 0, 1, 'C')
        
        # Class and term
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 8)
        self.cell(0, 4, f"Class: {class_name} | Term: {term} | Year: {year}", 0, 1, 'C')
        
        self.ln(2)
        self.add_separator()
        self.ln(2)
    
    def _get_system_label(self):
        """Get system label based on rule"""
        if self.system_rule == 'acsee':
            return "ADVANCED LEVEL (ACSEE)"
        elif self.system_rule == 'csee':
            return "ORDINARY LEVEL (CSEE)"
        elif self.system_rule == 'plse':
            return "PRIMARY LEVEL (PLSE)"
        else:
            return "ACADEMIC REPORT"
    
    def _build_horizontal_student_info(self, student: Dict[str, Any]):
        """Build student info in HORIZONTAL layout"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(40, 5, "STUDENT INFORMATION:", 0, 0, 'L')
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 8)
        self.set_text_color(0, 0, 0)
        
        info_parts = []
        
        if 'name' in student:
            info_parts.append(f"Name: {student['name']}")
        if 'admission' in student:
            info_parts.append(f"Adm: {student['admission']}")
        if 'gender' in student:
            gender = 'M' if student['gender'] == 'M' else 'F' if student['gender'] == 'F' else student['gender']
            info_parts.append(f"Gender: {gender}")
        if 'class' in student:
            info_parts.append(f"Class: {student['class']}")
        
        # Join with separator
        info_text = " | ".join(info_parts)
        self.cell(0, 5, info_text, 0, 1, 'L')
        
        self.ln(2)
    
    def _build_compact_summary(self, summary: Dict[str, Any]):
        """Build COMPACT academic summary (HORIZONTAL layout)"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(40, 5, "ACADEMIC SUMMARY:", 0, 0, 'L')
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 8)
        self.set_text_color(0, 0, 0)
        
        summary_parts = []
        
        # Always show these
        if 'total' in summary:
            summary_parts.append(f"Total: {summary['total']:.0f}")
        if 'average' in summary:
            summary_parts.append(f"Avg: {summary['average']:.1f}%")
        if 'grade' in summary:
            summary_parts.append(f"Grade: {summary['grade']}")
        
        # System-specific additions
        if self.system_rule == 'acsee':
            if 'division' in summary:
                summary_parts.append(f"Div: {summary['division']}")
            if 'points' in summary:
                summary_parts.append(f"Points: {summary['points']}")
            if 'principals' in summary:
                summary_parts.append(f"Principals: {summary['principals']}")
        
        elif self.system_rule == 'csee':
            if 'division' in summary:
                summary_parts.append(f"Div: {summary['division']}")
            if 'points' in summary:
                summary_parts.append(f"Points: {summary['points']}")
        
        # Common fields
        if 'rank' in summary:
            summary_parts.append(f"Rank: {summary['rank']}")
        if 'status' in summary:
            summary_parts.append(f"Status: {summary['status']}")
        
        # Join with separator
        summary_text = " | ".join(summary_parts)
        
        # Calculate if we need to wrap
        text_width = self.get_string_width(summary_text)
        if text_width > 150:  # If too long, split into two lines
            # Find middle point
            parts = summary_text.split(" | ")
            mid = len(parts) // 2
            line1 = " | ".join(parts[:mid])
            line2 = " | ".join(parts[mid:])
            
            self.cell(0, 4, line1, 0, 1, 'L')
            self.set_x(50)  # Indent second line
            self.cell(0, 4, line2, 0, 1, 'L')
        else:
            self.cell(0, 5, summary_text, 0, 1, 'L')
        
        # Remark if available
        if 'remark' in summary:
            self.set_font(PDFConstants.ITALIC_FONT, "I", 8)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.cell(0, 4, f"Remarks: {summary['remark']}", 0, 1, 'L')
            self.reset_styles()
        
        self.ln(3)
        self.add_separator()
        self.ln(2)
    
    def _build_compact_subjects_table(self, subjects):
        """Build COMPACT subjects table"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 5, "SUBJECT PERFORMANCE:", 0, 1, 'L')
        self.ln(1)
        
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
        
        # Determine table layout based on system
        if self.system_rule == 'acsee':
            headers = ["Subject", "Marks", "Grade", "Points", "Status"]
            col_widths = [70, 25, 25, 25, 45]
        elif self.system_rule == 'csee':
            headers = ["Subject", "Marks", "Grade", "Points", "Rank"]
            col_widths = [70, 25, 25, 25, 35]
        elif self.system_rule == 'plse':
            headers = ["Subject", "Marks", "Grade", "Status", "Rank"]
            col_widths = [70, 25, 25, 35, 30]
        else:
            headers = ["Subject", "Marks", "Grade", "Status"]
            col_widths = [80, 30, 30, 50]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 8)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 6, header, 1, 0, 'C', 1)
        self.ln()
        
        # Draw table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 8)
        
        for idx, subject in enumerate(subjects_list):
            # Alternate row colors
            if idx % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            rank = subject.get('subject_rank', '')
            attended = subject.get('attended', True)
            passed = subject.get('pass', subject.get('pass', True))
            
            # Truncate long subject names
            name_display = name[:20] + '...' if len(name) > 20 else name
            
            # Draw row based on system
            if self.system_rule == 'acsee':
                # ACSEE row
                if not attended:
                    marks_text = "ABS"
                    grade_text = "ABS"
                    points_text = "ABS"
                    status = "ABSENT"
                elif not passed:
                    marks_text = f"{marks:.0f}" if marks else "0"
                    grade_text = grade
                    points_text = str(points) if points else "0"
                    status = "FAIL"
                else:
                    marks_text = f"{marks:.0f}" if marks else "0"
                    grade_text = grade
                    points_text = str(points) if points else "0"
                    status = "PASS"
                
                self.cell(col_widths[0], 5, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 5, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 5, grade_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 5, points_text, 1, 0, 'C', 1)
                
                # Color code status
                if status == "ABSENT":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                elif status == "FAIL":
                    self.set_text_color(*PDFConstants.WARNING_COLOR)
                
                self.cell(col_widths[4], 5, status, 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
            
            elif self.system_rule == 'csee':
                # CSEE row
                if not attended:
                    marks_text = "ABS"
                    grade_text = "ABS"
                    points_text = "ABS"
                    rank_text = "N/A"
                else:
                    marks_text = f"{marks:.0f}" if marks else "0"
                    grade_text = grade
                    points_text = str(points) if points else "0"
                    rank_text = str(rank) if rank else ''
                
                self.cell(col_widths[0], 5, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 5, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 5, grade_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 5, points_text, 1, 0, 'C', 1)
                self.cell(col_widths[4], 5, rank_text, 1, 1, 'C', 1)
            
            elif self.system_rule == 'plse':
                # PLSE row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                rank_text = str(rank) if rank else ''
                
                self.cell(col_widths[0], 5, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 5, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 5, grade, 1, 0, 'C', 1)
                
                # Color code status
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[3], 5, status, 1, 0, 'C', 1)
                self.set_text_color(0, 0, 0)
                self.cell(col_widths[4], 5, rank_text, 1, 1, 'C', 1)
            
            else:
                # Generic row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                
                self.cell(col_widths[0], 5, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 5, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 5, grade, 1, 0, 'C', 1)
                
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[3], 5, status, 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
        
        self.ln(3)
    
    def _build_compact_footer(self, class_info: Dict[str, Any]):
        """Build COMPACT footer"""
        self.add_separator()
        
        self.set_font(PDFConstants.DEFAULT_FONT, "I", 7)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        
        # System info
        system_label = self._get_system_label()
        self.cell(0, 3, f"System: {system_label}", 0, 1, 'L')
        
        # Generation info
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 3, f"Generated: {date_printed}", 0, 1, 'L')
        
        # Confidential notice
        if self.config.get('confidential', True):
            self.set_font(PDFConstants.DEFAULT_FONT, "I", 6)
            self.cell(0, 3, "Confidential - For official use only", 0, 1, 'C')
    
    def _create_error_pdf(self, error_message: str) -> str:
        """Create error PDF file"""
        from fpdf import FPDF
        
        filename = generate_filename("error", "student_report")
        filepath = get_temp_path(filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(*PDFConstants.DANGER_COLOR)
        pdf.cell(0, 8, "Error Generating Report", 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, f"Error: {error_message[:150]}")
        
        pdf.output(filepath)
        return filepath


# ========== ALIAS CLASSES (SAME AS BEFORE) ==========

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