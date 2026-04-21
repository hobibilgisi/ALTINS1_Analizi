"""
ALTINS1 Analiz — UI Yardımcı Fonksiyonları
Grafik etkileşimleri, EMA çizgileri ve Plotly render ayarları.
"""

from typing import Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import turkce_tarih_ekseni


# ── Plotly grafik render config (mobil uyumlu) ─────────────────
PLOTLY_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    "displaylogo": False,
}


def add_ema_traces(
    fig: go.Figure,
    series: pd.Series,
    ema_states: Dict[str, bool],
    label_prefix: str = "",
    line_dash: str = "dash",
    **add_trace_kw,
) -> None:
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


def ema_checkboxes(container, prefix: str, default_on: bool = True) -> Dict[str, bool]:
    """4 EMA checkbox'ı + tümünü aç/kapat toggle oluşturur ve dict döner."""
    _all_key = f"{prefix}_ema_all"
    _keys = {
        "ema20": f"{prefix}_ema20",
        "ema50": f"{prefix}_ema50",
        "ema100": f"{prefix}_ema100",
        "ema200": f"{prefix}_ema200",
    }

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
        "ema100": c3.checkbox("🟣 EMA 100", value=False, key=_keys["ema100"]),
        "ema200": c4.checkbox("🔴 EMA 200", value=False, key=_keys["ema200"]),
    }


def apply_chart_font(
    fig: go.Figure,
    font_size: int,
    chart_height: int,
    grafik_kilidi: bool,
) -> go.Figure:
    """Grafik içi metin boyutlarını ayarlar.
    Dikey crosshair + hover etiketleri her çizginin Y konumunda."""
    for _tr in fig.data:
        is_ohlc = _tr.__class__.__name__ in ("Candlestick", "Ohlc")
        if not is_ohlc and hasattr(_tr, "yhoverformat"):
            _tr.yhoverformat = ".2f"
        if not is_ohlc and hasattr(_tr, "hovertemplate") and _tr.hovertemplate is None:
            _tr.hovertemplate = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        _clr = None
        if hasattr(_tr, "line") and _tr.line and getattr(_tr.line, "color", None):
            _clr = _tr.line.color
        elif hasattr(_tr, "marker") and _tr.marker and getattr(_tr.marker, "color", None):
            _clr = _tr.marker.color
        if _clr:
            _tr.hoverlabel = dict(
                font=dict(color=_clr, size=font_size),
                bgcolor="rgba(30,30,30,0.85)",
                bordercolor=_clr,
            )

    _drag = False if grafik_kilidi else "zoom"
    fig.update_layout(
        font=dict(size=font_size),
        title_font_size=font_size + 4,
        legend_font_size=font_size,
        height=chart_height,
        dragmode=_drag,
        title_x=0.0,
        title_xanchor="left",
        title_y=0.96,
        margin=dict(l=5, r=5, t=50, b=60),
        hovermode="x",
        hoverlabel=dict(
            font_size=font_size,
            namelength=-1,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(
        tickfont_size=font_size - 1,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikecolor="#888888",
        spikedash="dot",
    )
    fig.update_yaxes(
        tickfont_size=font_size - 1,
        ticklabelposition="inside",
        title_text="",
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikecolor="#888888",
        spikedash="dot",
        hoverformat=".2f",
    )
    if fig.layout.annotations:
        for ann in fig.layout.annotations:
            ann.font = dict(size=font_size)

    # Son günün verisini 5 gün sağa uzat — geniş dokunma alanı oluşturur,
    # kullanıcı bu boş bölgeye dokunarak son günün değerini kolayca okuyabilir.
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
        _ext_x = [_last_x + pd.Timedelta(days=d) for d in (1, 2, 3, 4, 5)]
        _tr.x = list(_tr.x) + _ext_x
        _tr.y = list(_tr.y) + [_last_y] * 5
        if _max_date is None or _last_x > _max_date:
            _max_date = _last_x
    if _max_date is not None:
        fig.update_xaxes(range=[None, _max_date + pd.Timedelta(days=6)])

    turkce_tarih_ekseni(fig)
    return fig
