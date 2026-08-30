# Minimum Attainment Cost (MAC): Benchmark-Based Accessibility Metric

A lightweight, dependency-light toolkit for computing transportation
accessibility from an origin-destination (OD) travel-time matrix, built
around **Minimum Attainment Cost (MAC)** -- a benchmark-based accessibility
measure. Two conventional measures, shortest path and cumulative
opportunity, are included alongside it as supporting building blocks and
for comparison. 

This code is a product of "A National, Multidimensional Measure of Healthcare Accessibility for AD/ADRD Risk Factors" of the Gateway Exposome Coordinating Center (GECC) pilot Project Program funded by the National Institute on Aging U24 award. 

## Why MAC

The two classic accessibility measures both require the analyst to pick an
arbitrary parameter up front:

- **Shortest path** answers "how far to the nearest opportunity", but says
  nothing about how much capacity is there once you arrive.
- **Cumulative opportunity** counts opportunities within a fixed
  travel-time threshold (e.g. "jobs within 30 minutes") -- but that
  threshold is arbitrary, and a raw count doesn't account for how much
  demand (population) is competing for those opportunities. It also makes
  it hard to compare across opportunity categories with very different
  baseline supply (e.g. pharmacies vs. hospitals): the same 30-minute
  window means something completely different for each.

**MAC flips the question.** Instead of fixing a travel-time threshold and
seeing what you get, it fixes a target *ratio* -- opportunities per capita,
benchmarked against the study area as a whole -- and asks: **how many
minutes does this specific origin need before it reaches that same
standard?**

This has two useful properties:

- The threshold adapts to each origin, instead of being fixed arbitrarily.
- Because the benchmark ratio is defined per opportunity category, MAC
  values are comparable *across* categories -- a MAC of 40 minutes for
  pharmacies and a MAC of 40 minutes for hospitals mean the same thing:
  both places are 40 minutes from matching the regional average level of
  service for that category.

## How MAC works

For a given origin and a single opportunity category:

1. Start at threshold = 1 minute.
2. At each threshold, compute the local ratio:
   `ratio = (opportunities reachable within threshold) / population * 1000`
3. Increase the threshold until `ratio >= benchmark_ratio`.
4. The threshold at which this first happens is the origin's MAC.
5. If the benchmark is never reached within a maximum search window (e.g.
   180 minutes), the origin is flagged as not attaining the benchmark
   (given a sentinel value like `999`).

**Interpretation:** a low MAC means the benchmark is reached quickly (the
origin is well-served relative to the region); a high or "exceeded" MAC
means the origin has to travel much further than typical to reach the same
level of access.

Under the hood, each step of this search is a cumulative opportunity query
-- MAC is essentially cumulative opportunity accessibility run repeatedly
across increasing thresholds until a demand-adjusted benchmark is met,
rather than stopping at one threshold chosen in advance.

> This implementation computes MAC for a single opportunity category (one
> OD matrix + one benchmark ratio) at a time. To run it across several
> categories (e.g. multiple industry codes), call
> `minimum_attainment_cost()` once per category in your own loop -- see
> [Running MAC across multiple categories](#running-mac-across-multiple-opportunity-categories).

## Supporting metrics

Included alongside MAC, mainly as building blocks and reference points:

| Metric | Question it answers |
|---|---|
| **Shortest Path** | How many minutes to the *nearest* opportunity? |
| **Cumulative Opportunity** | How many opportunities are reachable within *N* minutes? |

Cumulative opportunity in particular is worth having on its own: it's the
query MAC calls internally at every threshold, and it's useful by itself
when you *do* want a fixed, conventional threshold (e.g. reporting "jobs
within 30 minutes" alongside MAC for context).

## Project structure

```
accessibility-metrics/
├── accessibility_metrics.py   # AccessibilityCalculator: MAC + shortest path + cumulative opportunity
├── config.py                  # Paths and parameters you edit locally
├── generate_sample_data.py    # Creates small synthetic data for testing
├── example_usage.py           # End-to-end example, MAC first
├── requirements.txt
├── LICENSE                    # MIT license
├── CITATION.cff                # Citation metadata (fill in before publishing)
├── data/
│   └── README.md              # Expected data schema (no real data included)
└── outputs/                   # Results are written here (git-ignored)
```

## A note on data

**The real OD travel-time matrix is not included in this repository** --
these matrices are typically millions of rows and far too large for git.
Instead:

- `data/README.md` documents the exact schema your OD matrix and
  population data need.
- `generate_sample_data.py` creates a small synthetic dataset so you can
  run and verify the code before plugging in your own data.
- `config.py` is where you point the code at your real files once you have
  them locally.

## Installation

```bash
git clone <this-repo-url>
cd accessibility-metrics
pip install -r requirements.txt
```

## Usage

### 1. Try it with sample data

```bash
python generate_sample_data.py
python example_usage.py
```

### 2. Compute MAC on your own data

1. Place your OD matrix and population files according to the schema in
   `data/README.md`.
2. Update the paths and column names in `config.py`.
3. Use `AccessibilityCalculator`:

```python
import pandas as pd
from accessibility_metrics import AccessibilityCalculator

calc = AccessibilityCalculator(origin_col="OriginName", time_col="Total_Time_Min")

population = pd.read_csv("data/population.csv")

# Minimum Attainment Cost: minutes needed to reach a benchmark ratio
mac = calc.minimum_attainment_cost(
    "data/od_matrix/hospital.csv",
    population_df=population,
    benchmark_ratio=5.0,       # e.g. 5 opportunities per 1,000 residents
    population_col="population",
    id_col="geoid",
    max_threshold=180,
    exceed_value=999,
)
```

### 3. Supporting metrics (optional)

```python
# Shortest path: minutes to the nearest opportunity
shortest = calc.shortest_path("data/od_matrix/hospital.csv")

# Cumulative opportunity: opportunities reachable within a fixed 45-minute window
cumopp = calc.cumulative_opportunity("data/od_matrix/hospital.csv", threshold=45)
```

Every method also accepts an already-loaded DataFrame instead of a path
(e.g. `calc.shortest_path(my_df)`), which is useful if your OD data comes
from somewhere other than a plain CSV.

### Running MAC across multiple opportunity categories

If you have several OD matrices (one per category) and a benchmark ratio
for each, loop over them yourself:

```python
results = {}
for category, (source, benchmark) in category_config.items():
    results[category] = calc.minimum_attainment_cost(
        source,
        population_df=population,
        benchmark_ratio=benchmark,
        population_col="population",
    )
```

## Dependencies

- pandas
- numpy

## Related Work

| Type  | Name                                                         | Description                                             |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------- |
| Code  | [Adaptive OD Cost Matrix](https://github.com/kim-kyusik/adaptive-od-cost-matrix) | Computes the OD travel-time matrices used as input here |
| Data  | [GECC Dataverse](TBD)                                        | Published dataset files from this project               |
| Paper | TBD                                                          | TBD                                                     |

## License

MIT -- see [LICENSE](LICENSE). Free to use, modify, and redistribute with
attribution.

## Citation

If you use this code (or the MAC method) in your work, please cite it --
see [CITATION.cff](CITATION.cff). 

