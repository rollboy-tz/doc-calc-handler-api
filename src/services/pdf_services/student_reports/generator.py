"""
Student Report Generator - FIXED SPACING & SUMMARY LAYOUT
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


class StudentReportGenerator(BasePDFTemplate):
    """Base student report generator - PROPER SPACING"""
    
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
            
            # Build PDF
            self._build_proper_document(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_proper_document(self, student_data: Dict[str, Any], 
                               class_info: Dict[str, Any], 
                               school_info: Dict[str, Any]):
        """Build document with PROPER spacing"""
        # Detect system
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # ===== HEADER =====
        self._build_proper_header(school_info, class_info)
        
        # ===== STUDENT INFO (GOOD AS IS) =====
        self._build_proper_student_info(student_data.get('student', {}))
        
        # ===== ACADEMIC SUMMARY (FIXED LAYOUT) =====
        summary = student_data.get('summary', {})
        self._build_proper_summary_table(summary)
        
        # ===== SUBJECTS TABLE =====
        if 'subjects' in student_data:
            self._build_proper_subjects_table(student_data['subjects'])
        
        # ===== FOOTER =====
        self._build_proper_footer(class_info)
    
    def _build_proper_header(self, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Build header with proper spacing"""
        # School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 14)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        self.cell(0, 8, school_name, 0, 1, 'C')
        
        # System and exam
        system_label = self._get_system_label()
        
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 6, system_label, 0, 1, 'C')
        
        # Exam name
        exam_name = class_info.get('exam_name', 'EXAMINATION')
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 11)
        self.cell(0, 6, exam_name, 0, 1, 'C')
        
        # Class and term
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.cell(0, 5, f"Class: {class_name} | Term: {term} | Year: {year}", 0, 1, 'C')
        
        self.ln(8)
        self.add_separator()
        self.ln(5)
    
    def _get_system_label(self):
        """Get system label"""
        if self.system_rule == 'acsee':
            return "ADVANCED CERTIFICATE OF SECONDARY EDUCATION (ACSEE)"
        elif self.system_rule == 'csee':
            return "CERTIFICATE OF SECONDARY EDUCATION (CSEE)"
        elif self.system_rule == 'plse':
            return "PRIMARY SCHOOL LEAVING EXAMINATION (PLSE)"
        else:
            return "ACADEMIC PERFORMANCE REPORT"
    
    def _build_proper_student_info(self, student: Dict[str, Any]):
        """Build student info - GOOD SPACING"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 6, "STUDENT INFORMATION", 0, 1, 'L')
        self.ln(2)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.set_text_color(0, 0, 0)
        
        # Name and Admission
        if 'name' in student:
            self.cell(40, 5, "Name:", 0, 0, 'L')
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.cell(0, 5, student['name'], 0, 1, 'L')
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        
        if 'admission' in student:
            self.cell(40, 5, "Admission No:", 0, 0, 'L')
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.cell(0, 5, student['admission'], 0, 1, 'L')
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        
        # Gender, Class, Year in one line
        info_line = []
        if 'gender' in student:
            gender_display = "Male" if student['gender'] == 'M' else "Female" if student['gender'] == 'F' else student['gender']
            info_line.append(f"Gender: {gender_display}")
        
        if 'class' in student:
            info_line.append(f"Class: {student['class']}")
        
        if 'year' in student:
            info_line.append(f"Year: {student['year']}")
        
        if info_line:
            self.cell(40, 5, "Details:", 0, 0, 'L')
            self.cell(0, 5, " | ".join(info_line), 0, 1, 'L')
        
        self.ln(8)
        self.add_separator()
        self.ln(5)
    
    def _build_proper_summary_table(self, summary: Dict[str, Any]):
        """Build academic summary as PROPER TABLE"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 6, "ACADEMIC SUMMARY", 0, 1, 'L')
        self.ln(3)
        
        # Table headers
        headers = ["ITEM", "DETAILS", "STATUS"]
        col_widths = [50, 80, 60]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
        self.ln()
        
        # Reset styles for data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        # Summary data rows
        summary_rows = []
        
        # Core performance
        if 'total' in summary:
            summary_rows.append(("Total Marks", f"{summary['total']:.0f}", ""))
        if 'average' in summary:
            summary_rows.append(("Average Score", f"{summary['average']:.1f}%", ""))
        if 'grade' in summary:
            summary_rows.append(("Grade", summary['grade'], ""))
        
        # System-specific
        if self.system_rule == 'acsee':
            if 'division' in summary:
                summary_rows.append(("Division", summary['division'], ""))
            if 'points' in summary:
                summary_rows.append(("Points", str(summary['points']), ""))
            if 'principals' in summary:
                summary_rows.append(("Principals", str(summary['principals']), ""))
        
        elif self.system_rule == 'csee':
            if 'division' in summary:
                summary_rows.append(("Division", summary['division'], ""))
            if 'points' in summary:
                summary_rows.append(("Points", str(summary['points']), ""))
        
        # Common fields
        if 'rank' in summary:
            summary_rows.append(("Class Position", str(summary['rank']), ""))
        if 'status' in summary:
            summary_rows.append(("Overall Status", "", summary['status']))
        
        # Subjects passed
        if 'subjects_passed' in summary and 'subjects_total' in summary:
            passed = summary['subjects_passed']
            total = summary['subjects_total']
            percentage = (passed / total * 100) if total > 0 else 0
            summary_rows.append(("Subjects Passed", f"{passed}/{total} ({percentage:.1f}%)", ""))
        
        # Draw rows
        for i, (label, value, status) in enumerate(summary_rows):
            # Alternate row colors
            if i % 2 == 0:
                self.set_fill_color(*PDFConstants.LIGHT_COLOR)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Draw cells
            self.cell(col_widths[0], 6, label, 1, 0, 'L', 1)
            self.cell(col_widths[1], 6, value, 1, 0, 'C', 1)
            
            # Status with color coding
            if status:
                if status == "PASS":
                    self.set_text_color(*PDFConstants.SUCCESS_COLOR)
                elif status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                else:
                    self.set_text_color(*PDFConstants.WARNING_COLOR)
            
            self.cell(col_widths[2], 6, status, 1, 1, 'C', 1)
            
            # Reset text color
            self.set_text_color(0, 0, 0)
        
        # Remarks if available
        if 'remark' in summary and summary['remark']:
            self.ln(3)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            self.cell(0, 5, f"Remarks: {summary['remark']}", 0, 1, 'L')
        
        self.ln(8)
        self.add_separator()
        self.ln(5)
    
    def _build_proper_subjects_table(self, subjects):
        """Build subjects table with proper spacing"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 6, "SUBJECT PERFORMANCE", 0, 1, 'L')
        self.ln(3)
        
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
        
        # Determine table headers based on system
        if self.system_rule == 'acsee':
            headers = ["SUBJECT", "MARKS", "GRADE", "POINTS", "STATUS"]
            col_widths = [70, 30, 30, 30, 40]
        elif self.system_rule == 'csee':
            headers = ["SUBJECT", "MARKS", "GRADE", "POINTS", "RANK"]
            col_widths = [70, 30, 30, 30, 30]
        elif self.system_rule == 'plse':
            headers = ["SUBJECT", "MARKS", "GRADE", "STATUS", "RANK"]
            col_widths = [70, 30, 30, 40, 30]
        else:
            headers = ["SUBJECT", "MARKS", "GRADE", "STATUS"]
            col_widths = [80, 35, 35, 50]
        
        # Draw header
        self.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
        self.ln()
        
        # Draw table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
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
            name_display = name[:25] + '...' if len(name) > 25 else name
            
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
                
                self.cell(col_widths[0], 6, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 6, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 6, grade_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 6, points_text, 1, 0, 'C', 1)
                
                # Color code status
                if status == "ABSENT":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                elif status == "FAIL":
                    self.set_text_color(*PDFConstants.WARNING_COLOR)
                
                self.cell(col_widths[4], 6, status, 1, 1, 'C', 1)
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
                
                self.cell(col_widths[0], 6, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 6, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 6, grade_text, 1, 0, 'C', 1)
                self.cell(col_widths[3], 6, points_text, 1, 0, 'C', 1)
                self.cell(col_widths[4], 6, rank_text, 1, 1, 'C', 1)
            
            elif self.system_rule == 'plse':
                # PLSE row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                rank_text = str(rank) if rank else ''
                
                self.cell(col_widths[0], 6, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 6, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 6, grade, 1, 0, 'C', 1)
                
                # Color code status
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[3], 6, status, 1, 0, 'C', 1)
                self.set_text_color(0, 0, 0)
                self.cell(col_widths[4], 6, rank_text, 1, 1, 'C', 1)
            
            else:
                # Generic row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                
                self.cell(col_widths[0], 6, name_display, 1, 0, 'L', 1)
                self.cell(col_widths[1], 6, marks_text, 1, 0, 'C', 1)
                self.cell(col_widths[2], 6, grade, 1, 0, 'C', 1)
                
                if status == "FAIL":
                    self.set_text_color(*PDFConstants.DANGER_COLOR)
                
                self.cell(col_widths[3], 6, status, 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
        
        self.ln(8)
    
    def _build_proper_footer(self, class_info: Dict[str, Any]):
        """Build footer with proper spacing"""
        self.add_separator()
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        
        # Generation info
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 5, f"Generated on: {date_printed}", 0, 1, 'L')
        
        # School/Class info
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', '')
        
        if class_name or term:
            info_parts = []
            if class_name:
                info_parts.append(f"Class: {class_name}")
            if term:
                info_parts.append(f"Term: {term}")
            
            self.cell(0, 5, " | ".join(info_parts), 0, 1, 'L')
        
        # Confidential notice
        if self.config.get('confidential', True):
            self.set_font(PDFConstants.DEFAULT_FONT, "I", 8)
            self.cell(0, 5, "Confidential - For official use only", 0, 1, 'C')
    
    def _create_error_pdf(self, error_message: str) -> str:
        """Create error PDF file"""
        from fpdf import FPDF
        
        filename = generate_filename("error", "student_report")
        filepath = get_temp_path(filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*PDFConstants.DANGER_COLOR)
        pdf.cell(0, 8, "Error Generating Report", 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Error: {error_message[:150]}")
        
        pdf.output(filepath)
        return filepath


# ========== ALIAS CLASSES (SAME) ==========

class ACSEEReportGenerator(StudentReportGenerator):
    """ACSEE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'acsee'
        config['system_name'] = config.get('system_name', 'ADVANCED LEVEL (ACSEE)')
        super().__init__(config)

class CSEEReportGenerator(StudentReportGenerator):
    """CSEE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'csee'
        config['system_name'] = config.get('system_name', 'ORDINARY LEVEL (CSEE)')
        super().__init__(config)

class PLSEReportGenerator(StudentReportGenerator):
    """PLSE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'plse'
        config['system_name'] = config.get('system_name', 'PRIMARY LEVEL (PLSE)')
        super().__init__(config)

class GenericReportGenerator(StudentReportGenerator):
    """Generic Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = config.get('system_rule', 'generic')
        config['system_name'] = config.get('system_name', 'ACADEMIC REPORT')
        super().__init__(config)