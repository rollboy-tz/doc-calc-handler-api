"""
Student Reports Module Initialization
"""

# Export main classes
from .generator import (
    StudentReportGenerator,
    ACSEEReportGenerator,
    CSEEReportGenerator,
    PLSEReportGenerator,
    GenericReportGenerator
)

from .validator import StudentReportValidator
from .templates import StudentReportTemplates

__version__ = "1.0.0"
__author__ = "EduManager Pro"
__all__ = [
    'StudentReportGenerator',
    'ACSEEReportGenerator',
    'CSEEReportGenerator',
    'PLSEReportGenerator',
    'GenericReportGenerator',
    'StudentReportValidator',
    'StudentReportTemplates'
]