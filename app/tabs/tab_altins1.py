"""Tab 1 — ALTINS1 Analizi: Gerçek vs Beklenen karşılaştırma grafiği."""
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

from typing import TYPE_CHECKING, Any, cast

import pandas as pd
import plotly.graph_objects as go  # pyright: ignore[reportMissingTypeStubs]
import streamlit as st

from app.charts import create_altins1_vs_expected_chart
from app.series_utils import common_index, divide_by_rate, has_data
from app.ui_helpers import add_ema_traces, apply_chart_font, ema_checkboxes, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """ALTINS1 Gerçek vs Beklenen karşılaştırma grafiğini çizer."""
    altins1_hist_series = ctx.series.altins1
    gram_gold_hist_series = ctx.series.gram_gold_tl
    beklenen_hist_series = ctx.series.beklenen
    spread_hist_series = ctx.series.spread
    usdtry_hist_series = ctx.series.usdtry
    beklenen = ctx.current.beklenen_altins1

    with st.expander("⚙️ Grafik Ayarları", expanded=False):
        tab1_ccy = st.radio("Para birimi", ["TL", "USD"], horizontal=True, key="tab1_currency")
        _t1c1, _t1c2 = st.columns(2)
        _show_t1_gercek = _t1c1.checkbox("🔵 ALTINS1 Gerçek", value=True, key="t1_gercek")
        _show_t1_beklenen = _t1c2.checkbox("🟠 %1 Gr Altın", value=True, key="t1_beklenen")
        st.markdown("**EMA — S1 (ALTINS1)**")
        _t1_ema_s1 = ema_checkboxes(st, "t1s1", default_on=False)
        st.markdown("**EMA — GR (Gram Altın)**")
        _t1_ema_gr = ema_checkboxes(st, "t1gr", default_on=False)

    if has_data(altins1_hist_series) and has_data(gram_gold_hist_series) and has_data(beklenen_hist_series):
        assert altins1_hist_series is not None
        assert gram_gold_hist_series is not None
        assert beklenen_hist_series is not None
        common = common_index(altins1_hist_series, gram_gold_hist_series, beklenen_hist_series)
        if len(common) > 0:
            a1 = altins1_hist_series.loc[common]
            gt = gram_gold_hist_series.loc[common]
            bek = beklenen_hist_series.loc[common]

            if tab1_ccy == "USD" and has_data(usdtry_hist_series):
                assert usdtry_hist_series is not None
                usd_rate = usdtry_hist_series.loc[common]
                a1 = divide_by_rate(a1, usd_rate)
                gt = divide_by_rate(gt, usd_rate)
                bek = divide_by_rate(bek, usd_rate)
                common = common_index(a1, gt, bek)
                a1 = a1.loc[common]
                gt = gt.loc[common]
                bek = bek.loc[common]

            st.caption(
                f"📅 Ortak tarih aralığı: {common.min().strftime('%d.%m.%Y')} — "
                f"{common.max().strftime('%d.%m.%Y')} ({len(common)} gün)"
            )
            fig_vs = create_altins1_vs_expected_chart(
                a1, gt,
                beklenen_series=bek,
                currency=tab1_ccy,
            )
            for _tr in cast(list[Any], cast(Any, fig_vs).data):
                if "Gerçek" in _tr.name and not _show_t1_gercek:
                    _tr.visible = False
                if ("%1 Gr" in _tr.name or "Beklenen" in _tr.name) and not _show_t1_beklenen:
                    _tr.visible = False
            # Makas oranı: merkezi spread serisini kullan (TL modunda)
            if tab1_ccy == "TL" and spread_hist_series is not None:
                _makas_series = spread_hist_series.loc[spread_hist_series.index.intersection(common)]
            else:
                _makas_series = (a1 - bek) / bek * 100
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
            add_ema_traces(fig_vs, bek, _t1_ema_gr, label_prefix="gr ")
            apply_chart_font(fig_vs, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
            st.plotly_chart(fig_vs, width="stretch", config=PLOTLY_CONFIG)
        else:
            st.warning("ALTINS1 ve gram altın TL tarih aralıkları örtüşmüyor.")
    elif has_data(altins1_hist_series):
        assert altins1_hist_series is not None
        st.info("Tarihsel gram altın TL verisi eşleştirilemedi. Sadece ALTINS1 gösteriliyor.")
        fig_only = go.Figure()
        fig_only.add_trace(go.Scatter(
            x=altins1_hist_series.index, y=altins1_hist_series.values,
            mode="lines", name="ALTINS1", line=dict(color="#42a5f5", width=2),
        ))
        if beklenen is not None:
            fig_only.add_hline(y=beklenen, line_dash="dash", line_color="#ffa726",
                               annotation_text=f"Güncel Beklenen: ₺{beklenen:.2f}")
        fig_only.update_layout(title="ALTINS1 Tarihsel Fiyat", template="plotly_dark",
                               yaxis_title="TL", height=ctx.chart_height)
        apply_chart_font(fig_only, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_only, width="stretch", config=PLOTLY_CONFIG)
    else:
        st.warning("ALTINS1 tarihsel verisi yüklenemedi.")
