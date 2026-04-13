"""Tab 3 — Normalize Karşılaştırma grafiği."""

from typing import TYPE_CHECKING

import streamlit as st

from app.charts import create_overlay_chart
from app.ui_helpers import apply_chart_font, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """Normalize edilmiş çoklu seri karşılaştırma grafiğini çizer."""
    altins1_hist_series = ctx.series.altins1
    gram_gold_hist_series = ctx.series.gram_gold_tl
    ons_usd_hist_series = ctx.series.ons_usd
    usdtry_hist_series = ctx.series.usdtry
    faiz_hist_series = ctx.series.faiz

    with st.expander("⚙️ Grafik Ayarları", expanded=False):
        norm_ccy = st.radio("Para birimi", ["TL", "USD"], horizontal=True, key="norm_currency")

        # Mevcut serileri topla
        _norm_series = {}
        if altins1_hist_series is not None and len(altins1_hist_series) > 0:
            _norm_series["altins1"] = altins1_hist_series
        if gram_gold_hist_series is not None and len(gram_gold_hist_series) > 0:
            _norm_series["gram"] = gram_gold_hist_series
        # Not: Ons TL ve gram altın TL normalize edilince aynı çizgiyi verir
        # (ikisi de ons×USDTRY'den türer). Bu yüzden ons'u ayrı gösteriyoruz:
        # TL modunda ons TL, USD modunda ons USD.
        if norm_ccy == "USD" and ons_usd_hist_series is not None and len(ons_usd_hist_series) > 0:
            _norm_series["ons"] = ons_usd_hist_series
        elif ons_usd_hist_series is not None and len(ons_usd_hist_series) > 0:
            _norm_series["ons"] = ons_usd_hist_series  # Ons her zaman USD göster
        if faiz_hist_series is not None and len(faiz_hist_series) > 0:
            _norm_series["faiz"] = faiz_hist_series

        # Checkbox'lar — sadece mevcut seriler için göster
        _t3_cols = st.columns(len(_norm_series)) if _norm_series else []
        _t3_show = {}
        _t3_meta = {
            "altins1": ("🔵 ALTINS1", "t3_altins1"),
            "gram": ("🟠 Gram Altın", "t3_gram"),
            "ons": ("🟣 Ons Altın (USD)", "t3_ons"),
            "faiz": ("🔴 ABD 10Y Faiz", "t3_faiz"),
        }
        for i, key in enumerate(_norm_series):
            lbl, cb_key = _t3_meta[key]
            _t3_show[key] = _t3_cols[i].checkbox(lbl, value=True, key=cb_key)

    # Checkbox'a göre serileri filtrele
    _norm_visible = {k: v for k, v in _norm_series.items() if _t3_show.get(k, True)}

    if len(_norm_visible) >= 1:
        # Ortak tarih aralığını bul — tüm seriler aynı noktadan başlasın
        common_start = max(s.index.min() for s in _norm_visible.values())
        common_end = min(s.index.max() for s in _norm_visible.values())

        a1 = altins1_hist_series.loc[common_start:common_end] if "altins1" in _norm_visible else None
        gt = gram_gold_hist_series.loc[common_start:common_end] if "gram" in _norm_visible else None
        ot = _norm_series["ons"].loc[common_start:common_end] if "ons" in _norm_visible else None
        fz = faiz_hist_series.loc[common_start:common_end] if "faiz" in _norm_visible else None

        if norm_ccy == "USD" and usdtry_hist_series is not None:
            usd_rate = usdtry_hist_series.loc[common_start:common_end]
            if a1 is not None:
                ci = a1.index.intersection(usd_rate.index)
                a1 = a1.loc[ci] / usd_rate.loc[ci]
            if gt is not None:
                ci = gt.index.intersection(usd_rate.index)
                gt = gt.loc[ci] / usd_rate.loc[ci]
            # ot ve fz zaten USD bazlı, dönüşüm gerekmez

        fig_overlay = create_overlay_chart(
            altins1_series=a1,
            gram_gold_series=gt,
            ons_gold_series=ot,
            faiz_series=fz,
            currency=norm_ccy,
        )
        apply_chart_font(fig_overlay, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_overlay, width="stretch", config=PLOTLY_CONFIG)
        st.caption(
            f"📅 Ortak aralık: {common_start.strftime('%d.%m.%Y')} — {common_end.strftime('%d.%m.%Y')} | "
            f"Tüm seriler ilk değere göre normalize edilmiştir (başlangıç = 0%)."
        )
    else:
        st.warning("Normalize karşılaştırma için yeterli tarihsel veri bulunamadı.")
