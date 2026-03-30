"""
ALTINS1 Analiz — Hesaplama Modülü
Gram altın TL hesaplama ve makas (spread) analizi.

ALTINS1 = 0.01 gram altın sertifikası.
Beklenen ALTINS1 = Gram Altın TL × 0.01
Makas (%) = (Gerçek ALTINS1 - Beklenen ALTINS1) / Beklenen ALTINS1 × 100
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from app.config import TROY_OUNCE_GRAM, ALTINS1_GRAM_KATSAYI

logger = logging.getLogger(__name__)


def calculate_gram_gold_tl(ons_usd: float, usd_try: float) -> float:
    """Gram altın TL = (Ons Altın USD × Dolar/TL) / 31.1035"""
    return (ons_usd * usd_try) / TROY_OUNCE_GRAM


def calculate_expected_altins1(gram_gold_tl: float) -> float:
    """Beklenen ALTINS1 fiyatı = Gram Altın TL × 0.01"""
    return gram_gold_tl * ALTINS1_GRAM_KATSAYI


def calculate_spread(altins1_price: float, gram_gold_tl: float) -> float:
    """ALTINS1 gerçek fiyat ile beklenen fiyat arasındaki makası (%) hesaplar.

    Formül: Makas (%) = (ALTINS1 - Beklenen) / Beklenen × 100
    Beklenen = gram_gold_tl × 0.01

    Pozitif = ALTINS1 primli, Negatif = ALTINS1 iskontolu
    """
    beklenen = gram_gold_tl * ALTINS1_GRAM_KATSAYI
    if beklenen == 0:
        logger.error("Beklenen ALTINS1 fiyatı sıfır — makas hesaplanamaz")
        return 0.0
    return ((altins1_price - beklenen) / beklenen) * 100


def calculate_spread_from_expected(altins1_price: float, expected_price: float) -> float:
    """Doğrudan beklenen fiyattan makas hesaplar."""
    if expected_price == 0:
        return 0.0
    return ((altins1_price - expected_price) / expected_price) * 100


def calculate_spread_series(
    altins1_series: pd.Series,
    gram_gold_tl_series: pd.Series,
) -> pd.Series:
    """Tarihsel makas serisini hesaplar.

    Args:
        altins1_series: ALTINS1 kapanış fiyat serisi
        gram_gold_tl_series: Gram altın TL fiyat serisi

    Returns:
        Makas (%) serisi — (ALTINS1 - Beklenen) / Beklenen × 100
    """
    beklenen = gram_gold_tl_series * ALTINS1_GRAM_KATSAYI
    spread = ((altins1_series - beklenen) / beklenen) * 100
    return spread


def spread_statistics(spread_series: pd.Series) -> dict:
    """Makas serisinin istatistiklerini hesaplar."""
    clean = spread_series.dropna()
    if clean.empty:
        return {"ortalama": None, "medyan": None, "std": None, "min": None, "max": None, "guncel": None}
    return {
        "ortalama": round(clean.mean(), 2),
        "medyan": round(clean.median(), 2),
        "std": round(clean.std(), 2),
        "min": round(clean.min(), 2),
        "max": round(clean.max(), 2),
        "guncel": round(clean.iloc[-1], 2) if len(clean) > 0 else None,
    }
