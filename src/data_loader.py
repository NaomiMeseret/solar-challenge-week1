"""
Data loading utilities for solar radiation datasets.

This module provides the SolarDataLoader class for loading, validating, and
managing solar radiation measurement data from CSV files. It handles common
data quality issues such as encoding problems and missing timestamps.

Typical usage example:
    loader = SolarDataLoader(data_dir='data')
    df = loader.load_country_data('benin')
    if loader.validate_columns(df):
        info = loader.get_data_info(df)
        print(f"Loaded {info['rows']} rows covering {info['date_range']}")

Author: Naomi Meseret
Date: November 2025
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class SolarDataLoader:
    """
    Load and validate solar radiation measurement data.
    
    This class provides methods to load solar radiation data from CSV files,
    validate required columns, and extract basic dataset information. It handles
    encoding issues and standardizes timestamp parsing across different data sources.
    
    Attributes:
        data_dir (Path): Directory path where data files are stored
        
    Example:
        >>> loader = SolarDataLoader(data_dir='data')
        >>> df = loader.load_country_data('benin')
        >>> loader.validate_columns(df)
        True
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data loader with specified data directory.
        
        Creates the data directory if it doesn't exist to ensure smooth operation.
        
        Args:
            data_dir: Directory containing data files (default: 'data')
        """
        self.data_dir = Path(data_dir)
        # Create directory if it doesn't exist (safe operation)
        self.data_dir.mkdir(exist_ok=True)
        
    def load_csv(self, filename: str, parse_dates: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load CSV file into DataFrame with encoding fallback.
        
        This method handles common encoding issues in solar data files by attempting
        UTF-8 first, then falling back to Latin-1. It also skips the second row
        which typically contains units in solar measurement files.
        
        Args:
            filename: Name of CSV file (e.g., 'benin-malanville.csv')
            parse_dates: List of columns to parse as dates (optional)
            
        Returns:
            DataFrame with loaded data and parsed timestamps
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            
        Example:
            >>> loader = SolarDataLoader()
            >>> df = loader.load_csv('benin-malanville.csv')
            Loaded 49196 records from benin-malanville.csv
        """
        filepath = self.data_dir / filename
        
        # Check file existence before attempting to load
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Try UTF-8 encoding first (standard), fallback to Latin-1 for legacy files
        try:
            df = pd.read_csv(filepath, encoding='utf-8', skiprows=[1])  # Skip units row
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1', skiprows=[1])
        
        # Parse Timestamp column if present, coerce errors to NaT
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        print(f"Loaded {len(df)} records from {filename}")
        
        return df
    
    def load_country_data(self, country: str) -> pd.DataFrame:
        """
        Load data for specific country using standardized naming convention.
        
        Constructs filename from country name and loads the corresponding CSV file.
        All country data files follow the pattern: {country}-malanville.csv
        
        Args:
            country: Country name (e.g., 'benin', 'sierra-leone', 'togo')
            
        Returns:
            DataFrame with country data including all measurement columns
            
        Example:
            >>> loader = SolarDataLoader()
            >>> benin_df = loader.load_country_data('benin')
            Loaded 49196 records from benin-malanville.csv
        """
        # Construct filename using standard naming pattern
        filename = f"{country.lower()}-malanville.csv"
        return self.load_csv(filename)
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame contains all required solar measurement columns.
        
        Checks for presence of essential columns needed for solar radiation analysis.
        Prints warning message if any required columns are missing.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all required columns present, False otherwise
            
        Example:
            >>> loader = SolarDataLoader()
            >>> df = loader.load_country_data('benin')
            >>> if not loader.validate_columns(df):
            ...     print("Data validation failed")
        """
        # Define all required columns for complete solar radiation analysis
        required_columns = [
            'Timestamp',      # Time of measurement
            'GHI', 'DNI', 'DHI',  # Solar irradiance components
            'ModA', 'ModB',   # Module sensor readings
            'Tamb',           # Ambient temperature
            'RH',             # Relative humidity
            'WS', 'WSgust', 'WSstdev',  # Wind measurements
            'WD', 'WDstdev',  # Wind direction
            'BP',             # Barometric pressure
            'Cleaning',       # Cleaning event flag
            'Precipitation',  # Rainfall
            'TModA', 'TModB'  # Module temperatures
        ]
        
        # Find any missing columns using set difference
        missing = set(required_columns) - set(df.columns)
        
        if missing:
            print(f"Warning: Missing columns: {missing}")
            return False
        
        return True
    
    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """
        Extract comprehensive metadata about the dataset.
        
        Provides key statistics about dataset structure, size, and column types.
        Useful for initial data exploration and validation.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing:
                - rows: Number of observations
                - columns: Number of variables
                - memory_usage_mb: Memory footprint in megabytes
                - date_range: Tuple of (min_date, max_date) if Timestamp exists
                - numeric_columns: List of numeric column names
                - categorical_columns: List of categorical column names
                
        Example:
            >>> info = loader.get_data_info(df)
            >>> print(f"Dataset spans {info['date_range']}")
            >>> print(f"Memory usage: {info['memory_usage_mb']:.2f} MB")
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            # Calculate memory usage in MB for resource planning
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            # Extract date range if Timestamp column exists
            'date_range': (df['Timestamp'].min(), df['Timestamp'].max()) if 'Timestamp' in df.columns else None,
            # Identify numeric columns for statistical analysis
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            # Identify categorical columns for grouping operations
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
