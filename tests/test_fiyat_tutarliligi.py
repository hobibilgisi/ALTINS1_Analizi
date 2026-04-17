"""
Fiyat Tutarliligi Testi

Merkezi veri kaynagi (MarketData) uzerinden:
- live.altins1 == series.altins1.iloc[-1]
- current.gram_gold_tl == series.gram_gold_tl.iloc[-1]   (ayni formul)
- current.beklenen_altins1 == series.beklenen.iloc[-1]
- current.makas_pct == series.spread.iloc[-1]

Eger bu test geciyorsa, programin HER noktasinda ayni degerler gosterilir.
"""

import pytest
import pandas as pd
from app.market_data import fetch_market_data


def test_fiyat_tutarliligi():
    """Anlik fiyatlar ile tarihsel serinin son degeri AYNI olmalidir."""
    data = fetch_market_data(period="1mo")
    live = data.live
    current = data.current
    series = data.series

    today = pd.Timestamp.today().normalize()

    # ALTINS1: Mynet'ten gelen tek deger, her yerde ayni
    if live.altins1 and series.altins1 is not None and today in series.altins1.index:
        altins1_son = series.altins1.loc[today]
        assert abs(altins1_son - live.altins1) < 0.01, (
            f"ALTINS1 tutarsiz: series={altins1_son} vs live={live.altins1}"
        )

    # Gram Altin TL: current snapshot ile tarihsel seri son degeri ayni olmali
    if current.gram_gold_tl is not None and series.gram_gold_tl is not None and today in series.gram_gold_tl.index:
        gram_son = series.gram_gold_tl.loc[today]
        assert abs(gram_son - current.gram_gold_tl) < 0.01, (
            f"Gram Altin tutarsiz: series={gram_son} vs current={current.gram_gold_tl}"
        )

    # Beklenen ALTINS1: current snapshot ile tarihsel seri son degeri ayni olmali
    if current.beklenen_altins1 is not None and series.beklenen is not None and today in series.beklenen.index:
        beklenen_son = series.beklenen.loc[today]
        assert abs(beklenen_son - current.beklenen_altins1) < 0.01, (
            f"Beklenen tutarsiz: series={beklenen_son} vs current={current.beklenen_altins1}"
        )

    # Makas (%): current snapshot ile tarihsel seri son degeri ayni olmali
    if current.makas_pct is not None and series.spread is not None and today in series.spread.index:
        spread_son = series.spread.loc[today]
        assert abs(spread_son - current.makas_pct) < 0.1, (
            f"Makas tutarsiz: series={spread_son} vs current={current.makas_pct}"
        )

    # Program geneli sadece current snapshot kullanmali
    if current.altins1 is not None and series.altins1 is not None:
        assert abs(current.altins1 - float(series.altins1.dropna().iloc[-1])) < 0.01

    if current.gram_gold_tl is not None and series.gram_gold_tl is not None:
        assert abs(current.gram_gold_tl - float(series.gram_gold_tl.dropna().iloc[-1])) < 0.01

    if current.beklenen_altins1 is not None and series.beklenen is not None:
        assert abs(current.beklenen_altins1 - float(series.beklenen.dropna().iloc[-1])) < 0.01

    if current.makas_pct is not None and series.spread is not None:
        assert abs(current.makas_pct - float(series.spread.dropna().iloc[-1])) < 0.1

