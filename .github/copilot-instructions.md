---
description: ALTINS1 Analiz projesi için geliştirme talimatları
applyTo: altins1_analiz/**
---

# ALTINS1 Proje Talimatları

## Proje Yapısı
- Ana uygulama: `main.py` (Streamlit)
- Modüller: `app/` altında (charts, data_fetcher, reserve_tracker, signal_engine, vb.)
- Testler: `tests/`
- İşlem günlüğü: `ISLEMLER.md`
- Yapılacaklar: `YAPILACAKLAR.md`
- Değişiklik kaydı: `CHANGELOG.md`

## Oturum Başlangıcı
1. `YAPILACAKLAR.md` dosyasını oku — bekleyen maddeler var mı kontrol et.
2. `ISLEMLER.md` son oturumu oku — bağlamı koru.
3. Kullanıcıya bekleyen yapılacakları hatırlat.

## Oturum Sonu (HER OTURUMDA UYGULANMALI)
Kullanıcı oturumu kapatmadan veya uzun süre sessiz kaldığında:

1. **YAPILACAKLAR.md güncelle**:
   - Tamamlanan maddeleri `~~üstü çizili~~` yap ve `✅` ekle.
   - Yeni çıkan yapılacakları ekle.

2. **ISLEMLER.md güncelle**:
   - Yeni bir oturum bloğu aç (sıradaki numara + tarih).
   - Yapılan her işlemi maddeler halinde yaz (dosya adı, ne değişti, neden).
   - Hangi yapılacak maddenin tamamlandığını belirt.

3. **CHANGELOG.md güncelle**:
   - Kullanıcıya görünür değişiklikleri sürüm notları formatında ekle.

4. Kullanıcıya kısa bir oturum özeti sun.

## Kod Standartları
- Türkçe UI metinleri, İngilizce kod/değişken adları.
- Merkezi fonksiyonlar: tarih formatı `turkce_tarih_ekseni()`, font `_apply_chart_font()`.
- Streamlit dark theme, plotly_dark template.
- Mobil öncelikli responsive tasarım.
