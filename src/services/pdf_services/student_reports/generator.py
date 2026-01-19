"""
Student Report Generator - FINAL LAYOUT (As requested)
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


class StudentReportGenerator(BasePDFTemplate):
    """Student report generator - FINAL LAYOUT"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_rule = self.config.get('system_rule', '').lower()
        self.system_name = self.config.get('system_name', '')
        
        # Use soft colors
        self._setup_soft_colors()
        
        # Set default margins for layout
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(left=15, top=15, right=15)
    
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
        """Generate student report PDF with FINAL LAYOUT"""
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
            
            # Build document with FINAL LAYOUT
            self._build_final_layout(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _build_final_layout(self, student_data: Dict[str, Any], 
                            class_info: Dict[str, Any], 
                            school_info: Dict[str, Any]):
        """Build document with FINAL LAYOUT as specified"""
        # Detect system
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # ===== FINAL HEADER (3 lines as specified) =====
        self._build_final_header(school_info, class_info)
        
        # ===== STUDENT INFO (Simple vertical) =====
        self._build_final_student_info(student_data.get('student', {}))
        
        # ===== ACADEMIC SUMMARY TABLE (5 columns) =====
        summary = student_data.get('summary', {})
        self._build_final_summary_table(summary)
        
        # ===== SUBJECTS TABLE (Swahili headers) =====
        if 'subjects' in student_data:
            self._build_final_subjects_table(student_data['subjects'])
        
        # ===== FINAL FOOTER (3 columns) =====
        self._build_final_footer()
    
    def _build_final_header(self, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Build FINAL header (3 lines)"""
        # Line 1: School name - BIG
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*self.soft_primary)
        
        school_name = school_info.get('name', 'SHULE YA MSINGI MIPEKO')
        self.cell(0, 12, school_name, 0, 1, 'C')
        
        # Line 2: Exam name - MEDIUM
        self.set_font(PDFConstants.BOLD_FONT, "B", 14)
        self.set_text_color(*self.soft_secondary)
        
        exam_name = class_info.get('exam_name', 'MTIHANI WA NUSU MUHURA AU MUHURA DARASA RA 6')
        self.cell(0, 10, exam_name, 0, 1, 'C')
        
        # Line 3: Term/Year - SMALL
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f"MUHURA WA {term} - {year}", 0, 1, 'C')
        
        # Optional: Exam details
        exam_code = class_info.get('exam_code', '')
        exam_date = class_info.get('exam_date', '')
        
        if exam_code or exam_date:
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.set_text_color(100, 100, 100)
            
            details = []
            if exam_code:
                details.append(f"Jina la Mtihani: {exam_code}")
            if exam_date:
                details.append(f"Tarehe ya Mtihani: {exam_date}")
            
            self.cell(0, 6, " | ".join(details), 0, 1, 'C')
        
        self.ln(10)
        self._add_final_separator()
        self.ln(8)
    
    def _build_final_student_info(self, student: Dict[str, Any]):
        """Build FINAL student info (vertical)"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 8, "TAARIFA ZA MWANAFUNZI", 0, 1, 'L')
        self.ln(3)
        
        # Simple vertical layout
        info_items = []
        
        # Name
        if 'name' in student:
            info_items.append(("Jina:", student['name'], True))
        
        # Admission
        if 'admission' in student:
            info_items.append(("Nambari ya Ukumbusho:", student['admission'], True))
        
        # Gender
        if 'gender' in student:
            gender_map = {
                'M': 'Mwanaume',
                'F': 'Mwanamke',
                'male': 'Mwanaume',
                'female': 'Mwanamke'
            }
            gender = student['gender']
            gender_display = gender_map.get(gender.lower(), gender)
            info_items.append(("Jinsia:", gender_display, False))
        
        # Class (if available)
        if 'class' in student:
            info_items.append(("Darasa:", student['class'], False))
        
        # Display all items
        for label, value, is_bold in info_items:
            # Label
            self.set_font(PDFConstants.BOLD_FONT, "B", 10)
            self.set_text_color(*self.soft_secondary)
            self.cell(50, 7, label, 0, 0, 'L')
            
            # Value
            if is_bold:
                self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
            else:
                self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            
            self.set_text_color(0, 0, 0)
            self.cell(0, 7, str(value), 0, 1, 'L')
        
        self.ln(10)
        self._add_final_separator()
        self.ln(8)
    
    def _build_final_summary_table(self, summary: Dict[str, Any]):
        """Build FINAL academic summary table (5 columns)"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 8, "TAARIFA ZA JUMLA YA MAFANIKIO", 0, 1, 'L')
        self.ln(3)
        
        # ===== MAIN TABLE - 5 COLUMNS =====
        # Column widths for 5 columns
        col_widths = [38, 38, 38, 38, 38]  # Equal widths
        
        # Headers as specified
        headers = ["TOTAL MARKS", "AVERAGE SCORE", "GRADE", "POSITION", "STATUS"]
        
        # Draw header row
        self.set_fill_color(*self.soft_primary)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Prepare values
        total_marks = f"{summary.get('total', 0):.0f}" if 'total' in summary else "N/A"
        average_score = f"{summary.get('average', 0):.1f}%" if 'average' in summary else "N/A"
        grade = summary.get('grade', 'N/A')
        position = str(summary.get('rank', 'N/A')) if 'rank' in summary else "N/A"
        status = summary.get('status', 'PASS')
        
        values = [total_marks, average_score, grade, position, status]
        
        # Draw data row
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 10)
        
        for i, value in enumerate(values):
            # Color coding
            if i == 2:  # GRADE column
                if value in ["A", "B", "C", "I", "II", "III"]:
                    self.set_text_color(*self.soft_success)
                elif value in ["D", "E", "F"]:
                    self.set_text_color(*self.soft_danger)
                else:
                    self.set_text_color(0, 0, 0)
            elif i == 4:  # STATUS column
                if value == "PASS":
                    self.set_text_color(*self.soft_success)
                elif value == "FAIL":
                    self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[i], 8, value, 1, 0, 'C', 1)
            self.set_text_color(0, 0, 0)  # Reset color
        
        self.ln()
        
        # ===== REMARKS SECTION =====
        if 'remark' in summary and summary['remark']:
            self.ln(8)
            self.set_font(PDFConstants.ITALIC_FONT, "I", 10)
            self.set_text_color(*self.soft_secondary)
            
            remark = summary['remark']
            # Add icon/emoji before remarks
            remark_text = f"🔥 Maoni: {remark}"
            
            self.multi_cell(0, 6, remark_text, 0, 'L')
        
        self.ln(12)
        self._add_final_separator()
        self.ln(8)
    
    def _build_final_subjects_table(self, subjects):
        """Build FINAL subjects table with Swahili headers"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 8, "MAFANIKIO KATIKA SOMO", 0, 1, 'L')
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
        
        # Table headers in Swahili
        headers = ["#", "SOMO", "ALAMA", "DARAJA", "STATUS"]
        col_widths = [12, 88, 35, 35, 40]
        
        # Draw header
        self.set_fill_color(*self.soft_primary)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Draw table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            fill_color = self.soft_light if idx % 2 == 1 else (255, 255, 255)
            self.set_fill_color(*fill_color)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            passed = subject.get('pass', True)
            
            # Format marks
            marks_text = f"{marks:.0f}" if isinstance(marks, (int, float)) else str(marks)
            
            # Draw row
            # 1. Number
            self.cell(col_widths[0], 8, str(idx), 1, 0, 'C', 1)
            
            # 2. Subject name
            self.cell(col_widths[1], 8, name, 1, 0, 'L', 1)
            
            # 3. Marks
            self.cell(col_widths[2], 8, marks_text, 1, 0, 'C', 1)
            
            # 4. Grade with color coding
            if grade in ["A", "B", "C", "I", "II", "III"]:
                self.set_text_color(*self.soft_success)
            elif grade in ["D", "E", "F"]:
                self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[3], 8, grade, 1, 0, 'C', 1)
            self.set_text_color(0, 0, 0)
            
            # 5. Status with color coding
            status = "PASS" if passed else "FAIL"
            if status == "PASS":
                self.set_text_color(*self.soft_success)
            else:
                self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[4], 8, status, 1, 1, 'C', 1)
            self.set_text_color(0, 0, 0)
        
        self.ln(12)
    
    def _build_final_footer(self):
        """Build FINAL footer with 3 columns"""
        # Get current position
        current_y = self.get_y()
        page_height = 297  # A4 height in mm
        
        # Move to bottom if needed
        if current_y < page_height - 30:
            self.set_y(page_height - 30)
        
        # Add separator line
        self._add_final_separator()
        
        # Footer with 3 columns
        footer_height = 8
        
        # Calculate column positions
        left_x = 15
        center_x = 105  # Middle of page
        right_x = 180
        
        # Save current y position
        footer_y = self.get_y()
        
        # LEFT: System name
        self.set_xy(left_x, footer_y)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 8)
        self.set_text_color(*self.soft_secondary)
        self.cell(80, footer_height, "Primary School Leaving Examination System", 0, 0, 'L')
        
        # CENTER: Page number
        self.set_xy(center_x - 30, footer_y)
        center_text = f"Ukurasa wa {self.page_no()}"
        self.cell(60, footer_height, center_text, 0, 0, 'C')
        
        # RIGHT: Support contact
        self.set_xy(right_x - 40, footer_y)
        right_text = "Msaada: +255 123 456 789"
        self.cell(40, footer_height, right_text, 0, 1, 'R')
        
        # Generation date (small, below)
        date_y = footer_y + footer_height
        self.set_xy(center_x - 40, date_y)
        self.set_font(PDFConstants.ITALIC_FONT, "I", 7)
        self.set_text_color(150, 150, 150)
        
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        date_text = f"📅 Imetolewa: {date_printed}"
        self.cell(80, 5, date_text, 0, 0, 'C')
    
    def _add_final_separator(self):
        """Add separator line"""
        y = self.get_y()
        self.line(15, y, 195, y)
        self.ln(5)
    
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


# ========== PLSE SPECIFIC GENERATOR ==========

class PLSEReportGenerator(StudentReportGenerator):
    """PLSE Report Generator with specific layout"""
    def __init__(self, config: dict = None):
        config = config or {}
        config['system_rule'] = 'plse'
        config['system_name'] = 'Primary School Leaving Examination'
        super().__init__(config)
    
    def _build_final_header(self, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Override for PLSE specific header"""
        # Line 1: School name
        self.set_font(PDFConstants.BOLD_FONT, "B", 16)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 12, "SHULE YA MSINGI MIPEKO", 0, 1, 'C')
        
        # Line 2: Exam name
        self.set_font(PDFConstants.BOLD_FONT, "B", 14)
        self.set_text_color(*self.soft_secondary)
        self.cell(0, 10, "MTIHANI WA NUSU MUHURA AU MUHURA DARASA RA 6", 0, 1, 'C')
        
        # Line 3: Term/Year
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        self.set_font(PDFConstants.DEFAULT_FONT, "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f"MUHURA WA {term} - {year}", 0, 1, 'C')
        
        # Exam details
        exam_code = class_info.get('exam_code', 'PLSE MOCK 2024 001')
        exam_date = class_info.get('exam_date', '')
        
        if exam_code or exam_date:
            self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
            self.set_text_color(100, 100, 100)
            
            details = f"Jina la Mtihani: {exam_code}"
            if exam_date:
                details += f" | Tarehe ya Mtihani: {exam_date}"
            
            self.cell(0, 6, details, 0, 1, 'C')
        
        self.ln(10)
        self._add_final_separator()
        self.ln(8)
    
    def _build_final_subjects_table(self, subjects):
        """Override for PLSE subjects table"""
        self.set_font(PDFConstants.BOLD_FONT, "B", 12)
        self.set_text_color(*self.soft_primary)
        self.cell(0, 8, "MAFANIKIO KATIKA SOMO", 0, 1, 'L')
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
        
        # Table headers in Swahili
        headers = ["#", "SOMO", "ALAMA", "DARAJA", "STATUS"]
        col_widths = [12, 88, 35, 35, 40]
        
        # Draw header
        self.set_fill_color(*self.soft_primary)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Draw table data
        self.set_text_color(0, 0, 0)
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            fill_color = self.soft_light if idx % 2 == 1 else (255, 255, 255)
            self.set_fill_color(*fill_color)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            passed = subject.get('pass', True)
            
            # Format subject name
            # Convert English subject names to Swahili if needed
            name_map = {
                'English': 'Kiingereza',
                'Kiswahili': 'Kiswahili',
                'Mathematics': 'Hisabati',
                'Science': 'Sayansi',
                'Social Studies': 'Maarifa ya Jamii',
                'Civics': 'Uraia'
            }
            subject_name = name_map.get(name, name)
            
            # Format marks
            marks_text = f"{marks:.0f}" if isinstance(marks, (int, float)) else str(marks)
            
            # Draw row
            self.cell(col_widths[0], 8, str(idx), 1, 0, 'C', 1)
            self.cell(col_widths[1], 8, subject_name, 1, 0, 'L', 1)
            self.cell(col_widths[2], 8, marks_text, 1, 0, 'C', 1)
            
            # Grade with color
            if grade in ["A", "B", "C"]:
                self.set_text_color(*self.soft_success)
            elif grade in ["D", "E", "F"]:
                self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[3], 8, grade, 1, 0, 'C', 1)
            self.set_text_color(0, 0, 0)
            
            # Status with color
            status = "PASS" if passed else "FAIL"
            if status == "PASS":
                self.set_text_color(*self.soft_success)
            else:
                self.set_text_color(*self.soft_danger)
            
            self.cell(col_widths[4], 8, status, 1, 1, 'C', 1)
            self.set_text_color(0, 0, 0)
        
        self.ln(12)