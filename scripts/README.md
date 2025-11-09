# Scripts Directory

This directory contains executable Python scripts for data profiling and cleaning operations.

## Available Scripts

### 1. profile_data.py
Generate comprehensive data quality reports for solar radiation datasets.

**Usage**:
```bash
python scripts/profile_data.py <country> [--output-dir <directory>]
```

**Examples**:
```bash
# Profile Benin dataset
python scripts/profile_data.py benin

# Profile Togo dataset with custom output directory
python scripts/profile_data.py togo --output-dir my_reports
```

**Outputs**:
- Summary statistics CSV
- Missing value report CSV
- Comprehensive text report
- Data quality scores

**Features**:
- Descriptive statistics (mean, median, std, skewness, kurtosis)
- Missing value analysis with threshold warnings
- Outlier detection using Z-score method
- Data quality scoring (completeness, validity, uniqueness)

---

### 2. clean_data.py
Clean and prepare solar radiation datasets for analysis.

**Usage**:
```bash
python scripts/clean_data.py <country> [--output-dir <directory>] [--keep-outliers]
```

**Examples**:
```bash
# Clean Benin dataset (removes outliers)
python scripts/clean_data.py benin

# Clean Sierra Leone dataset and keep outliers
python scripts/clean_data.py sierra-leone --keep-outliers

# Clean with custom output directory
python scripts/clean_data.py togo --output-dir cleaned_data
```

**Outputs**:
- Cleaned CSV file: `data/<country>_clean.csv`
- Cleaning log CSV: `reports/<country>_cleaning_log.csv`

**Cleaning Pipeline**:
1. Remove duplicate records
2. Handle missing values (median imputation)
3. Validate irradiance values (non-negative constraint)
4. Remove/cap outliers (optional)
5. Generate cleaning report

---

## Script Development Guidelines

### Adding New Scripts
1. Place script in this directory
2. Import modules from `src/` using relative paths
3. Add command-line argument parsing with argparse
4. Include comprehensive docstrings
5. Update this README

### Best Practices
- Use descriptive function and variable names
- Include error handling for file operations
- Provide informative console output
- Generate both CSV and text reports
- Follow PEP 8 style guidelines

---

## Dependencies

All scripts require the packages listed in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

**File not found errors**:
- Ensure data files are in the `data/` directory
- Check file naming: `<country>-malanville.csv`

**Import errors**:
- Run scripts from project root directory
- Verify virtual environment is activated

**Memory errors with large datasets**:
- Process data in chunks
- Use `--keep-outliers` to skip outlier removal
