"""
Templates for student reports
"""
from typing import Dict, Any, List, Tuple
from ..base.constants import PDFConstants

class StudentReportTemplates:
    """Templates for student report sections"""
    
    @staticmethod
    def get_system_label(system_rule: str) -> str:
        """Get system label based on rule"""
        labels = {
            'acsee': "Advanced Certificate of Secondary Education",
            'csee': "Certificate of Secondary Education",
            'plse': "Primary School Leaving Examination",
            'generic': "Academic Performance Report"
        }
        return labels.get(system_rule.lower(), "Academic Report")
    
    @staticmethod
    def get_subject_headers(system_rule: str) -> Tuple[List[str], List[int]]:
        """Get table headers and column widths based on system"""
        if system_rule == 'acsee':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS"]
            widths = [12, 85, 30, 30, 30]
        elif system_rule == 'csee':
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "POINTS"]
            widths = [12, 85, 30, 30, 30]
        elif system_rule == 'plse':
            headers = ["#", "SOMO", "ALAMA", "DARAJA", "STATUS"]
            widths = [12, 85, 30, 30, 40]
        else:
            headers = ["NO.", "SUBJECT", "MARKS", "GRADE", "STATUS"]
            widths = [12, 85, 30, 30, 40]
        
        return headers, widths
    
    @staticmethod
    def format_student_info(student: Dict[str, Any]) -> str:
        """Format student information"""
        lines = []
        
        if 'name' in student:
            lines.append(f"Jina: {student['name']}")
        if 'admission' in student:
            lines.append(f"Nambari ya Ukumbusho: {student['admission']}")
        if 'gender' in student:
            gender_map = {'M': 'Mwanaume', 'F': 'Mwanamke', 'male': 'Mwanaume', 'female': 'Mwanamke'}
            gender = gender_map.get(student['gender'].lower(), student['gender'])
            lines.append(f"Jinsia: {gender}")
        if 'class' in student:
            lines.append(f"Darasa: {student['class']}")
        if 'year' in student:
            lines.append(f"Mwaka: {student['year']}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_summary_data(summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format summary data for display"""
        formatted = summary.copy()
        
        # Format percentage
        if 'average' in formatted:
            formatted['average_display'] = f"{formatted['average']:.1f}%"
        
        # Format total marks
        if 'total' in formatted:
            formatted['total_display'] = f"{formatted['total']:.0f}"
        
        # Ensure status
        if 'status' not in formatted:
            formatted['status'] = 'PASS'
        
        return formatted
    
    @staticmethod
    def get_grade_color(grade: str) -> tuple:
        """Get color for grade based on value"""
        grade = str(grade).upper()
        
        if grade in ["A", "B", "C", "I", "II", "III", "PASS"]:
            return PDFConstants.SUCCESS_COLOR
        elif grade in ["D", "E", "F", "FAIL", "ABS"]:
            return PDFConstants.DANGER_COLOR
        else:
            return (0, 0, 0)  # Black
    
    @staticmethod
    def translate_subject_name(subject: str) -> str:
        """Translate subject names to Swahili"""
        translations = {
            'english': 'Kiingereza',
            'kiswahili': 'Kiswahili',
            'mathematics': 'Hisabati',
            'science': 'Sayansi',
            'social studies': 'Maarifa ya Jamii',
            'civics': 'Uraia',
            'history': 'Historia',
            'geography': 'Jiografia',
            'physics': 'Fizikia',
            'chemistry': 'Kemia',
            'biology': 'Biolojia',
            'religious education': 'Elimu ya Dini',
            'vocational skills': 'Stadi za Kazi'
        }
        
        subject_lower = subject.lower()
        return translations.get(subject_lower, subject.title())