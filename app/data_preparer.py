"""
ALTINS1 Analiz -- Tarihsel Veri Hazirlayici
yfinance / Mynet ham verilerini grafik-hazir serilere donusturur.

Kural: Tum turevi degerler (gram_gold_tl, beklenen, spread) AYNI formulle
hesaplanir -- ne tarihsel seride ne anlik veride farkli kaynak kullanilir.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

import pandas as pd

from app.config import TROY_OUNCE_GRAM, ALTINS1_GRAM_KATSAYI
from app.calculator import calculate_gram_gold_tl, calculate_spread_series

if TYPE_CHECKING:
    from app.market_data import LivePrices


def _has_value(value: Optional[float]) -> bool:
    return value is not None and not pd.isna(value)


def _append_today(series: pd.Series, value: float, today: pd.Timestamp) -> pd.Series:
    """Seriyi kopyalayip bugunku degeri tek noktadan yazar."""
    updated = series.copy()
    updated.loc[today] = value
    return updated.sort_index()


@dataclass
class PreparedSeries:
    """Grafiklerde kullanilacak tum hazir seriler."""
    gram_gold_tl: Optional[pd.Series] = None
    ons_gold_tl: Optional[pd.Series] = None
    ons_usd: Optional[pd.Series] = None
    usdtry: Optional[pd.Series] = None
    altins1: Optional[pd.Series] = None
    beklenen: Optional[pd.Series] = None
    ons_silver_usd: Optional[pd.Series] = None
    gram_silver_tl: Optional[pd.Series] = None
    faiz: Optional[pd.Series] = None
    bist100: Optional[pd.Series] = None
    spread: Optional[pd.Series] = None


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame index'ini timezone-free, gunluk ve tekil hale getirir."""
    df = df.copy()
    idx = pd.to_datetime(df.index)
    if idx.tz is not None:
        idx = idx.tz_convert(None)
    df.index = idx.normalize()
    return df[~df.index.duplicated(keep="last")]


def prepare_all_series(history: dict, altins1_hist, live: LivePrices) -> PreparedSeries:
    """Ham tarihsel verileri isleyerek grafik-hazir seriler doner.

    ONEMLI: Bugunku deger enjeksiyonu, tarihsel seriyle AYNI kaynaktan
    (yfinance ons x usdtry / 31.1035) yapilir. Truncgil fiyatlari
    burada KULLANILMAZ -- bu tutarliligi garanti eder.

    Args:
        history: fetch_all_history() sonucu (dict of DataFrames)
        altins1_hist: fetch_altins1_mynet() tarihsel DataFrame
        live: LivePrices nesnesi (merkezi anlik fiyatlar)
    """
    result = PreparedSeries()

    # -- Ons altin + Dolar/TL -> Gram altin TL --
    has_ons = history.get("ons_altin_usd") is not None
    has_usdtry = history.get("dolar_tl") is not None

    usdtry_hist = None
    if has_ons and has_usdtry:
        ons_hist = _normalize_index(history["ons_altin_usd"])
        usdtry_hist = _normalize_index(history["dolar_tl"])
        common_idx = ons_hist.index.intersection(usdtry_hist.index)
        if len(common_idx) > 0:
            # gram_gold_tl = ons x usdtry / 31.1035 (TEK FORMUL)
            result.gram_gold_tl = (
                ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
            ) / TROY_OUNCE_GRAM
            result.ons_gold_tl = (
                ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
            )
            result.ons_usd = ons_hist.loc[common_idx, "Close"]
            result.usdtry = usdtry_hist.loc[common_idx, "Close"]

    # -- ALTINS1 tarihsel Close --
    if altins1_hist is not None and not altins1_hist.empty and "Close" in altins1_hist.columns:
        clean = _normalize_index(altins1_hist)
        result.altins1 = clean["Close"]

    # -- Gumus --
    if history.get("ons_gumus_usd") is not None:
        gumus = _normalize_index(history["ons_gumus_usd"])
        result.ons_silver_usd = gumus["Close"]
        if usdtry_hist is not None:
            silver_common = gumus.index.intersection(usdtry_hist.index)
            if len(silver_common) > 0:
                result.gram_silver_tl = (
                    gumus.loc[silver_common, "Close"] * usdtry_hist.loc[silver_common, "Close"]
                ) / TROY_OUNCE_GRAM

    # -- Faiz (ABD 10Y) --
    if history.get("faiz_us10y") is not None:
        faiz = _normalize_index(history["faiz_us10y"])
        if "Close" in faiz.columns and not faiz["Close"].dropna().empty:
            result.faiz = faiz["Close"]

    # -- BIST 100 Endeksi --
    if history.get("bist100") is not None:
        bist = _normalize_index(history["bist100"])
        if "Close" in bist.columns and not bist["Close"].dropna().empty:
            result.bist100 = bist["Close"]

    # -- Anlik veriyle bugunu esitle (AYNI KAYNAKTAN) --
    # live.ons_usd + live.usdtry ham verileridir.
    # Tarihsel serideki gram_gold_tl ayni formulle hesaplanir.
    # Bu sayede seri icinde kaynak tutarsizligi OLMAZ
    today = pd.Timestamp(datetime.now().date())

    if result.gram_gold_tl is not None and _has_value(live.ons_usd) and _has_value(live.usdtry):
        result.gram_gold_tl = _append_today(result.gram_gold_tl, calculate_gram_gold_tl(live.ons_usd, live.usdtry), today)
    if result.altins1 is not None and _has_value(live.altins1):
        result.altins1 = _append_today(result.altins1, live.altins1, today)
    if result.ons_usd is not None and _has_value(live.ons_usd):
        result.ons_usd = _append_today(result.ons_usd, live.ons_usd, today)
    if result.usdtry is not None and _has_value(live.usdtry):
        result.usdtry = _append_today(result.usdtry, live.usdtry, today)
    if result.ons_gold_tl is not None and _has_value(live.ons_usd) and _has_value(live.usdtry):
        result.ons_gold_tl = _append_today(result.ons_gold_tl, live.ons_usd * live.usdtry, today)
    if result.ons_silver_usd is not None and _has_value(live.ons_silver_usd):
        result.ons_silver_usd = _append_today(result.ons_silver_usd, live.ons_silver_usd, today)
    if result.gram_silver_tl is not None and _has_value(live.ons_silver_usd) and _has_value(live.usdtry):
        result.gram_silver_tl = _append_today(
            result.gram_silver_tl,
            (live.ons_silver_usd * live.usdtry) / TROY_OUNCE_GRAM,
            today,
        )
    if result.faiz is not None and _has_value(live.faiz_us10y):
        result.faiz = _append_today(result.faiz, live.faiz_us10y, today)

    # -- Beklenen ALTINS1 + Tarihsel makas --
    if result.altins1 is not None and result.gram_gold_tl is not None:
        sp_common = result.altins1.index.intersection(result.gram_gold_tl.index)
        if len(sp_common) > 0:
            result.beklenen = result.gram_gold_tl.loc[sp_common] * ALTINS1_GRAM_KATSAYI
            result.spread = calculate_spread_series(
                result.altins1.loc[sp_common],
                result.gram_gold_tl.loc[sp_common],
            )

    return result
