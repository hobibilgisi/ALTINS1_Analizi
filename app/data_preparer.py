"""
ALTINS1 Analiz — Tarihsel Veri Hazırlayıcı
yfinance / Mynet ham verilerini grafik-hazır serilere dönüştürür.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd

from app.config import TROY_OUNCE_GRAM
from app.calculator import calculate_spread_series


@dataclass
class PreparedSeries:
    """Grafiklerde kullanılacak tüm hazır seriler."""
    gram_gold_tl: Optional[pd.Series] = None
    ons_gold_tl: Optional[pd.Series] = None
    ons_usd: Optional[pd.Series] = None
    usdtry: Optional[pd.Series] = None
    altins1: Optional[pd.Series] = None
    ons_silver_usd: Optional[pd.Series] = None
    gram_silver_tl: Optional[pd.Series] = None
    faiz: Optional[pd.Series] = None
    spread: Optional[pd.Series] = None


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame index'ini timezone-free, günlük ve tekil hale getirir."""
    df = df.copy()
    idx = pd.to_datetime(df.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    df.index = idx.normalize()
    return df[~df.index.duplicated(keep="last")]


def prepare_all_series(history: dict, altins1_hist, prices: dict) -> PreparedSeries:
    """Ham tarihsel verileri işleyerek grafik-hazır seriler döner.

    Args:
        history: fetch_all_history() sonucu (dict of DataFrames)
        altins1_hist: fetch_altins1_mynet() tarihsel DataFrame
        prices: fetch_current_prices() sonucu (dict)
    """
    result = PreparedSeries()

    # ── Ons altın + Dolar/TL → Gram altın TL ──────────────────
    has_ons = history.get("ons_altin_usd") is not None
    has_usdtry = history.get("dolar_tl") is not None

    usdtry_hist = None
    if has_ons and has_usdtry:
        ons_hist = _normalize_index(history["ons_altin_usd"])
        usdtry_hist = _normalize_index(history["dolar_tl"])
        common_idx = ons_hist.index.intersection(usdtry_hist.index)
        if len(common_idx) > 0:
            result.gram_gold_tl = (
                ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
            ) / TROY_OUNCE_GRAM
            result.ons_gold_tl = (
                ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
            )
            result.ons_usd = ons_hist.loc[common_idx, "Close"]
            result.usdtry = usdtry_hist.loc[common_idx, "Close"]

    # ── ALTINS1 tarihsel Close ─────────────────────────────────
    if altins1_hist is not None and not altins1_hist.empty and "Close" in altins1_hist.columns:
        clean = _normalize_index(altins1_hist)
        result.altins1 = clean["Close"]

    # ── Gümüş ─────────────────────────────────────────────────
    if history.get("ons_gumus_usd") is not None:
        gumus = _normalize_index(history["ons_gumus_usd"])
        result.ons_silver_usd = gumus["Close"]
        if usdtry_hist is not None:
            silver_common = gumus.index.intersection(usdtry_hist.index)
            if len(silver_common) > 0:
                result.gram_silver_tl = (
                    gumus.loc[silver_common, "Close"] * usdtry_hist.loc[silver_common, "Close"]
                ) / TROY_OUNCE_GRAM

    # ── Faiz (ABD 10Y) ────────────────────────────────────────
    if history.get("faiz_us10y") is not None:
        faiz = _normalize_index(history["faiz_us10y"])
        if "Close" in faiz.columns and not faiz["Close"].dropna().empty:
            result.faiz = faiz["Close"]

    # ── Anlık veriyle bugünü eşitle ────────────────────────────
    today = pd.Timestamp(datetime.now().date())
    live_gram = prices.get("gram_altin_tl")
    live_s1 = prices.get("altins1_fiyat")
    if result.gram_gold_tl is not None and live_gram:
        result.gram_gold_tl[today] = live_gram
        result.gram_gold_tl = result.gram_gold_tl.sort_index()
    if result.altins1 is not None and live_s1:
        result.altins1[today] = live_s1
        result.altins1 = result.altins1.sort_index()

    # ── Tarihsel makas ─────────────────────────────────────────
    if result.altins1 is not None and result.gram_gold_tl is not None:
        sp_common = result.altins1.index.intersection(result.gram_gold_tl.index)
        if len(sp_common) > 0:
            result.spread = calculate_spread_series(
                result.altins1.loc[sp_common],
                result.gram_gold_tl.loc[sp_common],
            )

    return result
