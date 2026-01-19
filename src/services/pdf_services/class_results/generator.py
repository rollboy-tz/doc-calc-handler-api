"""
services/pdf_services/class_results/generator.py
"""
import os
import tempfile
from datetime import datetime
from ..base.template import PDFBaseTemplate

class ClassResultsGenerator(PDFBaseTemplate):
    """Generate class result sheets using fpdf2"""
    
    def __init__(self):
        super().__init__()
        # Set landscape orientation
        self.set_display_mode(orientation='landscape')
        self.margin_x = 10
        self.margin_y = 10
    
    def generate(self, class_data, school_info):
        """Generate class results PDF"""
        try:
            # Create file
            class_name = class_data['metadata']['class_name']
            filename = f"class_results_{class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Build content
            self._build_content(class_data, school_info)
            
            # Output PDF
            self.output(filepath)
            
            return filepath
            
        except Exception as e:
            return self._create_error(str(e))
    
    def _build_content(self, class_data, school_info):
        """Build class results content"""
        # Header
        if school_info.get('name'):
            self.set_font("helvetica", "B", 16)
            self.cell(0, 10, school_info['name'], 0, 1, 'C')
            self.ln(5)
        
        # Title
        metadata = class_data['metadata']
        title = f"CLASS RESULTS - {metadata['class_name']} - TERM {metadata.get('term', '1')}"
        
        self.set_font("helvetica", "B", 14)
        self.cell(0, 10, title, 0, 1, 'C')
        
        # Exam info
        exam_date = metadata.get('exam_date', datetime.now().strftime('%Y-%m-%d'))
        exam_name = metadata.get('exam_name', 'Term Examination')
        
        self.set_font("helvetica", "", 11)
        self.cell(0, 8, f"Exam: {exam_name} | Date: {exam_date}", 0, 1, 'C')
        self.ln(10)
        
        # Students table
        students = class_data['students']
        
        # Create table header
        self._create_students_table(students)
        
        # Class statistics if available
        if 'statistics' in class_data:
            self.ln(15)
            self._add_statistics(class_data['statistics'])
    
    def _create_students_table(self, students):
        """Create students results table"""
        # Table header
        self.set_fill_color(*self.colors['primary'])
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 10)
        
        headers = ["POS", "NAME", "ADM NO", "TOTAL", "AVG%", "GRADE", "REMARKS"]
        col_widths = [20, 100, 60, 40, 40, 40, 80]
        
        # Draw header
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        self.ln()
        
        # Students data
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 9)
        
        for student in students:
            # Check if new page needed (keep 3 rows margin)
            if self.get_y() > self.h - 40:
                self.add_page()
                # Redraw header on new page
                self.set_fill_color(*self.colors['primary'])
                self.set_text_color(255, 255, 255)
                self.set_font("helvetica", "B", 10)
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
                self.ln()
                self.set_fill_color(255, 255, 255)
                self.set_text_color(0, 0, 0)
                self.set_font("helvetica", "", 9)
            
            # Draw student row
            self.cell(col_widths[0], 8, str(student.get('position', '')), 1, 0, 'C', 1)
            self.cell(col_widths[1], 8, student['name'][:25], 1, 0, 'L', 1)
            self.cell(col_widths[2], 8, student['admission'], 1, 0, 'C', 1)
            self.cell(col_widths[3], 8, str(student.get('total_marks', 0)), 1, 0, 'C', 1)
            self.cell(col_widths[4], 8, f"{student.get('average', 0):.1f}", 1, 0, 'C', 1)
            self.cell(col_widths[5], 8, student.get('grade', ''), 1, 0, 'C', 1)
            self.cell(col_widths[6], 8, student.get('remark', '')[:20], 1, 1, 'L', 1)
    
    def _add_statistics(self, stats):
        """Add class statistics"""
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "CLASS STATISTICS", 0, 1)
        self.ln(5)
        
        # Statistics table
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(*self.colors['dark'])
        self.set_text_color(255, 255, 255)
        
        stats_headers = ["Metric", "Value"]
        self.cell(60, 10, stats_headers[0], 1, 0, 'L', 1)
        self.cell(40, 10, stats_headers[1], 1, 1, 'C', 1)
        
        # Stats data
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 10)
        
        stats_data = [
            ("Class Average", f"{stats.get('average', 0):.1f}%"),
            ("Highest Score", str(stats.get('highest', 0))),
            ("Lowest Score", str(stats.get('lowest', 0))),
            ("Total Students", str(stats.get('count', 0))),
            ("Pass Rate", f"{stats.get('pass_rate', 0):.1f}%")
        ]
        
        for label, value in stats_data:
            self.cell(60, 8, label, 1, 0, 'L', 1)
            self.cell(40, 8, value, 1, 1, 'C', 1)
    
    def _create_error(self, error_msg):
        """Create error file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        pdf = FPDF(orientation='L')  # Landscape
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Error Generating Class Results", 0, 1, 'C')
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 10, f"Error: {error_msg[:100]}")
        pdf.output(temp_file.name)
        
        return temp_file.name