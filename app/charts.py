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

    fig.update_layout(
        title=title,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=1000,
        margin=dict(l=50, r=50, t=50, b=30),
    )
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

    fig.update_layout(
        title="ALTINS1 Makas Analizi — Cari vs Beklenen Fiyat (%)",
        template="plotly_dark",
        yaxis_title="Makas (%)",
        height=750,
        margin=dict(l=50, r=50, t=50, b=30),
    )
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

    fig.update_layout(
        title=f"ALTINS1 Analizi ({ccy})",
        template="plotly_dark",
        height=750,
        margin=dict(l=50, r=50, t=50, b=30),
    )
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
                line=dict(color="#ef5350", width=2, dash="dash"),
            )
        )

    fig.update_layout(
        title=f"Normalize Karşılaştırma ({ccy})",
        template="plotly_dark",
        yaxis_title="",
        yaxis=dict(showticklabels=False),
        height=750,
        margin=dict(l=50, r=50, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
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

    fig.update_layout(
        title="ALTINS1 vs Gram Altın TL Karşılaştırma",
        template="plotly_dark",
        yaxis_title="Fiyat (TL)",
        height=750,
        margin=dict(l=50, r=50, t=50, b=30),
    )
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

    fig.update_layout(
        title=f"{unit_label} Altın vs {unit_label} Gümüş ({ccy})",
        template="plotly_dark",
        height=750,
        margin=dict(l=50, r=50, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(title_text=f"{unit_label} Altın ({sym})", secondary_y=False)
    fig.update_yaxes(title_text=f"{unit_label} Gümüş ({sym})", secondary_y=True)
    return fig
