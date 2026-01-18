# services/extractors/base_extractor.py
"""
BASE EXTRACTOR - Abstract class for all data extractors
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd

class BaseExtractor(ABC):
    """Abstract base class for all data extractors"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_data: List[Dict] = []
        self.metadata: Dict = {}
        self.errors: List[str] = []
    
    @abstractmethod
    def extract(self) -> Dict:
        """
        Extract data from file - must be implemented by subclasses
        
        Returns:
            Dict containing extracted data
        """
        pass
    
    def clean_column_name(self, column_name: Any) -> str:
        """
        Clean and normalize column names
        
        Args:
            column_name: Original column name
            
        Returns:
            Cleaned column name
        """
        if not isinstance(column_name, str):
            column_name = str(column_name)
        
        # Clean the name
        cleaned = column_name.strip()
        
        # Remove "Unnamed: " prefixes
        if cleaned.startswith('Unnamed:'):
            return 'extra_column'
        
        # Convert to lowercase and normalize
        cleaned = (
            cleaned.lower()
            .replace(' ', '_')
            .replace('-', '_')
            .replace('.', '_')
            .replace('(', '')
            .replace(')', '')
        )
        
        # Remove multiple underscores
        cleaned = '_'.join([part for part in cleaned.split('_') if part])
        
        return cleaned
    
    def safe_string(self, value: Any) -> str:
        """Safely convert value to string"""
        if pd.isna(value):
            return ''
        return str(value).strip()
    
    def safe_float(self, value: Any) -> float:
        """Safely convert value to float"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def add_error(self, error: str):
        """Add extraction error"""
        self.errors.append(error)
    
    def get_extraction_summary(self) -> Dict:
        """Get extraction summary"""
        return {
            'success': len(self.errors) == 0,
            'errors': self.errors,
            'records_extracted': len(self.raw_data),
            'metadata': self.metadata
        }