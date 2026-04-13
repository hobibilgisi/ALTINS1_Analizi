"""
ALTINS1 Analiz — Ana Uygulama (Streamlit)
Altın sertifikası takip ve sinyal sistemi.

ALTINS1 = 0.01 gram altın sertifikası (BIST).
Beklenen Fiyat = Gram Altın TL × 0.01
Makas (%) = (Gerçek ALTINS1 - Beklenen) / Beklenen × 100

Çalıştırma: streamlit run main.py
"""

import logging
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import (
    AppConfig, SignalThresholds,
    ALTINS1_GRAM_KATSAYI,
    APP_VERSION, APP_VERSION_DATE, APP_VERSION_NOTES,
)
from app.data_fetcher import (
    fetch_current_prices, fetch_all_history, fetch_altins1_mynet,
    is_bist_open, load_prices_from_cache,
)
from app.signal_engine import evaluate_signal, generate_signal_message, SignalType
from app.news_fetcher import get_daily_and_weekly_news
from app.email_notifier import send_daily_signal_email
from app.config import EmailConfig
from app.data_preparer import prepare_all_series
from app.tabs import TabContext
from app.tabs import (
    tab_altins1, tab_spread, tab_normalize,
    tab_ons, tab_gold_silver, tab_news,
    tab_reserves, tab_guide,
)

# ── Logging ────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
_log_handlers = [logging.StreamHandler()]
try:
    _log_handlers.append(logging.FileHandler("logs/app.log", encoding="utf-8"))
except OSError:
    pass  # Cloud ortamda dosya yazılamayabilir
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=_log_handlers,
)
logger = logging.getLogger(__name__)

# ── Streamlit Sayfa Ayarları ───────────────────────────────────
config = AppConfig()
st.set_page_config(
    page_title=config.page_title,
    page_icon=config.page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PWA Desteği (Ana Ekrana Ekleme) ────────────────────────────
st.markdown("""
<link rel="manifest" href="./static/manifest.json">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="ALTINS1 Analiz">
<meta name="theme-color" content="#ffa726">
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.title("🪙 ALTINS1 Analiz")
    st.markdown("---")

    if st.button("🔄 Verileri Yenile", width="stretch"):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("---")
    # Piyasa Verileri için yer ayır — veriler yüklendikten sonra doldurulacak
    _piyasa_container = st.container()

    st.markdown("---")
    st.subheader("🔤 Yazı Boyutu")
    _font_size = st.slider("Metin boyutu (px)", 14, 28, 21, 1, key="font_size")
    st.subheader("📏 Grafik Yüksekliği")
    _chart_height = st.slider("Yükseklik (px)", 400, 1200, 750, 50, key="chart_height")
    st.subheader("� Grafik Etkileşimi")
    _grafik_kilidi = st.toggle("Grafik Kilidi (mobil için önerilir)", value=True, key="grafik_kilidi",
                                help="Açıkken grafiklere dokunma yakınlaştırma yapmaz. Kaydırma ve değer okuma rahatlaşır.")
    st.subheader("�📅 Tarihsel Veri")
    period = st.selectbox("Periyot", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

# ── Dinamik yazı boyutu CSS ────────────────────────────────────
st.markdown(f"""
<style>
    /* ── Streamlit Cloud GitHub/Fork butonu ve footer gizleme ── */
    .stDeployButton,
    [data-testid="stToolbarActions"] > a[href*="github"],
    .stAppDeployButton,
    .viewerBadge_container__r5tak,
    .viewerBadge_link__qRIco,
    [data-testid="manage-app-button"] {{
        display: none !important;
    }}
    footer {{
        visibility: hidden !important;
        height: 0 !important;
    }}
    footer::after {{
        display: none !important;
    }}
    /* Sidebar genişliği: ekranın 1/4'ü (sadece açıkken) */
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        width: 25vw !important;
        min-width: 300px;
        max-width: 480px;
    }}
    /* Ana içerik sidebar kapanınca tüm ekrana yayılsın */
    .stMainBlockContainer {{
        max-width: 100% !important;
    }}
    section[data-testid="stSidebar"] .stMetricValue {{
        font-size: {max(_font_size - 2, 14)}px !important;
    }}
    section[data-testid="stSidebar"] .stMetricLabel {{
        font-size: {max(_font_size - 4, 12)}px !important;
    }}
    /* Genel metin, paragraf, caption, metric, tablo */
    .stMainBlockContainer p,
    .stMainBlockContainer span,
    .stMainBlockContainer label,
    .stMainBlockContainer td,
    .stMainBlockContainer th,
    .stMainBlockContainer .stMetricValue,
    .stMainBlockContainer .stMetricLabel,
    .stMainBlockContainer .stCaption,
    .stMainBlockContainer li,
    .stMainBlockContainer div[data-testid="stText"] {{
        font-size: {_font_size}px !important;
    }}
    /* Metric delta */
    .stMainBlockContainer div[data-testid="stMetricDelta"] {{
        font-size: {max(_font_size - 2, 10)}px !important;
    }}
    /* Checkbox, radio, selectbox etiketleri */
    .stMainBlockContainer .stCheckbox label span,
    .stMainBlockContainer .stRadio label span,
    .stMainBlockContainer .stSelectbox label {{
        font-size: {_font_size}px !important;
    }}
    /* Tab etiketleri */
    .stMainBlockContainer button[data-baseweb="tab"] {{
        font-size: {_font_size + 2}px !important;
    }}
    /* Başlıklar (header/subheader) */
    .stMainBlockContainer h1 {{
        font-size: {_font_size + 14}px !important;
    }}
    .stMainBlockContainer h2 {{
        font-size: {_font_size + 10}px !important;
    }}
    .stMainBlockContainer h3 {{
        font-size: {_font_size + 6}px !important;
    }}
    /* ── Tab başlıkları: taşma yerine alt satıra geç ── */
    div[data-baseweb="tab-list"] {{
        flex-wrap: wrap !important;
        gap: 4px 0 !important;
    }}
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        white-space: nowrap !important;
    }}
    /* ── Seçili tab: alt çizgi highlight yerine text underline ── */
    div[data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    div[data-baseweb="tab-list"] button[aria-selected="true"] {{
        text-decoration: underline !important;
        text-underline-offset: 4px !important;
        text-decoration-thickness: 3px !important;
    }}
    /* ── Responsive: Mobil (<768px) ── */
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"][aria-expanded="true"] {{
            width: 85vw !important;
            min-width: 0 !important;
        }}
        .stMainBlockContainer h1 {{
            font-size: {max(_font_size + 4, 20)}px !important;
        }}
        .stMainBlockContainer h2 {{
            font-size: {max(_font_size + 2, 18)}px !important;
        }}
        div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
            font-size: {max(_font_size - 2, 12)}px !important;
            padding: 6px 8px !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)


# ── Veri Çekme (cache'li) ─────────────────────────────────────
@st.cache_data(ttl=config.cache_ttl_sec)
def load_prices():
    return fetch_current_prices()


@st.cache_data(ttl=config.cache_ttl_sec)
def load_altins1_history():
    _, hist_df = fetch_altins1_mynet()
    return hist_df


@st.cache_data(ttl=config.cache_ttl_sec)
def load_history(period_val):
    return fetch_all_history(period=period_val)


@st.cache_data(ttl=600)
def load_news_split():
    return get_daily_and_weekly_news()


# ── Ana Sayfa ──────────────────────────────────────────────────
st.title("📊 ALTINS1 Analiz — Altın Sertifikası Takip ve Sinyal Sistemi")
st.caption("ALTINS1 = 0.01 gram altın sertifikası | Beklenen Fiyat = Gram Altın TL × 0.01")

# ── Seans Durumu ───────────────────────────────────────────────
bist_acik = is_bist_open()

# Verileri yükle (canlı çek, başarısızsa cache'den oku)
prices = load_prices()
_from_cache = False

if not prices.get("altins1_fiyat") or not prices.get("gram_altin_tl"):
    cached = load_prices_from_cache()
    if cached:
        prices = cached
        _from_cache = True

if not bist_acik:
    cache_time = prices.get("_cache_time", "")
    if cache_time:
        try:
            ct = datetime.fromisoformat(cache_time)
            cache_str = ct.strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            cache_str = str(cache_time)
    else:
        cache_str = "bilinmiyor"
    st.info(
        f"🔒 **BIST seansı kapalı** — Gösterilen veriler son seans verilerine dayanmaktadır. "
        f"(Son güncelleme: {cache_str})"
    )
elif _from_cache:
    st.warning(
        "⚠️ Canlı veri çekilemedi, son kaydedilen veriler gösteriliyor. "
        "İnternet bağlantınızı kontrol edin."
    )
altins1_hist = load_altins1_history()
history = load_history(period)

# ── Tarihsel veri hazırlığı ────────────────────────────────────
_series = prepare_all_series(history, altins1_hist, prices)
spread_hist = _series.spread

avg_spread = float(spread_hist.mean()) if spread_hist is not None and len(spread_hist) > 0 else 15.0
buy_th = round(avg_spread, 1)
strong_buy_th = round(avg_spread - 5.0, 1)

# ── Sidebar (alt kısım — sinyal eşikleri) ─────────────────────
with st.sidebar:
    st.markdown("---")
    st.subheader("⚙️ Sinyal Eşikleri")
    st.caption("Alım eşikleri ortalama tarihsel makasa bağlıdır.")
    st.info(f"📊 Ort. Makas: **%{avg_spread:.1f}** → Alım eşiği: **%{buy_th}**")
    st.info(f"🟢 Güçlü Alım eşiği (ort. − 5): **%{strong_buy_th}**")
    sell_th = st.slider("Satım eşiği (%)", 20.0, 50.0, 35.0, 1.0)
    strong_sell_th = st.slider("Güçlü Satım eşiği (%)", 30.0, 70.0, 50.0, 1.0)

thresholds = SignalThresholds(
    strong_buy=strong_buy_th,
    buy_threshold=buy_th,
    sell_threshold=sell_th,
    strong_sell=strong_sell_th,
)

# ═══════════════════════════════════════════════════════════════
# 1) ALTINS1 MAKAS ANALİZİ → Sidebar'a taşındı
# ═══════════════════════════════════════════════════════════════

altins1_fiyat = prices.get("altins1_fiyat")
gram_altin_tl = prices.get("gram_altin_tl")
beklenen = prices.get("beklenen_altins1")
makas_pct = prices.get("makas_pct")

# Sinyal hesapla (sidebar ve e-posta için kullanılacak)
if makas_pct:
    signal = evaluate_signal(makas_pct, thresholds)
    signal_msg = generate_signal_message(signal, makas_pct)
else:
    signal = SignalType.NEUTRAL
    signal_msg = "Veri bekleniyor…"

color_map = {
    SignalType.STRONG_BUY: "#00c853",
    SignalType.BUY: "#7cb342",
    SignalType.NEUTRAL: "#78909c",
    SignalType.SELL: "#ff9800",
    SignalType.STRONG_SELL: "#d50000",
}

# Sidebar'daki ayrılmış alanı doldur — Makas + Sinyal + Piyasa Verileri
with _piyasa_container:
    if altins1_fiyat and gram_altin_tl and beklenen:
        # Sinyal kutusu (en üstte)
        st.markdown(
            f'<div style="padding:10px; border-radius:8px; '
            f'background-color:{color_map[signal]}; color:white; '
            f'font-size:{max(_font_size - 2, 13)}px; text-align:center; margin:4px 0 8px 0;">'
            f'{signal_msg}</div>',
            unsafe_allow_html=True,
        )
        # Makas metrikleri (tek satır, 3 sütun)
        _sc1, _sc2, _sc3 = st.columns(3)
        _sc1.metric("ALTINS1", f"₺{altins1_fiyat:,.2f}")
        _sc2.metric("%1 Gr Altın", f"₺{beklenen:,.2f}")
        _sc3.metric("Makas", f"%{makas_pct:,.1f}", delta=f"{makas_pct:+.1f}%")

        st.markdown("---")
        st.subheader("💰 Piyasa Verileri")
        # İki sütunlu piyasa verileri
        _market_items = [
            ("Gram Altın TL", f"₺{gram_altin_tl:,.2f}"),
        ]
        ons_val = prices.get("ons_altin_usd")
        if ons_val:
            _market_items.append(("Ons Altın (USD)", f"${ons_val:,.2f}"))
        for lbl, key, fmt_fn in [
            ("Dolar/TL", "dolar_tl", lambda v: f"₺{v:,.4f}"),
            ("Çeyrek Altın", "ceyrek_altin", lambda v: f"₺{v:,.2f}"),
        ]:
            val = prices.get(key)
            if val:
                _market_items.append((lbl, fmt_fn(val)))

        # Hacim (Lot) — anlık + aylık ortalama
        _hacim_lot = prices.get("hacim_lot")
        if _hacim_lot:
            _market_items.append(("Hacim (Lot)", f"{_hacim_lot:,.0f}"))
            from app.data_fetcher import load_volume_avg
            _avg_vol = load_volume_avg(30)
            if _avg_vol:
                _market_items.append(("30G Ort. Hacim", f"{_avg_vol:,.0f}"))

        for i in range(0, len(_market_items), 2):
            cols = st.columns(2)
            cols[0].metric(_market_items[i][0], _market_items[i][1])
            if i + 1 < len(_market_items):
                cols[1].metric(_market_items[i + 1][0], _market_items[i + 1][1])

        update_date = prices.get("update_date")
        if update_date:
            st.caption(f"📡 {update_date}")

        with st.expander("📐 Makas Hesaplama Detayı"):
            st.markdown(f"""
| Parametre | Değer |
|---|---|
| Gram Altın TL (piyasa) | ₺{gram_altin_tl:,.2f} |
| ALTINS1 Katsayısı | {ALTINS1_GRAM_KATSAYI} (0.01 gram) |
| **%1 Gr Altın** | **₺{beklenen:,.2f}** |
| ALTINS1 Gerçek Fiyat (BIST) | ₺{altins1_fiyat:,.2f} |
| **Makas (%)** | **%{makas_pct:.2f}** |
| Formül | (Gerçek - Beklenen) / Beklenen × 100 |
""")
    else:
        st.warning("⚠️ Fiyat verisi alınamadı.")

if not altins1_fiyat or not gram_altin_tl:
    st.error(
        "⚠️ ALTINS1 veya gram altın fiyatı alınamadı ve önceki kayıtlı veri de bulunamadı. "
        "İnternet bağlantınızı kontrol edin. İlk çalıştırmada seans saatlerinde veri çekilmesi gerekir."
    )
    st.json(prices)


# ═══════════════════════════════════════════════════════════════
# 2) GRAFİKLER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("📈 Grafikler")


# ── Tab Bağlamı ────────────────────────────────────────────────
_tab_ctx = TabContext(
    series=_series,
    prices=prices,
    history=history,
    spread_hist=spread_hist,
    thresholds=thresholds,
    font_size=_font_size,
    chart_height=_chart_height,
    grafik_kilidi=_grafik_kilidi,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 ALTINS1 Analizi",
    "📊 S1/Gr Oranı Analizi",
    "📈 Normalize Karşılaştırma",
    "🕯️ Ons Altın (XAU/USD)",
    "🥇🥈 Altın vs Gümüş",
    "📰 Haberler",
    "🏦 Merkez Bankaları",
    "📖 Bilgi Rehberi",
])

with tab1:
    tab_altins1.render(_tab_ctx)

with tab2:
    tab_spread.render(_tab_ctx)

with tab3:
    tab_normalize.render(_tab_ctx)

with tab4:
    tab_ons.render(_tab_ctx)

with tab5:
    tab_gold_silver.render(_tab_ctx)

with tab6:
    daily_news, weekly_news = load_news_split()
    tab_news.render(daily_news, weekly_news)

with tab7:
    tab_reserves.render(_grafik_kilidi)

with tab8:
    tab_guide.render()


# ═══════════════════════════════════════════════════════════════
# 4) E-POSTA BİLDİRİM
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("📧 E-posta Bildirim")

with st.expander("E-posta Ayarları ve Gönderim", expanded=False):
    # Ortam değişkenlerinden config yükle
    _email_cfg = EmailConfig.from_env()

    # Sidebar'dan override edilebilecek alanlar
    _smtp_server = st.text_input("SMTP Sunucu", value=_email_cfg.smtp_server or "smtp.gmail.com")
    _smtp_port = st.number_input("SMTP Port", value=_email_cfg.smtp_port, min_value=1, max_value=65535)
    _sender = st.text_input("Gönderen E-posta", value=_email_cfg.sender_email)
    _password = st.text_input("Uygulama Şifresi", value=_email_cfg.sender_password, type="password")

    st.markdown("**Alıcılar** (her satıra bir e-posta)")
    _recipients_text = st.text_area(
        "Alıcı Listesi",
        value="\n".join(_email_cfg.recipients) if _email_cfg.recipients else "",
        height=100,
        help="Her satıra bir e-posta adresi yazın.",
    )

    _recipient_list = [r.strip() for r in _recipients_text.split("\n") if r.strip()]

    if _recipient_list:
        st.caption(f"📬 {len(_recipient_list)} alıcıya gönderilecek")

    col_send, col_test = st.columns(2)

    # Güncel sinyal verisini hazırla
    _email_prices = {
        "altins1_fiyat": prices.get("altins1_fiyat"),
        "gram_altin_tl": prices.get("gram_altin_tl"),
        "beklenen_altins1": prices.get("beklenen_altins1"),
        "makas_pct": prices.get("makas_pct"),
        "ons_altin_usd": prices.get("ons_altin_usd"),
        "dolar_tl": prices.get("dolar_tl"),
    }
    _email_thresholds = {
        "strong_buy": thresholds.strong_buy,
        "buy": thresholds.buy_threshold,
        "sell": thresholds.sell_threshold,
        "strong_sell": thresholds.strong_sell,
        "avg_spread": avg_spread,
    }

    _active_signal = evaluate_signal(prices.get("makas_pct", 0) or 0, thresholds)
    _active_signal_msg = generate_signal_message(_active_signal, prices.get("makas_pct", 0) or 0)

    with col_send:
        if st.button("📤 Sinyal Özeti Gönder", width="stretch"):
            if not _sender or not _password:
                st.error("SMTP gönderen e-posta ve şifre gerekli.")
            elif not _recipient_list:
                st.error("En az bir alıcı adresi girin.")
            else:
                _cfg = EmailConfig(
                    smtp_server=_smtp_server,
                    smtp_port=_smtp_port,
                    sender_email=_sender,
                    sender_password=_password,
                    recipients=_recipient_list,
                )
                with st.spinner("E-posta gönderiliyor..."):
                    ok = send_daily_signal_email(
                        _cfg, _active_signal, _active_signal_msg,
                        _email_prices, _email_thresholds,
                    )
                if ok:
                    st.success(f"✅ {len(_recipient_list)} alıcıya gönderildi!")
                else:
                    st.error("❌ Gönderim başarısız. Logları kontrol edin.")

    with col_test:
        if st.button("🧪 Test E-postası", width="stretch"):
            if not _sender or not _password:
                st.error("SMTP bilgileri eksik.")
            else:
                _cfg = EmailConfig(
                    smtp_server=_smtp_server,
                    smtp_port=_smtp_port,
                    sender_email=_sender,
                    sender_password=_password,
                    recipients=[_sender],
                )
                with st.spinner("Test gönderiliyor..."):
                    ok = send_daily_signal_email(
                        _cfg, _active_signal, _active_signal_msg,
                        _email_prices, _email_thresholds,
                        recipients=[_sender],
                    )
                if ok:
                    st.success(f"✅ Test e-postası {_sender} adresine gönderildi!")
                else:
                    st.error("❌ Test başarısız. SMTP ayarlarını kontrol edin.")


# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")

_footer_cols = st.columns([3, 1])
with _footer_cols[0]:
    st.caption(f"ALTINS1 Analiz v{APP_VERSION} | Yalnızca bilgi amaçlıdır, yatırım tavsiyesi değildir.")
with _footer_cols[1]:
    with st.expander("📋 Güncelleme Notu"):
        st.markdown(f"**v{APP_VERSION}** — {APP_VERSION_DATE}")
        for _note in APP_VERSION_NOTES:
            st.markdown(f"- {_note}")

