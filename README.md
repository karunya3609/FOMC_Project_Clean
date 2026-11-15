# FOMC SEP Dot Plot Extraction

Extracts individual participant projections (the dots) from the Federal Reserve's
Summary of Economic Projections (SEP) PDFs, January 2012 through September 2026.

## Output
`outputs/projections.csv` has columns `Year`, `Projection`, `SEP_Date`
(59 meetings, 4,404 rows). `Year` is the projection year or `Longer Run`.

## Setup
    pip install opencv-python pymupdf numpy pandas scikit-learn requests

## Usage

Add a new meeting (2015 or later):

    cd notebooks
    python3 extract_sep.py 2026-12-09              # extract and append to the CSV
    python3 extract_sep.py 2026-12-09 --dry-run    # print only, don't save

Before a new meeting works, add its (year, month) to `Y_AXIS_MAX` in
`run_2015-plus.py` (the top gridline value on the chart). If the date is already
in the CSV the script stops rather than adding duplicates. New rows use the date
format 2026-12-09.

Rebuild everything from scratch:

    rm outputs/projections.csv      # required: the scripts append
    cd notebooks && python3 run_all_seps.py

Running `run_all_seps.py` twice without deleting the CSV duplicates every row.

## Files
- `notebooks/run_2012-2014.py` - extraction for 2012-2014 (includes Jan and Apr 2012)
- `notebooks/run_2015-plus.py` - extraction for 2015 onward
- `notebooks/run_all_seps.py` - runs both
- `notebooks/extract_sep.py` - extract one meeting by date

