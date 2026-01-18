# services/generators/marksheet_generator.py
"""
FULL MARK SHEET TEMPLATE GENERATOR
For all subjects in one sheet
"""
import pandas as pd
from io import BytesIO
from .base_generator import BaseGenerator

class MarksheetGenerator(BaseGenerator):
    """Generate full marksheet template for all subjects"""
    
    def __init__(self, class_name="FORM 4", stream="", subjects=None):
        self.class_name = class_name
        self.stream = stream
        self.subjects = subjects or [
            "MATHEMATICS", "ENGLISH", "KISWAHILI",
            "PHYSICS", "CHEMISTRY", "BIOLOGY",
            "GEOGRAPHY", "HISTORY", "CIVICS", "COMMERCE"
        ]
    
    def generate(self, student_count=10):
        """Generate Excel template"""
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
        
        # Add empty subject columns
        for subject in self.subjects:
            df[subject] = ''
        
        # Add remarks column
        df['remarks'] = ''
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = f"{self.class_name}_{self.stream}" if self.stream else self.class_name
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Apply formatting
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Basic formatting
            self._apply_basic_formatting(worksheet)
            
            # Set column widths
            column_widths = {
                'A': 15,  # admission_no
                'B': 12,  # student_id
                'C': 25,  # full_name
                'D': 10,  # gender
                'E': 10,  # class
                'F': 10,  # stream
            }
            
            # Subject columns (12 width each)
            for i in range(len(self.subjects)):
                col_letter = get_column_letter(7 + i)  # Start from column G
                column_widths[col_letter] = 12
            
            # Remarks column
            remarks_col = get_column_letter(7 + len(self.subjects))
            column_widths[remarks_col] = 25
            
            self._set_column_widths(worksheet, column_widths)
            
            # Add instructions sheet
            self._add_instructions_sheet(workbook)
        
        output.seek(0)
        return output
    
    def _add_instructions_sheet(self, workbook):
        """Add instructions sheet"""
        instructions_ws = workbook.create_sheet(title="INSTRUCTIONS")
        
        instructions = [
            ["📘 FULL MARK SHEET TEMPLATE"],
            [""],
            ["HOW TO USE:"],
            ["1. DO NOT EDIT columns A-F (student information)"],
            ["2. Fill marks in subject columns (G onwards)"],
            ["3. Use numbers only (0-100)"],
            ["4. Leave blank if student absent"],
            ["5. Add remarks in last column if needed"],
            [""],
            ["SAVE AND UPLOAD:"],
            ["1. Save the filled file"],
            ["2. Upload to /api/extract/multi-subject"],
            ["3. System will extract and process data"]
        ]
        
        for row_idx, instruction in enumerate(instructions, start=1):
            cell = instructions_ws.cell(row=row_idx, column=1, value=instruction[0])
            if row_idx == 1:
                cell.font = Font(bold=True, size=14, color="366092")
    
    def get_info(self):
        """Get template information"""
        return {
            'type': 'full_marksheet',
            'class': self.class_name,
            'stream': self.stream,
            'subjects': self.subjects,
            'student_columns': ['admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream'],
            'total_columns': 6 + len(self.subjects) + 1,
            'filename': f"Marksheet_{self.class_name}_{self.stream}.xlsx" if self.stream else f"Marksheet_{self.class_name}.xlsx"
        }