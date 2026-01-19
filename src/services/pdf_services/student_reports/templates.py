"""
Templates for student reports
"""
from ..base.constants import PDFConstants

class StudentReportTemplates:
    """Templates for student report sections"""
    
    @staticmethod
    def student_info(student: dict) -> str:
        """Generate student info text"""
        return f"""
Name: {student.get('name', 'N/A')}
Admission: {student.get('admission', 'N/A')}
Gender: {student.get('gender', 'N/A')}
Class: {student.get('class', 'N/A')}
Year: {student.get('year', 'N/A')}
        """.strip()
    
    @staticmethod
    def summary_table(summary: dict) -> list:
        """Generate summary table data"""
        return [
            ["Total Marks", f"{summary.get('total', 0)}"],
            ["Average Score", f"{summary.get('average', 0):.2f}%"],
            ["Grade", summary.get('grade', 'N/A')],
            ["Position", summary.get('position', 'N/A')],
            ["Division", summary.get('division', 'N/A')],
            ["Remarks", summary.get('remark', 'N/A')]
        ]
    
    @staticmethod
    def subjects_table(subjects: list) -> tuple:
        """Generate subjects table data and column widths"""
        headers = ["No.", "Subject", "Score", "Grade", "Remarks"]
        data = []
        
        for i, subject in enumerate(subjects, 1):
            data.append([
                str(i),
                subject.get('name', 'N/A'),
                str(subject.get('score', 0)),
                subject.get('grade', 'N/A'),
                subject.get('remarks', '')[:20]  # Limit remarks length
            ])
        
        col_widths = [10, 70, 30, 30, 50]
        return headers, data, col_widths