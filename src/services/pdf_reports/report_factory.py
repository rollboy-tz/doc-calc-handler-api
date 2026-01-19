"""
Report Factory - Simple and Clean
"""
from .student_report import StudentReport
from .class_sheet import ClassSheet
import logging

logger = logging.getLogger(__name__)

class ReportFactory:
    """Factory to create reports"""
    
    @staticmethod
    def create(report_type, system_config=None):
        """
        Create report generator
        
        Args:
            report_type: 'student_report' or 'class_sheet'
            system_config: System metadata for footer
        
        Returns:
            Report generator instance
        """
        reports = {
            'student_report': StudentReport,
            'class_sheet': ClassSheet,
        }
        
        if report_type not in reports:
            logger.error(f"Unknown report type: {report_type}")
            raise ValueError(f"Report type must be: {list(reports.keys())}")
        
        return reports[report_type](system_config)