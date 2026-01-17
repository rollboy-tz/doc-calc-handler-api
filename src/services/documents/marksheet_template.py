# services/documents/marksheet_template.py
"""
MARK SHEET TEMPLATE
For teachers to download, fill marks, and upload
Excel format with student names pre-filled
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
from .base_document import BaseDocument
from datetime import datetime

class MarkSheetTemplate(BaseDocument):
    """
    Mark Sheet Template for teachers
    
    Features:
    - Student names pre-filled from database
    - Empty columns for marks only
    - No formulas, no calculations
    - Clean formatting
    - Instructions sheet
    """
    
    def __init__(self, student_list, class_info=None, **kwargs):
        """
        Initialize mark sheet template
        
        Args:
            student_list: List of students (from database)
            class_info: Dictionary with class details
            **kwargs: Additional parameters
        """
        super().__init__(student_list, document_type='marksheet_template', **kwargs)
        
        self.class_info = class_info or {}
        self.subjects = kwargs.get('subjects', [])
        self.include_instructions = kwargs.get('include_instructions', True)
        
        # Set metadata
        self.metadata.update({
            'class_name': self.class_info.get('name', 'Unknown'),
            'stream': self.class_info.get('stream', ''),
            'term': self.class_info.get('term', 'Term 1'),
            'year': self.class_info.get('year', datetime.now().year),
            'subjects': self.subjects,
            'student_count': len(student_list) if student_list else 0
        })
    
    def generate(self):
        """Generate the mark sheet template"""
        # Prepare student data
        students_df = self._prepare_student_data()
        
        # Add empty columns for subjects
        for subject in self.subjects:
            students_df[subject] = ''  # Empty for teacher to fill
        
        self.processed_data = students_df
        return self
    
    def _prepare_student_data(self):
        """Prepare student data for template"""
        students = self.raw_data
        
        if not students:
            # Create sample data for testing
            students = [
                {'admission_no': 'ADM001', 'student_id': 'STU001', 'full_name': 'SAMPLE STUDENT 1'},
                {'admission_no': 'ADM002', 'student_id': 'STU002', 'full_name': 'SAMPLE STUDENT 2'}
            ]
        
        # Create DataFrame with required columns
        df = pd.DataFrame(students)
        
        # Ensure required columns exist
        required_columns = ['admission_no', 'student_id', 'full_name']
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = f'{col.upper()}_MISSING'
        
        # Reorder columns
        column_order = required_columns + ['class', 'stream'] if 'class' in df.columns else required_columns
        df = df[column_order]
        
        return df
    
    def to_excel_bytes(self):
        """
        Generate Excel template as bytes
        
        Returns:
            BytesIO object with Excel file
        """
        if self.processed_data is None:
            self.generate()
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheet
            self.processed_data.to_excel(
                writer, 
                sheet_name='ENTER MARKS HERE', 
                index=False
            )
            
            workbook = writer.book
            worksheet = writer.sheets['ENTER MARKS HERE']
            
            # Apply formatting
            self._apply_excel_formatting(workbook, worksheet)
            
            # Add instructions sheet if requested
            if self.include_instructions:
                self._add_instructions_sheet(workbook)
        
        output.seek(0)
        return output
    
    def _apply_excel_formatting(self, workbook, worksheet):
        """Apply formatting to Excel worksheet"""
        # Header styling
        header_fill = PatternFill(
            start_color="366092",  # Dark blue
            end_color="366092",
            fill_type="solid"
        )
        header_font = Font(color="FFFFFF", bold=True, size=11)
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Student info columns styling (read-only)
        info_fill = PatternFill(
            start_color="F2F2F2",  # Light gray
            end_color="F2F2F2",
            fill_type="solid"
        )
        
        # Mark columns styling (editable)
        mark_fill = PatternFill(
            start_color="FFFFFF",  # White
            end_color="FFFFFF",
            fill_type="solid"
        )
        
        # Border
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Apply to all cells
        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = thin_border
                
                # Header row
                if cell.row == 1:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = header_alignment
                # Student info columns (A, B, C) - read-only
                elif cell.column <= 3:  # Columns A, B, C
                    cell.fill = info_fill
                    cell.font = Font(color="000000", size=10)
                # Mark columns - editable
                else:
                    cell.fill = mark_fill
                    cell.font = Font(color="000000", size=10)
                    cell.alignment = Alignment(horizontal="center")
        
        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _add_instructions_sheet(self, workbook):
        """Add instructions sheet"""
        instructions_ws = workbook.create_sheet(title="INSTRUCTIONS")
        
        instructions = [
            ["⚠️ IMPORTANT INSTRUCTIONS ⚠️"],
            [""],
            ["1. DO NOT EDIT OR DELETE:"],
            ["   - Admission Number column"],
            ["   - Student ID column"],
            ["   - Student Name column"],
            [""],
            ["2. ENTER MARKS ONLY IN:"],
            ["   - Subject columns (Mathematics, English, etc.)"],
            ["   - Marks range: 0 to 100"],
            ["   - Leave blank if student did not take exam"],
            [""],
            ["3. SAVE THE FILE:"],
            ["   - Use the same filename"],
            ["   - Do not add extra columns"],
            ["   - Do not change column order"],
            [""],
            ["4. UPLOAD BACK TO SYSTEM:"],
            ["   - Upload this file after filling marks"],
            ["   - System will calculate grades automatically"],
            [""],
            ["📞 For help, contact system administrator."]
        ]
        
        # Write instructions
        for row_idx, instruction in enumerate(instructions, start=1):
            for col_idx, text in enumerate(instruction, start=1):
                cell = instructions_ws.cell(row=row_idx, column=col_idx, value=text)
                
                # Style title
                if row_idx == 1:
                    cell.font = Font(bold=True, color="FF0000", size=14)
                    cell.alignment = Alignment(horizontal="center")
        
        # Adjust column width
        instructions_ws.column_dimensions['A'].width = 60
    
    def get_template_info(self):
        """Get template information"""
        return {
            'filename': self._generate_filename(),
            'student_count': len(self.processed_data) if self.processed_data is not None else 0,
            'subjects': self.subjects,
            'instructions': 'Fill marks in subject columns only. Do not edit student information.'
        }
    
    def _generate_filename(self):
        """Generate filename for template"""
        class_name = self.class_info.get('name', 'Class').replace(' ', '_')
        stream = self.class_info.get('stream', '')
        term = self.class_info.get('term', 'Term1')
        year = self.class_info.get('year', datetime.now().year)
        
        if stream:
            return f"MarkSheet_{class_name}_{stream}_{term}_{year}.xlsx"
        else:
            return f"MarkSheet_{class_name}_{term}_{year}.xlsx"
    
    def get_binary(self):
        """Get document as binary stream (for API)"""
        return self.to_excel_bytes()