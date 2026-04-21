"""Tab 8 — Bilgi Rehberi."""

import streamlit as st


def render() -> None:
    """Bilgi rehberi sayfasını gösterir."""
    st.markdown("""
<div style="
    background: rgba(255,167,38,0.08);
    border-left: 4px solid #ffa726;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-family: monospace;
    font-size: 14px;
    color: #ffe082;
    line-height: 1.8;
">
    <b>ALTINS1</b> = 0.01 gram altın sertifikası (BIST)<br>
    <b>Beklenen Fiyat</b> = Gram Altın TL × 0.01<br>
    <b>Makas (%)</b> = (Gerçek ALTINS1 − Beklenen) / Beklenen × 100
</div>
""", unsafe_allow_html=True)
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
