"""
Unit tests for data_loader module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import SolarDataLoader


class TestSolarDataLoader:
    """Test suite for SolarDataLoader class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.loader = SolarDataLoader(data_dir="data")
    
    def test_initialization(self):
        """Test loader initialization."""
        assert self.loader.data_dir == Path("data")
        assert self.loader.data_dir.exists()
    
    def test_validate_columns_complete(self):
        """Test validation with all required columns."""
        required_cols = [
            'Timestamp', 'GHI', 'DNI', 'DHI', 'ModA', 'ModB',
            'Tamb', 'RH', 'WS', 'WSgust', 'WSstdev',
            'WD', 'WDstdev', 'BP', 'Cleaning', 'Precipitation',
            'TModA', 'TModB'
        ]
        df = pd.DataFrame(columns=required_cols)
        assert self.loader.validate_columns(df) == True
    
    def test_validate_columns_incomplete(self):
        """Test validation with missing columns."""
        df = pd.DataFrame(columns=['Timestamp', 'GHI'])
        assert self.loader.validate_columns(df) == False
    
    def test_get_data_info(self):
        """Test data info extraction."""
        df = pd.DataFrame({
            'Timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'GHI': np.random.rand(100) * 1000,
            'Tamb': np.random.rand(100) * 30
        })
        
        info = self.loader.get_data_info(df)
        
        assert info['rows'] == 100
        assert info['columns'] == 3
        assert 'memory_usage_mb' in info
        assert info['date_range'] is not None
        assert len(info['numeric_columns']) == 2


class TestDataValidation:
    """Test data validation functions."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        loader = SolarDataLoader()
        df = pd.DataFrame()
        info = loader.get_data_info(df)
        assert info['rows'] == 0
        assert info['columns'] == 0
    
    def test_numeric_column_detection(self):
        """Test numeric column identification."""
        loader = SolarDataLoader()
        df = pd.DataFrame({
            'numeric1': [1, 2, 3],
            'numeric2': [1.1, 2.2, 3.3],
            'text': ['a', 'b', 'c']
        })
        info = loader.get_data_info(df)
        assert len(info['numeric_columns']) == 2
        assert len(info['categorical_columns']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
