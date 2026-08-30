"""
example_usage.py

Demonstrates the three accessibility metrics on sample data.

Run `python generate_sample_data.py` first if `data/sample_od_matrix.csv`
does not exist yet, or edit `config.py` to point at your own OD matrix.

Usage
-----
    python example_usage.py
"""

import pandas as pd

import config
from accessibility_metrics import AccessibilityCalculator


def main():
    if not config.OD_MATRIX_PATH.exists():
        raise FileNotFoundError(
            f"{config.OD_MATRIX_PATH} not found.\n"
            f"Run `python generate_sample_data.py` to create sample data, "
            f"or point config.OD_MATRIX_PATH at your own OD matrix CSV."
        )

    calc = AccessibilityCalculator(origin_col=config.ORIGIN_COL, time_col=config.TIME_COL)
    source = config.OD_MATRIX_PATH  # a CSV path; a DataFrame works too

    # 1. Shortest path accessibility -----------------------------------------
    shortest = calc.shortest_path(source)
    print("\n--- Shortest path accessibility (minutes to nearest opportunity) ---")
    print(shortest.head())

    # 2. Cumulative opportunity accessibility (e.g. within 30 minutes) -------
    cumopp = calc.cumulative_opportunity(source, threshold=30)
    print("\n--- Cumulative opportunity accessibility (count within 30 min) ---")
    print(cumopp.head())

    # 3. Minimum Attainment Cost ----------------------------------------------
    population = pd.read_csv(config.POPULATION_PATH)
    mac = calc.minimum_attainment_cost(
        source,
        population_df=population,
        benchmark_ratio=config.BENCHMARK_RATIO,
        population_col="population",
        id_col="geoid",
        max_threshold=config.MAX_THRESHOLD,
        exceed_value=config.EXCEED_THRESHOLD,
    )
    print("\n--- Minimum Attainment Cost (minutes needed to reach benchmark ratio) ---")
    print(mac.head())

    out_path = config.OUTPUT_DIR / "mac_result.csv"
    mac.to_csv(out_path, index=False)
    print(f"\nSaved MAC results to {out_path}")


if __name__ == "__main__":
    main()
