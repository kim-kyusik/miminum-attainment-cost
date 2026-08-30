"""
Project configuration.

Edit the paths and parameters below to point at your own OD travel-time
matrix and population data. Real data is NOT included in this repository
(see data/README.md) because OD matrices are typically far too large for
git.
"""

from pathlib import Path

# --- Directories -----------------------------------------------------------
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(exist_ok=True)

# --- Data sources ------------------------------------------------------------
# Point this at your own OD matrix CSV. If you have one OD matrix per
# opportunity category, just swap this path (or pass a different `source`
# straight into AccessibilityCalculator -- a CSV path or a DataFrame both work).
OD_MATRIX_PATH = DATA_DIR / "od_matrix" / "sample_od_matrix.csv"

# Population data: one row per origin, with the denominator population used
# for cumulative-opportunity ratios (e.g. population aged 45+).
POPULATION_PATH = DATA_DIR / "sample_population.csv"

# --- Column names in your OD matrix ------------------------------------------
ORIGIN_COL = "OriginName"
TIME_COL = "Total_Time_Min"

# --- Minimum Attainment Cost (MAC) parameters --------------------------------
MAX_THRESHOLD = 180       # minutes; largest travel time to search
EXCEED_THRESHOLD = 999    # value assigned when the benchmark is never reached
BENCHMARK_RATIO = 5.0     # example: 5 opportunities per 1,000 people
