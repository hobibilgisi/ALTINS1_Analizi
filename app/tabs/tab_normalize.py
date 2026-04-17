"""Tab 3 — Normalize Karşılaştırma grafiği."""

from typing import TYPE_CHECKING

import streamlit as st

from app.charts import create_overlay_chart, create_correlation_chart
from app.series_utils import (
    divide_by_rate,
    earliest_end,
    filter_series_map,
    has_data,
    latest_end,
    latest_start,
    slice_from_start,
    slice_to_range,
)
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
        _norm_series = filter_series_map({
            "altins1": altins1_hist_series,
            "gram": gram_gold_hist_series,
        })
        # Not: Ons TL ve gram altın TL normalize edilince aynı çizgiyi verir
        # (ikisi de ons×USDTRY'den türer). Bu yüzden ons'u ayrı gösteriyoruz:
        # TL modunda ons TL, USD modunda ons USD.
        if norm_ccy == "USD" and has_data(ons_usd_hist_series):
            _norm_series["ons"] = ons_usd_hist_series
        elif has_data(ons_usd_hist_series):
            _norm_series["ons"] = ons_usd_hist_series  # Ons her zaman USD göster
        if has_data(faiz_hist_series):
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

        # Ortak başlangıç: tüm serilerin başladığı en geç tarih
        # Bitiş: HER SERİ kendi son tarihine kadar uzar — bir serinin
        # gecikmesi diğerlerini kesmez (faiz, bist100 gibi seriler
        # altins1/gram'ın bugünkü değerini kesmemelidir)
        common_start = latest_start(_norm_visible)
        aligned_norm = slice_from_start(_norm_visible, common_start)

        a1 = aligned_norm.get("altins1")
        gt = aligned_norm.get("gram")
        ot = aligned_norm.get("ons")
        fz = aligned_norm.get("faiz")

        # Grafik caption için son tarih: ana seriler (altins1/gram) arasından max
        _main_ends = {k: s for k, s in aligned_norm.items() if k in ("altins1", "gram", "ons")}
        common_end = latest_end(_main_ends) if _main_ends else common_start

        if norm_ccy == "USD" and has_data(usdtry_hist_series):
            usd_rate = usdtry_hist_series.loc[common_start:common_end]
            if a1 is not None:
                a1 = divide_by_rate(a1, usd_rate)
            if gt is not None:
                gt = divide_by_rate(gt, usd_rate)
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
        # Grafik altına merkezi live değerlerini göster — seri kesim tarihinden bağımsız
        last_date = common_end
        # ctx.current: tüm programın tek çözülmüş güncel referansı
        _cur_altins1 = ctx.current.altins1
        _cur_beklenen = ctx.current.beklenen_altins1
        _cur_gram_tl = ctx.current.gram_gold_tl
        st.caption(
            f"📅 Ortak aralık: {common_start.strftime('%d.%m.%Y')} — {common_end.strftime('%d.%m.%Y')} | "
            f"Tüm seriler ilk değere göre normalize edilmiştir (başlangıç = 0%)."
        )
        st.info(
            f"**GÜNCEL DEĞERLER (Tüm Grafiklerde Aynı Kaynak — current):**\n"
            f"ALTINS1: {f'₺{_cur_altins1:.2f}' if _cur_altins1 is not None else '-'}  |  "
            f"%1 Gr Altın (Beklenen): {f'₺{_cur_beklenen:.2f}' if _cur_beklenen is not None else '-'}  |  "
            f"Gram Altın TL: {f'₺{_cur_gram_tl:.2f}' if _cur_gram_tl is not None else '-'}\n"
            f"(Grafik aralığı: {last_date.strftime('%d.%m.%Y')}'ye kadar)"
        )
    else:
        st.warning("Normalize karşılaştırma için yeterli tarihsel veri bulunamadı.")

    # ── Borsa-Altın Korelasyonu Grafiği ────────────────────────
    st.markdown("---")
    st.subheader("📈 Borsa-Altın Korelasyonu")
    st.caption("BIST 100, Gram Altın TL ve ALTINS1 normalize karşılaştırması — borsa yönünün altın sertifikasına etkisini gösterir.")

    bist100_hist_series = ctx.series.bist100

    _corr_series = filter_series_map({
        "altins1": altins1_hist_series,
        "gram": gram_gold_hist_series,
        "bist100": bist100_hist_series,
    })

    if len(_corr_series) >= 2:
        corr_start = latest_start(_corr_series)
        corr_end = earliest_end(_corr_series)
        corr_aligned = slice_to_range(_corr_series, corr_start, corr_end)

        c_a1 = corr_aligned.get("altins1")
        c_gt = corr_aligned.get("gram")
        c_bist = corr_aligned.get("bist100")

        fig_corr = create_correlation_chart(
            altins1_series=c_a1,
            gram_gold_series=c_gt,
            bist100_series=c_bist,
        )
        apply_chart_font(fig_corr, ctx.font_size, ctx.chart_height, ctx.grafik_kilidi)
        st.plotly_chart(fig_corr, width="stretch", config=PLOTLY_CONFIG)
        st.caption(
            f"📅 Ortak aralık: {corr_start.strftime('%d.%m.%Y')} — {corr_end.strftime('%d.%m.%Y')} | "
            f"Tüm seriler ilk değere göre normalize edilmiştir (başlangıç = 0%)."
        )
    else:
        st.warning("Borsa-Altın korelasyon grafiği için yeterli veri bulunamadı.")
