"""Seri hizalama ve ortak tarih araligi yardimcilari."""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def has_data(series: Optional[pd.Series]) -> bool:
    return series is not None and len(series.dropna()) > 0


def filter_series_map(series_map: Dict[str, Optional[pd.Series]]) -> Dict[str, pd.Series]:
    return {key: series for key, series in series_map.items() if has_data(series)}


def latest_start(series_map: Dict[str, pd.Series]) -> pd.Timestamp:
    return max(series.index.min() for series in series_map.values())


def earliest_end(series_map: Dict[str, pd.Series]) -> pd.Timestamp:
    return min(series.index.max() for series in series_map.values())


def latest_end(series_map: Dict[str, pd.Series]) -> pd.Timestamp:
    return max(series.index.max() for series in series_map.values())


def common_index(*series_list: Optional[pd.Series]) -> pd.Index:
    valid = [series.index for series in series_list if has_data(series)]
    if not valid:
        return pd.Index([])
    common = valid[0]
    for index in valid[1:]:
        common = common.intersection(index)
    return common


def slice_from_start(series_map: Dict[str, pd.Series], start: pd.Timestamp) -> Dict[str, pd.Series]:
    return {key: series.loc[start:] for key, series in series_map.items()}


def slice_to_range(series_map: Dict[str, pd.Series], start: pd.Timestamp, end: pd.Timestamp) -> Dict[str, pd.Series]:
    return {key: series.loc[start:end] for key, series in series_map.items()}


def divide_by_rate(series: pd.Series, rate_series: pd.Series) -> pd.Series:
    common = series.index.intersection(rate_series.index)
    return series.loc[common] / rate_series.loc[common]


def multiply_by_rate(series: pd.Series, rate_series: pd.Series) -> pd.Series:
    common = series.index.intersection(rate_series.index)
    return series.loc[common] * rate_series.loc[common]