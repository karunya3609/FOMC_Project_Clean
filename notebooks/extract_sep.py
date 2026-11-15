"""
Extract the dot plot data for ONE FOMC SEP date.

Usage (from the notebooks/ folder):
    python3 extract_sep.py 2026-12-09
    python3 extract_sep.py 2026-12-09 --dry-run     # print only, don't save

This is just a wrapper around the existing pipeline in run_2015-plus.py
(download_sep + process_sep). Output rows are identical to what run_2015-plus.py
produces for that date, and they are saved the same way (appended to the CSV).

The only addition: if the date is already in the CSV, it stops instead of
appending a second copy.

Before a new meeting works, its (year, month) must be in Y_AXIS_MAX inside
run_2015-plus.py.
"""

import argparse
import importlib.util
import os
import sys
from datetime import date, datetime

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "..", "outputs", "projections.csv")


def already_in_csv(sep_date, csv_path=CSV_PATH):
    """True if this date already has rows (checks both 2026-09-16 and 9/16/2026 formats)."""
    if not os.path.exists(csv_path):
        return False
    dates = set(pd.read_csv(csv_path, usecols=["SEP_Date"])["SEP_Date"].astype(str))
    us_style = f"{sep_date.month}/{sep_date.day}/{sep_date.year}"
    return str(sep_date) in dates or us_style in dates


def save_to_csv(df, csv_path=CSV_PATH):
    """Same logic as save_to_csv() in the existing scripts."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)


def load_pipeline():
    path = os.path.join(HERE, "run_2015-plus.py")
    if not os.path.exists(path):
        sys.exit(f"Can't find {path}. Keep extract_sep.py in the same folder as run_2015-plus.py.")
    spec = importlib.util.spec_from_file_location("pipeline_2015_plus", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    parser = argparse.ArgumentParser(description="Extract SEP dot plot data for one FOMC date.")
    parser.add_argument("date", help="SEP release date, YYYY-MM-DD (e.g. 2026-12-09)")
    parser.add_argument("--dry-run", action="store_true", help="print results, don't save")
    args = parser.parse_args()

    try:
        sep_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        sys.exit("Date must look like 2026-12-09")
    if sep_date > date.today():
        sys.exit(f"{sep_date} is in the future, nothing to download yet.")
    if sep_date.year < 2015:
        sys.exit("This script is for 2015+ dates (it uses the run_2015-plus.py logic).")

    os.chdir(HERE)  # the pipeline uses relative paths (sep_pdfs/, page.png)
    pipe = load_pipeline()

    if (sep_date.year, sep_date.month) not in pipe.Y_AXIS_MAX:
        sys.exit(
            f"No Y_AXIS_MAX entry for {sep_date.year}-{sep_date.month:02d}. "
            "Add it in run_2015-plus.py, then retry."
        )

    print(f"-- {sep_date} --")
    pdf_path = pipe.download_sep(sep_date)
    if not pdf_path:
        sys.exit("Could not get the PDF (not published yet, wrong date, or network issue).")

    df = pipe.process_sep(sep_date, pdf_path)
    if df is None:
        sys.exit("Extraction failed, nothing written.")

    print(df.to_string())

    if args.dry_run:
        print("\nDry run: CSV not modified.")
        return
    if already_in_csv(sep_date):
        sys.exit(f"\n{sep_date} is already in the CSV. Nothing written (to avoid duplicates).")

    save_to_csv(df)
    print(f"\nSaved {len(df)} rows -> {os.path.abspath(CSV_PATH)}")


if __name__ == "__main__":
    main()