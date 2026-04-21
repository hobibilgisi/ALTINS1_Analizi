"""
ALTINS1 Analiz — Sinyal Motoru
Makas, hacim ve BIST100 korelasyon sinyalleri üretir.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import pandas as pd

from app.config import SignalThresholds

logger = logging.getLogger(__name__)


class SignalType(Enum):
    STRONG_BUY = "GÜÇLÜ ALIM"
    BUY = "ALIM"
    NEUTRAL = "NÖTR"
    SELL = "SATIM"
    STRONG_SELL = "GÜÇLÜ SATIM"


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
        SignalType.STRONG_BUY: f"🟢 GÜÇLÜ ALIM SİNYALİ! Makas: %{spread_pct:.2f} — Makas tarihsel ortalamanın çok altında, ALTINS1 görece ucuz!",
        SignalType.BUY: f"🟡 ALIM SİNYALİ. Makas: %{spread_pct:.2f} — Makas ortalamanın altında, alım fırsatı olabilir.",
        SignalType.NEUTRAL: f"⚪ NÖTR. Makas: %{spread_pct:.2f} — Normal aralıkta.",
        SignalType.SELL: f"🟠 SATIM SİNYALİ. Makas: %{spread_pct:.2f} — Makas ortalamanın üstünde, satış düşünülebilir.",
        SignalType.STRONG_SELL: f"🔴 GÜÇLÜ SATIM SİNYALİ! Makas: %{spread_pct:.2f} — Makas tarihsel ortalamanın çok üstünde, ALTINS1 aşırı primli!",
    }
    return messages.get(signal_type, "Sinyal değerlendirilemedi.")


# ── Hacim Dikkat Sinyali ───────────────────────────────────────

@dataclass
class VolumeSignal:
    """Günlük hacim ile aylık ortalama karşılaştırması."""
    active: bool = False
    ratio: float = 0.0          # hacim / ort_hacim
    gunluk: float = 0.0
    ortalama: float = 0.0
    message: str = ""
    color: str = "#78909c"


def evaluate_volume_signal(
    hacim_lot: Optional[float],
    avg_lot: Optional[float],
    ratio_threshold: float = 1.5,
) -> VolumeSignal:
    """Günlük hacim aylık ortalamanın threshold katını aşarsa DİKKAT sinyali üretir.

    ratio_threshold=1.5 → günlük hacim aylık ort'un %50 üzerinde ise tetiklenir.
    """
    if hacim_lot is None or avg_lot is None or avg_lot == 0:
        return VolumeSignal(message="⚫ Hacim verisi yok.", color="#455a64")

    ratio = hacim_lot / avg_lot
    sig = VolumeSignal(ratio=ratio, gunluk=hacim_lot, ortalama=avg_lot)

    if ratio >= ratio_threshold:
        sig.active = True
        if ratio >= 3.0:
            sig.message = (
                f"🔶 YÜKSEK HACİM DİKKAT!\n"
                f"Bugün {hacim_lot:,.0f} lot işlem gördü.\n"
                f"Bu, 30 günlük ortalamanın ({avg_lot:,.0f} lot) {ratio:.1f} katı.\n"
                f"Olağandışı hareketlilik — yakın takip önerilir."
            )
            sig.color = "#e65100"
        else:
            sig.message = (
                f"⚠️ HACİM DİKKAT\n"
                f"Bugün {hacim_lot:,.0f} lot işlem gördü.\n"
                f"30 günlük ort: {avg_lot:,.0f} lot → {ratio:.1f}× üzerinde.\n"
                f"Artan ilgi gözlemleniyor."
            )
            sig.color = "#f57f17"
    else:
        sig.message = (
            f"Bugün {hacim_lot:,.0f} lot işlem gördü.\n"
            f"30 günlük ort: {avg_lot:,.0f} lot\n"
            f"Hacim normal seyrediyor (%{ratio * 100:.0f})."
        )
        sig.color = "#f9a825"  # koyu sarı — her durumda

    return sig


# ── BIST100 Korelasyon Sinyali ─────────────────────────────────

@dataclass
class Bist100Signal:
    """ALTINS1 — BIST100 ters korelasyon yön sinyali."""
    available: bool = False
    correlation: float = 0.0    # son 20 günlük korelasyon
    s1_trend: str = ""          # "yukari" / "asagi" / "yatay"
    bist_trend: str = ""
    message: str = ""
    color: str = "#78909c"


def _trend_label(pct_change: float, threshold: float = 1.0) -> str:
    if pct_change > threshold:
        return "yukari"
    elif pct_change < -threshold:
        return "asagi"
    return "yatay"


def evaluate_bist100_signal(
    altins1_series: Optional[pd.Series],
    bist100_series: Optional[pd.Series],
    window: int = 20,
) -> Bist100Signal:
    """Son N günlük korelasyon + trend yönüne bakarak karar destek sinyali üretir.

    Negatif korelasyon + trend ayrışması → anlamlı sinyal.
    """
    sig = Bist100Signal()

    if altins1_series is None or bist100_series is None:
        sig.message = "⚫ BIST100 verisi yok."
        sig.color = "#455a64"
        return sig

    common = altins1_series.index.intersection(bist100_series.index)
    if len(common) < window + 2:
        sig.message = "⚫ Korelasyon için yetersiz veri."
        sig.color = "#455a64"
        return sig

    s1 = altins1_series.loc[common].iloc[-window:]
    bist = bist100_series.loc[common].iloc[-window:]

    s1_ret = s1.pct_change().dropna()
    bist_ret = bist.pct_change().dropna()

    corr = float(s1_ret.corr(bist_ret))
    sig.available = True
    sig.correlation = corr

    # Son 5 günlük yüzde değişim → trend
    s1_5d = float((s1.iloc[-1] / s1.iloc[-5] - 1) * 100) if len(s1) >= 5 else 0.0
    bist_5d = float((bist.iloc[-1] / bist.iloc[-5] - 1) * 100) if len(bist) >= 5 else 0.0

    sig.s1_trend = _trend_label(s1_5d)
    sig.bist_trend = _trend_label(bist_5d)

    corr_str = f"r={corr:+.2f}"

    if corr < -0.3:
        # Ters korelasyon: yön sinyali anlamlı
        if sig.bist_trend == "yukari" and sig.s1_trend in ("asagi", "yatay"):
            sig.message = (
                f"📉 BIST Yükseliyor — S1 Baskı Altında\n"
                f"Son 5 gün: BIST +%{bist_5d:.1f} / S1 %{s1_5d:+.1f}\n"
                f"Korelasyon: {corr_str} (ters ilişki aktif)\n"
                f"S1'de baskı devam edebilir."
            )
            sig.color = "#1565c0"
        elif sig.bist_trend == "asagi" and sig.s1_trend in ("yukari", "yatay"):
            sig.message = (
                f"📈 BIST Düşüyor — S1 Güç Kazanabilir\n"
                f"Son 5 gün: BIST %{bist_5d:.1f} / S1 +%{s1_5d:.1f}\n"
                f"Korelasyon: {corr_str} (ters ilişki aktif)\n"
                f"S1 için fırsat penceresi olabilir."
            )
            sig.color = "#0d47a1"
        else:
            sig.message = (
                f"↔️ Ters Korelasyon Var — Trend Belirsiz\n"
                f"Son 5 gün: BIST %{bist_5d:+.1f} / S1 %{s1_5d:+.1f}\n"
                f"Korelasyon: {corr_str}\n"
                f"Yön netleşene dek izlemeye devam et."
            )
            sig.color = "#1565c0"
    elif corr > 0.3:
        sig.message = (
            f"🔄 Pozitif Korelasyon — Olağandışı\n"
            f"Son 5 gün: BIST %{bist_5d:+.1f} / S1 %{s1_5d:+.1f}\n"
            f"Korelasyon: {corr_str}\n"
            f"S1 ve BIST aynı yönde — tipik ters ilişki bozulmuş."
        )
        sig.color = "#1565c0"
    else:
        sig.message = (
            f"Korelasyon zayıf ({corr_str})\n"
            f"Son 5 gün: BIST %{bist_5d:+.1f} / S1 %{s1_5d:+.1f}\n"
            f"S1 ile BIST arasında belirgin ilişki gözlenmiyor."
        )
        sig.color = "#1565c0"

    return sig
