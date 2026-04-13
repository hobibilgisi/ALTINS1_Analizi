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

        _stat_items = [
            ("Güncel", stats.get("guncel"), "%", "Şu anki makas oranı. ALTINS1'in beklenen fiyattan yüzde kaç uzakta olduğunu gösterir."),
            ("Ortalama", stats.get("ortalama"), "%", "Seçilen dönemdeki tüm günlerin makas ortalaması. Genel eğilimi gösterir."),
            ("Medyan", stats.get("medyan"), "%", "Makas değerlerinin tam ortasındaki değer. Uç değerlerden etkilenmez, ortalamadan daha güvenilir bir göstergedir."),
            ("Std", stats.get("std"), "", "Standart Sapma — makas değerlerinin ne kadar dalgalandığını gösterir. Düşükse piyasa sakin, yüksekse dalgalıdır."),
            ("Min", stats.get("min"), "%", "Dönem içinde makas oranının düştüğü en düşük değer."),
            ("Max", stats.get("max"), "%", "Dönem içinde makas oranının çıktığı en yüksek değer."),
        ]

        # Mobilde 3×2 grid, masaüstünde 6×1 grid
        _row1 = st.columns(3)
        _row2 = st.columns(3)
        _grid = _row1 + _row2
        for i, (label, value, prefix, tooltip) in enumerate(_stat_items):
            with _grid[i]:
                st.metric(label, f"{prefix}{value}" if value is not None else "—", help=tooltip)
    else:
        st.info("Makas analizi için ALTINS1 + gram altın TL tarihsel verisi gereklidir.")
