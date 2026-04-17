"""CurrentPrices cozumleme mantigi icin saf birim testleri."""

import pandas as pd

from app.market_data import LivePrices, resolve_current_prices
from app.data_preparer import PreparedSeries


def test_current_prices_prefers_live_values_when_available():
    live = LivePrices(
        altins1=83.99,
        ons_usd=3210.0,
        usdtry=38.56,
        ceyrek_altin=7000.0,
    )
    series = PreparedSeries(
        altins1=pd.Series([83.88], index=[pd.Timestamp("2026-04-18")]),
        ons_usd=pd.Series([3209.0], index=[pd.Timestamp("2026-04-18")]),
        usdtry=pd.Series([38.54], index=[pd.Timestamp("2026-04-18")]),
        gram_gold_tl=pd.Series([6988.04], index=[pd.Timestamp("2026-04-18")]),
        beklenen=pd.Series([69.88], index=[pd.Timestamp("2026-04-18")]),
        spread=pd.Series([20.03], index=[pd.Timestamp("2026-04-18")]),
    )

    current = resolve_current_prices(live=live, series=series)

    assert current.altins1 == 83.99
    assert current.ons_usd == 3210.0
    assert current.usdtry == 38.56
    assert round(current.gram_gold_tl, 2) == round((3210.0 * 38.56) / 31.1035, 2)
    assert round(current.beklenen_altins1, 2) == round(current.gram_gold_tl * 0.01, 2)
    assert round(current.makas_pct, 2) == round(((83.99 - current.beklenen_altins1) / current.beklenen_altins1) * 100, 2)
    assert current.ceyrek_altin == 7000.0


def test_current_prices_falls_back_to_live_when_series_missing():
    live = LivePrices(
        altins1=82.0,
        ons_usd=3220.0,
        usdtry=39.0,
    )

    current = resolve_current_prices(live=live, series=PreparedSeries())

    assert current.altins1 == live.altins1
    assert round(current.gram_gold_tl, 6) == round((3220.0 * 39.0) / 31.1035, 6)
    assert round(current.beklenen_altins1, 6) == round(current.gram_gold_tl * 0.01, 6)
    assert round(current.makas_pct, 6) == round(((82.0 - current.beklenen_altins1) / current.beklenen_altins1) * 100, 6)