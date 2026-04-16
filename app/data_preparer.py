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
from app.calculator import calculate_spread_series

if TYPE_CHECKING:
    from app.market_data import LivePrices


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
    # live.gram_gold_tl = live.ons_usd x live.usdtry / 31.1035
    # Tarihsel serideki gram_gold_tl de ayni formulle hesaplandi
    # Bu sayede seri icinde kaynak tutarsizligi OLMAZ
    today = pd.Timestamp(datetime.now().date())

    if result.gram_gold_tl is not None and live.gram_gold_tl:
        result.gram_gold_tl[today] = live.gram_gold_tl
        result.gram_gold_tl = result.gram_gold_tl.sort_index()
    if result.altins1 is not None and live.altins1:
        result.altins1[today] = live.altins1
        result.altins1 = result.altins1.sort_index()
    if result.ons_usd is not None and live.ons_usd:
        result.ons_usd[today] = live.ons_usd
        result.ons_usd = result.ons_usd.sort_index()
    if result.usdtry is not None and live.usdtry:
        result.usdtry[today] = live.usdtry
        result.usdtry = result.usdtry.sort_index()
    if result.ons_gold_tl is not None and live.ons_usd and live.usdtry:
        result.ons_gold_tl[today] = live.ons_usd * live.usdtry
        result.ons_gold_tl = result.ons_gold_tl.sort_index()

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
