"""
ALTINS1 Analiz — Sinyal Motoru
Makas analizine göre alım/satım sinyalleri üretir.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import pandas as pd

from app.config import SignalThresholds

logger = logging.getLogger(__name__)


class SignalType(Enum):
    STRONG_BUY = "GÜÇLÜ ALIM"
    BUY = "ALIM"
    NEUTRAL = "NÖTR"
    SELL = "SATIM"
    STRONG_SELL = "GÜÇLÜ SATIM"


@dataclass
class Signal:
    """Tek bir sinyal kaydı."""
    timestamp: str
    signal_type: SignalType
    spread_pct: float
    altins1_price: float
    gram_gold_tl: float
    message: str


def evaluate_signal(spread_pct: float, thresholds: Optional[SignalThresholds] = None) -> SignalType:
    """Mevcut makasa göre sinyal türünü belirler.

    Args:
        spread_pct: Güncel makas yüzdesi
        thresholds: Eşik değerleri (varsayılan: SignalThresholds())

    Returns:
        SignalType enum değeri
    """
    if thresholds is None:
        thresholds = SignalThresholds()

    if spread_pct <= thresholds.strong_buy:
        return SignalType.STRONG_BUY
    elif spread_pct <= thresholds.buy_threshold:
        return SignalType.BUY
    elif spread_pct >= thresholds.strong_sell:
        return SignalType.STRONG_SELL
    elif spread_pct >= thresholds.sell_threshold:
        return SignalType.SELL
    else:
        return SignalType.NEUTRAL


def generate_signal_message(signal_type: SignalType, spread_pct: float) -> str:
    """Sinyal tipine göre kullanıcıya gösterilecek mesaj üretir."""
    messages = {
        SignalType.STRONG_BUY: f"🟢 GÜÇLÜ ALIM SİNYALİ! Makas: %{spread_pct:.2f} — ALTINS1, gram altından ucuz!",
        SignalType.BUY: f"🟡 ALIM SİNYALİ. Makas: %{spread_pct:.2f} — ALTINS1, gram altına çok yakın.",
        SignalType.NEUTRAL: f"⚪ NÖTR. Makas: %{spread_pct:.2f} — Normal aralıkta.",
        SignalType.SELL: f"🟠 SATIM SİNYALİ. Makas: %{spread_pct:.2f} — ALTINS1 primli, satış düşünülebilir.",
        SignalType.STRONG_SELL: f"🔴 GÜÇLÜ SATIM SİNYALİ! Makas: %{spread_pct:.2f} — ALTINS1 aşırı primli!",
    }
    return messages.get(signal_type, "Sinyal değerlendirilemedi.")


def evaluate_spread_series(
    spread_series: pd.Series,
    thresholds: Optional[SignalThresholds] = None,
) -> pd.Series:
    """Tarihsel makas serisini sinyal serisine dönüştürür.

    Returns:
        SignalType değerlerinden oluşan seri
    """
    if thresholds is None:
        thresholds = SignalThresholds()
    return spread_series.apply(lambda s: evaluate_signal(s, thresholds))
