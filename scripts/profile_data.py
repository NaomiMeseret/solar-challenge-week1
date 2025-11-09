"""
Data profiling script for solar radiation datasets.
Run this script to generate comprehensive data quality reports.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.data_loader import SolarDataLoader
from src.data_profiler import DataProfiler
import argparse


def profile_dataset(country: str, output_dir: str = 'reports'):
    """
    Profile a country's solar dataset.
    
    Args:
        country: Country name
        output_dir: Directory to save reports
    """
    print(f"\n{'='*60}")
    print(f"DATA PROFILING: {country.upper()}")
    print(f"{'='*60}\n")
    
    loader = SolarDataLoader()
    
    try:
        df = loader.load_country_data(country)
    except FileNotFoundError:
        print(f"Error: Data file for {country} not found.")
        print("Please ensure data files are in the 'data/' directory.")
        return
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"Date Range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")
    
    profiler = DataProfiler(df)
    
    print("\n" + "-"*60)
    print("SUMMARY STATISTICS")
    print("-"*60)
    summary_stats = profiler.generate_summary_statistics()
    print(summary_stats.to_string())
    
    print("\n" + "-"*60)
    print("MISSING VALUE ANALYSIS")
    print("-"*60)
    missing_report = profiler.missing_value_report()
    if len(missing_report) > 0:
        print(missing_report.to_string())
    else:
        print("✓ No missing values detected")
    
    print("\n" + "-"*60)
    print("OUTLIER DETECTION (Z-SCORE METHOD)")
    print("-"*60)
    outliers_z = profiler.detect_outliers_zscore()
    if outliers_z:
        for col, stats in outliers_z.items():
            print(f"\n{col}:")
            print(f"  Outliers: {stats['count']} ({stats['percentage']:.2f}%)")
    else:
        print("✓ No significant outliers detected (Z-score > 3)")
    
    print("\n" + "-"*60)
    print("DATA QUALITY SCORE")
    print("-"*60)
    quality = profiler.data_quality_score()
    for metric, score in quality.items():
        print(f"{metric.replace('_', ' ').title()}: {score:.2f}%")
    
    os.makedirs(output_dir, exist_ok=True)
    
    report_file = os.path.join(output_dir, f'{country}_profile_report.txt')
    with open(report_file, 'w') as f:
        f.write(f"DATA PROFILING REPORT: {country.upper()}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Dataset Shape: {df.shape}\n")
        f.write(f"Date Range: {df['Timestamp'].min()} to {df['Timestamp'].max()}\n\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("-"*60 + "\n")
        f.write(summary_stats.to_string())
        f.write("\n\n")
        f.write("MISSING VALUES\n")
        f.write("-"*60 + "\n")
        f.write(missing_report.to_string() if len(missing_report) > 0 else "No missing values\n")
        f.write("\n\n")
        f.write("DATA QUALITY SCORES\n")
        f.write("-"*60 + "\n")
        for metric, score in quality.items():
            f.write(f"{metric.replace('_', ' ').title()}: {score:.2f}%\n")
    
    print(f"\n📊 Profile report saved to: {report_file}")
    
    summary_stats.to_csv(os.path.join(output_dir, f'{country}_summary_stats.csv'))
    if len(missing_report) > 0:
        missing_report.to_csv(os.path.join(output_dir, f'{country}_missing_values.csv'), index=False)
    
    print(f"\n{'='*60}")
    print("PROFILING COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Profile solar radiation dataset')
    parser.add_argument('country', type=str, help='Country name (e.g., benin, togo, sierra-leone)')
    parser.add_argument('--output-dir', type=str, default='reports', help='Output directory for reports')
    
    args = parser.parse_args()
    
    profile_dataset(args.country, args.output_dir)
