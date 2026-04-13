"""Tab modülleri paket başlatıcı ve ortak TabContext tanımı."""

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from app.config import SignalThresholds
from app.data_preparer import PreparedSeries


@dataclass
class TabContext:
    """Tüm grafik tab'ları tarafından paylaşılan uygulama bağlamı."""

    series: PreparedSeries
    prices: Dict
    history: Dict
    spread_hist: Optional[pd.Series]
    thresholds: SignalThresholds
    font_size: int
    chart_height: int
    grafik_kilidi: bool
