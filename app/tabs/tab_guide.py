"""Tab 8 — Bilgi Rehberi."""

import streamlit as st


def render() -> None:
    """Bilgi rehberi sayfasını gösterir."""
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
