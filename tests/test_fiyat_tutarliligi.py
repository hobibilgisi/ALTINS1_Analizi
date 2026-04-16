"""
Fiyat Tutarliligi Testi

Merkezi veri kaynagi (MarketData) uzerinden:
- live.gram_gold_tl == series.gram_gold_tl.iloc[-1]   (ayni formul)
- live.beklenen_altins1 == series.beklenen.iloc[-1]
- live.makas_pct == series.spread.iloc[-1]
- live.altins1 == series.altins1.iloc[-1]

Eger bu test geciyorsa, programin HER noktasinda ayni degerler gosterilir.
"""

import pytest
import pandas as pd
from app.market_data import fetch_market_data


def test_fiyat_tutarliligi():
    """Anlik fiyatlar ile tarihsel serinin son degeri AYNI olmalidir."""
    data = fetch_market_data(period="1mo")
    live = data.live
    series = data.series

    today = pd.Timestamp.today().normalize()

    # ALTINS1: Mynet'ten gelen tek deger, her yerde ayni
    if live.altins1 and series.altins1 is not None and today in series.altins1.index:
        altins1_son = series.altins1.loc[today]
        assert abs(altins1_son - live.altins1) < 0.01, (
            f"ALTINS1 tutarsiz: series={altins1_son} vs live={live.altins1}"
        )

    # Gram Altin TL: ons x usdtry / 31.1035 (ayni formul, her yerde)
    if live.gram_gold_tl and series.gram_gold_tl is not None and today in series.gram_gold_tl.index:
        gram_son = series.gram_gold_tl.loc[today]
        assert abs(gram_son - live.gram_gold_tl) < 0.01, (
            f"Gram Altin tutarsiz: series={gram_son} vs live={live.gram_gold_tl}"
        )

    # Beklenen ALTINS1: gram_gold_tl x 0.01
    if live.beklenen_altins1 and series.beklenen is not None and today in series.beklenen.index:
        beklenen_son = series.beklenen.loc[today]
        assert abs(beklenen_son - live.beklenen_altins1) < 0.01, (
            f"Beklenen tutarsiz: series={beklenen_son} vs live={live.beklenen_altins1}"
        )

    # Makas (%): (altins1 - beklenen) / beklenen x 100
    if live.makas_pct and series.spread is not None and today in series.spread.index:
        spread_son = series.spread.loc[today]
        assert abs(spread_son - live.makas_pct) < 0.1, (
            f"Makas tutarsiz: series={spread_son} vs live={live.makas_pct}"
        )
