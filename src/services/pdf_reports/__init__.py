"""
services/pdf_reports/__init__.py
FIXED - Remove circular import
"""
# KABLA (WRONG):
# from .report_routes import report_routes  # ← HAPA NDIO ERROR

# BADA YA KUREKEBISHA (CORRECT):
from .report_factory import ReportFactory
from .utils import SafeImageHandler, ReportMetadata

__all__ = ['ReportFactory', 'SafeImageHandler', 'ReportMetadata']