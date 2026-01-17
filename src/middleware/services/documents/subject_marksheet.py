# services/documents/subject_marksheet.py
"""
SUBJECT MARKSHEET TEMPLATE
For subject teachers to fill marks for ONE subject only
"""
import pandas as pd
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
from .base_document import BaseDocument

class SubjectMarkSheet(BaseDocument):
    """
    Single Subject Mark Sheet for subject teachers
    
    Features:
    - Student names pre-filled
    - ONE subject column only
    - Teacher fills marks for their subject only
    - Can be used by multiple teachers for same class
    """
    
    def __init__(self, student_list, subject_info=None, **kwargs):
        """
        Initialize subject mark sheet
        
        Args:
            student_list: List of students
            subject_info: Dictionary with subject details
            **kwargs: Additional parameters
        """
        super().__init__(student_list, document_type='subject_marksheet', **kwargs)
        
        self.subject_info = subject_info or {}
        self.subject_name = subject_info.get('name', 'Mathematics')
        self.subject_code = subject_info.get('code', 'MATH')
        self.max_score = subject_info.get('max_score', 100)
        
        # Set metadata
        self.metadata.update({
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'max_score': self.max_score,
            'teacher_name': subject_info.get('teacher', ''),
            'student_count': len(student_list) if student_list else 0
        })
    
    def generate(self):
        """Generate the subject mark sheet template"""
        # Prepare student data
        students_df = self._prepare_student_data()
        
        # Add subject column
        students_df[self.subject_name] = ''  # Empty for teacher to fill
        
        # Add additional columns if needed
        students_df['Remarks'] = ''  # For teacher comments
        
        self.processed_data = students_df
        return self
    
    def _prepare_student_data(self):
        """Prepare student data for template"""
        students = self.raw_data
        
        if not students:
            # Create sample data for testing
            students = [
                {'admission_no': 'ADM001', 'student_id': 'STU001', 'full_name': 'SAMPLE STUDENT 1', 'class': 'Form 4', 'stream': 'East'},
                {'admission_no': 'ADM002', 'student_id': 'STU002', 'full_name': 'SAMPLE STUDENT 2', 'class': 'Form 4', 'stream': 'East'}
            ]
        
        # Create DataFrame with required columns
        df = pd.DataFrame(students)
        
        # Ensure required columns exist
        required_columns = ['admission_no', 'student_id', 'full_name', 'class', 'stream']
        
        for col in required_columns:
            if col not in df.columns:
                if col in ['class', 'stream']:
                    df[col] = 'NOT SET'
                else:
                    df[col] = f'{col.upper()}_MISSING'
        
        # Reorder columns
        column_order = required_columns
        df = df[column_order]
        
        return df
    
    def to_excel_bytes(self):
        """Generate Excel template as bytes"""
        if self.processed_data is None:
            self.generate()
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheet
            self.processed_data.to_excel(
                writer, 
                sheet_name=f'{self.subject_code} MARKS', 
                index=False
            )
            
            workbook = writer.book
            worksheet = writer.sheets[f'{self.subject_code} MARKS']
            
            # Apply formatting
            self._apply_excel_formatting(workbook, worksheet)
            
            # Add instructions sheet
            self._add_instructions_sheet(workbook)
        
        output.seek(0)
        return output
    
    def _apply_excel_formatting(self, workbook, worksheet):
        """Apply formatting to Excel worksheet"""
        # Header styling
        header_fill = PatternFill(
            start_color="4F81BD",  # Subject-specific color
            end_color="4F81BD",
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
        
        # Subject column styling (editable)
        subject_fill = PatternFill(
            start_color="E6F3FF",  # Light blue for subject
            end_color="E6F3FF",
            fill_type="solid"
        )
        
        # Remarks column styling
        remarks_fill = PatternFill(
            start_color="FFF2CC",  # Light yellow
            end_color="FFF2CC",
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
                
                # Data rows
                elif cell.row > 1:
                    col_letter = get_column_letter(cell.column)
                    
                    # Student info columns (A-E) - read-only
                    if cell.column <= 5:  # Columns A-E (student info)
                        cell.fill = info_fill
                        cell.font = Font(color="000000", size=10)
                    
                    # Subject column (F) - editable marks
                    elif cell.column == 6:  # Column F (subject marks)
                        cell.fill = subject_fill
                        cell.font = Font(color="000000", size=10, bold=True)
                        cell.alignment = Alignment(horizontal="center")
                        cell.number_format = '0'  # Integer format
                    
                    # Remarks column (G) - editable comments
                    elif cell.column == 7:  # Column G (remarks)
                        cell.fill = remarks_fill
                        cell.font = Font(color="000000", size=9, italic=True)
        
        # Set column widths
        column_widths = {
            'A': 12,  # Admission No
            'B': 10,  # Student ID
            'C': 25,  # Full Name
            'D': 8,   # Class
            'E': 8,   # Stream
            'F': 15,  # Subject Marks
            'G': 30   # Remarks
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
        
        # Add subject title
        worksheet.insert_rows(1)
        worksheet.merge_cells('A1:G1')
        title_cell = worksheet['A1']
        title_cell.value = f"{self.subject_name.upper()} - MARK SHEET"
        title_cell.font = Font(bold=True, size=14, color="4F81BD")
        title_cell.alignment = Alignment(horizontal="center")
        title_cell.fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
    
    def _add_instructions_sheet(self, workbook):
        """Add instructions sheet for subject teacher"""
        instructions_ws = workbook.create_sheet(title="INSTRUCTIONS")
        
        instructions = [
            [f"📘 {self.subject_name.upper()} MARK SHEET INSTRUCTIONS"],
            [""],
            ["TEACHER INFORMATION:"],
            [f"Subject: {self.subject_name}"],
            [f"Subject Code: {self.subject_code}"],
            [f"Maximum Score: {self.max_score}"],
            [f"Teacher: {self.subject_info.get('teacher', '[Your Name]')}"],
            [""],
            ["📝 HOW TO FILL:"],
            ["1. DO NOT EDIT OR DELETE:"],
            ["   - Admission Number (Column A)"],
            ["   - Student ID (Column B)"],
            ["   - Student Name (Column C)"],
            ["   - Class & Stream (Columns D & E)"],
            [""],
            ["2. ENTER IN SUBJECT COLUMN ONLY (Column F):"],
            [f"   - {self.subject_name} marks only"],
            [f"   - Range: 0 to {self.max_score}"],
            ["   - Leave blank if absent"],
            ["   - Use whole numbers only"],
            [""],
            ["3. OPTIONAL: Add remarks (Column G):"],
            ["   - 'Absent' if student missed exam"],
            ["   - 'Incomplete' if part of exam missed"],
            ["   - Any relevant comments"],
            [""],
            ["4. FOR CLASS TEACHER:"],
            ["   - This sheet is for ONE SUBJECT only"],
            ["   - Other teachers will fill their own sheets"],
            ["   - Class teacher will combine all sheets"],
            [""],
            ["5. SAVE AND SUBMIT:"],
            [f"   - Filename: {self._generate_filename()}"],
            ["   - Submit to class teacher"],
            ["   - Deadline: [Enter deadline date]"],
            [""],
            ["⚠️ IMPORTANT:"],
            ["- Do not add extra columns"],
            ["- Do not change column order"],
            ["- Submit only this subject's marks"],
            [""],
            ["📞 Contact: [Class Teacher/Administrator]"]
        ]
        
        # Write instructions
        for row_idx, instruction in enumerate(instructions, start=1):
            for col_idx, text in enumerate(instruction, start=1):
                cell = instructions_ws.cell(row=row_idx, column=col_idx, value=text)
                
                # Style based on content
                if row_idx == 1:  # Title
                    cell.font = Font(bold=True, color="4F81BD", size=16)
                    cell.alignment = Alignment(horizontal="center")
                elif any(keyword in str(text) for keyword in ["TEACHER", "HOW TO", "OPTIONAL", "FOR CLASS", "SAVE", "IMPORTANT"]):
                    cell.font = Font(bold=True, color="000000", size=11)
                elif "⚠️" in str(text):
                    cell.font = Font(bold=True, color="FF0000", size=12)
        
        # Adjust column width
        instructions_ws.column_dimensions['A'].width = 60
        
        # Add teacher signature area
        sig_row = len(instructions) + 3
        instructions_ws.cell(row=sig_row, column=1, value="Teacher's Signature: ________________________")
        instructions_ws.cell(row=sig_row, column=1).font = Font(italic=True)
        
        instructions_ws.cell(row=sig_row+1, column=1, value="Date: ________________________")
        instructions_ws.cell(row=sig_row+1, column=1).font = Font(italic=True)
    
    def _generate_filename(self):
        """Generate filename for subject mark sheet"""
        class_name = self.subject_info.get('class_name', 'Class').replace(' ', '_')
        stream = self.subject_info.get('stream', '')
        subject_code = self.subject_code
        term = self.subject_info.get('term', 'Term1')
        
        if stream:
            return f"MarkSheet_{subject_code}_{class_name}_{stream}_{term}.xlsx"
        else:
            return f"MarkSheet_{subject_code}_{class_name}_{term}.xlsx"
    
    def get_binary(self):
        """Get document as binary stream"""
        return self.to_excel_bytes()
    
    def get_template_summary(self):
        """Get summary of template"""
        return {
            'subject': self.subject_name,
            'filename': self._generate_filename(),
            'student_count': len(self.processed_data) if self.processed_data is not None else 0,
            'columns': ['Admission No', 'Student ID', 'Name', 'Class', 'Stream', f'{self.subject_name} Marks', 'Remarks'],
            'max_score': self.max_score,
            'instructions': f'Fill {self.subject_name} marks in column F only. Do not edit student information.'
        }