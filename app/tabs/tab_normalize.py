"""Tab 3 — Normalize Karşılaştırma grafiği."""

from typing import TYPE_CHECKING

import streamlit as st

from app.charts import create_overlay_chart, create_correlation_chart
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

        # Ortak tarih aralığını bul — eğer tüm serilerde bugünkü fiyat varsa, bugüne kadar uzat
        today = max(s.index.max() for s in _norm_visible.values())
        common_start = max(s.index.min() for s in _norm_visible.values())
        # Eğer tüm serilerde today varsa, ortak bitişi today yap
        if all(today in s.index for s in _norm_visible.values()):
            common_end = today
        else:
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
        # Grafik altına merkezi live değerlerini göster — seri kesim tarihinden bağımsız
        last_date = common_end
        # ctx.live: tüm programın tek merkezi referansı — her yerde aynı değer
        _cur_altins1 = ctx.live.altins1
        _cur_beklenen = ctx.live.beklenen_altins1   # gram_gold_tl × 0.01 (beklenen ALTINS1)
        _cur_gram_tl = ctx.live.gram_gold_tl
        st.caption(
            f"📅 Ortak aralık: {common_start.strftime('%d.%m.%Y')} — {common_end.strftime('%d.%m.%Y')} | "
            f"Tüm seriler ilk değere göre normalize edilmiştir (başlangıç = 0%)."
        )
        st.info(
            f"**GÜNCEL DEĞERLER (Tüm Grafiklerde Aynı Kaynak — live):**\n"
            f"ALTINS1: {f'₺{_cur_altins1:.2f}' if _cur_altins1 else '-'}  |  "
            f"%1 Gr Altın (Beklenen): {f'₺{_cur_beklenen:.2f}' if _cur_beklenen else '-'}  |  "
            f"Gram Altın TL: {f'₺{_cur_gram_tl:.2f}' if _cur_gram_tl else '-'}\n"
            f"(Grafik aralığı: {last_date.strftime('%d.%m.%Y')}'ye kadar)"
        )
    else:
        st.warning("Normalize karşılaştırma için yeterli tarihsel veri bulunamadı.")

    # ── Borsa-Altın Korelasyonu Grafiği ────────────────────────
    st.markdown("---")
    st.subheader("📈 Borsa-Altın Korelasyonu")
    st.caption("BIST 100, Gram Altın TL ve ALTINS1 normalize karşılaştırması — borsa yönünün altın sertifikasına etkisini gösterir.")

    bist100_hist_series = ctx.series.bist100

    _corr_series = {}
    if altins1_hist_series is not None and len(altins1_hist_series) > 0:
        _corr_series["altins1"] = altins1_hist_series
    if gram_gold_hist_series is not None and len(gram_gold_hist_series) > 0:
        _corr_series["gram"] = gram_gold_hist_series
    if bist100_hist_series is not None and len(bist100_hist_series) > 0:
        _corr_series["bist100"] = bist100_hist_series

    if len(_corr_series) >= 2:
        corr_start = max(s.index.min() for s in _corr_series.values())
        corr_end = min(s.index.max() for s in _corr_series.values())

        c_a1 = altins1_hist_series.loc[corr_start:corr_end] if "altins1" in _corr_series else None
        c_gt = gram_gold_hist_series.loc[corr_start:corr_end] if "gram" in _corr_series else None
        c_bist = bist100_hist_series.loc[corr_start:corr_end] if "bist100" in _corr_series else None

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
