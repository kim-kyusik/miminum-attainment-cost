"""
generate_sample_data.py

Creates a small synthetic OD travel-time matrix and population table so the
accessibility metrics can be run and verified without any real (and likely
much larger) data.

Usage
-----
    python generate_sample_data.py

The generated files are written under `data/` and are git-ignored -- they
exist only for local testing.
"""

import numpy as np
import pandas as pd

import config

np.random.seed(42)

N_ORIGINS = 20
N_DESTINATIONS = 15


def main():
    origin_ids = [f"origin_{i:03d}" for i in range(N_ORIGINS)]
    dest_ids = [f"dest_{j:03d}" for j in range(N_DESTINATIONS)]

    # Synthetic OD matrix: every origin-destination pair with a random travel time
    rows = [
        (o, d, round(float(np.random.uniform(2, 90)), 1))
        for o in origin_ids
        for d in dest_ids
    ]
    od_matrix = pd.DataFrame(rows, columns=["OriginName", "DestinationName", "Total_Time_Min"])

    # Synthetic population table
    population = pd.DataFrame({
        "geoid": origin_ids,
        "population": np.random.randint(500, 5000, size=N_ORIGINS),
    })

    config.OD_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    od_matrix.to_csv(config.OD_MATRIX_PATH, index=False)
    population.to_csv(config.POPULATION_PATH, index=False)

    print(f"Sample OD matrix written to {config.OD_MATRIX_PATH} ({len(od_matrix)} rows)")
    print(f"Sample population written to {config.POPULATION_PATH} ({len(population)} rows)")


if __name__ == "__main__":
    main()
