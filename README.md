# FOMC SEP Dot Plot Extraction Pipeline

An automated pipeline for extracting Federal Reserve FOMC Summary of Economic Projections (SEP) dot plot data from PDFs (2012-present).

## Overview

This project automatically fetches FOMC SEP PDF documents and extracts individual participant projections from dot plots. The pipeline handles:

- **Date Range**: June 2012 – Present (2012-2026)
- **Data Format**: Individual projection values for target federal funds rate
- **Output**: Single CSV file with 10,000+ data points

### Important Note on Historical Data
SEP documents prior to June 2012 do not use dot plots. Instead, they present participant projections as numerical tables. This pipeline is specifically designed for dot plot data (2012+). Extracting pre-2012 table-based data would require separate logic and is outside the current scope.

## Project Structure
## Features

✅ **Automatic PDF Fetching**: Downloads from Federal Reserve website  
✅ **Format Adaptability**: Handles layout changes across 2012-2026  
✅ **Robust Detection**: Computer vision (OpenCV) for dot detection  
✅ **Year Assignment**: KMeans clustering for year-based grouping  
✅ **Calibration Logic**: Dynamic grid line detection and projection mapping  
✅ **Portable**: Works with any home directory (no hardcoded paths)  

## Usage

```bash
cd notebooks/
python3 run_all_seps.py
```

This runs both 2012-2014 and 2015+ pipelines, outputting to `outputs/projections.csv`.

## Technical Details

### 2012-2014 Logic
- Uses distance transform for tight dot detection
- 1% gridline spacing (0.25% increment projections)
- Early 2012 dates (Jan, April) include -1.0 offset correction
- Special handling for Sept/Dec 2014 transition to 0.25% spacing

### 2015+ Logic
- Standard erosion-based dot detection
- 0.25% gridline spacing (0.125% increment projections)
- Automatic page index detection (page 2 for 2015-2020, page 4 for 2021+)
- HSV-based color detection with year-specific ranges

### Output Format

| Year | Projection | SEP_Date |
|------|-----------|----------|
| 2012 | 0.25 | 2012-06-20 |
| 2013 | 0.50 | 2012-06-20 |
| ... | ... | ... |

## Dependencies
cat > /Users/knimm/Documents/FOMC_Project_Clean/.gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Project outputs (keep PDFs, ignore individual debug/temp files)
outputs/projections.csv
notebooks/debug_*.png
notebooks/page.png
notebooks/*.pyc

# Don't ignore sep_pdfs folder, but could ignore if too large
# sep_pdfs/
