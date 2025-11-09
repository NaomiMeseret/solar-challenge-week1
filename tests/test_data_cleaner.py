"""
Unit tests for data_cleaner module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_cleaner import DataCleaner


class TestDataCleaner:
    """Test suite for DataCleaner class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        np.random.seed(42)
        self.df = pd.DataFrame({
            'GHI': np.random.rand(100) * 1000,
            'DNI': np.random.rand(100) * 900,
            'Tamb': np.random.rand(100) * 35,
            'RH': np.random.rand(100) * 100
        })
        self.cleaner = DataCleaner(self.df)
    
    def test_initialization(self):
        """Test cleaner initialization."""
        assert len(self.cleaner.df) == 100
        assert len(self.cleaner.cleaning_log) == 0
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df_dups = pd.DataFrame({
            'A': [1, 1, 2, 3],
            'B': [4, 4, 5, 6]
        })
        cleaner = DataCleaner(df_dups)
        result = cleaner.remove_duplicates()
        assert len(result) == 3
    
    def test_handle_missing_values_median(self):
        """Test missing value handling with median strategy."""
        df_missing = self.df.copy()
        df_missing.loc[0:10, 'GHI'] = np.nan
        cleaner = DataCleaner(df_missing)
        result = cleaner.handle_missing_values(strategy='median')
        assert result['GHI'].isnull().sum() == 0
    
    def test_handle_missing_values_drop(self):
        """Test missing value handling with drop strategy."""
        df_missing = self.df.copy()
        df_missing.loc[0:5, 'GHI'] = np.nan
        cleaner = DataCleaner(df_missing)
        result = cleaner.handle_missing_values(strategy='drop')
        assert len(result) == 94
    
    def test_validate_irradiance_values(self):
        """Test irradiance validation."""
        df_negative = self.df.copy()
        df_negative.loc[0:5, 'GHI'] = -100
        cleaner = DataCleaner(df_negative)
        result = cleaner.validate_irradiance_values()
        assert (result['GHI'] >= 0).all()
    
    def test_cap_outliers_iqr(self):
        """Test outlier capping."""
        df_outliers = self.df.copy()
        df_outliers.loc[0, 'GHI'] = 10000
        cleaner = DataCleaner(df_outliers)
        result = cleaner.cap_outliers_iqr(['GHI'])
        assert result['GHI'].max() < 10000
    
    def test_get_cleaning_report(self):
        """Test cleaning report generation."""
        self.cleaner.remove_duplicates()
        report = self.cleaner.get_cleaning_report()
        assert isinstance(report, pd.DataFrame)
        assert 'action' in report.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
