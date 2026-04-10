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
import plotly.graph_objects as go
import streamlit as st

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import (
    AppConfig, SignalThresholds, TROY_OUNCE_GRAM,
    ALTINS1_GRAM_KATSAYI,
)
from app.data_fetcher import (
    fetch_current_prices, fetch_all_history, fetch_altins1_mynet,
    is_bist_open, load_prices_from_cache,
)
from app.calculator import (
    calculate_gram_gold_tl,
    calculate_expected_altins1,
    calculate_spread,
    calculate_spread_series,
    spread_statistics,
)
from app.signal_engine import evaluate_signal, generate_signal_message, SignalType
from app.charts import (
    create_price_chart, create_spread_chart,
    create_altins1_vs_expected_chart, create_overlay_chart,
    create_gold_silver_chart,
)
from app.news_fetcher import get_gold_news, get_daily_and_weekly_news
from app.email_notifier import send_daily_signal_email
from app.config import EmailConfig

# ── Logging ────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
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
def load_news():
    return get_gold_news()


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
# Tarihsel gram altın TL hesapla (ons × USDTRY / 31.1035)
has_ons_hist = history.get("ons_altin_usd") is not None
has_usdtry_hist = history.get("dolar_tl") is not None
gram_gold_hist_series = None
ons_gold_tl_hist_series = None
ons_usd_hist_series = None
usdtry_hist_series = None

if has_ons_hist and has_usdtry_hist:
    ons_hist = history["ons_altin_usd"]
    usdtry_hist = history["dolar_tl"]
    ons_hist = ons_hist.copy()
    usdtry_hist = usdtry_hist.copy()
    ons_hist.index = pd.to_datetime(ons_hist.index).tz_localize(None).normalize()
    usdtry_hist.index = pd.to_datetime(usdtry_hist.index).tz_localize(None).normalize()
    ons_hist = ons_hist[~ons_hist.index.duplicated(keep="last")]
    usdtry_hist = usdtry_hist[~usdtry_hist.index.duplicated(keep="last")]
    common_idx = ons_hist.index.intersection(usdtry_hist.index)
    if len(common_idx) > 0:
        gram_gold_hist_series = (
            ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
        ) / TROY_OUNCE_GRAM
        ons_gold_tl_hist_series = (
            ons_hist.loc[common_idx, "Close"] * usdtry_hist.loc[common_idx, "Close"]
        )
        ons_usd_hist_series = ons_hist.loc[common_idx, "Close"]
        usdtry_hist_series = usdtry_hist.loc[common_idx, "Close"]

# ALTINS1 tarihsel Close serisi (tarih normalize)
altins1_hist_series = None
if altins1_hist is not None and not altins1_hist.empty and "Close" in altins1_hist.columns:
    altins1_hist_clean = altins1_hist.copy()
    idx = pd.to_datetime(altins1_hist_clean.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    altins1_hist_clean.index = idx.normalize()
    altins1_hist_clean = altins1_hist_clean[~altins1_hist_clean.index.duplicated(keep="last")]
    altins1_hist_series = altins1_hist_clean["Close"]

# ── Gümüş tarihsel veri hazırlığı ─────────────────────────────
has_gumus_hist = history.get("ons_gumus_usd") is not None
ons_silver_usd_hist_series = None
gram_silver_hist_series = None

if has_gumus_hist:
    gumus_hist = history["ons_gumus_usd"].copy()
    gumus_hist.index = pd.to_datetime(gumus_hist.index).tz_localize(None).normalize()
    gumus_hist = gumus_hist[~gumus_hist.index.duplicated(keep="last")]
    ons_silver_usd_hist_series = gumus_hist["Close"]
    if has_usdtry_hist:
        silver_common = gumus_hist.index.intersection(usdtry_hist.index)
        if len(silver_common) > 0:
            gram_silver_hist_series = (
                gumus_hist.loc[silver_common, "Close"] * usdtry_hist.loc[silver_common, "Close"]
            ) / TROY_OUNCE_GRAM


# ── Faiz tarihsel veri hazırlığı ─────────────────────────────
has_faiz_hist = history.get("faiz_us10y") is not None
faiz_hist_series = None

if has_faiz_hist:
    faiz_hist = history["faiz_us10y"].copy()
    faiz_hist.index = pd.to_datetime(faiz_hist.index).tz_localize(None).normalize()
    faiz_hist = faiz_hist[~faiz_hist.index.duplicated(keep="last")]
    if "Close" in faiz_hist.columns and not faiz_hist["Close"].dropna().empty:
        faiz_hist_series = faiz_hist["Close"]

# ── Anlık veriyle tarihsel son günü eşitle ────────────────────
# Üst paneldeki anlık makas (truncgil gram altın + mynet anlık ALTINS1) ile
# grafikteki tarihsel makas (yfinance hesaplama + mynet tarihsel Close) farklı
# kaynaklar kullandığı için tutarsız olabiliyor. Bugünün değerini anlık veriyle güncelle.
_today = pd.Timestamp(datetime.now().date())
_live_gram = prices.get("gram_altin_tl")
_live_s1 = prices.get("altins1_fiyat")
if gram_gold_hist_series is not None and _live_gram:
    gram_gold_hist_series[_today] = _live_gram
    gram_gold_hist_series = gram_gold_hist_series.sort_index()
if altins1_hist_series is not None and _live_s1:
    altins1_hist_series[_today] = _live_s1
    altins1_hist_series = altins1_hist_series.sort_index()

# Tarihsel makas hesabı (eşikler için)
spread_hist = None
if altins1_hist_series is not None and gram_gold_hist_series is not None:
    _sp_common = altins1_hist_series.index.intersection(gram_gold_hist_series.index)
    if len(_sp_common) > 0:
        spread_hist = calculate_spread_series(
            altins1_hist_series.loc[_sp_common],
            gram_gold_hist_series.loc[_sp_common],
        )

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


def _add_ema_traces(fig, series, ema_states, label_prefix="", line_dash="dash", **add_trace_kw):
    """Plotly figürüne EMA çizgileri ekler.

    ema_states: dict {"ema20": bool, "ema50": bool, "ema100": bool, "ema200": bool}
    label_prefix: EMA etiketlerinin önüne eklenecek kısaltma (ör. "s1 ", "gr ")
    line_dash: çizgi stili ("dash", "dot", "dashdot" vb.)
    add_trace_kw: fig.add_trace'e geçirilecek ek parametreler (row, col, secondary_y vb.)
    """
    _ema_cfg = [
        (20, ema_states.get("ema20", False), "#29b6f6", f"{label_prefix}EMA 20"),
        (50, ema_states.get("ema50", False), "#66bb6a", f"{label_prefix}EMA 50"),
        (100, ema_states.get("ema100", False), "#ab47bc", f"{label_prefix}EMA 100"),
        (200, ema_states.get("ema200", False), "#ef5350", f"{label_prefix}EMA 200"),
    ]
    for _w, _vis, _clr, _lbl in _ema_cfg:
        if _vis and len(series) >= _w:
            _ema = series.ewm(span=_w, adjust=False).mean()
            fig.add_trace(
                go.Scatter(
                    x=_ema.index, y=_ema.values,
                    mode="lines", name=_lbl,
                    line=dict(color=_clr, width=1.5, dash=line_dash),
                ),
                **add_trace_kw,
            )


def _ema_checkboxes(container, prefix, default_on=True):
    """4 EMA checkbox'ı + tümünü aç/kapat toggle oluşturur ve dict döner."""
    _all_key = f"{prefix}_ema_all"
    _keys = {
        "ema20": f"{prefix}_ema20",
        "ema50": f"{prefix}_ema50",
        "ema100": f"{prefix}_ema100",
        "ema200": f"{prefix}_ema200",
    }

    # "Tümü" değiştiğinde bireysel checkbox'ları session_state üzerinden güncelle
    def _on_all_change():
        _val = st.session_state[_all_key]
        for _k in _keys.values():
            st.session_state[_k] = _val

    row_top = container.columns([1, 1])
    row_top[0].checkbox("✅ Tümü", value=False, key=_all_key, on_change=_on_all_change)
    c1, c2, c3, c4 = container.columns(4)
    return {
        "ema20": c1.checkbox("🔵 EMA 20", value=default_on, key=_keys["ema20"]),
        "ema50": c2.checkbox("🟢 EMA 50", value=default_on, key=_keys["ema50"]),
        "ema100": c3.checkbox("� EMA 100", value=False, key=_keys["ema100"]),
        "ema200": c4.checkbox("🔴 EMA 200", value=False, key=_keys["ema200"]),
    }


def _apply_chart_font(fig):
    """Grafik içi metin boyutlarını _font_size'a göre ayarlar.
    Dikey crosshair + hover etiketleri her çizginin Y konumunda."""
    # Tüm trace'lerde hover formatını 2 ondalık + kompakt etiket
    # + hover etiketini çizgi rengine eşitle
    for _tr in fig.data:
        # Candlestick ve OHLC'ye özel hover formatı atama (kendi hover'ı var)
        is_ohlc = _tr.__class__.__name__ in ("Candlestick", "Ohlc")
        if not is_ohlc and hasattr(_tr, "yhoverformat"):
            _tr.yhoverformat = ".2f"
        if not is_ohlc and hasattr(_tr, "hovertemplate") and _tr.hovertemplate is None:
            _tr.hovertemplate = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        # Etiket arka planını çizgi/marker rengine eşitle
        _clr = None
        if hasattr(_tr, "line") and _tr.line and getattr(_tr.line, "color", None):
            _clr = _tr.line.color
        elif hasattr(_tr, "marker") and _tr.marker and getattr(_tr.marker, "color", None):
            _clr = _tr.marker.color
        if _clr:
            _tr.hoverlabel = dict(
                font=dict(color=_clr, size=_font_size),
                bgcolor="rgba(30,30,30,0.85)",
                bordercolor=_clr,
            )
    # Grafik kilidi: mobilde yanlışlıkla zoom/seçim yapılmasını engeller
    _drag = False if _grafik_kilidi else "zoom"

    fig.update_layout(
        font=dict(size=_font_size),
        title_font_size=_font_size + 4,
        legend_font_size=_font_size,
        height=_chart_height,
        # Mobil dokunma sorununu engelle — grafik kilidi
        dragmode=_drag,
        # Başlığı sol üste al, araç çubuğuyla çakışmasın
        title_x=0.0,
        title_xanchor="left",
        title_y=0.98,
        margin=dict(l=50, r=50, t=80, b=30),
        # "x" modu: her trace kendi Y konumunda etiket gösterir
        hovermode="x",
        hoverlabel=dict(
            font_size=_font_size,
            namelength=-1,
        ),
    )
    fig.update_xaxes(
        tickfont_size=_font_size - 1,
        # Dikey crosshair çizgisi
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikecolor="#888888",
        spikedash="dot",
    )
    fig.update_yaxes(
        tickfont_size=_font_size - 1,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikecolor="#888888",
        spikedash="dot",
        hoverformat=".2f",
    )
    # Annotation'lar (hline etiketleri vb.)
    if fig.layout.annotations:
        for ann in fig.layout.annotations:
            ann.font = dict(size=_font_size)

    # ── Son günün verisini 2 gün sağa uzat (düz çizgi) ────────
    _max_date = None
    for _tr in fig.data:
        if _tr.__class__.__name__ != "Scatter":
            continue
        if _tr.x is None or _tr.y is None or len(_tr.x) == 0:
            continue
        _last_x = pd.Timestamp(_tr.x[-1])
        _last_y = _tr.y[-1] if _tr.y[-1] is not None else None
        if _last_y is None:
            continue
        _ext_x = [_last_x + pd.Timedelta(days=1), _last_x + pd.Timedelta(days=2)]
        _tr.x = list(_tr.x) + _ext_x
        _tr.y = list(_tr.y) + [_last_y, _last_y]
        if _max_date is None or _last_x > _max_date:
            _max_date = _last_x
    # X ekseni sağ sınırını uzat
    if _max_date is not None:
        fig.update_xaxes(range=[None, _max_date + pd.Timedelta(days=3)])

    # Türkçe tarih ekseni — tüm trace ekleme/mutasyon işlemlerinden SONRA uygula
    turkce_tarih_ekseni(fig)

    return fig


# ── Plotly grafik render config (mobil uyumlu) ─────────────────
_plotly_config = {
    "scrollZoom": False,          # Kaydırma ile zoom engelle
    "displayModeBar": True,       # Araç çubuğu göster
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],  # Seçim araçlarını kaldır
    "displaylogo": False,         # Plotly logosunu gizle
}

# Türkçe tarih ekseni: charts.py modülünde merkezi olarak tanımlı
from app.charts import turkce_tarih_ekseni


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
    with st.expander("⚙️ Grafik Ayarları", expanded=False):
        tab1_ccy = st.radio("Para birimi", ["TL", "USD"], horizontal=True, key="tab1_currency")
        _t1c1, _t1c2 = st.columns(2)
        _show_t1_gercek = _t1c1.checkbox("🔵 ALTINS1 Gerçek", value=True, key="t1_gercek")
        _show_t1_beklenen = _t1c2.checkbox("🟠 %1 Gr Altın", value=True, key="t1_beklenen")
        st.markdown("**EMA — S1 (ALTINS1)**")
        _t1_ema_s1 = _ema_checkboxes(st, "t1s1", default_on=False)
        st.markdown("**EMA — GR (Gram Altın)**")
        _t1_ema_gr = _ema_checkboxes(st, "t1gr", default_on=False)

    if altins1_hist_series is not None and gram_gold_hist_series is not None:
        # Ortak indeks bul
        common = altins1_hist_series.index.intersection(gram_gold_hist_series.index)
        if len(common) > 0:
            a1 = altins1_hist_series.loc[common]
            gt = gram_gold_hist_series.loc[common]
            ons_for_chart = None

            # Ons altın serisini hazırla (ortak aralıkta)
            if ons_gold_tl_hist_series is not None:
                ons_common = ons_gold_tl_hist_series.index.intersection(common)
                if len(ons_common) > 0:
                    ons_for_chart = ons_gold_tl_hist_series.loc[ons_common]

            if tab1_ccy == "USD" and usdtry_hist_series is not None:
                usd_rate = usdtry_hist_series.loc[usdtry_hist_series.index.intersection(common)]
                ci = a1.index.intersection(usd_rate.index)
                a1 = a1.loc[ci] / usd_rate.loc[ci]
                gt = gt.loc[ci] / usd_rate.loc[ci]
                # Ons: doğrudan USD serisini kullan
                if ons_usd_hist_series is not None:
                    ons_common_usd = ons_usd_hist_series.index.intersection(ci)
                    ons_for_chart = ons_usd_hist_series.loc[ons_common_usd] if len(ons_common_usd) > 0 else None
                common = ci

            st.caption(
                f"📅 Ortak tarih aralığı: {common.min().strftime('%d.%m.%Y')} — "
                f"{common.max().strftime('%d.%m.%Y')} ({len(common)} gün)"
            )
            fig_vs = create_altins1_vs_expected_chart(
                a1, gt,
                currency=tab1_ccy,
            )
            for _tr in fig_vs.data:
                if "Gerçek" in _tr.name and not _show_t1_gercek:
                    _tr.visible = False
                if ("%1 Gr" in _tr.name or "Beklenen" in _tr.name) and not _show_t1_beklenen:
                    _tr.visible = False
            beklenen_series = gt * ALTINS1_GRAM_KATSAYI
            # Makas oranı trace — hover'da her tarihte görünsün, çizgi en üstte beyaz
            _makas_series = (a1 - beklenen_series) / beklenen_series * 100
            _makas_series_int = _makas_series.round(0).astype(int)
            # Son günü 2 gün ileriye uzat
            _last_date = _makas_series.index[-1]
            _last_val = _makas_series_int.values[-1]
            _ext_x = [_last_date + pd.Timedelta(days=1), _last_date + pd.Timedelta(days=2)]
            _ext_y = [a1.max() * 1.03] * 2
            _ext_val = [_last_val, _last_val]
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
            _add_ema_traces(fig_vs, a1, _t1_ema_s1, label_prefix="s1 ", line_dash="dot")
            _add_ema_traces(fig_vs, beklenen_series, _t1_ema_gr, label_prefix="gr ")
            _apply_chart_font(fig_vs)
            st.plotly_chart(fig_vs, width="stretch", config=_plotly_config)
        else:
            st.warning("ALTINS1 ve gram altın TL tarih aralıkları örtüşmüyor.")
    elif altins1_hist_series is not None:
        st.info("Tarihsel gram altın TL verisi eşleştirilemedi. Sadece ALTINS1 gösteriliyor.")
        fig_only = go.Figure()
        fig_only.add_trace(go.Scatter(
            x=altins1_hist_series.index, y=altins1_hist_series.values,
            mode="lines", name="ALTINS1", line=dict(color="#42a5f5", width=2),
        ))
        if beklenen:
            fig_only.add_hline(y=beklenen, line_dash="dash", line_color="#ffa726",
                               annotation_text=f"Güncel Beklenen: ₺{beklenen:.2f}")
        fig_only.update_layout(title="ALTINS1 Tarihsel Fiyat", template="plotly_dark",
                               yaxis_title="TL", height=_chart_height)
        _apply_chart_font(fig_only)
        st.plotly_chart(fig_only, width="stretch", config=_plotly_config)
    else:
        st.warning("ALTINS1 tarihsel verisi yüklenemedi.")

with tab2:
    if spread_hist is not None and len(spread_hist) > 0:
        with st.expander("⚙️ Grafik Ayarları", expanded=False):
            _t2c1, _t2c2 = st.columns(2)
            _show_t2_makas = _t2c1.checkbox("🟠 Makas (%)", value=True, key="t2_makas")
            _show_t2_cumavg = _t2c2.checkbox("🔵 Kümülatif Ortalama", value=True, key="t2_cumavg")
            _t2_ema = _ema_checkboxes(st, "t2")

        fig_spread = create_spread_chart(
            spread_hist,
            buy_threshold=buy_th,
            sell_threshold=sell_th,
            strong_buy_threshold=strong_buy_th,
            strong_sell_threshold=strong_sell_th,
        )
        for _tr in fig_spread.data:
            if "Makas" in _tr.name and not _show_t2_makas:
                _tr.visible = False
            if "Kümülatif" in _tr.name and not _show_t2_cumavg:
                _tr.visible = False
        _add_ema_traces(fig_spread, spread_hist, _t2_ema)
        _apply_chart_font(fig_spread)
        st.plotly_chart(fig_spread, width="stretch", config=_plotly_config)

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

with tab3:
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
        # Ortak tarih aralığını bul — tüm seriler aynı noktadan başlasın
        common_start = max(s.index.min() for s in _norm_visible.values())
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
        _apply_chart_font(fig_overlay)
        st.plotly_chart(fig_overlay, width="stretch", config=_plotly_config)
        st.caption(
            f"📅 Ortak aralık: {common_start.strftime('%d.%m.%Y')} — {common_end.strftime('%d.%m.%Y')} | "
            f"Tüm seriler ilk değere göre normalize edilmiştir (başlangıç = 0%)."
        )
    else:
        st.warning("Normalize karşılaştırma için yeterli tarihsel veri bulunamadı.")

with tab4:
    if has_ons_hist:
        with st.expander("⚙️ Grafik Ayarları", expanded=False):
            _t4c1, _t4c2 = st.columns(2)
            _show_t4_fiyat = _t4c1.checkbox("🟢 Fiyat", value=True, key="t4_fiyat")
            _show_t4_hacim = _t4c2.checkbox("🔵 Hacim", value=True, key="t4_hacim")
            _t4_ema = _ema_checkboxes(st, "t4")

        fig_xau = create_price_chart(history["ons_altin_usd"], title="Ons Altın (XAU/USD)")
        for _tr in fig_xau.data:
            if _tr.name == "Fiyat" and not _show_t4_fiyat:
                _tr.visible = False
            if _tr.name == "Hacim" and not _show_t4_hacim:
                _tr.visible = False
        _t4_close = history["ons_altin_usd"]["Close"]
        _add_ema_traces(fig_xau, _t4_close, _t4_ema, row=1, col=1)
        _apply_chart_font(fig_xau)
        st.plotly_chart(fig_xau, width="stretch", config=_plotly_config)
    else:
        st.warning("Ons altın tarihsel verisi yüklenemedi.")

with tab5:
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
            _t5_ema_gold = _ema_checkboxes(st, "t5g")
        with _t5_ema_col2:
            st.caption("⚪ Gümüş EMA")
            _t5_ema_silver = _ema_checkboxes(st, "t5s")

    # Veri seçimi
    if t5_unit == "Ons":
        _gold_s = ons_usd_hist_series
        _silver_s = ons_silver_usd_hist_series
    else:
        _gold_s = gram_gold_hist_series
        _silver_s = gram_silver_hist_series

    if _gold_s is not None and _silver_s is not None:
        gs_common = _gold_s.index.intersection(_silver_s.index)
        if len(gs_common) > 0:
            _g = _gold_s.loc[gs_common].copy()
            _s = _silver_s.loc[gs_common].copy()

            # USD dönüşümü (gram TL → USD)
            if t5_ccy == "USD" and t5_unit == "Gram" and usdtry_hist_series is not None:
                usd_rate = usdtry_hist_series.loc[usdtry_hist_series.index.intersection(gs_common)]
                ci = _g.index.intersection(usd_rate.index)
                _g = _g.loc[ci] / usd_rate.loc[ci]
                _s = _s.loc[ci] / usd_rate.loc[ci]
                gs_common = ci
            # TL dönüşümü (ons USD → TL)
            elif t5_ccy == "TL" and t5_unit == "Ons" and usdtry_hist_series is not None:
                usd_rate = usdtry_hist_series.loc[usdtry_hist_series.index.intersection(gs_common)]
                ci = _g.index.intersection(usd_rate.index)
                _g = _g.loc[ci] * usd_rate.loc[ci]
                _s = _s.loc[ci] * usd_rate.loc[ci]
                gs_common = ci

            fig_gs = create_gold_silver_chart(
                _g, _s, unit=t5_unit.lower(), currency=t5_ccy,
            )
            for _tr in fig_gs.data:
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

            _add_ema_traces(fig_gs, _g, _t5_ema_gold, label_prefix="Au ", secondary_y=False)
            _add_ema_traces(fig_gs, _s, _t5_ema_silver, label_prefix="Ag ", line_dash="dot", secondary_y=True)
            _apply_chart_font(fig_gs)
            st.plotly_chart(fig_gs, width="stretch", config=_plotly_config)
            st.caption(
                f"📅 Ortak aralık: {gs_common.min().strftime('%d.%m.%Y')} — "
                f"{gs_common.max().strftime('%d.%m.%Y')} ({len(gs_common)} gün)"
            )
            st.metric("Altın/Gümüş Oranı (Güncel)", f"{_ratio_series.iloc[-1]:.1f}")
        else:
            st.warning("Altın ve gümüş tarih aralıkları örtüşmüyor.")
    else:
        st.warning("Altın veya gümüş tarihsel verisi yüklenemedi.")


with tab6:
    st.subheader("📰 Haberler")
    daily_news, weekly_news = load_news_split()

    # Günlük haberler (son 24 saat)
    st.subheader("📅 Günlük — Son 24 Saat")
    if daily_news:
        for item in daily_news[:15]:
            with st.expander(f"**{item.source}** — {item.title}"):
                if item.published:
                    st.caption(f"📅 {item.published}")
                if item.summary:
                    st.write(item.summary[:300] + "..." if len(item.summary or "") > 300 else item.summary)
                st.markdown(f"[Habere git →]({item.link})")
    else:
        st.info("Son 24 saatte ilgili haber bulunamadı.")

    # Haftalık haberler (1-7 gün öncesi)
    st.subheader("📰 Haftalık — Altın, Döviz, Jeopolitik, Ekonomi")
    if weekly_news:
        for item in weekly_news[:20]:
            with st.expander(f"**{item.source}** — {item.title}"):
                if item.published:
                    st.caption(f"📅 {item.published}")
                if item.summary:
                    st.write(item.summary[:300] + "..." if len(item.summary or "") > 300 else item.summary)
                st.markdown(f"[Habere git →]({item.link})")
    else:
        st.info("Bu hafta ilgili haber bulunamadı.")

with tab7:
    from app.reserve_tracker import (
        fetch_reserve_data, get_reserve_sources_info,
        get_highlighted_reserves, get_cache_date,
        save_daily_snapshot, get_all_tracked_countries,
        get_default_chart_countries, get_period_options,
        build_history_dataframe,
    )
    from app.reserve_signals import (
        compute_all_signals, compute_composite_signal,
    )
    import plotly.graph_objects as go

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
                index=3,  # varsayılan: Son 1 Yıl
                key="reserve_chart_period",
            )

        # Grafik modu: ton / % değişim
        show_pct = st.toggle("% Değişim Göster", value=False, key="reserve_pct_toggle")

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
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=60, r=20, t=30, b=40),
                    hovermode="x",
                    template="plotly_dark",
                    dragmode=False if _grafik_kilidi else "zoom",
                )

                if show_pct:
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

                st.plotly_chart(turkce_tarih_ekseni(fig), width="stretch", key="reserve_change_chart", config=_plotly_config)

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

# ═══════════════════════════════════════════════════════════════
# TAB 8 — BİLGİ REHBERİ
# ═══════════════════════════════════════════════════════════════
with tab8:
    st.subheader("📖 Bilgi Rehberi")
    st.caption("Altın piyasası, ALTINS1 sertifikası ve analiz yöntemleri hakkında kapsamlı rehber")

    st.info(
        "📝 Bu bölüm hazırlanıyor. Yakında burada altın piyasası, ALTINS1 sertifikası, "
        "ons-gram-dolar ilişkileri, merkez bankası rezervleri ve "
        "programın sunduğu analizlerin nasıl yorumlanacağına dair "
        "kapsamlı bir rehber yer alacak."
    )

    # İçindekiler (yapı hazır, içerik sonra eklenecek)
    st.markdown("##### 📑 İçindekiler")
    st.markdown("""
1. **ALTINS1 Nedir?** — Sertifikanın yapısı, gram altınla ilişkisi, makas kavramı
2. **Altın Fiyatı Nasıl Oluşur?** — Ons altın, dolar/TL, gram altın TL ilişkisi
3. **Makas Analizi** — Spread nedir, alım-satım sinyalleri ne anlama gelir
4. **Merkez Bankası Altın Rezervleri** — Neden önemli, altın fiyatını nasıl etkiler
5. **Sinyal Paneli Nasıl Okunur?** — Her göstergenin anlamı ve yorumu
6. **Temel Analiz vs Teknik Analiz** — Altın için hangi yöntemler kullanılır
7. **Sık Sorulan Sorular**
""")

    st.caption("💡 Bu rehber, programı ilk kez kullananlar için hazırlanmaktadır.")


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
st.caption("ALTINS1 Analiz v0.5.0 | Yalnızca bilgi amaçlıdır, yatırım tavsiyesi değildir.")
