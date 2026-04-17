"""
ALTINS1 Analiz — Ana Uygulama (Streamlit)
Altın sertifikası takip ve sinyal sistemi.

ALTINS1 = 0.01 gram altın sertifikası (BIST).
Beklenen Fiyat = Gram Altın TL × 0.01
Makas (%) = (Gerçek ALTINS1 - Beklenen) / Beklenen × 100

Çalıştırma: streamlit run main.py
"""
# pyright: reportUnknownVariableType=false

import base64
import logging
import os
import sys
import time
from datetime import datetime
from typing import Callable, List, cast
from zoneinfo import ZoneInfo

import streamlit as st
from streamlit_autorefresh import st_autorefresh as _st_autorefresh  # pyright: ignore[reportMissingTypeStubs]

st_autorefresh = cast(Callable[..., int], _st_autorefresh)

_TZ_ISTANBUL = ZoneInfo("Europe/Istanbul")

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import (
    AppConfig, SignalThresholds,
    ALTINS1_GRAM_KATSAYI,
    APP_VERSION_FULL,
    APP_VERSION_DATE, APP_VERSION_NOTES,
    EmailConfig,
)
from app.data_fetcher import is_bist_open
from app.market_data import fetch_market_data
from app.signal_engine import evaluate_signal, generate_signal_message, SignalType
from app.news_fetcher import get_daily_and_weekly_news
from app.email_notifier import send_daily_signal_email
from app.tabs import TabContext
from app.tabs import (
    tab_altins1, tab_spread,
    tab_ons, tab_gold_silver, tab_news,
    tab_reserves, tab_guide,
)

# ── Logging ────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
_log_handlers: List[logging.Handler] = [logging.StreamHandler()]
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
<link rel="apple-touch-icon" href="./static/icon-192.png">
<link rel="icon" type="image/x-icon" href="./static/favicon.ico">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="ALTINS1 Analiz">
<meta name="theme-color" content="#ffa726">
""", unsafe_allow_html=True)

# ── Açılış Animasyonu (Splash Screen) ─────────────────────────
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False
    st.session_state.splash_start = time.time()

if not st.session_state.splash_shown:
    _elapsed = time.time() - st.session_state.splash_start
    if _elapsed >= 4.5:
        st.session_state.splash_shown = True
        st.rerun()
    else:
        st_autorefresh(interval=500, key="splash_autorefresh")
        _webp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "altins1_logo_transparent.webp")
        with open(_webp_path, "rb") as _f:
            _gif_b64 = base64.b64encode(_f.read()).decode()
        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: #000000 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"],
        #MainMenu, footer {{
            display: none !important;
        }}
        .stMainBlockContainer, .block-container {{
            padding: 0 !important;
            max-width: 100vw !important;
        }}
        .splash-wrapper {{
            display: flex;
            width: 100vw;
            height: 100vh;
            justify-content: center;
            align-items: center;
            background: #000000;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 9999;
        }}
        .splash-wrapper img {{
            max-width: 70vw;
            max-height: 70vh;
            object-fit: contain;
        }}
        </style>
        <div class="splash-wrapper">
            <img src="data:image/webp;base64,{_gif_b64}" alt="ALTINS1 Logo">
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.image("static/icon-128.png", width=80)
    st.title("ALTINS1 Analiz")
    st.markdown("---")

    if st.button("🔄 Verileri Yenile", width="stretch"):
        st.cache_data.clear()
        st.rerun()
    _now_tr = datetime.now(_TZ_ISTANBUL)
    st.caption(f"Son güncelleme: {_now_tr.strftime('%H:%M:%S')}")

    # ── Seans açıkken otomatik yenileme (her 2 dakikada bir) ──
    _auto_refresh_enabled = st.toggle(
        "⏱️ Otomatik Yenile (2 dk)", value=True, key="auto_refresh",
        help="Seans açıkken sayfa her 2 dakikada otomatik güncellenir.",
    )
    if _auto_refresh_enabled and is_bist_open():
        st_autorefresh(interval=2 * 60 * 1000, key="bist_autorefresh")

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
        width: min(33vw, 400px) !important;
        min-width: 220px;
        max-width: 98vw;
    }}
    /* Ana içerik sidebar kapanınca tüm ekrana yayılsın */
    .stMainBlockContainer {{
        max-width: 100% !important;
    }}
    section[data-testid="stSidebar"] .stMetricValue {{
        font-size: clamp(10px, 2vw, 22px) !important;
        min-width: 0 !important;
        line-height: 1.1 !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        flex-shrink: 1 !important;
    }}
    section[data-testid="stSidebar"] .stMetricLabel {{
        font-size: clamp(9px, 1.7vw, 15px) !important;
        min-width: 0 !important;
        line-height: 1.1 !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        flex-shrink: 1 !important;
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
        font-size: clamp(10px, 2vw, 22px) !important;
        min-width: 0 !important;
        line-height: 1.1 !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        flex-shrink: 1 !important;
    }}
    /* Metric delta */
    .stMainBlockContainer div[data-testid="stMetricDelta"] {{
        font-size: {max(_font_size - 2, 10)}px !important;
    }}
    /* Checkbox, radio, selectbox etiketleri */
    .stMainBlockContainer .stCheckbox label span,
    .stMainBlockContainer .stRadio label span,
    .stMainBlockContainer .stSelectbox label {{
        font-size: clamp(9px, 1.7vw, 15px) !important;
        min-width: 0 !important;
        line-height: 1.1 !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        flex-shrink: 1 !important;
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


# ── Veri Çekme (cache'li) — TEK GİRİŞ NOKTASI ───────────────
@st.cache_data(ttl=config.cache_ttl_sec)
def load_market(period_val: str):
    """Tüm verileri TEK seferde çeker. Programın dış dünyayla tek temas noktası."""
    return fetch_market_data(period=period_val)


@st.cache_data(ttl=600)
def load_news_split():
    return get_daily_and_weekly_news()


# ── Ana Sayfa ──────────────────────────────────────────────────
st.title("📊 ALTINS1 Analiz — Altın Sertifikası Takip ve Sinyal Sistemi")
st.caption("ALTINS1 = 0.01 gram altın sertifikası | Beklenen Fiyat = Gram Altın TL × 0.01")

# ── Seans Durumu ───────────────────────────────────────────────
bist_acik = is_bist_open()

# Tüm verileri TEK seferde yükle (canlı çek, başarısızsa cache'den tamamla)
market = load_market(period)
_live = market.live
_current = market.current
_series = market.series
_has_live = _current.has_core_prices

if not bist_acik:
    cache_time = _live.cache_time
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
elif not _has_live:
    st.warning(
        "⚠️ Canlı veri çekilemedi, son kaydedilen veriler gösteriliyor. "
        "İnternet bağlantınızı kontrol edin."
    )

# Tarihsel veri referansları (tek kaynaktan)
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


# ── Tek Merkezi Referans Değerler ─────────────────────────────
# _live nesnesi TÜM veri için tek kaynak. Tüm metrikler, info boxlar,
# e-posta vs. buradaki değişkenleri kullanır — seri kesimlerine BAĞIMLI DEĞİL.
altins1_fiyat = _current.altins1
gram_altin_tl = _current.gram_gold_tl
beklenen = _current.beklenen_altins1
makas_pct = _current.makas_pct

# Sinyal hesapla (sidebar ve e-posta için kullanılacak)
if makas_pct is not None:
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
    if _current.has_core_prices:
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
        # İki sütunlu piyasa verileri — tüm değerler merkezi _live'dan
        _market_items = [
            ("Gram Altın TL", f"₺{gram_altin_tl:,.2f}"),
        ]
        if _current.ons_usd is not None:
            _market_items.append(("Ons Altın (USD)", f"${_current.ons_usd:,.2f}"))
        if _current.usdtry is not None:
            _market_items.append(("Dolar/TL", f"₺{_current.usdtry:,.4f}"))
        if _current.ceyrek_altin is not None:
            _market_items.append(("Çeyrek Altın", f"₺{_current.ceyrek_altin:,.2f}"))

        # Hacim (Lot) — anlık + aylık ortalama
        if _current.hacim_lot is not None:
            _market_items.append(("Hacim (Lot)", f"{_current.hacim_lot:,.0f}"))
            from app.data_fetcher import load_volume_avg
            _avg_vol = load_volume_avg(30)
            if _avg_vol is not None:
                _market_items.append(("30G Ort. Hacim", f"{_avg_vol:,.0f}"))

        for i in range(0, len(_market_items), 2):
            cols = st.columns(2)
            cols[0].metric(_market_items[i][0], _market_items[i][1])
            if i + 1 < len(_market_items):
                cols[1].metric(_market_items[i + 1][0], _market_items[i + 1][1])

        if _current.update_date:
            st.caption(f"📡 {_current.update_date}")

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

if altins1_fiyat is None or gram_altin_tl is None:
    st.error(
        "⚠️ ALTINS1 veya gram altın fiyatı alınamadı ve önceki kayıtlı veri de bulunamadı. "
        "İnternet bağlantınızı kontrol edin. İlk çalıştırmada seans saatlerinde veri çekilmesi gerekir."
    )


# ═══════════════════════════════════════════════════════════════
# 2) GRAFİKLER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("📈 Grafikler")


# ── Tab Bağlamı ────────────────────────────────────────────────
_tab_ctx = TabContext(
    series=_series,
    current=_current,
    history_raw=market.history_raw,
    spread_hist=spread_hist,
    thresholds=thresholds,
    font_size=_font_size,
    chart_height=_chart_height,
    grafik_kilidi=_grafik_kilidi,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 ALTINS1 Analizi",
    "📊 S1/Gr Oranı Analizi",
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
    tab_ons.render(_tab_ctx)

with tab4:
    tab_gold_silver.render(_tab_ctx)

with tab5:
    daily_news, weekly_news = load_news_split()
    tab_news.render(daily_news, weekly_news)

with tab6:
    tab_reserves.render(_grafik_kilidi)

with tab7:
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

    # Güncel sinyal verisini hazırla — merkezi referans değişkenlerden al
    _email_prices = {
        "altins1_fiyat": altins1_fiyat,
        "gram_altin_tl": gram_altin_tl,
        "beklenen_altins1": beklenen,
        "makas_pct": makas_pct,
        "ons_altin_usd": _current.ons_usd,
        "dolar_tl": _current.usdtry,
    }
    _email_thresholds = {
        "strong_buy": thresholds.strong_buy,
        "buy": thresholds.buy_threshold,
        "sell": thresholds.sell_threshold,
        "strong_sell": thresholds.strong_sell,
        "avg_spread": avg_spread,
    }

    # Sinyal hesabı: makas_pct zaten _series.spread'den alındı (merkezi, tutarlı)
    _email_makas = makas_pct if makas_pct is not None else 0
    _active_signal = evaluate_signal(_email_makas, thresholds)
    _active_signal_msg = generate_signal_message(_active_signal, _email_makas)

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
    st.caption(f"ALTINS1 Analiz v{APP_VERSION_FULL} | Yalnızca bilgi amaçlıdır, yatırım tavsiyesi değildir.")
with _footer_cols[1]:
    with st.expander("📋 Güncelleme Notu"):
        st.markdown(f"**v{APP_VERSION_FULL}** — {APP_VERSION_DATE}")
        for _note in APP_VERSION_NOTES:
            st.markdown(f"- {_note}")

