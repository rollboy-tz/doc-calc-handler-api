"""
report_factory.py - ADD LOGGER
"""
import logging  # ✨ ADD THIS LINE

# ✨ DEFINE LOGGER
logger = logging.getLogger(__name__)

class ReportFactory:
    """Factory to create report generators"""
    
    @staticmethod
    def create(report_type, system_config=None):
        """
        Create report generator
        """
        if report_type == 'student_report':
            from .student_report import StudentReport
            return StudentReport(system_config)
        
        elif report_type == 'class_sheet':
            from .class_sheet import ClassSheet
            return ClassSheet(system_config)
        
        else:
            logger.error(f"Unknown report type: {report_type}")  # ✨ NOW LOGGER IS DEFINED
            raise ValueError(f"Unknown report type: {report_type}")