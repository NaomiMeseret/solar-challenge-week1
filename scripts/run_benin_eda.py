"""
Benin EDA Analysis - Task 2
Comprehensive exploratory data analysis for solar radiation data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from src.data_loader import SolarDataLoader
from src.data_profiler import DataProfiler
from src.data_cleaner import DataCleaner
from src.eda_analyzer import EDAAnalyzer
from src.visualization import SolarVisualizer

plt.style.use('default')
sns.set_palette("husl")

print("="*70)
print("BENIN SOLAR RADIATION DATA - EXPLORATORY DATA ANALYSIS")
print("="*70)

# Load data
loader = SolarDataLoader()
df_raw = loader.load_country_data('benin')

print(f"\nDataset Shape: {df_raw.shape}")
print(f"Date Range: {df_raw['Timestamp'].min()} to {df_raw['Timestamp'].max()}")
print(f"Duration: {(df_raw['Timestamp'].max() - df_raw['Timestamp'].min()).days} days")

# Task 2.1: Summary Statistics & Missing-Value Report
print("\n" + "="*70)
print("1. SUMMARY STATISTICS & MISSING VALUE REPORT")
print("="*70)

profiler = DataProfiler(df_raw)
summary_stats = profiler.generate_summary_statistics()
print("\nSummary Statistics:")
print(summary_stats.to_string())

missing_report = profiler.missing_value_report()
if len(missing_report) > 0:
    print("\n⚠️ Missing Values Detected:")
    print(missing_report.to_string())
else:
    print("\n✓ No missing values")

quality_scores = profiler.data_quality_score()
print("\nData Quality Scores:")
for metric, score in quality_scores.items():
    print(f"  {metric}: {score:.2f}%")

# Task 2.2: Outlier Detection & Basic Cleaning
print("\n" + "="*70)
print("2. OUTLIER DETECTION & BASIC CLEANING")
print("="*70)

outliers_z = profiler.detect_outliers_zscore(threshold=3.0)
print("\nZ-Score Outliers (|Z| > 3):")
for col, stats_dict in outliers_z.items():
    print(f"  {col}: {stats_dict['count']} outliers ({stats_dict['percentage']:.2f}%)")

cleaner = DataCleaner(df_raw)
df_clean = cleaner.clean_pipeline(remove_outliers=True)

print(f"\nCleaning Summary:")
print(f"  Original rows: {len(df_raw)}")
print(f"  Clean rows: {len(df_clean)}")
print(f"  Retention: {(len(df_clean)/len(df_raw)*100):.2f}%")

# Save cleaned data
df_clean.to_csv('data/benin_clean.csv', index=False)
print("✓ Cleaned data saved to data/benin_clean.csv")

# Task 2.3: Time Series Analysis
print("\n" + "="*70)
print("3. TIME SERIES ANALYSIS")
print("="*70)

analyzer = EDAAnalyzer(df_clean)

monthly_patterns = analyzer.analyze_monthly_patterns(['GHI', 'DNI', 'DHI', 'Tamb'])
print("\nMonthly Patterns (Mean Values):")
print(monthly_patterns.round(2))

hourly_patterns = analyzer.analyze_hourly_patterns(['GHI', 'DNI'])
print("\nHourly Patterns - Peak Hours:")
peak_hour = hourly_patterns[('GHI', 'mean')].idxmax()
peak_ghi = hourly_patterns[('GHI', 'mean')].max()
print(f"  Peak GHI Hour: {peak_hour}:00 ({peak_ghi:.2f} W/m²)")

# Task 2.4: Cleaning Impact Analysis
print("\n" + "="*70)
print("4. CLEANING IMPACT ANALYSIS")
print("="*70)

cleaning_impact = analyzer.cleaning_impact_analysis()
if cleaning_impact:
    for module, stats_dict in cleaning_impact.items():
        print(f"\n{module}:")
        print(f"  Cleaned avg: {stats_dict['avg_when_cleaned']:.2f} W/m²")
        print(f"  Not cleaned avg: {stats_dict['avg_when_not_cleaned']:.2f} W/m²")
        print(f"  Performance change: {stats_dict['percent_change']:.2f}%")

# Task 2.5: Correlation & Relationship Analysis
print("\n" + "="*70)
print("5. CORRELATION & RELATIONSHIP ANALYSIS")
print("="*70)

corr_cols = ['GHI', 'DNI', 'DHI', 'TModA', 'TModB', 'Tamb', 'RH', 'WS']
corr_matrix = analyzer.correlation_analysis(columns=corr_cols)
print("\nCorrelation Matrix:")
print(corr_matrix.round(3))

strong_corr = analyzer.find_strong_correlations(threshold=0.7)
print("\nStrong Correlations (|r| > 0.7):")
for var1, var2, corr in strong_corr[:10]:
    print(f"  {var1} <-> {var2}: {corr:.3f}")

# Task 2.6: Wind Analysis & Distribution
print("\n" + "="*70)
print("6. WIND ANALYSIS & DISTRIBUTION")
print("="*70)

wind_stats = analyzer.wind_analysis()
for key, value in wind_stats.items():
    print(f"  {key}: {value}")

# Task 2.7: Temperature Analysis
print("\n" + "="*70)
print("7. TEMPERATURE & HUMIDITY ANALYSIS")
print("="*70)

temp_humid = analyzer.temperature_humidity_analysis()
for key, value in temp_humid.items():
    print(f"  {key}: {value}")

# Task 2.8: Irradiance Analysis
print("\n" + "="*70)
print("8. SOLAR IRRADIANCE ANALYSIS")
print("="*70)

irr_analysis = analyzer.irradiance_analysis()
for component, stats_dict in irr_analysis.items():
    if isinstance(stats_dict, dict) and 'mean' in stats_dict:
        print(f"\n{component}:")
        for metric, value in stats_dict.items():
            if metric != 'total_energy':
                print(f"  {metric}: {value:.2f}")

# Generate Insights
print("\n" + "="*70)
print("KEY INSIGHTS")
print("="*70)

insights = analyzer.generate_insights()
for i, insight in enumerate(insights, 1):
    print(f"{i}. {insight}")

# Export results
os.makedirs('reports', exist_ok=True)
summary_stats.to_csv('reports/benin_summary_statistics.csv')
corr_matrix.to_csv('reports/benin_correlation_matrix.csv')

print("\n" + "="*70)
print("ANALYSIS COMPLETE - Reports saved to reports/ directory")
print("="*70)
