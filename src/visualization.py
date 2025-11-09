"""
Visualization utilities for solar radiation data analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class SolarVisualizer:
    """Create visualizations for solar radiation analysis."""
    
    def __init__(self, df: pd.DataFrame, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize visualizer.
        
        Args:
            df: DataFrame to visualize
            style: Matplotlib style
        """
        self.df = df.copy()
        plt.style.use('default')
        sns.set_palette("husl")
        
    def plot_time_series(self, columns: List[str], figsize: Tuple[int, int] = (15, 8), 
                        date_column: str = 'Timestamp'):
        """
        Plot time series for multiple columns.
        
        Args:
            columns: Columns to plot
            figsize: Figure size
            date_column: Timestamp column name
        """
        fig, axes = plt.subplots(len(columns), 1, figsize=figsize, sharex=True)
        
        if len(columns) == 1:
            axes = [axes]
        
        for idx, col in enumerate(columns):
            if col in self.df.columns:
                axes[idx].plot(self.df[date_column], self.df[col], linewidth=0.8, alpha=0.7)
                axes[idx].set_ylabel(col, fontsize=10, fontweight='bold')
                axes[idx].grid(True, alpha=0.3)
                axes[idx].set_title(f'{col} Over Time', fontsize=11)
        
        plt.xlabel(date_column, fontsize=10, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_correlation_heatmap(self, columns: List[str] = None, figsize: Tuple[int, int] = (12, 10)):
        """
        Plot correlation heatmap.
        
        Args:
            columns: Columns to include
            figsize: Figure size
        """
        if columns is None:
            columns = ['GHI', 'DNI', 'DHI', 'TModA', 'TModB', 'Tamb', 'RH', 'WS', 'BP']
            columns = [col for col in columns if col in self.df.columns]
        
        corr_matrix = self.df[columns].corr()
        
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        return fig
    
    def plot_distributions(self, columns: List[str], figsize: Tuple[int, int] = (15, 10)):
        """
        Plot histograms for multiple columns.
        
        Args:
            columns: Columns to plot
            figsize: Figure size
        """
        n_cols = 3
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
        
        for idx, col in enumerate(columns):
            if col in self.df.columns:
                axes[idx].hist(self.df[col].dropna(), bins=50, alpha=0.7, edgecolor='black')
                axes[idx].set_xlabel(col, fontweight='bold')
                axes[idx].set_ylabel('Frequency')
                axes[idx].set_title(f'Distribution of {col}', fontweight='bold')
                axes[idx].grid(True, alpha=0.3)
        
        for idx in range(len(columns), len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        return fig
    
    def plot_scatter_matrix(self, columns: List[str], figsize: Tuple[int, int] = (14, 14)):
        """
        Create scatter plot matrix.
        
        Args:
            columns: Columns to include
            figsize: Figure size
        """
        subset_df = self.df[columns].dropna()
        
        fig = plt.figure(figsize=figsize)
        pd.plotting.scatter_matrix(subset_df, alpha=0.3, figsize=figsize, diagonal='hist')
        plt.suptitle('Scatter Plot Matrix', fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig
    
    def plot_box_plots(self, columns: List[str], figsize: Tuple[int, int] = (15, 6)):
        """
        Create box plots for outlier detection.
        
        Args:
            columns: Columns to plot
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        data_to_plot = [self.df[col].dropna() for col in columns if col in self.df.columns]
        labels = [col for col in columns if col in self.df.columns]
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Values', fontweight='bold')
        ax.set_title('Box Plots for Outlier Detection', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig
    
    def plot_cleaning_impact(self, figsize: Tuple[int, int] = (10, 6)):
        """
        Plot impact of cleaning on module performance.
        
        Args:
            figsize: Figure size
        """
        if 'Cleaning' not in self.df.columns:
            print("No 'Cleaning' column found")
            return None
        
        modules = ['ModA', 'ModB']
        modules = [m for m in modules if m in self.df.columns]
        
        cleaning_stats = self.df.groupby('Cleaning')[modules].mean()
        
        fig, ax = plt.subplots(figsize=figsize)
        cleaning_stats.T.plot(kind='bar', ax=ax, width=0.7)
        ax.set_xlabel('Module', fontweight='bold')
        ax.set_ylabel('Average Irradiance (W/m²)', fontweight='bold')
        ax.set_title('Module Performance: Cleaned vs Not Cleaned', fontsize=14, fontweight='bold')
        ax.legend(['Not Cleaned (0)', 'Cleaned (1)'], title='Cleaning Status')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        return fig
    
    def plot_monthly_patterns(self, column: str, figsize: Tuple[int, int] = (12, 6)):
        """
        Plot monthly patterns for a variable.
        
        Args:
            column: Column to analyze
            figsize: Figure size
        """
        df_temp = self.df.copy()
        df_temp['Month'] = pd.to_datetime(df_temp['Timestamp']).dt.month
        
        monthly_data = df_temp.groupby('Month')[column].agg(['mean', 'std'])
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.errorbar(monthly_data.index, monthly_data['mean'], yerr=monthly_data['std'], 
                   marker='o', linewidth=2, markersize=8, capsize=5)
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel(f'{column}', fontweight='bold')
        ax.set_title(f'Monthly Pattern: {column}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(1, 13))
        plt.tight_layout()
        
        return fig
    
    def plot_wind_rose(self, figsize: Tuple[int, int] = (10, 10)):
        """
        Create wind rose plot.
        
        Args:
            figsize: Figure size
        """
        if 'WS' not in self.df.columns or 'WD' not in self.df.columns:
            print("Wind speed (WS) or wind direction (WD) column not found")
            return None
        
        try:
            from windrose import WindroseAxes
            
            fig = plt.figure(figsize=figsize)
            ax = WindroseAxes.from_ax(fig=fig)
            ax.bar(self.df['WD'], self.df['WS'], normed=True, opening=0.8, edgecolor='white')
            ax.set_legend(title='Wind Speed (m/s)')
            ax.set_title('Wind Rose', fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()
            
            return fig
        except ImportError:
            print("Windrose package not available, creating polar plot instead")
            return self._plot_wind_polar(figsize)
    
    def _plot_wind_polar(self, figsize: Tuple[int, int] = (10, 10)):
        """Alternative wind visualization using polar plot."""
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'), figsize=figsize)
        
        theta = np.radians(self.df['WD'])
        r = self.df['WS']
        
        ax.scatter(theta, r, alpha=0.3, s=10)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title('Wind Direction and Speed', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        return fig
    
    def plot_bubble_chart(self, x_col: str, y_col: str, size_col: str, 
                         figsize: Tuple[int, int] = (12, 8)):
        """
        Create bubble chart.
        
        Args:
            x_col: X-axis column
            y_col: Y-axis column
            size_col: Column for bubble size
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        scatter = ax.scatter(self.df[x_col], self.df[y_col], 
                           s=self.df[size_col]*2, alpha=0.5, c=self.df[size_col], 
                           cmap='viridis', edgecolors='black', linewidth=0.5)
        
        ax.set_xlabel(x_col, fontweight='bold', fontsize=11)
        ax.set_ylabel(y_col, fontweight='bold', fontsize=11)
        ax.set_title(f'{y_col} vs {x_col} (Bubble size: {size_col})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(size_col, fontweight='bold')
        
        plt.tight_layout()
        
        return fig
    
    def plot_hourly_heatmap(self, column: str, figsize: Tuple[int, int] = (14, 8)):
        """
        Create heatmap showing hourly patterns across months.
        
        Args:
            column: Column to visualize
            figsize: Figure size
        """
        df_temp = self.df.copy()
        df_temp['Month'] = pd.to_datetime(df_temp['Timestamp']).dt.month
        df_temp['Hour'] = pd.to_datetime(df_temp['Timestamp']).dt.hour
        
        pivot_data = df_temp.pivot_table(values=column, index='Hour', columns='Month', aggfunc='mean')
        
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(pivot_data, cmap='YlOrRd', annot=True, fmt='.1f', linewidths=0.5, ax=ax)
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Hour of Day', fontweight='bold')
        ax.set_title(f'Average {column} by Hour and Month', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
