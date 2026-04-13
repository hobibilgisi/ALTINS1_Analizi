"""Tab 2 — S1/Gr Oranı (Makas) Analizi grafiği ve istatistikleri."""

from typing import TYPE_CHECKING

import streamlit as st

from app.calculator import spread_statistics
from app.charts import create_spread_chart
from app.ui_helpers import add_ema_traces, apply_chart_font, ema_checkboxes, PLOTLY_CONFIG

if TYPE_CHECKING:
    from app.tabs import TabContext


def render(ctx: "TabContext") -> None:
    """Makas grafiğini ve istatistikleri gösterir."""
    spread_hist = ctx.spread_hist

    if spread_hist is not None and len(spread_hist) > 0:
        with st.expander("⚙️ Grafik Ayarları", expanded=False):
            _t2c1, _t2c2 = st.columns(2)
            _show_t2_makas = _t2c1.checkbox("🟠 Makas (%)", value=True, key="t2_makas")
            _show_t2_cumavg = _t2c2.checkbox("🔵 Kümülatif Ortalama", value=True, key="t2_cumavg")
            _t2_ema = ema_checkboxes(st, "t2")

        fig_spread = create_spread_chart(
            spread_hist,
            buy_threshold=ctx.thresholds.buy_threshold,
            sell_threshold=ctx.thresholds.sell_threshold,
            strong_buy_threshold=ctx.thresholds.strong_buy,
            strong_sell_threshold=ctx.thresholds.strong_sell,
        )
        for _tr in fig_spread.data:
            if "Makas" in _tr.name and not _show_t2_makas:
                _tr.visible = False
            if "Kümülatif" in _tr.name and not _show_t2_cumavg:
                _tr.visible = False
        add_ema_traces(fig_spread, spread_hist, _t2_ema)
        apply_chart_font(fig_spread, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_spread, width="stretch", config=PLOTLY_CONFIG)

        # İstatistikler
        stats = spread_statistics(spread_hist)
        scols = st.columns(6)
        scols[0].metric("Güncel", f"%{stats['guncel']}" if stats["guncel"] else "—")
        scols[1].metric("Ortalama", f"%{stats['ortalama']}" if stats["ortalama"] else "—")
        scols[2].metric("Medyan", f"%{stats['medyan']}" if stats["medyan"] else "—")
        scols[3].metric("Std", f"{stats['std']}" if stats["std"] else "—")
        scols[4].metric("Min", f"%{stats['min']}" if stats["min"] else "—")
        scols[5].metric("Max", f"%{stats['max']}" if stats["max"] else "—")
    else:
        st.info("Makas analizi için ALTINS1 + gram altın TL tarihsel verisi gereklidir.")
