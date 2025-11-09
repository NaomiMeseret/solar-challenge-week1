"""
Data profiling utilities for comprehensive dataset analysis.

This module provides the DataProfiler class for generating detailed statistical
profiles of solar radiation datasets. It includes methods for summary statistics,
missing value analysis, outlier detection, and data quality scoring.

Typical usage example:
    profiler = DataProfiler(df)
    summary = profiler.generate_summary_statistics()
    missing_report = profiler.missing_value_report()
    outliers = profiler.detect_outliers_zscore()
    quality_score = profiler.calculate_quality_score()

Author: Naomi Meseret
Date: November 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


class DataProfiler:
    """
    Profile and analyze solar radiation datasets with comprehensive statistics.
    
    This class provides methods for data quality assessment including summary
    statistics, missing value analysis, outlier detection using Z-score and IQR
    methods, and overall data quality scoring.
    
    Attributes:
        df (pd.DataFrame): Copy of the dataset being profiled
        numeric_cols (List[str]): List of numeric column names
        
    Example:
        >>> profiler = DataProfiler(df)
        >>> stats = profiler.generate_summary_statistics()
        >>> print(f"Mean GHI: {stats.loc['mean', 'GHI']:.2f}")
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize profiler with dataset to analyze.
        
        Creates a copy of the DataFrame to avoid modifying the original data.
        Automatically identifies numeric columns for statistical analysis.
        
        Args:
            df: DataFrame to profile (will be copied internally)
        """
        # Create copy to avoid modifying original data
        self.df = df.copy()
        # Identify numeric columns for statistical analysis
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
    def generate_summary_statistics(self) -> pd.DataFrame:
        """
        Generate comprehensive summary statistics.
        
        Returns:
            DataFrame with summary statistics
        """
        summary = self.df[self.numeric_cols].describe()
        
        additional_stats = pd.DataFrame({
            'median': self.df[self.numeric_cols].median(),
            'mode': self.df[self.numeric_cols].mode().iloc[0] if len(self.df) > 0 else np.nan,
            'skewness': self.df[self.numeric_cols].skew(),
            'kurtosis': self.df[self.numeric_cols].kurtosis(),
            'variance': self.df[self.numeric_cols].var()
        }).T
        
        summary = pd.concat([summary, additional_stats])
        
        return summary
    
    def missing_value_report(self) -> pd.DataFrame:
        """
        Generate detailed missing value report.
        
        Returns:
            DataFrame with missing value statistics
        """
        missing_count = self.df.isnull().sum()
        missing_percent = (missing_count / len(self.df)) * 100
        
        report = pd.DataFrame({
            'column': self.df.columns,
            'missing_count': missing_count.values,
            'missing_percent': missing_percent.values,
            'dtype': self.df.dtypes.values
        })
        
        report = report[report['missing_count'] > 0].sort_values('missing_percent', ascending=False)
        
        high_missing = report[report['missing_percent'] > 5]
        if len(high_missing) > 0:
            print(f"\n⚠️  Columns with >5% missing values:")
            for _, row in high_missing.iterrows():
                print(f"  - {row['column']}: {row['missing_percent']:.2f}%")
        
        return report
    
    def detect_outliers_zscore(self, columns: List[str] = None, threshold: float = 3.0) -> Dict[str, pd.DataFrame]:
        """
        Detect outliers using Z-score method.
        
        Args:
            columns: List of columns to check (default: all numeric)
            threshold: Z-score threshold (default: 3.0)
            
        Returns:
            Dictionary mapping column names to outlier DataFrames
        """
        if columns is None:
            columns = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'WS', 'WSgust']
            columns = [col for col in columns if col in self.numeric_cols]
        
        outliers = {}
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            z_scores = np.abs(stats.zscore(self.df[col].dropna()))
            outlier_mask = z_scores > threshold
            
            if outlier_mask.sum() > 0:
                outliers[col] = {
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(self.df)) * 100,
                    'indices': self.df[col].dropna().index[outlier_mask].tolist()
                }
        
        return outliers
    
    def detect_outliers_iqr(self, columns: List[str] = None) -> Dict[str, Dict]:
        """
        Detect outliers using IQR method.
        
        Args:
            columns: List of columns to check
            
        Returns:
            Dictionary with outlier information
        """
        if columns is None:
            columns = self.numeric_cols
            
        outliers = {}
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            
            if outlier_mask.sum() > 0:
                outliers[col] = {
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(self.df)) * 100,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
        
        return outliers
    
    def data_quality_score(self) -> Dict[str, float]:
        """
        Calculate overall data quality scores.
        
        Returns:
            Dictionary with quality metrics
        """
        total_cells = self.df.size
        missing_cells = self.df.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        negative_irradiance = 0
        irradiance_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB']
        for col in irradiance_cols:
            if col in self.df.columns:
                negative_irradiance += (self.df[col] < 0).sum()
        
        validity = 100 - ((negative_irradiance / len(self.df)) * 100)
        
        duplicates = self.df.duplicated().sum()
        uniqueness = ((len(self.df) - duplicates) / len(self.df)) * 100
        
        overall_score = (completeness * 0.4 + validity * 0.4 + uniqueness * 0.2)
        
        return {
            'completeness': completeness,
            'validity': validity,
            'uniqueness': uniqueness,
            'overall_quality': overall_score
        }
    
    def generate_profile_report(self) -> Dict:
        """
        Generate comprehensive profile report.
        
        Returns:
            Dictionary with complete profiling results
        """
        report = {
            'summary_statistics': self.generate_summary_statistics(),
            'missing_values': self.missing_value_report(),
            'outliers_zscore': self.detect_outliers_zscore(),
            'outliers_iqr': self.detect_outliers_iqr(),
            'quality_score': self.data_quality_score()
        }
        
        return report
