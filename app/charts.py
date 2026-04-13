"""
ALTINS1 Analiz — Grafik Modülü
Plotly ile TradingView benzeri interaktif grafikler oluşturur.
"""

import logging
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.config import ALTINS1_GRAM_KATSAYI

logger = logging.getLogger(__name__)

# ── Merkezi Grafik Sabitleri ───────────────────────────────────
_DEFAULT_TEMPLATE = "plotly_dark"
_DEFAULT_HEIGHT = 750
_DEFAULT_MARGIN = dict(l=50, r=50, t=50, b=80)

# Renk paleti — tüm modüllerde tek kaynaktan
COLORS = {
    "altins1": "#42a5f5",
    "gram_altin": "#ffa726",
    "ons_altin": "#ab47bc",
    "gumus": "#c0c0c0",
    "gold": "#ffd700",
    "faiz": "#ef5350",
    "buy": "#26a69a",
    "sell": "#ef5350",
    "strong_buy": "#00e676",
    "strong_sell": "#d50000",
    "ema20": "#29b6f6",
    "ema50": "#66bb6a",
    "ema100": "#ab47bc",
    "ema200": "#ef5350",
    "neutral": "#78909c",
}


def apply_base_layout(fig: go.Figure, title: str = "",
                       height: int = _DEFAULT_HEIGHT,
                       yaxis_title: str = "",
                       **extra) -> go.Figure:
    """Tüm grafiklere uygulanacak ortak layout ayarları.

    Tek bir yerden kontrol edilir — template, margin, height.
    """
    layout = dict(
        title=title,
        template=_DEFAULT_TEMPLATE,
        height=height,
        margin=_DEFAULT_MARGIN,
        legend=dict(orientation="h", yanchor="top", y=-0.15,
                    xanchor="center", x=0.5),
    )
    if yaxis_title:
        layout["yaxis_title"] = yaxis_title
    layout.update(extra)
    fig.update_layout(**layout)
    return fig


# ── Türkçe ay adları (tüm grafikler için merkezi) ─────────────
_AY_TR = {
    1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May", 6: "Haz",
    7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara",
}

_AY_TR_UZUN = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}

# İngilizce → Türkçe ay eşleştirmesi (hover metinlerinde Plotly'nin ürettiği
# İngilizce ay adlarını yakalamak için)
_EN_TO_TR = {
    "Jan": "Oca", "Feb": "Şub", "Mar": "Mar", "Apr": "Nis",
    "May": "May", "Jun": "Haz", "Jul": "Tem", "Aug": "Ağu",
    "Sep": "Eyl", "Oct": "Eki", "Nov": "Kas", "Dec": "Ara",
}


def turkce_tarih_ekseni(fig: go.Figure) -> go.Figure:
    """Plotly figürünün TÜM x-eksenlerindeki tarih etiketlerini Türkçe yapar.

    - Tick etiketlerini Türkçe ay adlarıyla gösterir
    - Hover metinlerini Türkçe tarih formatına çevirir
    - Subplots, çoklu x-ekseni ve özel customdata destekler

    Bu fonksiyon her grafiğin SON adımında (tüm trace ekleme / mutasyon
    işlemlerinden sonra) çağrılmalıdır.
    """
    import re

    # ── 1) Tüm trace'lerden tarihleri topla ──────────────────────
    all_dates = []
    for trace in fig.data:
        x = getattr(trace, "x", None)
        if x is None:
            continue
        try:
            dates = pd.to_datetime(list(x))
            all_dates.extend(dates.dropna())
        except Exception:
            continue  # Bu trace'i atla, fonksiyondan çıkma

    if len(all_dates) < 2:
        return fig

    min_d = min(all_dates)
    max_d = max(all_dates)
    span = (max_d - min_d).days

    # ── 2) Tarih aralığına göre tick sıklığı ve format ───────────
    if span > 365 * 4:
        freq, fmt = "YS", lambda d: str(d.year)
    elif span > 365:
        freq, fmt = "QS", lambda d: f"{_AY_TR[d.month]} {d.year}"
    elif span > 120:
        freq, fmt = "MS", lambda d: f"{_AY_TR[d.month]} {d.year}"
    elif span > 30:
        freq, fmt = "2W-MON", lambda d: f"{d.day} {_AY_TR[d.month]}"
    else:
        freq, fmt = "W-MON", lambda d: f"{d.day} {_AY_TR[d.month]}"

    ticks = pd.date_range(start=min_d, end=max_d, freq=freq)
    if len(ticks) < 2:
        ticks = pd.date_range(start=min_d, end=max_d, periods=min(6, max(2, span)))
    if len(ticks) == 0:
        return fig

    tick_vals = ticks.tolist()
    tick_text = [fmt(d) for d in ticks]

    # ── 3) Tüm x-eksenleri güncelle (xaxis, xaxis2, xaxis3 …) ──
    layout_dict = fig.to_dict().get("layout", {})
    xaxis_keys = [k for k in layout_dict if k.startswith("xaxis")]
    if not xaxis_keys:
        xaxis_keys = ["xaxis"]

    for xkey in xaxis_keys:
        fig.update_layout(**{
            xkey: dict(
                tickmode="array",
                tickvals=tick_vals,
                ticktext=tick_text,
            )
        })

    # ── 4) Hover metinlerini Türkçe tarih formatına çevir ───────
    for trace in fig.data:
        x = getattr(trace, "x", None)
        if x is None:
            continue

        # Zaten customdata olan trace'leri koru (kendi hover mantığı var)
        if getattr(trace, "customdata", None) is not None:
            continue

        try:
            dates = pd.to_datetime(list(x))
        except Exception:
            continue

        tr_dates = [
            f"{d.day} {_AY_TR.get(d.month, '?')} {d.year}"
            if not pd.isna(d) else ""
            for d in dates
        ]
        trace.customdata = [[td] for td in tr_dates]

        trace_type = trace.__class__.__name__
        ht = getattr(trace, "hovertemplate", None)

        if ht and "%{x" in str(ht):
            # Mevcut template'te %{x|...} veya %{x} → %{customdata[0]}
            ht = re.sub(r"%\{x(\|[^}]*)?\}", "%{customdata[0]}", str(ht))
            trace.hovertemplate = ht
        elif trace_type in ("Candlestick", "Ohlc"):
            trace.hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "Açılış: %{open:,.2f}<br>"
                "Yüksek: %{high:,.2f}<br>"
                "Düşük: %{low:,.2f}<br>"
                "Kapanış: %{close:,.2f}"
                "<extra>%{fullData.name}</extra>"
            )
        elif ht:
            # Template var ama %{x} yok — başına Türkçe tarih ekle
            trace.hovertemplate = "<b>%{customdata[0]}</b><br>" + str(ht)
        else:
            # Template yok — varsayılan Türkçe hover
            trace.hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "<b>%{fullData.name}</b>: %{y:,.2f}"
                "<extra></extra>"
            )

    return fig


def create_price_chart(
    df: pd.DataFrame,
    title: str = "Fiyat Grafiği",
    show_volume: bool = True,
) -> go.Figure:
    """Mum (candlestick) grafiği oluşturur."""
    if show_volume and "Volume" in df.columns:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
        )
    else:
        fig = make_subplots(rows=1, cols=1)

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Fiyat",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1, col=1,
    )

    if show_volume and "Volume" in df.columns:
        vol = df["Volume"].fillna(0)
        colors = ["#26a69a" if c >= o else "#ef5350"
                  for o, c in zip(df["Open"], df["Close"])]
        fig.add_trace(
            go.Bar(x=df.index, y=vol, name="Hacim",
                   marker_color=colors, opacity=0.5),
            row=2, col=1,
        )

    apply_base_layout(fig, title=title, height=1000,
                      xaxis_rangeslider_visible=False)
    return fig


def create_spread_chart(
    spread_series: pd.Series,
    buy_threshold: float = 15.0,
    sell_threshold: float = 35.0,
    strong_buy_threshold: float = 5.0,
    strong_sell_threshold: float = 50.0,
) -> go.Figure:
    """Makas (spread) zaman serisi grafiği — ALTINS1 Cari vs beklenen fiyat."""
    fig = go.Figure()

    # Makas çizgisi
    fig.add_trace(
        go.Scatter(
            x=spread_series.index,
            y=spread_series.values,
            mode="lines",
            name="Makas (%)",
            line=dict(color="#ffa726", width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 167, 38, 0.1)",
        )
    )

    # Hareketli ortalama (tüm geçmiş ortalaması)
    cumulative_mean = spread_series.expanding().mean()
    fig.add_trace(
        go.Scatter(
            x=cumulative_mean.index,
            y=cumulative_mean.values,
            mode="lines",
            name="Kümülatif Ortalama",
            line=dict(color="#29b6f6", width=3, dash="solid"),
        )
    )

    # Güçlü alım eşiği
    fig.add_hline(
        y=strong_buy_threshold,
        line_dash="dot",
        line_color="#00e676",
        annotation_text=f"Güçlü Alım (%{strong_buy_threshold})",
        annotation_position="bottom left",
    )

    # Alım eşiği
    fig.add_hline(
        y=buy_threshold,
        line_dash="dash",
        line_color="#26a69a",
        annotation_text=f"Alım Eşiği (%{buy_threshold})",
        annotation_position="bottom left",
    )

    # Satım eşiği
    fig.add_hline(
        y=sell_threshold,
        line_dash="dash",
        line_color="#ef5350",
        annotation_text=f"Satım Eşiği (%{sell_threshold})",
        annotation_position="top left",
    )

    # Güçlü satım eşiği
    fig.add_hline(
        y=strong_sell_threshold,
        line_dash="dot",
        line_color="#d50000",
        annotation_text=f"Güçlü Satım (%{strong_sell_threshold})",
        annotation_position="top left",
    )

    apply_base_layout(fig, title="ALTINS1 Makas Analizi — Cari vs Beklenen Fiyat (%)",
                      yaxis_title="Makas (%)")
    return fig


def create_altins1_vs_expected_chart(
    altins1_series: pd.Series,
    gram_gold_tl_series: pd.Series,
    ons_gold_series: Optional[pd.Series] = None,
    gram_gold_raw_series: Optional[pd.Series] = None,
    currency: str = "TL",
) -> go.Figure:
    """ALTINS1 cari fiyat ile beklenen fiyat (gram altın × 0.01) karşılaştırma.

    İki çizgi aynı ölçekte — aralarındaki fark = makas.
    Ons altını ve gram altın TL'yi ikincil Y ekseninde gösterir.
    """
    from plotly.subplots import make_subplots
    ccy = currency.upper()
    sym = "₺" if ccy == "TL" else "$"

    has_ons = ons_gold_series is not None and len(ons_gold_series) > 0
    has_gram_raw = gram_gold_raw_series is not None and len(gram_gold_raw_series) > 0
    use_secondary = has_ons or has_gram_raw

    if use_secondary:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()

    beklenen = gram_gold_tl_series * ALTINS1_GRAM_KATSAYI

    fig.add_trace(
        go.Scatter(
            x=altins1_series.index,
            y=altins1_series.values,
            mode="lines",
            name=f"ALTINS1 Cari ({ccy})",
            line=dict(color="#42a5f5", width=2),
        ),
        secondary_y=False if use_secondary else None,
    )

    fig.add_trace(
        go.Scatter(
            x=beklenen.index,
            y=beklenen.values,
            mode="lines",
            name=f"%1 Gr Altın ({ccy})",
            line=dict(color="#ffa726", width=2),
        ),
        secondary_y=False if use_secondary else None,
    )

    if has_gram_raw:
        fig.add_trace(
            go.Scatter(
                x=gram_gold_raw_series.index,
                y=gram_gold_raw_series.values,
                mode="lines",
                name=f"Gram Altın ({ccy})",
                line=dict(color="#66bb6a", width=2),
                opacity=0.8,
            ),
            secondary_y=True,
        )

    if has_ons:
        fig.add_trace(
            go.Scatter(
                x=ons_gold_series.index,
                y=ons_gold_series.values,
                mode="lines",
                name=f"Ons Altın ({ccy})",
                line=dict(color="#ab47bc", width=1.5, dash="dot"),
                opacity=0.7,
            ),
            secondary_y=True,
        )

    if use_secondary:
        sec_label = f"Gram Altın / Ons ({sym})" if has_ons and has_gram_raw else (
            f"Gram Altın ({sym})" if has_gram_raw else f"Ons Altın ({sym})"
        )
        fig.update_yaxes(title_text=sec_label, secondary_y=True)

    apply_base_layout(fig, title=f"ALTINS1 Analizi ({ccy})")
    fig.update_yaxes(title_text=f"ALTINS1 ({sym})", secondary_y=False if use_secondary else None)
    return fig


def create_overlay_chart(
    altins1_series: Optional[pd.Series] = None,
    gram_gold_series: Optional[pd.Series] = None,
    ons_gold_series: Optional[pd.Series] = None,
    faiz_series: Optional[pd.Series] = None,
    currency: str = "TL",
) -> go.Figure:
    """Altın göstergeleri tek grafikte (normalize edilmiş — % değişim).

    Farklı ölçekleri karşılaştırılabilir yapmak için tüm seriler
    ilk değere göre normalize edilir (başlangıç = 0%).
    """
    fig = go.Figure()
    ccy = currency.upper()

    def _normalize(s: pd.Series) -> pd.Series:
        """İlk geçerli değere göre % değişim."""
        first = s.dropna().iloc[0] if len(s.dropna()) > 0 else 1
        return ((s / first) - 1) * 100

    if altins1_series is not None and len(altins1_series) > 0:
        norm = _normalize(altins1_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name=f"ALTINS1 ({ccy})",
                line=dict(color="#42a5f5", width=2),
            )
        )

    if gram_gold_series is not None and len(gram_gold_series) > 0:
        norm = _normalize(gram_gold_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name=f"Gram Altın ({ccy})",
                line=dict(color="#ffa726", width=3),
            )
        )

    if ons_gold_series is not None and len(ons_gold_series) > 0:
        norm = _normalize(ons_gold_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name="Ons Altın (USD)",
                line=dict(color="#ab47bc", width=2),
            )
        )

    if faiz_series is not None and len(faiz_series) > 0:
        norm = _normalize(faiz_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name="ABD 10Y Faiz (%)",
                line=dict(color="#ef5350", width=2),
            )
        )

    apply_base_layout(fig, title=f"Normalize Kar\u015f\u0131la\u015ft\u0131rma ({ccy})",
                      yaxis=dict(showticklabels=False))
    return fig

def create_correlation_chart(
    altins1_series: Optional[pd.Series] = None,
    gram_gold_series: Optional[pd.Series] = None,
    bist100_series: Optional[pd.Series] = None,
) -> go.Figure:
    """BIST100, Gram Altın TL ve ALTINS1 normalize karşılaştırma grafiği.

    Tüm seriler ilk değere göre % değişim olarak gösterilir.
    Borsa yönü ile altın sertifikası arasındaki korelasyonu görselleştirir.
    """
    fig = go.Figure()

    def _normalize(s: pd.Series) -> pd.Series:
        first = s.dropna().iloc[0] if len(s.dropna()) > 0 else 1
        return ((s / first) - 1) * 100

    if bist100_series is not None and len(bist100_series) > 0:
        norm = _normalize(bist100_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name="BIST 100",
                line=dict(color="#e53935", width=2.5),
            )
        )

    if gram_gold_series is not None and len(gram_gold_series) > 0:
        norm = _normalize(gram_gold_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name="Gram Altın TL",
                line=dict(color="#ffa726", width=2.5),
            )
        )

    if altins1_series is not None and len(altins1_series) > 0:
        norm = _normalize(altins1_series)
        fig.add_trace(
            go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines",
                name="ALTINS1",
                line=dict(color="#42a5f5", width=2.5),
            )
        )

    apply_base_layout(fig, title="📈 Borsa-Altın Korelasyonu (Normalize)",
                      yaxis=dict(showticklabels=False))
    return fig

def create_comparison_chart(
    altins1_series: pd.Series,
    gram_gold_series: pd.Series,
) -> go.Figure:
    """ALTINS1 ve gram altın TL fiyatlarını karşılaştıran grafik."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=altins1_series.index,
            y=altins1_series.values,
            mode="lines",
            name="ALTINS1",
            line=dict(color="#42a5f5", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=gram_gold_series.index,
            y=gram_gold_series.values,
            mode="lines",
            name="Gram Altın TL (hesaplanan)",
            line=dict(color="#ffa726", width=2),
        )
    )

    apply_base_layout(fig, title="ALTINS1 vs Gram Alt\u0131n TL Kar\u015f\u0131la\u015ft\u0131rma",
                      yaxis_title="Fiyat (TL)")
    return fig


def create_gold_silver_chart(
    gold_series: pd.Series,
    silver_series: pd.Series,
    unit: str = "ons",
    currency: str = "USD",
) -> go.Figure:
    """Altın vs Gümüş dual Y-axis karşılaştırma grafiği.

    Args:
        unit: "ons" veya "gram"
        currency: "TL" veya "USD"
    """
    ccy = currency.upper()
    sym = "₺" if ccy == "TL" else "$"
    unit_label = "Ons" if unit == "ons" else "Gram"

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=gold_series.index,
            y=gold_series.values,
            mode="lines",
            name=f"{unit_label} Altın ({ccy})",
            line=dict(color="#ffd700", width=2),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=silver_series.index,
            y=silver_series.values,
            mode="lines",
            name=f"{unit_label} Gümüş ({ccy})",
            line=dict(color="#c0c0c0", width=2),
        ),
        secondary_y=True,
    )

    apply_base_layout(fig, title=f"{unit_label} Altın vs {unit_label} Gümüş ({ccy})")
    fig.update_yaxes(title_text=f"{unit_label} Altın ({sym})", secondary_y=False)
    fig.update_yaxes(title_text=f"{unit_label} Gümüş ({sym})", secondary_y=True)
    return fig
