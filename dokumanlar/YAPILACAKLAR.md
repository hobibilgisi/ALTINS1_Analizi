# ALTINS1 — Yapılacaklar

> Son güncelleme: 13 Nisan 2026

## 1. ✅ ~~Son Güncelleme Tarihi/Saati~~ (TAMAMLANDI)
- ~~"BIST seansı kapalı" uyarısında "Son güncelleme: bilinmiyor" yerine gerçek tarih ve saat gösterilmeli.~~
- `fetch_current_prices()` artık `_cache_time` döndürüyor.

## 2. ✅ ~~Tarihler Hâlâ İngilizce (Kısmen)~~ (TAMAMLANDI)
- ~~Bazı grafiklerde tarihler Türkçe, bazılarında hâlâ İngilizce geliyor.~~
- `turkce_tarih_ekseni()` tüm 7 grafiğe uygulanıyor (6'sı `apply_chart_font()` üzerinden, 1'i doğrudan).
- Tick etiketleri, hover metinleri, candlestick/scatter tüm trace tipleri kapsanıyor.

## 3. ✅ ~~Grafik Yakınlaştırma Kapatılmamış~~ (TAMAMLANDI)
- ~~`_grafik_kilidi` veya dragmode ayarı bazı grafiklerde hâlâ zoom'a izin veriyor.~~
- Tüm grafiklerde `apply_chart_font()` üzerinden tutarlı `dragmode` uygulanıyor. Rezerv grafiği de ayrıca kontrol ediliyor.

## 4. ✅ ~~Rezerv Değişim Grafiği — Ölçek Sorunu~~ (TAMAMLANDI)
- ~~Ülkelerin ton ölçekleri çok farklı, üst üste binen çizgiler anlamsız.~~
- Varsayılan ülkeler: ABD, Çin, Türkiye. Diğerleri multiselect ile seçimlik.
- Varsayılan mod: % değişim. Periyotlar: 1, 2, 6, 12 ay (varsayılan: 12 ay).

## 5. ✅ ~~Tab Başlıkları Taşma Sorunu~~ (TAMAMLANDI)
- ~~Grafik tabları (emoji + isim) uzun olduğunda yatay scroll gerektiriyor.~~
- ~~Tab başlıkları ekrandan taşınca **alt satıra geçmeli** (wrap).~~
- CSS `flex-wrap: wrap` eklendi; tablar artık alt satıra geçiyor.

## 6. ✅ ~~Tam Responsive Tasarım~~ (TAMAMLANDI)
- ~~Tüm uygulama mobil/tablet/masaüstü ekranlarda düzgün görünmeli.~~
- ~~Layout, font boyutu, grafik yüksekliği vb. ekran boyutuna uymalı.~~
- `@media (max-width: 768px)` media query ile sidebar, başlık ve tab boyutları mobilde küçültülüyor.

## 7. ✅ ~~KRİTİK: Proje Dosyaları Karışmış — Temizlik Gerekli~~ (TAMAMLANDI)
- ~~`altins1_analiz` (geliştirme) ile `ALTINS1_StrCloud` (cloud deploy) arasındaki farklar tespit edildi.~~
- ~~Cloud sürümü 18 dosya, +1616 satır güncelleme ile senkronize edildi.~~
- ~~Lokal `ALTINS1_StrCloud` klasörü zaten mevcut değildi (sadece GitHub'da).~~
- **Durum**: `altins1_analiz` = geliştirme ortamı | `ALTINS1_StrCloud` (GitHub) = Streamlit Cloud deploy
- **Tamamlanma**: 11 Nisan 2026

## 8. ✅ ~~MD Dosyalarını Klasöre Taşıma~~ (TAMAMLANDI)
- ~~Kök dizindeki tüm `.md` dosyaları `docs/` gibi bir klasöre taşınsın.~~
- CHANGELOG.md, ISLEMLER.md, TALIMATLAR.md, YAPILACAKLAR.md → `dokumanlar/` klasörüne taşındı.
- README.md kök dizinde kaldı (GitHub konvansiyonu).

## 9. Kapsamlı Yazılım Mimari Dokümantasyonu
- Yazılım mimarı bakış açısıyla tam bir rehber hazırlanacak:
  - Proje gereksinimleri ve amaç
  - Modül yapısı ve sorumlulukları
  - Modüller arası ilişkiler ve bağımlılık haritası
  - Fonksiyon/nesne katalog (imzalar, parametreler, dönüş değerleri)
  - Veri akışı (data flow) diyagramı
  - Dış bağımlılıklar (API'ler, kütüphaneler, servisler)
  - Konfigürasyon ve ortam değişkenleri
  - Deployment mimarisi (Streamlit Cloud, GitHub)
  - Hata yönetimi ve loglama stratejisi
  - Genel algoritmalar (sinyal motoru, spread hesaplama, rezerv takibi vb.)
  - Bilinen kısıtlamalar ve teknik borç
