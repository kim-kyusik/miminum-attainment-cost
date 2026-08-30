"""
accessibility_metrics.py

Core transportation accessibility metrics computed from an Origin-Destination
(OD) travel-time matrix, using plain pandas -- no external database required.

Implements three measures:

1. Shortest Path Accessibility
   The travel time from each origin to its nearest opportunity.

2. Cumulative Opportunity Accessibility
   The number of opportunities reachable from each origin within a given
   travel-time threshold.

3. Minimum Attainment Cost (MAC)
   The minimum travel-time threshold at which an origin's local cumulative
   opportunity ratio first meets or exceeds a benchmark ratio (e.g. a
   regional or national average of opportunities per 1,000 population).

The OD matrix can be supplied either as a path to a CSV file or as an
already-loaded pandas DataFrame -- whichever is more convenient. Nothing
here depends on any particular database engine.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import pandas as pd

ODSource = Union[str, "os.PathLike[str]", pd.DataFrame]


@dataclass
class AccessibilityCalculator:
    """
    Computes accessibility metrics from an OD travel-time matrix using pandas.

    Parameters
    ----------
    origin_col : str
        Column name identifying the origin in the OD matrix.
    time_col : str
        Column name for travel time, in minutes.
    """

    origin_col: str = "OriginName"
    time_col: str = "Total_Time_Min"

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #
    def _load(self, source: ODSource) -> pd.DataFrame:
        """
        Load an OD matrix.

        Accepts either a CSV file path or an already-loaded DataFrame (in
        which case it is returned as-is -- useful for avoiding repeated
        disk reads, e.g. inside `minimum_attainment_cost`).
        """
        if isinstance(source, pd.DataFrame):
            return source
        return pd.read_csv(source)

    # ------------------------------------------------------------------ #
    # 1. Shortest path accessibility
    # ------------------------------------------------------------------ #
    def shortest_path(self, source: ODSource, threshold: Optional[float] = None) -> pd.DataFrame:
        """
        Minimum travel time from each origin to its nearest opportunity.

        Parameters
        ----------
        source : str, path, or pd.DataFrame
            OD matrix CSV path, or an already-loaded DataFrame.
        threshold : float, optional
            Cap on travel time in minutes. If provided, opportunities beyond
            this time are excluded before taking the minimum. If None, the
            true nearest opportunity is returned regardless of distance.

        Returns
        -------
        pd.DataFrame
            Columns: [origin_id, access_time].
        """
        od = self._load(source)
        if threshold is not None:
            od = od[od[self.time_col] <= threshold]

        result = (
            od.groupby(self.origin_col)[self.time_col]
            .min()
            .reset_index()
            .rename(columns={self.origin_col: "origin_id", self.time_col: "access_time"})
        )
        return result

    # ------------------------------------------------------------------ #
    # 2. Cumulative opportunity accessibility
    # ------------------------------------------------------------------ #
    def cumulative_opportunity(self, source: ODSource, threshold: float) -> pd.DataFrame:
        """
        Number of opportunities reachable from each origin within
        `threshold` minutes of travel time.

        Parameters
        ----------
        source : str, path, or pd.DataFrame
            OD matrix CSV path, or an already-loaded DataFrame.
        threshold : float
            Travel-time threshold in minutes (e.g. 30, 45, 60). Required.

        Returns
        -------
        pd.DataFrame
            Columns: [origin_id, access_count].
        """
        if threshold is None:
            raise ValueError(
                "`threshold` is required for cumulative opportunity accessibility, e.g. 30, 45, 60."
            )

        od = self._load(source)
        within = od[od[self.time_col] <= threshold]

        result = (
            within.groupby(self.origin_col)
            .size()
            .reset_index(name="access_count")
            .rename(columns={self.origin_col: "origin_id"})
        )
        return result

    # ------------------------------------------------------------------ #
    # 3. Minimum Attainment Cost (MAC)
    # ------------------------------------------------------------------ #
    def minimum_attainment_cost(
        self,
        source: ODSource,
        population_df: pd.DataFrame,
        benchmark_ratio: float,
        population_col: str,
        id_col: str = "geoid",
        scale: float = 1000,
        max_threshold: int = 180,
        exceed_value: float = 999,
        log_every: int = 30,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Minimum Attainment Cost (MAC): the smallest travel-time threshold at
        which an origin's local cumulative-opportunity ratio first meets or
        exceeds a benchmark ratio.

        The local ratio at threshold t is:

            ratio(t) = (opportunities reachable within t minutes) / population * scale

        MAC is the smallest t for which ratio(t) >= benchmark_ratio. Origins
        that never reach the benchmark within `max_threshold` minutes are
        assigned `exceed_value`.

        The OD matrix is loaded once (if given as a path) and then filtered
        in memory at each threshold, so this does not re-read the file on
        every iteration.

        Parameters
        ----------
        source : str, path, or pd.DataFrame
            OD matrix for a single opportunity category (e.g. one industry
            or one facility type). To compute MAC for multiple categories,
            call this method once per category with the category's own
            `source` and `benchmark_ratio`.
        population_df : pd.DataFrame
            Must contain `id_col` and `population_col`, one row per origin.
        benchmark_ratio : float
            Target ratio to attain (e.g. a national-average opportunities
            per 1,000 residents figure).
        population_col : str
            Column in `population_df` holding the denominator population
            (e.g. population aged 45+).
        id_col : str
            Column identifying each origin. Must match the values produced
            by `origin_col` in the OD matrix.
        scale : float
            Multiplier applied to the ratio (1000 for "per 1,000 people").
        max_threshold : int
            Largest travel time (minutes) to search before giving up.
        exceed_value : float
            Value assigned to origins that never reach the benchmark.
        log_every : int
            Print progress every N minutes of threshold searched.
        verbose : bool
            Whether to print progress messages.

        Returns
        -------
        pd.DataFrame
            Columns: [id_col, "mac"].
        """
        od = self._load(source)  # loaded once, reused at every threshold below

        origins = pd.DataFrame({id_col: population_df[id_col].unique()})
        origins["mac"] = np.nan

        for threshold in range(1, max_threshold + 1):
            counts = self.cumulative_opportunity(od, threshold)
            counts = counts.rename(columns={"origin_id": id_col, "access_count": "count"})

            merged = counts.merge(population_df[[id_col, population_col]], on=id_col, how="left")
            merged["ratio"] = merged["count"] / merged[population_col] * scale

            newly_met = merged.loc[merged["ratio"] >= benchmark_ratio, id_col]
            mask = origins[id_col].isin(newly_met) & origins["mac"].isna()
            origins.loc[mask, "mac"] = threshold

            if origins["mac"].notna().all():
                if verbose:
                    print(f"All origins reached the benchmark by threshold={threshold} min.")
                break

            if verbose and threshold % log_every == 0:
                done = origins["mac"].notna().sum()
                print(f"threshold={threshold} min completed ({done}/{len(origins)} origins done).")

        origins.loc[origins["mac"].isna(), "mac"] = exceed_value
        return origins
