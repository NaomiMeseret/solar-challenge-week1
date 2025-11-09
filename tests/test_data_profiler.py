"""
Unit tests for data_profiler module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_profiler import DataProfiler


class TestDataProfiler:
    """Test suite for DataProfiler class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        np.random.seed(42)
        self.df = pd.DataFrame({
            'GHI': np.random.rand(1000) * 1000,
            'DNI': np.random.rand(1000) * 900,
            'Tamb': np.random.rand(1000) * 35 + 15,
            'RH': np.random.rand(1000) * 100,
            'WS': np.random.rand(1000) * 10
        })
        self.profiler = DataProfiler(self.df)
    
    def test_initialization(self):
        """Test profiler initialization."""
        assert len(self.profiler.df) == 1000
        assert len(self.profiler.numeric_cols) == 5
    
    def test_summary_statistics(self):
        """Test summary statistics generation."""
        summary = self.profiler.generate_summary_statistics()
        assert 'mean' in summary.index
        assert 'std' in summary.index
        assert 'median' in summary.index
        assert 'skewness' in summary.index
        assert summary.shape[1] == 5
    
    def test_missing_value_report_no_missing(self):
        """Test missing value report with complete data."""
        report = self.profiler.missing_value_report()
        assert len(report) == 0
    
    def test_missing_value_report_with_missing(self):
        """Test missing value report with missing data."""
        df_missing = self.df.copy()
        df_missing.loc[0:50, 'GHI'] = np.nan
        profiler = DataProfiler(df_missing)
        report = profiler.missing_value_report()
        assert len(report) > 0
        assert report.iloc[0]['column'] == 'GHI'
    
    def test_outlier_detection_zscore(self):
        """Test Z-score outlier detection."""
        df_outliers = self.df.copy()
        df_outliers.loc[0, 'GHI'] = 5000
        profiler = DataProfiler(df_outliers)
        outliers = profiler.detect_outliers_zscore(['GHI'], threshold=3.0)
        assert 'GHI' in outliers
        assert outliers['GHI']['count'] > 0
    
    def test_outlier_detection_iqr(self):
        """Test IQR outlier detection."""
        outliers = self.profiler.detect_outliers_iqr(['GHI', 'DNI'])
        assert isinstance(outliers, dict)
    
    def test_data_quality_score(self):
        """Test data quality scoring."""
        quality = self.profiler.data_quality_score()
        assert 'completeness' in quality
        assert 'validity' in quality
        assert 'uniqueness' in quality
        assert 'overall_quality' in quality
        assert quality['completeness'] == 100.0
    
    def test_generate_profile_report(self):
        """Test complete profile report generation."""
        report = self.profiler.generate_profile_report()
        assert 'summary_statistics' in report
        assert 'missing_values' in report
        assert 'outliers_zscore' in report
        assert 'quality_score' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
