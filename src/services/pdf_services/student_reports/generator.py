"""
Student Report Generator - WITH TABLE HEADERS & LANDSCAPE
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from ..base.template import BasePDFTemplate
from ..base.utils import generate_filename, get_temp_path
from ..base.constants import PDFConstants


class StudentReportGenerator(BasePDFTemplate):
    """Student report generator with headers and landscape"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.system_rule = self.config.get('system_rule', '').lower()
        self.system_name = self.config.get('system_name', '')
        
        # Set landscape orientation
        self._setup_landscape()
    
    def _setup_landscape(self):
        """Setup for landscape orientation"""
        # We'll handle this in the generation
    
    def generate(self, 
                 student_data: Dict[str, Any],
                 class_info: Dict[str, Any] = None,
                 school_info: Dict[str, Any] = None) -> str:
        """Generate student report PDF in LANDSCAPE"""
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
            
            # Create new PDF with LANDSCAPE
            from fpdf import FPDF
            
            # Create landscape PDF
            self._pdf = FPDF(orientation='L', unit='mm', format='A4')
            self._setup_pdf_basics()
            
            # Build document
            self._build_landscape_document(student_data, class_info or {}, school_info or {})
            
            # Output PDF
            self._pdf.output(filepath)
            return filepath
            
        except Exception as e:
            return self._create_error_pdf(str(e))
    
    def _setup_pdf_basics(self):
        """Setup basic PDF properties"""
        pdf = self._pdf
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("helvetica", "", 10)
    
    def _build_landscape_document(self, student_data: Dict[str, Any], 
                                  class_info: Dict[str, Any], 
                                  school_info: Dict[str, Any]):
        """Build document in LANDSCAPE layout"""
        pdf = self._pdf
        
        # Detect system
        if not self.system_rule and 'rule' in class_info:
            self.system_rule = class_info['rule'].lower()
        
        # ===== HEADER =====
        self._build_landscape_header(pdf, school_info, class_info)
        
        # ===== STUDENT INFO =====
        self._build_landscape_student_info(pdf, student_data.get('student', {}))
        
        # ===== ACADEMIC SUMMARY TABLE WITH HEADERS =====
        summary = student_data.get('summary', {})
        self._build_summary_table_with_headers(pdf, summary)
        
        # ===== SUBJECTS TABLE =====
        if 'subjects' in student_data:
            self._build_landscape_subjects_table(pdf, student_data['subjects'])
        
        # ===== FOOTER =====
        self._build_landscape_footer(pdf, class_info)
    
    def _build_landscape_header(self, pdf, school_info: Dict[str, Any], class_info: Dict[str, Any]):
        """Build header for landscape"""
        # School name
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
        
        school_name = school_info.get('name', 'SCHOOL NAME')
        pdf.cell(0, 10, school_name, 0, 1, 'C')
        
        # System label
        system_label = self._get_system_label()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
        pdf.cell(0, 8, system_label, 0, 1, 'C')
        
        # Exam and class info
        exam_name = class_info.get('exam_name', 'EXAMINATION')
        class_name = class_info.get('class_name', '')
        term = class_info.get('term', 'I')
        year = class_info.get('year', datetime.now().year)
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, exam_name, 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 11)
        info_text = f"Class: {class_name} | Term: {term} | Year: {year}"
        pdf.cell(0, 7, info_text, 0, 1, 'C')
        
        pdf.ln(5)
        self._add_separator(pdf)
        pdf.ln(5)
    
    def _get_system_label(self):
        """Get system label"""
        if self.system_rule == 'acsee':
            return "ADVANCED CERTIFICATE OF SECONDARY EDUCATION"
        elif self.system_rule == 'csee':
            return "CERTIFICATE OF SECONDARY EDUCATION"
        elif self.system_rule == 'plse':
            return "PRIMARY SCHOOL LEAVING EXAMINATION"
        else:
            return "ACADEMIC PERFORMANCE REPORT"
    
    def _build_landscape_student_info(self, pdf, student: Dict[str, Any]):
        """Build student info for landscape"""
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
        pdf.cell(0, 8, "STUDENT INFORMATION", 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        
        # Create info table
        col1 = 40
        col2 = 80
        col3 = 40
        col4 = 80
        
        # Row 1: Name and Admission
        if 'name' in student:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            pdf.cell(col1, 6, "Name:", 0, 0, 'L')
            
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col2, 6, student['name'], 0, 0, 'L')
        
        if 'admission' in student:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            pdf.cell(col3, 6, "Admission No:", 0, 0, 'L')
            
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col4, 6, student['admission'], 0, 1, 'L')
        else:
            pdf.ln(6)
        
        # Row 2: Gender and Class
        if 'gender' in student:
            gender_display = "Male" if student['gender'] == 'M' else "Female" if student['gender'] == 'F' else student['gender']
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            pdf.cell(col1, 6, "Gender:", 0, 0, 'L')
            
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col2, 6, gender_display, 0, 0, 'L')
        
        if 'class' in student:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            pdf.cell(col3, 6, "Class:", 0, 0, 'L')
            
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col4, 6, student['class'], 0, 1, 'L')
        else:
            pdf.ln(6)
        
        pdf.ln(8)
        self._add_separator(pdf)
        pdf.ln(5)
    
    def _build_summary_table_with_headers(self, pdf, summary: Dict[str, Any]):
        """Build academic summary table WITH HEADERS"""
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
        pdf.cell(0, 8, "ACADEMIC PERFORMANCE SUMMARY", 0, 1, 'L')
        pdf.ln(3)
        
        # ===== TABLE WITH HEADERS =====
        # Define column widths for landscape (more space)
        col_widths = [45, 45, 45, 45, 45, 45]  # 6 columns for landscape
        
        # Table headers
        headers = ["TOTAL MARKS", "AVERAGE SCORE", "GRADE", "POSITION", "STATUS", "SUBJECTS PASSED"]
        
        # Draw header row with color
        pdf.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("helvetica", "B", 10)
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        pdf.ln()
        
        # Prepare values
        total_marks = f"{summary.get('total', 0):.0f}" if 'total' in summary else "N/A"
        average_score = f"{summary.get('average', 0):.1f}%" if 'average' in summary else "N/A"
        grade = summary.get('grade', 'N/A')
        position = str(summary.get('rank', 'N/A')) if 'rank' in summary else "N/A"
        status = summary.get('status', 'N/A')
        
        # Subjects passed
        if 'subjects_passed' in summary and 'subjects_total' in summary:
            passed = summary['subjects_passed']
            total = summary['subjects_total']
            subjects_passed = f"{passed}/{total}"
        else:
            subjects_passed = "N/A"
        
        values = [total_marks, average_score, grade, position, status, subjects_passed]
        
        # Draw data row
        pdf.set_fill_color(*PDFConstants.LIGHT_COLOR)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "B", 11)
        
        for i, value in enumerate(values):
            # Special formatting for certain columns
            if i == 2:  # GRADE column
                if value in ["A", "B", "C", "I", "II", "III"]:
                    pdf.set_text_color(*PDFConstants.SUCCESS_COLOR)
                elif value in ["D", "E", "F"]:
                    pdf.set_text_color(*PDFConstants.DANGER_COLOR)
                else:
                    pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
            
            elif i == 4:  # STATUS column
                if value == "PASS":
                    pdf.set_text_color(*PDFConstants.SUCCESS_COLOR)
                elif value == "FAIL":
                    pdf.set_text_color(*PDFConstants.DANGER_COLOR)
                else:
                    pdf.set_text_color(0, 0, 0)
            
            pdf.cell(col_widths[i], 8, value, 1, 0, 'C', 1)
            pdf.set_text_color(0, 0, 0)  # Reset color
        
        pdf.ln()
        
        # ===== ADDITIONAL METRICS ROW (if available) =====
        additional_metrics = []
        
        if 'division' in summary and summary['division']:
            additional_metrics.append(("DIVISION", summary['division']))
        
        if 'points' in summary and summary['points'] is not None:
            additional_metrics.append(("POINTS", str(summary['points'])))
        
        if self.system_rule == 'acsee' and 'principals' in summary:
            additional_metrics.append(("PRINCIPALS", str(summary['principals'])))
        
        if additional_metrics:
            pdf.ln(2)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            pdf.cell(0, 6, "ADDITIONAL METRICS:", 0, 1, 'L')
            
            # Draw additional metrics
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            
            metric_texts = []
            for label, value in additional_metrics:
                metric_texts.append(f"{label}: {value}")
            
            pdf.cell(0, 6, " | ".join(metric_texts), 0, 1, 'L')
        
        # Remarks
        if 'remark' in summary and summary['remark']:
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
            pdf.cell(30, 6, "REMARKS:", 0, 0, 'L')
            
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
            remark = summary['remark']
            if len(remark) > 100:
                remark = remark[:97] + "..."
            pdf.cell(0, 6, remark, 0, 1, 'L')
        
        pdf.ln(10)
        self._add_separator(pdf)
        pdf.ln(5)
    
    def _build_landscape_subjects_table(self, pdf, subjects):
        """Build subjects table for landscape"""
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*PDFConstants.PRIMARY_COLOR)
        pdf.cell(0, 8, "SUBJECT PERFORMANCE DETAILS", 0, 1, 'L')
        pdf.ln(3)
        
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
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS", "STATUS"]
            col_widths = [15, 80, 30, 30, 30, 40]
        elif self.system_rule == 'csee':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS", "RANK"]
            col_widths = [15, 80, 30, 30, 30, 30]
        elif self.system_rule == 'plse':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "STATUS", "RANK"]
            col_widths = [15, 80, 30, 30, 40, 30]
        else:
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "STATUS"]
            col_widths = [15, 100, 40, 40, 60]
        
        # Draw header
        pdf.set_fill_color(*PDFConstants.PRIMARY_COLOR)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("helvetica", "B", 10)
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        pdf.ln()
        
        # Draw table data
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 9)
        
        for idx, subject in enumerate(subjects_list, 1):
            # Alternate row colors
            if idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(*PDFConstants.LIGHT_COLOR)
            
            # Get data
            name = subject.get('name', 'N/A')
            marks = subject.get('marks', subject.get('score', 0))
            grade = subject.get('grade', 'N/A')
            points = subject.get('points', '')
            rank = subject.get('subject_rank', '')
            attended = subject.get('attended', True)
            passed = subject.get('pass', subject.get('pass', True))
            
            # Truncate long subject names
            name_display = name[:35] + '...' if len(name) > 35 else name
            
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
                
                pdf.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                pdf.cell(col_widths[1], 7, name_display, 1, 0, 'L', 1)
                pdf.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[3], 7, grade_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
                
                # Color code status
                if status == "ABSENT":
                    pdf.set_text_color(*PDFConstants.DANGER_COLOR)
                elif status == "FAIL":
                    pdf.set_text_color(*PDFConstants.WARNING_COLOR)
                
                pdf.cell(col_widths[5], 7, status, 1, 1, 'C', 1)
                pdf.set_text_color(0, 0, 0)
            
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
                
                pdf.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                pdf.cell(col_widths[1], 7, name_display, 1, 0, 'L', 1)
                pdf.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[3], 7, grade_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[4], 7, points_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
            
            elif self.system_rule == 'plse':
                # PLSE row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                rank_text = str(rank) if rank else ''
                
                pdf.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                pdf.cell(col_widths[1], 7, name_display, 1, 0, 'L', 1)
                pdf.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                
                # Color code status
                if status == "FAIL":
                    pdf.set_text_color(*PDFConstants.DANGER_COLOR)
                
                pdf.cell(col_widths[4], 7, status, 1, 0, 'C', 1)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_widths[5], 7, rank_text, 1, 1, 'C', 1)
            
            else:
                # Generic row
                status = "PASS" if passed else "FAIL"
                marks_text = f"{marks:.0f}" if marks else "0"
                
                pdf.cell(col_widths[0], 7, str(idx), 1, 0, 'C', 1)
                pdf.cell(col_widths[1], 7, name_display, 1, 0, 'L', 1)
                pdf.cell(col_widths[2], 7, marks_text, 1, 0, 'C', 1)
                pdf.cell(col_widths[3], 7, grade, 1, 0, 'C', 1)
                
                if status == "FAIL":
                    pdf.set_text_color(*PDFConstants.DANGER_COLOR)
                
                pdf.cell(col_widths[4], 7, status, 1, 1, 'C', 1)
                pdf.set_text_color(0, 0, 0)
        
        pdf.ln(5)
    
    def _build_landscape_footer(self, pdf, class_info: Dict[str, Any]):
        """Build footer for landscape"""
        self._add_separator(pdf)
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(*PDFConstants.SECONDARY_COLOR)
        
        # Generation info
        date_printed = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 5, f"Generated on: {date_printed}", 0, 1, 'L')
        
        # System info
        system_label = self._get_system_label()
        pdf.cell(0, 5, f"System: {system_label}", 0, 1, 'L')
        
        # Confidential notice
        if self.config.get('confidential', True):
            pdf.set_font("helvetica", "I", 8)
            pdf.cell(0, 5, "Confidential - For official use only", 0, 1, 'C')
    
    def _add_separator(self, pdf):
        """Add separator line"""
        pdf.line(15, pdf.get_y(), 285, pdf.get_y())  # 285mm for landscape width
    
    def _create_error_pdf(self, error_message: str) -> str:
        """Create error PDF file"""
        from fpdf import FPDF
        
        filename = generate_filename("error", "student_report")
        filepath = get_temp_path(filename)
        
        pdf = FPDF(orientation='L')  # Landscape for error too
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*PDFConstants.DANGER_COLOR)
        pdf.cell(0, 10, "Error Generating Report", 0, 1, 'C')
        
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, f"Error: {error_message[:200]}")
        
        pdf.output(filepath)
        return filepath


# ========== ALIAS CLASSES ==========

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