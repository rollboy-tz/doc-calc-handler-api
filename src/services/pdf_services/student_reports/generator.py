"""
Student Report Generator - CLEAN VERSION
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


class StudentReportGenerator(BasePDFTemplate):
    """Student report generator - CLEAN & PROFESSIONAL"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_rule = self.config.get('system_rule', '').lower()
        self.system_name = self.config.get('system_name', '')
        
        # Use soft colors
        self._setup_soft_colors()
    
    def _setup_soft_colors(self):
        """Setup soft colors for professional look"""
        self.soft_primary = (59, 89, 152)     # Softer blue
        self.soft_secondary = (72, 87, 117)   # Softer dark blue
        self.soft_success = (46, 125, 50)     # Softer green
        self.soft_danger = (211, 47, 47)      # Softer red
        self.soft_light = (245, 245, 245)     # Softer light gray
        self.soft_border = (224, 224, 224)    # Softer border
    
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
            
            # Build document
            self._build_clean_document(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_clean_document(self, student_data: Dict[str, Any], 
                              class_info: Dict[str, Any], 
                              school_info: Dict[str, Any]):
        """Build clean document"""
        # Detect system
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # ===== HEADER =====
        self._build_clean_header(school_info, class_info)
        
        # ===== STUDENT INFO (VERTICAL) =====
        self._build_vertical_student_info(student_data.get('student', {}))
        
        # ===== ACADEMIC SUMMARY TABLE =====
        summary = student_data.get('summary', {})
        self._build_clean_summary_table(summary)
        
        # ===== SUBJECTS TABLE =====
        if 'subjects' in student_data:
            self._build_clean_subjects_table(student_data['subjects'])
        
        # ===== FOOTER =====
        self._build_clean_footer(class_info)
    
    def _build_clean_header(self, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Build clean header"""
        # School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 14)
        self.set_text_color(*self.soft_primary)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        self.cell(0, 8, school_name, 0, 1, 'C')
        
        # System label
        system_label = self._get_system_label()
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*self.soft_secondary)
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
        info_text = f"Class: {class_name} | Term: {term} | Year: {year}"
        self.cell(0, 5, info_text, 0, 1, 'C')
        
        self.ln(8)
        self._add_soft_separator()
        self.ln(5)
    
    def _get_system_label(self):
        """Get system label"""
        if self.system_rule == 'acsee':
            return "Advanced Certificate of Secondary Education"
        elif self.system_rule == 'csee':
            return "Certificate of Secondary Education" 
        elif self.system_rule == 'plse':
            return "Primary School Leaving Examination"
        else:
            return "Academic Performance Report"
    
    def _build_vertical_student_info(self, student: Dict[str, Any]):
        """Build student info VERTICALLY"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 7, "STUDENT INFORMATION", 0, 1, 'L')
        self.ln(3)
        
        # Vertical list
        line_height = 6
        
        # Name
        if 'name' in student:
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(40, line_height, "Name:", 0, 0, 'L')
            
            self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, line_height, student['name'], 0, 1, 'L')
        
        # Admission
        if 'admission' in student:
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(40, line_height, "Admission No:", 0, 0, 'L')
            
            self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, line_height, student['admission'], 0, 1, 'L')
        
        # Gender
        if 'gender' in student:
            gender_display = "Male" if student['gender'] == 'M' else "Female" if student['gender'] == 'F' else student['gender']
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(40, line_height, "Gender:", 0, 0, 'L')
            
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, line_height, gender_display, 0, 1, 'L')
        
        # Class
        if 'class' in student:
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(40, line_height, "Class:", 0, 0, 'L')
            
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, line_height, student['class'], 0, 1, 'L')
        
        # Year (if available)
        if 'year' in student:
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(40, line_height, "Year:", 0, 0, 'L')
            
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, line_height, student['year'], 0, 1, 'L')
        
        self.ln(8)
        self._add_soft_separator()
        self.ln(5)
    
    def _build_clean_summary_table(self, summary: Dict[str, Any]):
        """Build clean academic summary table"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 7, "ACADEMIC PERFORMANCE SUMMARY", 0, 1, 'L')
        self.ln(3)
        
        # ===== CLEAN TABLE WITH HEADERS =====
        # Define column widths
        col_widths = [50, 50, 50, 50]  # 4 columns only
        
        # Table headers (SOFT COLORS)
        headers = ["TOTAL MARKS", "AVERAGE SCORE", "GRADE", "POSITION"]
        
        # Draw header row with SOFT color
        self.set_fill_color(*self.soft_primary)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
        self.ln()
        
        # Prepare values
        total_marks = f"{summary.get('total', 0):.0f}" if 'total' in summary else "N/A"
        average_score = f"{summary.get('average', 0):.1f}%" if 'average' in summary else "N/A"
        grade = summary.get('grade', 'N/A')
        position = str(summary.get('rank', 'N/A')) if 'rank' in summary else "N/A"
        
        values = [total_marks, average_score, grade, position]
        
        # Draw data row with SOFT light color
        self.set_fill_color(*self.soft_light)
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
        
        for i, value in enumerate(values):
            # Soft color coding for GRADE
            if i == 2:  # GRADE column
                if value in ["A", "B", "C", "I", "II", "III"]:
                    self.set_text_color(*self.soft_success)
                elif value in ["D", "E", "F"]:
                    self.set_text_color(*self.soft_danger)
                else:
                    self.set_text_color(0, 0, 0)
            
            self.cell(col_widths[i], 7, value, 1, 0, 'C', 1)
            self.set_text_color(0, 0, 0)  # Reset color
        
        self.ln()
        
        # ===== SECOND ROW FOR ADDITIONAL METRICS =====
        additional_headers = []
        additional_values = []
        
        # STATUS
        if 'status' in summary:
            additional_headers.append("STATUS")
            status_value = summary['status']
            additional_values.append(status_value)
        
        # DIVISION
        if 'division' in summary and summary['division']:
            additional_headers.append("DIVISION")
            additional_values.append(summary['division'])
        
        # POINTS (for ACSEE/CSEE)
        if 'points' in summary and summary['points'] is not None:
            if self.system_rule in ['acsee', 'csee']:
                additional_headers.append("POINTS")
                additional_values.append(str(summary['points']))
        
        # Draw second row if we have additional metrics
        if additional_headers:
            self.ln(1)
            
            # Adjust column widths for second row
            if len(additional_headers) == 1:
                sec_col_widths = [100, 100]
                # Center single item
                self.set_fill_color(*self.soft_light)
                self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
                
                # Color for STATUS
                if additional_headers[0] == "STATUS":
                    if additional_values[0] == "PASS":
                        self.set_text_color(*self.soft_success)
                    elif additional_values[0] == "FAIL":
                        self.set_text_color(*self.soft_danger)
                
                self.cell(100, 7, additional_headers[0], 1, 0, 'C', 1)
                self.cell(100, 7, additional_values[0], 1, 1, 'C', 1)
                self.set_text_color(0, 0, 0)
            
            elif len(additional_headers) == 2:
                sec_col_widths = [50, 50, 50, 50]
                self.set_fill_color(*self.soft_light)
                self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
                
                for i in range(4):
                    if i < len(additional_headers):
                        # Color coding
                        if additional_headers[i] == "STATUS":
                            if additional_values[i] == "PASS":
                                self.set_text_color(*self.soft_success)
                            elif additional_values[i] == "FAIL":
                                self.set_text_color(*self.soft_danger)
                        
                        self.cell(sec_col_widths[i], 7, additional_headers[i], 1, 0, 'C', 1)
                        self.set_text_color(0, 0, 0)
                    else:
                        self.cell(sec_col_widths[i], 7, "", 1, 0, 'C', 1)
                
                self.ln()
                
                # Values row
                self.set_fill_color(255, 255, 255)
                for i in range(4):
                    if i < len(additional_values):
                        # Color coding
                        if i < len(additional_headers) and additional_headers[i] == "STATUS":
                            if additional_values[i] == "PASS":
                                self.set_text_color(*self.soft_success)
                            elif additional_values[i] == "FAIL":
                                self.set_text_color(*self.soft_danger)
                        
                        self.cell(sec_col_widths[i], 7, additional_values[i], 1, 0, 'C', 1)
                        self.set_text_color(0, 0, 0)
                    else:
                        self.cell(sec_col_widths[i], 7, "", 1, 0, 'C', 1)
                
                self.ln()
        
        # ACSEE specific: Principals (if exists, add as note)
        if self.system_rule == 'acsee' and 'principals' in summary:
            self.ln(2)
            self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
            self.set_text_color(*self.soft_secondary)
            self.cell(0, 6, f"Principals: {summary['principals']}", 0, 1, 'L')
        
        # Remarks
        if 'remark' in summary and summary['remark']:
            self.ln(4)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 9)
            self.set_text_color(*self.soft_secondary)
            
            remark = summary['remark']
            if len(remark) > 80:
                remark = remark[:77] + "..."
            
            self.multi_cell(0, 5, f"Remarks: {remark}", 0, 'L')
        
        self.ln(8)
        self._add_soft_separator()
        self.ln(5)
    
    def _build_clean_subjects_table(self, subjects):
        """Build clean subjects table"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 11)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 7, "SUBJECT PERFORMANCE", 0, 1, 'L')
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
        
        # Determine table headers based on system (SIMPLIFIED)
        if self.system_rule == 'acsee':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS"]
            col_widths = [12, 85, 30, 30, 30]
        elif self.system_rule == 'csee':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS"]
            col_widths = [12, 85, 30, 30, 30]
        elif self.system_rule == 'plse':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "STATUS"]
            col_widths = [12, 85, 30, 30, 40]
        else:
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE"]
            col_widths = [12, 105, 40, 40]
        
        # Draw header with SOFT color
        self.set_fill_color(*self.soft_primary)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
        self.ln()
        
        # Draw table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors (SOFT)
            if idx % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(*self.soft_light)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            attended = subject.get('attended', True)
            passed = subject.get('pass', subject.get('pass', True))
            
            # Truncate long subject names
            name_display = name[:30] + '...' if len(name) > 30 else name
            
            # Draw row
            self.cell(col_widths[0], 6, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 6, name_display, 1, 0, 'L', 1)
            
            # Marks (handle ABSENT)
            if not attended:
                marks_text = "ABS"
                grade_text = "ABS"
                points_text = "ABS" if self.system_rule in ['acsee', 'csee'] else ""
            else:
                marks_text = f"{marks:.0f}" if marks else "0"
                grade_text = grade
                points_text = str(points) if points else ""
            
            self.cell(col_widths[2], 6, marks_text, 1, 0, 'C', 1)
            
            # Grade with SOFT color coding
            if grade_text == "ABS":
                self.set_text_color(*self.soft_danger)
            elif grade_text in ["A", "B", "C", "I", "II", "III"]:
                self.set_text_color(*self.soft_success)
            elif grade_text in ["D", "E", "F"]:
                self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[3], 6, grade_text, 1, 0, 'C', 1)
            self.set_text_color(0, 0, 0)
            
            # Last column
            if len(headers) > 4:
                if headers[4] == "POINTS":
                    self.cell(col_widths[4], 6, points_text, 1, 1, 'C', 1)
                elif headers[4] == "STATUS":
                    status = "PASS" if passed else "FAIL"
                    if status == "FAIL":
                        self.set_text_color(*self.soft_danger)
                    self.cell(col_widths[4], 6, status, 1, 1, 'C', 1)
                    self.set_text_color(0, 0, 0)
            else:
                self.ln()
        
        self.ln(5)
    
    def _build_clean_footer(self, class_info: Dict[str, Any]):
        """Build clean footer"""
        self._add_soft_separator()
        
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        self.set_text_color(*self.soft_secondary)
        
        # Generation info
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 5, f"Generated on: {date_printed}", 0, 1, 'L')
        
        # Class info
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', '')
        
        if class_name:
            self.cell(0, 5, f"Class: {class_name}", 0, 1, 'L')
        
        # System
        system_label = self._get_system_label()
        self.cell(0, 5, f"System: {system_label}", 0, 1, 'L')
        
        # Confidential notice (soft)
        if self.config.get('confidential', True):
            self.set_font(PDFConstants.ITALIC_FONT, "I", 8)
            self.set_text_color(*self.soft_secondary)
            self.cell(0, 5, "Confidential - For official use only", 0, 1, 'C')
    
    def _add_soft_separator(self):
        """Add soft separator line"""
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
    
    def _create_error_pdf(self, error_message: str) -> str:
        """Create error PDF file"""
        from fpdf import FPDF
        
        filename = generate_filename("error", "student_report")
        filepath = get_temp_path(filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*self.soft_danger)
        pdf.cell(0, 8, "Error Generating Report", 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Error: {error_message[:150]}")
        
        pdf.output(filepath)
        return filepath


# ========== ALIAS CLASSES ==========

class ACSEEReportGenerator(StudentReportGenerator):
    """ACSEE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'acsee'
        config['system_name'] = config.get('system_name', 'Advanced Level (ACSEE)')
        super().__init__(config)

class CSEEReportGenerator(StudentReportGenerator):
    """CSEE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'csee'
        config['system_name'] = config.get('system_name', 'Ordinary Level (CSEE)')
        super().__init__(config)

class PLSEReportGenerator(StudentReportGenerator):
    """PLSE Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'plse'
        config['system_name'] = config.get('system_name', 'Primary Level (PLSE)')
        super().__init__(config)

class GenericReportGenerator(StudentReportGenerator):
    """Generic Report Generator"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = config.get('system_rule', 'generic')
        config['system_name'] = config.get('system_name', 'Academic Report')
        super().__init__(config)