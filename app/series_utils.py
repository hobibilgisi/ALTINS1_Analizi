"""Seri hizalama ve ortak tarih araligi yardimcilari."""

from __future__ import annotations

from typing import Optional

import pandas as pd


def has_data(series: Optional[pd.Series]) -> bool:
    return series is not None and len(series.dropna()) > 0


def common_index(*series_list: Optional[pd.Series]) -> pd.Index:
    valid = [series.index for series in series_list if has_data(series)]
    if not valid:
        return pd.Index([])
    common = valid[0]
    for index in valid[1:]:
        common = common.intersection(index)
    return common


def divide_by_rate(series: pd.Series, rate_series: pd.Series) -> pd.Series:
    common = series.index.intersection(rate_series.index)
    return series.loc[common] / rate_series.loc[common]


def multiply_by_rate(series: pd.Series, rate_series: pd.Series) -> pd.Series:
    common = series.index.intersection(rate_series.index)
    return series.loc[common] * rate_series.loc[common]