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
        UTF-8 first, then falling back to Latin-1. It will try both with and
        without skipping the second row (which sometimes contains units) to be
        robust across different file formats.
        
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
        
        # Attempt multiple read strategies for robustness
        last_exception = None
        for skip in (None, [1]):
            for enc in ('utf-8', 'latin-1'):
                try:
                    df = pd.read_csv(filepath, encoding=enc, skiprows=skip)
                    # Try to identify a timestamp-like column (case-insensitive)
                    ts_col = None
                    for col in df.columns:
                        if isinstance(col, str) and col.strip().lower() == 'timestamp':
                            ts_col = col
                            break
                    if ts_col is not None:
                        df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
                        if ts_col != 'Timestamp':
                            df.rename(columns={ts_col: 'Timestamp'}, inplace=True)
                    print(f"Loaded {len(df)} records from {filename}")
                    return df
                except Exception as e:
                    last_exception = e
                    continue

        # If all strategies failed, raise the last exception
        raise last_exception if last_exception else RuntimeError("Failed to read CSV with all strategies")
    
    def load_country_data(self, country: str) -> pd.DataFrame:
        """
        Load data for a specific country by discovering the appropriate CSV file.
        
        This method searches the data directory for a raw CSV whose filename
        contains the country name (case-insensitive), ignoring spaces, hyphens,
        and underscores. Cleaned files are excluded (filenames containing
        'clean'). If exactly one candidate is found, it is loaded. If multiple
        candidates are found, the first one sorted by name is used.
        
        Args:
            country: Country name (e.g., 'benin', 'sierra leone', 'togo')
            
        Returns:
            DataFrame with country data including all measurement columns
            
        Raises:
            FileNotFoundError: If no matching raw CSV is found in the data directory
        """
        norm = lambda s: ''.join(ch for ch in s.lower() if ch.isalnum())
        target = norm(country)

        candidates = []
        for fname in os.listdir(self.data_dir):
            fl = fname.lower()
            if not fl.endswith('.csv'):
                continue
            if 'clean' in fl:
                # Skip already-cleaned outputs
                continue
            if target in norm(fl):
                candidates.append(fname)

        if not candidates:
            raise FileNotFoundError(
                f"No raw CSV found for country '{country}' in {self.data_dir}. "
                f"Please place the raw CSV in the data directory."
            )

        # Deterministic selection if multiple candidates
        candidates.sort()
        filename = candidates[0]
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
