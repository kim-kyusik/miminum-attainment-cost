# Data

This folder is intentionally empty in the repository.

The origin-destination (OD) travel-time matrix used in this project is too
large to host on GitHub, so it is **not included** here. To use this code,
supply your own data in the formats described below.

## 1. OD travel-time matrix

A plain CSV file, one row per origin-destination pair.

| Column          | Description                              |
|-----------------|-------------------------------------------|
| OriginName      | Origin identifier (e.g. block group ID)    |
| DestinationName | Destination / opportunity identifier       |
| Total_Time_Min  | Travel time in minutes                     |

Column names are configurable in `config.py` (`ORIGIN_COL`, `TIME_COL`).

If you have a separate OD matrix per opportunity category (e.g. one file
for grocery stores, one for hospitals), keep them as separate CSV files and
pass the relevant file path in as `source` when calling
`AccessibilityCalculator` methods -- each call loads only the file it needs.

You can also load a file yourself (e.g. with `pandas.read_parquet`, or after
some preprocessing) and pass the resulting DataFrame directly as `source`
instead of a path -- both are accepted everywhere.

## 2. Population data

One row per origin, with the population used as the denominator for
cumulative-opportunity ratios (e.g. population aged 45+).

| Column     | Description                                          |
|------------|-------------------------------------------------------|
| geoid      | Origin identifier (must match OriginName in the OD matrix) |
| population | Denominator population                                |

## Testing without real data

Run:

```bash
python generate_sample_data.py
```

This creates a small synthetic OD matrix and population table under
`data/`, so you can verify the code runs end-to-end before pointing it at
your own (much larger) dataset. These generated files are git-ignored and
will never be committed.
