"""
services/pdf_reports/report_factory.py
Simple Report Factory
"""
import logging

logger = logging.getLogger(__name__)

class ReportFactory:
    """Factory to create report generators"""
    
    @staticmethod
    def create(report_type, system_config=None):
        """
        Create report generator
        
        Args:
            report_type: 'student_report' or 'class_sheet'
            system_config: System configuration for footer
        
        Returns:
            Report generator instance
        """
        if report_type == 'student_report':
            from .student_report import StudentReport
            return StudentReport(system_config)
        
        elif report_type == 'class_sheet':
            from .class_sheet import ClassSheet
            return ClassSheet(system_config)
        
        else:
            logger.error(f"Unknown report type: {report_type}")
            raise ValueError(f"Report type must be 'student_report' or 'class_sheet', got: {report_type}")