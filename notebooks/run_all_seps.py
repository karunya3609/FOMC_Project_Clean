"""
run_all_seps.py
===============
Run this once from Terminal to process all SEP dates automatically.
It loops through every date, downloads the PDF, runs the full pipeline,
and appends results to projections.csv.

Usage:
    cd /Users/knimm/Documents/FOMC_Project_Clean/notebooks
    python3 run_all_seps.py
"""

import os
import requests
import fitz
import cv2
import numpy as np
import pandas as pd
from datetime import date
from sklearn.cluster import KMeans

# ── CONFIG ────────────────────────────────────────────────────────────
BASE_URL   = "https://www.federalreserve.gov/monetarypolicy/files/"
SAVE_DIR   = "sep_pdfs"
OUTPUT_DIR = "/Users/knimm/Documents/FOMC_Project_Clean/outputs"
CSV_PATH   = os.path.join(OUTPUT_DIR, "projections.csv")

top    = 410
bottom = 2200
left   = 200
right  = 2200

Y_AXIS_MAX = {
    (2021, 3): 4.0, (2021, 6): 4.0, (2021, 9): 4.0, (2021, 12): 4.0,
    (2022, 3): 4.0, (2022, 6): 5.0, (2022, 9): 6.0, (2022, 12): 6.0,
    (2023, 3): 6.0, (2023, 6): 7.0, (2023, 9): 7.0, (2023, 12): 7.0,
    (2024, 3): 7.0, (2024, 6): 7.0, (2024, 9): 7.0, (2024, 12): 7.0,
    (2025, 3): 6.0, (2025, 6): 6.0, (2025, 9): 6.0, (2025, 12): 6.0,
    (2026, 3): 6.0, (2026, 6): 6.0, (2026, 9): 6.0, (2026, 12): 6.0,
}

ALL_DATES = [
    date(2021, 3, 17), date(2021, 6, 16), date(2021, 9, 22), date(2021, 12, 15),
    date(2022, 3, 16), date(2022, 6, 15), date(2022, 9, 21), date(2022, 12, 14),
    date(2023, 3, 22), date(2023, 6, 14), date(2023, 9, 20), date(2023, 12, 13),
    date(2024, 3, 20), date(2024, 6, 12), date(2024, 9, 18), date(2024, 12, 18),
    date(2025, 3, 19), date(2025, 6, 18), date(2025, 9, 17), date(2025, 12, 10),
    date(2026, 3, 18), date(2026, 6, 17),
]

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── HELPERS ───────────────────────────────────────────────────────────

def download_sep(sep_date):
    local_path = os.path.join(SAVE_DIR, f"SEP_{sep_date}.pdf")
    if os.path.exists(local_path):
        print(f"  [CACHE]  {local_path}")
        return local_path
    url = BASE_URL + f"fomcprojtabl{sep_date.strftime('%Y%m%d')}.pdf"
    print(f"  [FETCH]  {url}")
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(r.content)
        print(f"  [OK]     Saved → {local_path}")
        return local_path
    elif r.status_code == 404:
        print(f"  [SKIP]   Not published yet (404)")
        return None
    else:
        print(f"  [ERROR]  HTTP {r.status_code}")
        return None


def detect_dots(mask, sep_date):
    # Older PDFs have larger dots that need more erosion to separate
    # Newer PDFs have smaller dots that need less erosion
    if sep_date.year <= 2024:
        kernel = np.ones((5, 5), np.uint8)
        iterations = 2
    else:
        kernel = np.ones((3, 3), np.uint8)
        iterations = 1

    eroded = cv2.erode(mask, kernel, iterations=iterations)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded, connectivity=8)
    centers = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 10:
            centers.append((centroids[i][0], centroids[i][1]))
    return centers
    

def get_calibration(unique_y, sep_date):
    gaps = [unique_y[i+1] - unique_y[i] for i in range(len(unique_y)-1)]
    median_gap = np.median(gaps)

    top_grid_y = None
    for i in range(len(unique_y) - 1):
        if abs((unique_y[i+1] - unique_y[i]) - median_gap) < 10:
            top_grid_y = unique_y[i]
            break

    pixels_per_0125 = median_gap / 2
    top_grid_value  = Y_AXIS_MAX[(sep_date.year, sep_date.month)]
    return top_grid_y, pixels_per_0125, top_grid_value


def y_to_rate(y, top_grid_y, pixels_per_0125, top_grid_value):
    steps   = (y - top_grid_y) / pixels_per_0125
    rate    = top_grid_value - (steps * 0.125)
    rounded = round(rate / 0.125) * 0.125
    return rounded


def process_sep(sep_date, pdf_path):
    print(f"  Processing...")

    n_clusters    = 5 if sep_date.month in (9, 12) else 4
    starting_year = sep_date.year

    # Render page 4 (index 3)
    doc  = fitz.open(pdf_path)
    page = doc[3]
    pix  = page.get_pixmap(matrix=fitz.Matrix(4, 4))
    pix.save("page.png")
    doc.close()

    # Load and crop
    img  = cv2.imread("page.png")
    crop = img[top:bottom, left:right]

    # Detect grid lines
    gray  = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                             threshold=100, minLineLength=1000, maxLineGap=20)

    y_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 5:
                y_lines.append(y1)

    unique_y = []
    for y in sorted(y_lines):
        if not unique_y or abs(y - unique_y[-1]) > 10:
            unique_y.append(y)

    top_grid_y, pixels_per_0125, top_grid_value = get_calibration(unique_y, sep_date)

    # Detect blue dots
    hsv        = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask       = cv2.inRange(hsv, np.array([80, 50, 50]), np.array([130, 255, 255]))
    kernel     = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)
    centers = detect_dots(mask_clean, sep_date)

    if not centers:
        print(f"  [WARN] No dots detected for {sep_date}")
        return None

    # KMeans clustering
    x_values = np.array([d[0] for d in centers]).reshape(-1, 1)
    kmeans   = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
    kmeans.fit(x_values)
    x_cluster_centers = list(sorted(kmeans.cluster_centers_.flatten()))

    # Build dataframe
    rows = []
    for cx, cy in centers:
        nearest       = min(x_cluster_centers, key=lambda c: abs(cx - c))
        cluster_index = x_cluster_centers.index(nearest)
        year          = str(starting_year + cluster_index) if cluster_index < n_clusters - 1 else "Longer Run"
        rows.append({"Year": year, "Projection": y_to_rate(cy, top_grid_y, pixels_per_0125, top_grid_value)})

    df_sorted             = pd.DataFrame(rows).sort_values(["Year", "Projection"])
    df_sorted["SEP_Date"] = str(sep_date)
    return df_sorted


def save_to_csv(df_sorted):
    if os.path.exists(CSV_PATH):
        df_sorted.to_csv(CSV_PATH, mode="a", header=False, index=False)
        print(f"  [CSV]    Appended → {CSV_PATH}")
    else:
        df_sorted.to_csv(CSV_PATH, index=False)
        print(f"  [CSV]    Created  → {CSV_PATH}")


# ── MAIN LOOP ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    today = date.today()

    for sep_date in ALL_DATES:
        print(f"\n── {sep_date} ──────────────────────────────")

        if sep_date > today:
            print(f"  [FUTURE] Not released yet, skipping.")
            continue

        pdf_path = download_sep(sep_date)
        if not pdf_path:
            continue

        df = process_sep(sep_date, pdf_path)
        if df is not None:
            print(df.to_string())
            save_to_csv(df)

    print("\n✓ Done. CSV saved to:", CSV_PATH)