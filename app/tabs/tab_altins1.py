"""Tab 1 — ALTINS1 Analizi: Gerçek vs Beklenen karşılaştırma grafiği."""

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import create_altins1_vs_expected_chart
from app.config import ALTINS1_GRAM_KATSAYI
from app.ui_helpers import add_ema_traces, apply_chart_font, ema_checkboxes, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """ALTINS1 Gerçek vs Beklenen karşılaştırma grafiğini çizer."""
    altins1_hist_series = ctx.series.altins1
    gram_gold_hist_series = ctx.series.gram_gold_tl
    ons_gold_tl_hist_series = ctx.series.ons_gold_tl
    ons_usd_hist_series = ctx.series.ons_usd
    usdtry_hist_series = ctx.series.usdtry
    beklenen = ctx.prices.get("beklenen_altins1")

    with st.expander("⚙️ Grafik Ayarları", expanded=False):
        tab1_ccy = st.radio("Para birimi", ["TL", "USD"], horizontal=True, key="tab1_currency")
        _t1c1, _t1c2 = st.columns(2)
        _show_t1_gercek = _t1c1.checkbox("🔵 ALTINS1 Gerçek", value=True, key="t1_gercek")
        _show_t1_beklenen = _t1c2.checkbox("🟠 %1 Gr Altın", value=True, key="t1_beklenen")
        st.markdown("**EMA — S1 (ALTINS1)**")
        _t1_ema_s1 = ema_checkboxes(st, "t1s1", default_on=False)
        st.markdown("**EMA — GR (Gram Altın)**")
        _t1_ema_gr = ema_checkboxes(st, "t1gr", default_on=False)

    if altins1_hist_series is not None and gram_gold_hist_series is not None:
        # Ortak indeks bul
        common = altins1_hist_series.index.intersection(gram_gold_hist_series.index)
        if len(common) > 0:
            a1 = altins1_hist_series.loc[common]
            gt = gram_gold_hist_series.loc[common]
            ons_for_chart = None

            # Ons altın serisini hazırla (ortak aralıkta)
            if ons_gold_tl_hist_series is not None:
                ons_common = ons_gold_tl_hist_series.index.intersection(common)
                if len(ons_common) > 0:
                    ons_for_chart = ons_gold_tl_hist_series.loc[ons_common]

            if tab1_ccy == "USD" and usdtry_hist_series is not None:
                usd_rate = usdtry_hist_series.loc[usdtry_hist_series.index.intersection(common)]
                ci = a1.index.intersection(usd_rate.index)
                a1 = a1.loc[ci] / usd_rate.loc[ci]
                gt = gt.loc[ci] / usd_rate.loc[ci]
                # Ons: doğrudan USD serisini kullan
                if ons_usd_hist_series is not None:
                    ons_common_usd = ons_usd_hist_series.index.intersection(ci)
                    ons_for_chart = ons_usd_hist_series.loc[ons_common_usd] if len(ons_common_usd) > 0 else None
                common = ci

            st.caption(
                f"📅 Ortak tarih aralığı: {common.min().strftime('%d.%m.%Y')} — "
                f"{common.max().strftime('%d.%m.%Y')} ({len(common)} gün)"
            )
            fig_vs = create_altins1_vs_expected_chart(
                a1, gt,
                currency=tab1_ccy,
            )
            for _tr in fig_vs.data:
                if "Gerçek" in _tr.name and not _show_t1_gercek:
                    _tr.visible = False
                if ("%1 Gr" in _tr.name or "Beklenen" in _tr.name) and not _show_t1_beklenen:
                    _tr.visible = False
            beklenen_series = gt * ALTINS1_GRAM_KATSAYI
            # Makas oranı trace — hover'da her tarihte görünsün, çizgi en üstte beyaz
            _makas_series = (a1 - beklenen_series) / beklenen_series * 100
            _makas_series_int = _makas_series.round(0).astype(int)
            # Son günü sağa uzat (gelecek tarih göstermeden)
            _last_date = _makas_series.index[-1]
            _last_val = _makas_series_int.values[-1]
            _ext_x = [_last_date + pd.Timedelta(hours=h) for h in (4, 8, 12, 16, 20)]
            _ext_y = [a1.max() * 1.03] * 5
            _ext_val = [_last_val] * 5
            fig_vs.add_trace(
                go.Scatter(
                    x=list(_makas_series.index) + _ext_x,
                    y=[a1.max() * 1.03] * len(_makas_series) + _ext_y,
                    mode="lines",
                    name="Makas %",
                    line=dict(color="#fff", width=2, dash="solid"),
                    showlegend=False,
                    hovertemplate="<b style='color:white'>Makas</b>: %{customdata:+d}%<extra></extra>",
                    customdata=list(_makas_series_int.values) + _ext_val,
                ),
            )
            add_ema_traces(fig_vs, a1, _t1_ema_s1, label_prefix="s1 ", line_dash="dot")
            add_ema_traces(fig_vs, beklenen_series, _t1_ema_gr, label_prefix="gr ")
            apply_chart_font(fig_vs, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
            st.plotly_chart(fig_vs, width="stretch", config=PLOTLY_CONFIG)
        else:
            st.warning("ALTINS1 ve gram altın TL tarih aralıkları örtüşmüyor.")
    elif altins1_hist_series is not None:
        st.info("Tarihsel gram altın TL verisi eşleştirilemedi. Sadece ALTINS1 gösteriliyor.")
        fig_only = go.Figure()
        fig_only.add_trace(go.Scatter(
            x=altins1_hist_series.index, y=altins1_hist_series.values,
            mode="lines", name="ALTINS1", line=dict(color="#42a5f5", width=2),
        ))
        if beklenen:
            fig_only.add_hline(y=beklenen, line_dash="dash", line_color="#ffa726",
                               annotation_text=f"Güncel Beklenen: ₺{beklenen:.2f}")
        fig_only.update_layout(title="ALTINS1 Tarihsel Fiyat", template="plotly_dark",
                               yaxis_title="TL", height=ctx.chart_height)
        apply_chart_font(fig_only, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_only, width="stretch", config=PLOTLY_CONFIG)
    else:
        st.warning("ALTINS1 tarihsel verisi yüklenemedi.")
