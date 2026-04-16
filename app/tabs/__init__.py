"""Tab modulleri paket baslatici ve ortak TabContext tanimi."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, TYPE_CHECKING

import pandas as pd

from app.config import SignalThresholds
from app.data_preparer import PreparedSeries

if TYPE_CHECKING:
    from app.market_data import LivePrices


@dataclass
class TabContext:
    """Tum grafik tab'lari tarafindan paylasilan uygulama baglami.

    ONEMLI: Anlik fiyatlar 'live' nesnesinden, tarihsel seriler 'series'
    nesnesinden alinir. Her ikisi de ayni kaynaktan turetilmistir,
    tutarsizlik YOKTUR.
    """

    series: PreparedSeries
    live: LivePrices            # Merkezi anlik fiyatlar
    history_raw: Dict           # Ham yfinance DataFrames (candlestick icin)
    spread_hist: Optional[pd.Series]
    thresholds: SignalThresholds
    font_size: int
    chart_height: int
    grafik_kilidi: bool
