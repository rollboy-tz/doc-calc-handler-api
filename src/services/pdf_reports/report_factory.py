"""
report_factory.py - UPGRADED VERSION
Same factory pattern, better error handling
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ReportFactory:
    """Factory to create enhanced report generators"""
    
    @staticmethod
    def create(report_type: str, system_config: Optional[dict] = None):
        """
        Create enhanced report generator
        
        Args:
            report_type: 'student_report' or 'class_sheet'
            system_config: Optional system configuration
        
        Returns:
            Report generator instance
        
        Raises:
            ValueError: If report_type is invalid
        """
        try:
            if report_type == 'student_report':
                from .student_report import StudentReport
                logger.debug(f"Creating StudentReport instance")
                return StudentReport(system_config)
            
            elif report_type == 'class_sheet':
                from .class_sheet import ClassSheet
                logger.debug(f"Creating ClassSheet instance")
                return ClassSheet(system_config)
            
            else:
                logger.error(f"Unknown report type requested: {report_type}")
                raise ValueError(f"Unsupported report type: {report_type}. "
                               f"Available types: 'student_report', 'class_sheet'")
                
        except ImportError as e:
            logger.critical(f"Module import error: {e}")
            raise
        except Exception as e:
            logger.error(f"Factory creation error: {e}")
            raise
    
    @staticmethod
    def get_available_reports():
        """Get list of available report types"""
        return ['student_report', 'class_sheet']