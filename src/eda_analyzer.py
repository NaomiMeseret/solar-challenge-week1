"""
Exploratory Data Analysis utilities for solar radiation data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from scipy.stats import pearsonr, spearmanr


class EDAAnalyzer:
    """Perform comprehensive exploratory data analysis."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize EDA analyzer.
        
        Args:
            df: DataFrame to analyze
        """
        self.df = df.copy()
        
    def time_series_summary(self, date_column: str = 'Timestamp') -> Dict:
        """
        Analyze time series characteristics.
        
        Args:
            date_column: Name of timestamp column
        """
        if date_column not in self.df.columns:
            return {}
        
        self.df[date_column] = pd.to_datetime(self.df[date_column])
        
        return {
            'date_range': (self.df[date_column].min(), self.df[date_column].max()),
            'total_days': (self.df[date_column].max() - self.df[date_column].min()).days,
            'frequency': pd.infer_freq(self.df[date_column]),
            'total_records': len(self.df)
        }
    
    def extract_temporal_features(self, date_column: str = 'Timestamp') -> pd.DataFrame:
        """
        Extract temporal features from timestamp.
        
        Args:
            date_column: Name of timestamp column
        """
        df_temp = self.df.copy()
        df_temp[date_column] = pd.to_datetime(df_temp[date_column])
        
        df_temp['Year'] = df_temp[date_column].dt.year
        df_temp['Month'] = df_temp[date_column].dt.month
        df_temp['Day'] = df_temp[date_column].dt.day
        df_temp['Hour'] = df_temp[date_column].dt.hour
        df_temp['DayOfWeek'] = df_temp[date_column].dt.dayofweek
        df_temp['Quarter'] = df_temp[date_column].dt.quarter
        
        return df_temp
    
    def analyze_monthly_patterns(self, value_columns: List[str]) -> pd.DataFrame:
        """
        Analyze patterns by month.
        
        Args:
            value_columns: Columns to analyze
        """
        df_temp = self.extract_temporal_features()
        
        monthly_stats = df_temp.groupby('Month')[value_columns].agg(['mean', 'median', 'std', 'min', 'max'])
        
        return monthly_stats
    
    def analyze_hourly_patterns(self, value_columns: List[str]) -> pd.DataFrame:
        """
        Analyze patterns by hour of day.
        
        Args:
            value_columns: Columns to analyze
        """
        df_temp = self.extract_temporal_features()
        
        hourly_stats = df_temp.groupby('Hour')[value_columns].agg(['mean', 'median', 'std'])
        
        return hourly_stats
    
    def correlation_analysis(self, columns: List[str] = None, method: str = 'pearson') -> pd.DataFrame:
        """
        Compute correlation matrix.
        
        Args:
            columns: Columns to include
            method: 'pearson' or 'spearman'
        """
        if columns is None:
            numeric_df = self.df.select_dtypes(include=[np.number])
        else:
            numeric_df = self.df[columns]
        
        corr_matrix = numeric_df.corr(method=method)
        
        return corr_matrix
    
    def find_strong_correlations(self, threshold: float = 0.7, columns: List[str] = None) -> List[Tuple]:
        """
        Find variable pairs with strong correlations.
        
        Args:
            threshold: Minimum absolute correlation
            columns: Columns to analyze
        """
        corr_matrix = self.correlation_analysis(columns=columns)
        
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) >= threshold:
                    strong_corr.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_matrix.iloc[i, j]
                    ))
        
        return sorted(strong_corr, key=lambda x: abs(x[2]), reverse=True)
    
    def cleaning_impact_analysis(self) -> Dict:
        """Analyze impact of cleaning events on module performance."""
        if 'Cleaning' not in self.df.columns:
            return {}
        
        analysis = {}
        
        for module in ['ModA', 'ModB']:
            if module in self.df.columns:
                cleaned = self.df[self.df['Cleaning'] == 1][module].mean()
                not_cleaned = self.df[self.df['Cleaning'] == 0][module].mean()
                
                analysis[module] = {
                    'avg_when_cleaned': cleaned,
                    'avg_when_not_cleaned': not_cleaned,
                    'difference': cleaned - not_cleaned,
                    'percent_change': ((cleaned - not_cleaned) / not_cleaned * 100) if not_cleaned != 0 else 0
                }
        
        return analysis
    
    def wind_analysis(self) -> Dict:
        """Analyze wind characteristics."""
        wind_stats = {}
        
        if 'WS' in self.df.columns:
            wind_stats['mean_speed'] = self.df['WS'].mean()
            wind_stats['max_speed'] = self.df['WS'].max()
            wind_stats['predominant_speed_range'] = pd.cut(self.df['WS'], bins=5).mode()[0]
        
        if 'WD' in self.df.columns:
            wind_stats['mean_direction'] = self.df['WD'].mean()
            wind_stats['direction_variability'] = self.df['WD'].std()
        
        if 'WSgust' in self.df.columns:
            wind_stats['max_gust'] = self.df['WSgust'].max()
            wind_stats['avg_gust'] = self.df['WSgust'].mean()
        
        return wind_stats
    
    def temperature_humidity_analysis(self) -> Dict:
        """Analyze relationship between temperature and humidity."""
        analysis = {}
        
        if 'Tamb' in self.df.columns and 'RH' in self.df.columns:
            corr, p_value = pearsonr(self.df['Tamb'].dropna(), self.df['RH'].dropna())
            analysis['temp_rh_correlation'] = corr
            analysis['p_value'] = p_value
        
        if 'RH' in self.df.columns and 'GHI' in self.df.columns:
            corr, p_value = pearsonr(self.df['RH'].dropna(), self.df['GHI'].dropna())
            analysis['rh_ghi_correlation'] = corr
            analysis['rh_ghi_p_value'] = p_value
        
        return analysis
    
    def irradiance_analysis(self) -> Dict:
        """Analyze solar irradiance components."""
        analysis = {}
        
        irradiance_cols = ['GHI', 'DNI', 'DHI']
        
        for col in irradiance_cols:
            if col in self.df.columns:
                analysis[col] = {
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median(),
                    'max': self.df[col].max(),
                    'std': self.df[col].std(),
                    'total_energy': self.df[col].sum()
                }
        
        if all(col in self.df.columns for col in irradiance_cols):
            analysis['ghi_dni_dhi_relationship'] = {
                'ghi_vs_dni_corr': self.df['GHI'].corr(self.df['DNI']),
                'ghi_vs_dhi_corr': self.df['GHI'].corr(self.df['DHI'])
            }
        
        return analysis
    
    def generate_insights(self) -> List[str]:
        """Generate key insights from analysis."""
        insights = []
        
        corr_analysis = self.find_strong_correlations(threshold=0.7)
        if corr_analysis:
            insights.append(f"Strong correlations found between {len(corr_analysis)} variable pairs")
        
        if 'GHI' in self.df.columns:
            peak_ghi = self.df['GHI'].max()
            avg_ghi = self.df['GHI'].mean()
            insights.append(f"Peak GHI: {peak_ghi:.2f} W/m², Average: {avg_ghi:.2f} W/m²")
        
        if 'Tamb' in self.df.columns:
            avg_temp = self.df['Tamb'].mean()
            max_temp = self.df['Tamb'].max()
            insights.append(f"Temperature range: {self.df['Tamb'].min():.1f}°C to {max_temp:.1f}°C (avg: {avg_temp:.1f}°C)")
        
        cleaning_impact = self.cleaning_impact_analysis()
        if cleaning_impact:
            for module, stats in cleaning_impact.items():
                if abs(stats['percent_change']) > 5:
                    insights.append(f"{module} shows {stats['percent_change']:.1f}% performance change with cleaning")
        
        return insights
