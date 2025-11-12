"""
Data cleaning script for solar radiation datasets.
Run this script to clean and prepare data for analysis.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.data_loader import SolarDataLoader
from src.data_cleaner import DataCleaner
import argparse


def clean_dataset(country: str, output_dir: str = 'data', remove_outliers: bool = True):
    """
    Clean a country's solar dataset.
    
    Args:
        country: Country name
        output_dir: Directory to save cleaned data
        remove_outliers: Whether to remove outliers
    """
    print(f"\n{'='*60}")
    print(f"DATA CLEANING: {country.upper()}")
    print(f"{'='*60}\n")
    
    loader = SolarDataLoader()
    
    try:
        df = loader.load_country_data(country)
    except FileNotFoundError:
        print(f"Error: Data file for {country} not found.")
        return
    
    print(f"Original dataset shape: {df.shape}")
    
    cleaner = DataCleaner(df)
    
    cleaned_df = cleaner.clean_pipeline(remove_outliers=remove_outliers)
    
    # Ensure consistent file naming: use slug version of country (spaces/hyphens -> underscores, lowercased)
    slug = country.strip().lower().replace(' ', '_').replace('-', '_')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{slug}_clean.csv')
    cleaner.save_clean_data(output_file)
    
    cleaning_report = cleaner.get_cleaning_report()
    report_file = os.path.join('reports', f'{slug}_cleaning_log.csv')
    os.makedirs('reports', exist_ok=True)
    cleaning_report.to_csv(report_file, index=False)
    print(f"📋 Cleaning log saved to: {report_file}")
    
    print(f"\n{'='*60}")
    print("CLEANING SUMMARY")
    print(f"{'='*60}")
    print(f"Original rows: {len(df)}")
    print(f"Cleaned rows: {len(cleaned_df)}")
    print(f"Rows removed: {len(df) - len(cleaned_df)}")
    print(f"Retention rate: {(len(cleaned_df)/len(df)*100):.2f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean solar radiation dataset')
    parser.add_argument('country', type=str, help='Country name')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory')
    parser.add_argument('--keep-outliers', action='store_true', help='Keep outliers (do not remove)')
    
    args = parser.parse_args()
    
    clean_dataset(args.country, args.output_dir, remove_outliers=not args.keep_outliers)
