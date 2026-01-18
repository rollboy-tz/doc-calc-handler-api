# services/validators/base_validator.py
"""
BASE VALIDATOR - Abstract class for all validators
"""
from abc import ABC, abstractmethod
from typing import Dict, List
import os

class BaseValidator(ABC):
    """Abstract base class for all validators"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.is_valid: bool = False
        
    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """Validate the input - must be implemented by subclasses"""
        pass
    
    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
    
    def clear_errors(self):
        """Clear all errors"""
        self.errors.clear()