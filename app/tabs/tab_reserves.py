"""Tab 7 — Merkez Bankası Altın Rezervleri, değişim grafikleri ve sinyal paneli."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import turkce_tarih_ekseni
from app.reserve_signals import compute_all_signals, compute_composite_signal
from app.reserve_tracker import (
    build_history_dataframe,
    fetch_reserve_data,
    get_all_tracked_countries,
    get_cache_date,
    get_default_chart_countries,
    get_highlighted_reserves,
    get_period_options,
    get_reserve_sources_info,
    save_daily_snapshot,
)
from app.ui_helpers import PLOTLY_CONFIG


def render(grafik_kilidi: bool) -> None:
    """Merkez bankası altın rezerv panelini gösterir."""
    st.caption(
        "ℹ️ WGC, IMF IFS ve Wikipedia kaynaklarından derlenen merkez bankası altın rezervlerinin "
        "tarihsel değişim grafiği ve sinyal paneli. Büyük merkez bankalarının alım/satım eğilimleri "
        "uzun vadeli altın fiyat trendleri için önemli bir gösterge niteliği taşır."
    )
    st.subheader("🏦 Merkez Bankası Altın Rezervleri")
    st.caption("Kaynak: WGC/IMF IFS tarihsel veri (2018+) + Wikipedia güncel veri")

    reserves = fetch_reserve_data()
    cache_date = get_cache_date()

    # Günlük snapshot'ı kaydet
    if reserves:
        save_daily_snapshot(reserves)

    if cache_date:
        st.caption(f"📅 Son güncelleme: {cache_date}")

    if reserves:
        # ── Öne çıkan ülkeler (kartlar) ──
        highlighted = get_highlighted_reserves(reserves)
        if highlighted:
            st.markdown("##### 🌍 Öne Çıkan Ülkeler")
            st.caption("ℹ️ **Altın Payı**: Ülkenin toplam döviz rezervleri içinde altının yüzdesel ağırlığı (IMF/WGC verisi)")
            cols = st.columns(5)
            for i, r in enumerate(highlighted):
                with cols[i % 5]:
                    tonnes_str = f"{r.gold_tonnes:,.1f}" if r.gold_tonnes else "—"
                    pct_str = f"{r.pct_of_reserves:.1f}%" if r.pct_of_reserves else "—"
                    rank_str = f"#{r.rank}" if r.rank else "—"
                    st.metric(
                        label=f"{r.country_tr} ({rank_str})",
                        value=f"{tonnes_str} ton",
                        delta=f"Altın Payı: {pct_str}",
                        delta_color="off",
                    )

        # ── DEĞİŞİM GRAFİĞİ ──
        st.markdown("---")
        st.markdown("##### 📈 Rezerv Değişim Takibi")
        st.caption(
            "ℹ️ 2018'den bugüne çeyreklik WGC/IMF IFS verisi + günlük Wikipedia snapshot'ları birleştirilir. "
            "Yeni veriler her gün otomatik kaydedilir."
        )

        # Kontroller
        _chart_col1, _chart_col2 = st.columns([3, 1])

        # Ülke seçimi
        all_tracked = get_all_tracked_countries()
        default_countries = get_default_chart_countries()

        # Kayıtlı ülkelerde olmayanları varsayılanlara ekle (ilk gün için)
        if not all_tracked:
            all_tracked = [r.country_tr for r in reserves if r.gold_tonnes]

        # Varsayılanları mevcut listede olanlarla filtrele
        valid_defaults = [c for c in default_countries if c in all_tracked]

        with _chart_col1:
            selected_countries = st.multiselect(
                "Ülke Seçimi",
                options=all_tracked,
                default=valid_defaults,
                key="reserve_chart_countries",
            )

        with _chart_col2:
            period_opts = get_period_options()
            period_key = st.selectbox(
                "Periyot",
                options=list(period_opts.keys()),
                format_func=lambda k: period_opts[k],
                index=3,  # varsayılan: Son 12 Ay
                key="reserve_chart_period",
            )

        # Grafik modu: ton / % değişim
        show_pct = st.toggle("% Değişim Göster", value=True, key="reserve_pct_toggle")

        if selected_countries:
            tonnes_df, pct_df = build_history_dataframe(selected_countries, period_key)
            _hist_days = len(tonnes_df) if tonnes_df is not None else 0

            if tonnes_df is not None and _hist_days >= 2:
                chart_df = pct_df if show_pct else tonnes_df

                fig = go.Figure()
                for col in chart_df.columns:
                    fig.add_trace(go.Scatter(
                        x=chart_df.index,
                        y=chart_df[col],
                        name=col,
                        mode="lines+markers",
                        hovertemplate=(
                            f"<b>{col}</b><br>"
                            "Tarih: %{x|%d.%m.%Y}<br>"
                            + ("Değişim: %{y:.2f}%<extra></extra>" if show_pct
                               else "Miktar: %{y:,.1f} ton<extra></extra>")
                        ),
                    ))

                y_title = "Değişim (%)" if show_pct else "Altın (Ton)"
                fig.update_layout(
                    height=500,
                    yaxis_title=y_title,
                    xaxis_title="",
                    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                    margin=dict(l=60, r=20, t=30, b=80),
                    hovermode="x",
                    template="plotly_dark",
                    dragmode=False if grafik_kilidi else "zoom",
                )

                if show_pct:
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

                st.plotly_chart(turkce_tarih_ekseni(fig), width="stretch", key="reserve_change_chart", config=PLOTLY_CONFIG)

                # Uyarı: az veri
                if _hist_days < 30:
                    st.info(
                        f"📊 Şu anda **{_hist_days} günlük** veri mevcut. "
                        f"Anlamlı trend analizi için en az 30 günlük veri gereklidir. "
                        f"Veriler her gün otomatik olarak birikmektedir."
                    )

                # Değişim özet tablosu
                if len(pct_df) >= 2:
                    with st.expander("📊 Değişim Özeti", expanded=True):
                        summary_rows = []
                        for col in pct_df.columns:
                            valid = pct_df[col].dropna()
                            if len(valid) >= 2:
                                first_val = tonnes_df[col].dropna().iloc[0]
                                last_val = tonnes_df[col].dropna().iloc[-1]
                                change = last_val - first_val
                                pct_change = valid.iloc[-1]
                                summary_rows.append({
                                    "Ülke": col,
                                    "Başlangıç (Ton)": f"{first_val:,.1f}",
                                    "Güncel (Ton)": f"{last_val:,.1f}",
                                    "Değişim (Ton)": f"{change:+,.1f}",
                                    "Değişim (%)": f"{pct_change:+.2f}%",
                                })
                        if summary_rows:
                            st.dataframe(
                                pd.DataFrame(summary_rows),
                                width="stretch",
                                hide_index=True,
                            )
            else:
                # Veri yetersiz — tablo formatında güncel verileri göster
                st.warning(
                    "📊 Grafik için yeterli tarihsel veri henüz birikmemiş. "
                    "Veriler her gün otomatik kaydedilir. Aşağıda seçili ülkelerin **güncel** rezerv miktarları görüntülenmektedir."
                )
                _sel_table = []
                for r in reserves:
                    if r.country_tr in selected_countries:
                        _sel_table.append({
                            "Ülke": r.country_tr,
                            "Sıra": f"#{r.rank}" if r.rank else "—",
                            "Altın (Ton)": f"{r.gold_tonnes:,.1f}" if r.gold_tonnes else "—",
                            "Altın Payı (%)": f"{r.pct_of_reserves:.1f}" if r.pct_of_reserves else "—",
                        })
                if _sel_table:
                    st.dataframe(pd.DataFrame(_sel_table), width="stretch", hide_index=True)
        else:
            st.info("Grafik için en az bir ülke seçin.")

        # ── MB SİNYAL PANELİ ──
        _render_signal_panel(reserves)

        # ── Tam tablo ──
        st.markdown("---")
        with st.expander("📊 Tüm Ülkeler (İlk 50)", expanded=False):
            table_data = []
            for r in reserves[:50]:
                table_data.append({
                    "Sıra": str(r.rank) if r.rank else "—",
                    "Ülke": r.country_tr,
                    "Altın (Ton)": f"{r.gold_tonnes:,.1f}" if r.gold_tonnes else "—",
                    "Altın Payı (%)": f"{r.pct_of_reserves:.1f}" if r.pct_of_reserves else "—",
                })
            st.dataframe(
                pd.DataFrame(table_data),
                width="stretch",
                hide_index=True,
            )

        # ── Kaynak listesi ──
        with st.expander("📎 Veri Kaynakları", expanded=False):
            sources = get_reserve_sources_info()
            reserve_df = pd.DataFrame([
                {
                    "Kurum": s["name"],
                    "Kod": s["code"],
                    "Güncelleme": s["update_freq"],
                }
                for s in sources
            ])
            st.dataframe(reserve_df, width="stretch", hide_index=True)
    else:
        st.warning("Altın rezerv verileri yüklenemedi. İnternet bağlantınızı kontrol edin.")


def _render_signal_panel(reserves) -> None:
    """Merkez bankası sinyal panelini oluşturur."""
    st.markdown("---")
    st.markdown("##### 📡 Merkez Bankası Sinyal Paneli")
    st.caption(
        "Merkez bankalarının altın alım/satım hareketlerinden üretilen yön sinyalleri. "
        "Veriler **WGC/IMF IFS** çeyreklik tarihsel verisine (2018+) dayanır."
    )

    # Sinyal hesapla: tüm takip edilen ülkelerle
    _signal_countries = get_all_tracked_countries()
    _signal_countries_hist = [c for c in _signal_countries
                              if c not in ("IMF", "BIS", "Avrupa Merkez Bankası")]
    _sig_df, _ = build_history_dataframe(_signal_countries_hist, "tumu")

    # Altın fiyat korelasyonu için çeyreklik ons fiyatı hazırla
    _gold_q = None
    try:
        import yfinance as yf
        _gold_hist = yf.Ticker("GC=F").history(period="7y", interval="3mo")
        if _gold_hist is not None and len(_gold_hist) > 4:
            _gold_q = _gold_hist["Close"]
            _gold_q.index = pd.to_datetime(_gold_q.index).tz_localize(None)
    except Exception:
        pass

    if _sig_df is not None and len(_sig_df) >= 2:
        _signals = compute_all_signals(
            _sig_df,
            reserves_data=reserves,
            gold_prices_quarterly=_gold_q,
        )
        _composite = compute_composite_signal(_signals)

        if _composite:
            # ── 1) ANA GÖSTERGE: Bileşik sinyal — büyük ve net ──
            _comp_col1, _comp_col2 = st.columns([3, 1])
            with _comp_col1:
                st.metric(
                    label=f"{_composite.emoji} {_composite.name}",
                    value=_composite.label,
                    delta=f"Puan: {_composite.value:+.0f} / 100",
                    delta_color="normal" if _composite.value >= 0 else "inverse",
                )
            with _comp_col2:
                st.caption("Sinyal gücü")
                _bar_val = max(0, min(100, int((_composite.value + 100) / 2)))
                st.progress(_bar_val)
                st.caption(f"{len(_signals)} gösterge · {len(_sig_df.columns)} MB")

            # ── 2) ÖNE ÇIKAN GÖSTERGELER: En değerli 3 sinyal öne çıkar ──
            # Sıralama: mutlak değere göre en güçlü 3 sinyal
            _sorted_signals = sorted(_signals, key=lambda s: abs(s.value), reverse=True)
            _top_signals = _sorted_signals[:3]
            _other_signals = _sorted_signals[3:]

            if _top_signals:
                st.markdown("")
                _top_cols = st.columns(len(_top_signals))
                for i, _s in enumerate(_top_signals):
                    with _top_cols[i]:
                        st.metric(
                            label=f"{_s.emoji} {_s.name}",
                            value=f"{_s.value:+.0f}",
                            delta=_s.label,
                            delta_color="normal" if _s.value >= 0 else "inverse",
                        )

            # ── 3) DİĞER GÖSTERGELER: Expander içinde detay ──
            if _other_signals:
                with st.expander(f"📊 Diğer Göstergeler ({len(_other_signals)})", expanded=False):
                    for _s in _other_signals:
                        _d_col1, _d_col2 = st.columns([1, 3])
                        with _d_col1:
                            st.metric(
                                label=f"{_s.emoji} {_s.name}",
                                value=f"{_s.value:+.0f}",
                            )
                        with _d_col2:
                            st.caption(_s.detail)

            # ── 4) TÜM SİNYAL DETAYLARI: Meraklılar için ──
            with st.expander("🔍 Tüm Sinyal Detayları", expanded=False):
                for _s in _sorted_signals:
                    st.markdown(f"**{_s.emoji} {_s.name}** — {_s.label} ({_s.value:+.0f})")
                    st.caption(_s.detail)
                st.markdown("---")
                st.caption(
                    "⚠️ Bu sinyaller yalnızca bilgi amaçlıdır, yatırım tavsiyesi değildir. "
                    "Çeyreklik veriye dayandığından kısa vadeli kararlar için yeterli olmayabilir."
                )
    else:
        st.info("Sinyal hesaplamak için yeterli tarihsel veri birikmemiş.")
