# FOMC SEP Extraction Pipeline

Computer vision pipeline for automatically fetching and extracting FOMC 
Summary of Economic Projections (SEP) dot plot data from Federal Reserve PDFs.

## Current Features
- Dynamic PDF fetching via standardized Fed URL pattern
- Auto-detection of 4 vs 5 year clusters (March/June vs September/December)
- Auto-calibration of grid spacing per PDF
- Blue dot masking and detection
- Projection quantization (0.125% increments)
- KMeans year clustering
- CSV export with SEP meeting date column
- Append-based CSV that grows over time across all meetings

## Inputs
- SEP meeting dates (manually updated in Cell 2 when Fed publishes new calendar)
- Latest date set in Cell 3 each time a new SEP is released

## Outputs
- `outputs/projections.csv` — all extracted projections with columns:
  - `Year` — projection year or "Longer Run"
  - `Projection` — federal funds rate projection
  - `SEP_Date` — meeting date the projection came from

## Current Data Coverage
- March 2025 through June 2026 (6 SEPs)
- Updates each time a new SEP is released (next: September 16, 2026)

## Tech Stack
- Python
- OpenCV
- pandas
- scikit-learn
- PyMuPDF
- NumPy
- matplotlib
- Jupyter Notebook
