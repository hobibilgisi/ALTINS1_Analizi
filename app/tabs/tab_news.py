"""Tab 6 — Haberler (RSS akışları)."""

from typing import List

import streamlit as st

from app.news_fetcher import NewsItem


def render(daily_news: List[NewsItem], weekly_news: List[NewsItem]) -> None:
    """Günlük ve haftalık haberleri gösterir."""
    st.caption(
        "ℹ️ Altın, döviz, merkez bankası ve jeopolitik gelişmelere dair RSS kaynaklarından "
        "derlenen haber akışı. Günlük (son 24 saat) ve haftalık olmak üzere iki bölüme ayrılmıştır."
    )
    st.subheader("📰 Haberler")

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
