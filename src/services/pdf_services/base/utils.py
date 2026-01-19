"""
Utility functions
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

def generate_filename(prefix: str, identifier: str, extension: str = "pdf") -> str:
    """Generate a filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_id = identifier.replace(" ", "_").replace("/", "_")
    return f"{prefix}_{safe_id}_{timestamp}.{extension}"

def get_temp_path(filename: str) -> str:
    """Get temporary file path"""
    return os.path.join(tempfile.gettempdir(), filename)

def validate_data(data: Dict[str, Any], required_fields: list) -> tuple:
    """Validate required fields in data"""
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""

def format_percentage(value: float) -> str:
    """Format percentage with 2 decimal places"""
    return f"{value:.2f}%"

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f"TSh {amount:,.0f}"