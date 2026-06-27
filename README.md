# FOMC SEP Extraction Pipeline

Computer vision pipeline for automatically fetching and extracting FOMC 
Summary of Economic Projections (SEP) dot plot data from Federal Reserve PDFs.

## How to Run

```bash
cd notebooks
python3 run_all_seps.py
```

## Features
- Automatically fetches SEP PDFs from the Fed website using standardized URL pattern
- Auto-detects 4 vs 5 year clusters (March/June vs September/December)
- Auto-calibrates grid spacing per PDF
- Handles different y-axis ranges across years (4.0% in 2021 up to 7.0% in 2023-2024)
- Blue dot detection with erosion-based separation for touching dots
- Projection quantization at 0.125% increments
- CSV appends over time — never overwrites historical data

## Data Coverage
- March 2021 through June 2026 (22 SEPs total)
- Next update: September 16, 2026

## Output
`outputs/projections.csv` with columns:
- `Year` — projection year or "Longer Run"
- `Projection` — federal funds rate projection
- `SEP_Date` — meeting date the projection came from

## Updating
When a new SEP is released, add the date to `ALL_DATES` in `run_all_seps.py` if not already there, then run the script. The new data appends automatically.

## Tech Stack
- Python, OpenCV, PyMuPDF, pandas, scikit-learn, NumPy
