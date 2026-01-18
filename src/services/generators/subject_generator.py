# services/generators/subject_generator.py
"""
SINGLE SUBJECT TEMPLATE GENERATOR
For one subject only
"""
import pandas as pd
from io import BytesIO
from .base_generator import BaseGenerator

class SubjectGenerator(BaseGenerator):
    """Generate single subject marksheet template"""
    
    def __init__(self, subject_name="MATHEMATICS", class_name="FORM 4", stream=""):
        self.subject_name = subject_name
        self.class_name = class_name
        self.stream = stream
    
    def generate(self, student_count=10):
        """Generate Excel template for single subject"""
        # Create sample students
        students = []
        for i in range(1, student_count + 1):
            students.append({
                'admission_no': f'ADM2024{i:03d}',
                'student_id': f'STU24{i:03d}',
                'full_name': f'STUDENT {i}',
                'gender': 'M' if i % 2 == 0 else 'F',
                'class': self.class_name,
                'stream': self.stream
            })
        
        # Create DataFrame
        df = pd.DataFrame(students)
        
        # Add subject column (empty for teacher to fill)
        df[self.subject_name] = ''
        
        # Add remarks column
        df['remarks'] = ''
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = f"{self.subject_name}_MARKS"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Apply formatting
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Basic formatting
            self._apply_basic_formatting(worksheet)
            
            # Highlight subject column (column G)
            from openpyxl.styles import PatternFill
            subject_fill = PatternFill(
                start_color="FFF2CC",  # Light yellow
                end_color="FFF2CC",
                fill_type="solid"
            )
            
            for row in range(2, student_count + 2):  # Skip header
                cell = worksheet.cell(row=row, column=7)  # Column G
                cell.fill = subject_fill
                cell.alignment = Alignment(horizontal="center")
                cell.number_format = '0'  # Integer format
            
            # Set column widths
            column_widths = {
                'A': 15,  # admission_no
                'B': 12,  # student_id
                'C': 25,  # full_name
                'D': 10,  # gender
                'E': 10,  # class
                'F': 10,  # stream
                'G': 15,  # subject marks (highlighted)
                'H': 25   # remarks
            }
            
            self._set_column_widths(worksheet, column_widths)
            
            # Add instructions
            self._add_instructions_sheet(workbook)
        
        output.seek(0)
        return output
    
    def _add_instructions_sheet(self, workbook):
        """Add instructions sheet"""
        instructions_ws = workbook.create_sheet(title="INSTRUCTIONS")
        
        instructions = [
            [f"📘 {self.subject_name} MARK SHEET TEMPLATE"],
            [""],
            ["HOW TO USE:"],
            [f"1. Fill {self.subject_name} marks in column G ONLY"],
            ["2. DO NOT EDIT columns A-F (student information)"],
            ["3. Use numbers only (0-100)"],
            ["4. Leave blank if student absent"],
            ["5. Add remarks in column H if needed"],
            [""],
            ["SAVE AND UPLOAD:"],
            ["1. Save the filled file"],
            ["2. Upload to /api/extract/single-subject"],
            [f"3. System will process {self.subject_name} marks"]
        ]
        
        for row_idx, instruction in enumerate(instructions, start=1):
            cell = instructions_ws.cell(row=row_idx, column=1, value=instruction[0])
            if row_idx == 1:
                cell.font = Font(bold=True, size=14, color="366092")
    
    def get_info(self):
        """Get template information"""
        return {
            'type': 'single_subject',
            'subject': self.subject_name,
            'class': self.class_name,
            'stream': self.stream,
            'columns': ['admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream', self.subject_name, 'remarks'],
            'filename': f"{self.subject_name}_Marksheet_{self.class_name}.xlsx"
        }