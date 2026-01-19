"""
PDF Package - FIXED VERSION
"""
from .student_report import StudentReportGenerator
from .class_report import ClassReportGenerator

# Export the CLASSES, not instances
__all__ = ['StudentReportGenerator', 'ClassReportGenerator']

# DO NOT create instances here
# Just export the classes