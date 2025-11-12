"""
Data cleaning utilities for solar radiation datasets.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from scipy import stats


class DataCleaner:
    """Clean and preprocess solar radiation data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize cleaner with dataset.
        
        Args:
            df: DataFrame to clean
        """
        self.df = df.copy()
        self.cleaning_log = []
        
    def log_action(self, action: str, details: str):
        """Log cleaning actions."""
        self.cleaning_log.append({'action': action, 'details': details})
        print(f"✓ {action}: {details}")
        
    def remove_duplicates(self) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_count - len(self.df)
        
        if removed > 0:
            self.log_action('Removed duplicates', f'{removed} duplicate rows removed')
        
        return self.df

    def coerce_numeric_columns(self) -> pd.DataFrame:
        cols = [
            'GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Tamb', 'RH', 'WS', 'WSgust',
            'WSstdev', 'WD', 'WDstdev', 'BP', 'Cleaning', 'Precipitation',
            'TModA', 'TModB'
        ]
        for col in cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        return self.df
    
    def handle_missing_values(self, strategy: str = 'median', threshold: float = 0.5) -> pd.DataFrame:
        """
        Handle missing values in dataset.
        
        Args:
            strategy: 'median', 'mean', 'drop', or 'forward_fill'
            threshold: Drop columns with missing ratio > threshold
        """
        missing_ratio = self.df.isnull().sum() / len(self.df)
        cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
        
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            self.log_action('Dropped columns', f'Removed {len(cols_to_drop)} columns with >{threshold*100}% missing')
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if strategy == 'median':
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    median_val = self.df[col].median()
                    self.df[col].fillna(median_val, inplace=True)
                    
        elif strategy == 'mean':
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    mean_val = self.df[col].mean()
                    self.df[col].fillna(mean_val, inplace=True)
                    
        elif strategy == 'forward_fill':
            self.df.fillna(method='ffill', inplace=True)
            
        elif strategy == 'drop':
            initial_count = len(self.df)
            self.df = self.df.dropna()
            removed = initial_count - len(self.df)
            self.log_action('Dropped rows', f'{removed} rows with missing values removed')
        
        return self.df
    
    def remove_outliers_zscore(self, columns: List[str], threshold: float = 3.0) -> pd.DataFrame:
        """
        Remove outliers using Z-score method.
        
        Args:
            columns: Columns to check for outliers
            threshold: Z-score threshold
        """
        initial_count = len(self.df)
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            z_scores = np.abs(stats.zscore(self.df[col].dropna()))
            valid_indices = self.df[col].dropna().index[z_scores <= threshold]
            self.df = self.df.loc[self.df.index.isin(valid_indices)]
        
        removed = initial_count - len(self.df)
        if removed > 0:
            self.log_action('Removed outliers', f'{removed} outlier rows removed (Z-score > {threshold})')
        
        return self.df
    
    def cap_outliers_iqr(self, columns: List[str]) -> pd.DataFrame:
        """
        Cap outliers using IQR method instead of removing.
        
        Args:
            columns: Columns to cap outliers
        """
        for col in columns:
            if col not in self.df.columns:
                continue
                
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            capped_count = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
            
            self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
            
            if capped_count > 0:
                self.log_action('Capped outliers', f'{col}: {capped_count} values capped')
        
        return self.df
    
    def validate_irradiance_values(self) -> pd.DataFrame:
        """Ensure irradiance values are non-negative."""
        irradiance_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB']
        
        for col in irradiance_cols:
            if col in self.df.columns:
                negative_count = (self.df[col] < 0).sum()
                if negative_count > 0:
                    self.df[col] = self.df[col].clip(lower=0)
                    self.log_action('Fixed negative values', f'{col}: {negative_count} values set to 0')
        
        return self.df
    
    def clean_pipeline(self, remove_outliers: bool = True) -> pd.DataFrame:
        """
        Execute complete cleaning pipeline.
        
        Args:
            remove_outliers: Whether to remove outliers
        """
        print("\n=== Starting Data Cleaning Pipeline ===\n")
        
        self.remove_duplicates()
        self.coerce_numeric_columns()
        self.handle_missing_values(strategy='median')
        self.validate_irradiance_values()
        
        if remove_outliers:
            outlier_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'WS', 'WSgust']
            self.remove_outliers_zscore(outlier_cols, threshold=3.0)
        
        print(f"\n=== Cleaning Complete ===")
        print(f"Final dataset shape: {self.df.shape}")
        
        return self.df
    
    def get_cleaning_report(self) -> pd.DataFrame:
        """Get report of all cleaning actions."""
        return pd.DataFrame(self.cleaning_log)
    
    def save_clean_data(self, filepath: str):
        """Save cleaned data to CSV."""
        self.df.to_csv(filepath, index=False)
        print(f"\n💾 Cleaned data saved to: {filepath}")
