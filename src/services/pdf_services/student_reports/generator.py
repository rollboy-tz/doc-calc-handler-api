"""
services/pdf_services/student_reports/generator.py
"""
import os
import tempfile
from datetime import datetime
from ..base.template import PDFBaseTemplate

class StudentReportGenerator(PDFBaseTemplate):
    """Generate student reports using fpdf2"""
    
    def __init__(self):
        super().__init__()
        self.margin_x = 10
        self.margin_y = 10
    
    def generate(self, student_data, class_info, school_info):
        """Generate student report PDF"""
        try:
            # Create file
            filename = f"student_report_{student_data['admission']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Build content
            self._build_content(student_data, class_info, school_info)
            
            # Output PDF
            self.output(filepath)
            
            return filepath
            
        except Exception as e:
            return self._create_error(str(e))
    
    def _build_content(self, student_data, class_info, school_info):
        """Build report content"""
        # School header
        if school_info.get('name'):
            self.set_font("helvetica", "B", 16)
            self.cell(0, 10, school_info['name'], 0, 1, 'C')
            self.ln(5)
        
        # Title
        self.set_font("helvetica", "B", 14)
        self.cell(0, 10, f"STUDENT ACADEMIC REPORT - TERM {class_info.get('term', '1')}", 0, 1, 'C')
        self.ln(5)
        
        # Student info
        self.set_font("helvetica", "", 12)
        self.cell(0, 8, f"Name: {student_data['name']}", 0, 1)
        self.cell(0, 8, f"Admission: {student_data['admission']}", 0, 1)
        self.cell(0, 8, f"Class: {class_info.get('class_name', 'N/A')}", 0, 1)
        self.cell(0, 8, f"Year: {datetime.now().year}", 0, 1)
        
        self.ln(10)
        
        # Performance section
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "ACADEMIC PERFORMANCE", 0, 1)
        self.ln(5)
        
        # Performance table
        self._create_performance_table(student_data)
        
        self.ln(15)
        
        # Additional info if available
        if student_data.get('subjects'):
            self._add_subjects_table(student_data['subjects'])
    
    def _create_performance_table(self, student_data):
        """Create performance summary table"""
        data = [
            ["Metric", "Value"],
            ["Total Marks", str(student_data.get('total_marks', 0))],
            ["Average", f"{student_data.get('average', 0):.1f}%"],
            ["Grade", student_data.get('grade', 'N/A')],
            ["Position", student_data.get('position', 'N/A')],
            ["Remark", student_data.get('remark', 'N/A')]
        ]
        
        # Table styling
        self.set_font("helvetica", "B", 11)
        col_widths = [60, 60]
        
        for row in data:
            if row[0] == "Metric":  # Header row
                self.set_fill_color(*self.colors['primary'])
                self.set_text_color(255, 255, 255)
                self.set_font("helvetica", "B", 11)
            else:
                self.set_fill_color(255, 255, 255)
                self.set_text_color(0, 0, 0)
                self.set_font("helvetica", "", 11)
            
            # Draw cells
            self.cell(col_widths[0], 10, row[0], 1, 0, 'L', 1)
            self.cell(col_widths[1], 10, row[1], 1, 1, 'C', 1)
    
    def _add_subjects_table(self, subjects):
        """Add subjects table if available"""
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "SUBJECT PERFORMANCE", 0, 1)
        self.ln(5)
        
        # Table header
        self.set_fill_color(*self.colors['dark'])
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 11)
        
        self.cell(80, 10, "Subject", 1, 0, 'L', 1)
        self.cell(30, 10, "Marks", 1, 0, 'C', 1)
        self.cell(30, 10, "Grade", 1, 0, 'C', 1)
        self.cell(40, 10, "Remarks", 1, 1, 'C', 1)
        
        # Subjects data
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 10)
        
        for subject in subjects:
            name = subject.get('name', '')[:25]
            self.cell(80, 8, name, 1, 0, 'L', 1)
            self.cell(30, 8, str(subject.get('marks', '')), 1, 0, 'C', 1)
            self.cell(30, 8, subject.get('grade', ''), 1, 0, 'C', 1)
            self.cell(40, 8, subject.get('remarks', '')[:15], 1, 1, 'C', 1)
    
    def _create_error(self, error_msg):
        """Create error file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Error Generating Report", 0, 1)
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 10, f"Error: {error_msg[:100]}")
        pdf.output(temp_file.name)
        
        return temp_file.name