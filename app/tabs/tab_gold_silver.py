"""Tab 5 — Altın vs Gümüş karşılaştırma grafiği."""
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go  # pyright: ignore[reportMissingTypeStubs]
import streamlit as st

from app.charts import create_gold_silver_chart
from app.series_utils import common_index, divide_by_rate, has_data, multiply_by_rate
from app.ui_helpers import add_ema_traces, apply_chart_font, ema_checkboxes, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """Altın/Gümüş karşılaştırma grafiğini çizer."""
    ons_usd_hist_series = ctx.series.ons_usd
    ons_silver_usd_hist_series = ctx.series.ons_silver_usd
    gram_gold_hist_series = ctx.series.gram_gold_tl
    gram_silver_hist_series = ctx.series.gram_silver_tl
    usdtry_hist_series = ctx.series.usdtry

    with st.expander("⚙️ Grafik Ayarları", expanded=False):
        # Birim ve para birimi seçimi
        _t5_opt1, _t5_opt2 = st.columns(2)
        t5_unit = _t5_opt1.radio("Birim", ["Ons", "Gram"], horizontal=True, key="t5_unit")
        t5_ccy = _t5_opt2.radio("Para birimi", ["TL", "USD"], horizontal=True, key="t5_currency")

        # Seriler & checkbox
        _t5c1, _t5c2 = st.columns(2)
        _show_t5_gold = _t5c1.checkbox("🟡 Altın", value=True, key="t5_gold")
        _show_t5_silver = _t5c2.checkbox("⚪ Gümüş", value=True, key="t5_silver")

        # Ayrı EMA seçenekleri
        _t5_ema_col1, _t5_ema_col2 = st.columns(2)
        with _t5_ema_col1:
            st.caption("🟡 Altın EMA")
            _t5_ema_gold = ema_checkboxes(st, "t5g")
        with _t5_ema_col2:
            st.caption("⚪ Gümüş EMA")
            _t5_ema_silver = ema_checkboxes(st, "t5s")

    # Veri seçimi
    if t5_unit == "Ons":
        _gold_s = ons_usd_hist_series
        _silver_s = ons_silver_usd_hist_series
    else:
        _gold_s = gram_gold_hist_series
        _silver_s = gram_silver_hist_series

    if has_data(_gold_s) and has_data(_silver_s):
        gs_common = common_index(_gold_s, _silver_s)
        if len(gs_common) > 0:
            _g = _gold_s.loc[gs_common].copy()
            _s = _silver_s.loc[gs_common].copy()

            # USD dönüşümü (gram TL → USD)
            if t5_ccy == "USD" and t5_unit == "Gram" and has_data(usdtry_hist_series):
                usd_rate = usdtry_hist_series.loc[gs_common]
                _g = divide_by_rate(_g, usd_rate)
                _s = divide_by_rate(_s, usd_rate)
                gs_common = common_index(_g, _s)
                _g = _g.loc[gs_common]
                _s = _s.loc[gs_common]
            # TL dönüşümü (ons USD → TL)
            elif t5_ccy == "TL" and t5_unit == "Ons" and has_data(usdtry_hist_series):
                usd_rate = usdtry_hist_series.loc[gs_common]
                _g = multiply_by_rate(_g, usd_rate)
                _s = multiply_by_rate(_s, usd_rate)
                gs_common = common_index(_g, _s)
                _g = _g.loc[gs_common]
                _s = _s.loc[gs_common]

            fig_gs = create_gold_silver_chart(
                _g, _s, unit=t5_unit.lower(), currency=t5_ccy,
            )
            for _tr in cast(list[Any], cast(Any, fig_gs).data):
                if "Altın" in _tr.name and not _show_t5_gold:
                    _tr.visible = False
                if "Gümüş" in _tr.name and not _show_t5_silver:
                    _tr.visible = False

            # Altın/Gümüş oran serisi — grafik en üstünde beyaz çizgi ile göster
            _ratio_series = _g / _s
            _ratio_int = _ratio_series.round(0).astype(int)
            fig_gs.add_trace(
                go.Scatter(
                    x=list(_ratio_series.index),
                    y=[_g.max() * 1.03] * len(_ratio_series),
                    mode="lines",
                    name="Oran",
                    line=dict(color="#fff", width=2, dash="solid"),
                    showlegend=False,
                    hovertemplate="<b style='color:white'>Au/Ag Oran</b>: %{customdata}<extra></extra>",
                    customdata=list(_ratio_int.values),
                ),
            )

            add_ema_traces(fig_gs, _g, _t5_ema_gold, label_prefix="Au ", secondary_y=False)
            add_ema_traces(fig_gs, _s, _t5_ema_silver, label_prefix="Ag ", line_dash="dot", secondary_y=True)
            apply_chart_font(fig_gs, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
            st.plotly_chart(fig_gs, width="stretch", config=PLOTLY_CONFIG)
            st.caption(
                f"📅 Ortak aralık: {gs_common.min().strftime('%d.%m.%Y')} — "
                f"{gs_common.max().strftime('%d.%m.%Y')} ({len(gs_common)} gün)"
            )
            st.metric("Altın/Gümüş Oranı (Güncel)", f"{_ratio_series.iloc[-1]:.1f}")
        else:
            st.warning("Altın ve gümüş tarih aralıkları örtüşmüyor.")
    else:
        st.warning("Altın veya gümüş tarihsel verisi yüklenemedi.")
