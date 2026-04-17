"""Tab modulleri paket baslatici ve ortak TabContext tanimi."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, TYPE_CHECKING

import pandas as pd

from app.config import SignalThresholds
from app.data_preparer import PreparedSeries

if TYPE_CHECKING:
    from app.market_data import CurrentPrices


@dataclass
class TabContext:
    """Tum grafik tab'lari tarafindan paylasilan uygulama baglami.

    ONEMLI: Programin guncel gostergeleri 'current' nesnesinden,
    tarihsel veriler 'series' nesnesinden alinir.
    """

    series: PreparedSeries
    current: "CurrentPrices"   # Program genelinde kullanilan tek cozulmus guncel gorunum
    history_raw: Dict           # Ham yfinance DataFrames (candlestick icin)
    spread_hist: Optional[pd.Series]
    thresholds: SignalThresholds
    font_size: int
    chart_height: int
    grafik_kilidi: bool
