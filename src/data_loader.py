"""
Data loading utilities for solar radiation datasets.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional, List


class SolarDataLoader:
    """Load and validate solar radiation measurement data."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def load_csv(self, filename: str, parse_dates: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load CSV file into DataFrame.
        
        Args:
            filename: Name of CSV file
            parse_dates: List of columns to parse as dates
            
        Returns:
            DataFrame with loaded data
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8', skiprows=[1])
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1', skiprows=[1])
        
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        print(f"Loaded {len(df)} records from {filename}")
        
        return df
    
    def load_country_data(self, country: str) -> pd.DataFrame:
        """
        Load data for specific country.
        
        Args:
            country: Country name (e.g., 'benin', 'sierra-leone', 'togo')
            
        Returns:
            DataFrame with country data
        """
        filename = f"{country.lower()}-malanville.csv"
        return self.load_csv(filename)
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame contains required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all required columns present
        """
        required_columns = [
            'Timestamp', 'GHI', 'DNI', 'DHI', 'ModA', 'ModB',
            'Tamb', 'RH', 'WS', 'WSgust', 'WSstdev',
            'WD', 'WDstdev', 'BP', 'Cleaning', 'Precipitation',
            'TModA', 'TModB'
        ]
        
        missing = set(required_columns) - set(df.columns)
        
        if missing:
            print(f"Warning: Missing columns: {missing}")
            return False
        
        return True
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Get basic information about dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with dataset information
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'date_range': (df['Timestamp'].min(), df['Timestamp'].max()) if 'Timestamp' in df.columns else None,
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
