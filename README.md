# FOMC SEP Extraction Pipeline

Computer vision pipeline for extracting FOMC Summary of Economic Projections (SEP) dot plot data from Federal Reserve PDFs.

## Current Features

- PDF graph extraction
- Blue dot masking/detection
- Gridline calibration
- Projection quantization (0.125 increments)
- KMeans year clustering
- CSV export

## Inputs

- SEP PDF releases

## Outputs

- Structured CSV files containing extracted projections

## Current Results

| SEP Release | Accuracy |
|---|---|
| March 2026 | ~100% |
| September 2025 | ~97% |

## Tech Stack

- Python
- OpenCV
- pandas
- scikit-learn
- PyMuPDF
- NumPy
- matplotlib
- Jupyter Notebook