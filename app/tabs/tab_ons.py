"""Tab 4 — Ons Altın (XAU/USD) fiyat ve hacim grafiği."""

from typing import TYPE_CHECKING

import streamlit as st

from app.charts import create_price_chart
from app.ui_helpers import add_ema_traces, apply_chart_font, ema_checkboxes, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """Ons altın fiyat ve hacim grafiğini çizer."""
    history = ctx.history_raw

    if history.get("ons_altin_usd") is not None:
        with st.expander("⚙️ Grafik Ayarları", expanded=False):
            _t4c1, _t4c2 = st.columns(2)
            _show_t4_fiyat = _t4c1.checkbox("🟢 Fiyat", value=True, key="t4_fiyat")
            _show_t4_hacim = _t4c2.checkbox("🔵 Hacim", value=True, key="t4_hacim")
            _t4_ema = ema_checkboxes(st, "t4")

        fig_xau = create_price_chart(history["ons_altin_usd"], title="Ons Altın (XAU/USD)")
        for _tr in fig_xau.data:
            if _tr.name == "Fiyat" and not _show_t4_fiyat:
                _tr.visible = False
            if _tr.name == "Hacim" and not _show_t4_hacim:
                _tr.visible = False
        _t4_close = history["ons_altin_usd"]["Close"]
        add_ema_traces(fig_xau, _t4_close, _t4_ema, row=1, col=1)
        apply_chart_font(fig_xau, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_xau, width="stretch", config=PLOTLY_CONFIG)
    else:
        st.warning("Ons altın tarihsel verisi yüklenemedi.")
