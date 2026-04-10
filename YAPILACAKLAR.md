# ALTINS1 — Yapılacaklar

> Tarih: 10 Nisan 2026 | Sonraki oturumda ele alınacak maddeler

## 1. Son Güncelleme Tarihi/Saati
- "BIST seansı kapalı" uyarısında "Son güncelleme: bilinmiyor" yerine gerçek tarih ve saat gösterilmeli.

## 2. Tarihler Hâlâ İngilizce (Kısmen)
- Bazı grafiklerde tarihler Türkçe, bazılarında hâlâ İngilizce geliyor.
- `turkce_tarih_ekseni()` tüm kenar durumları kapsayacak şekilde gözden geçirilmeli.

## 3. Grafik Yakınlaştırma Kapatılmamış
- `_grafik_kilidi` veya dragmode ayarı bazı grafiklerde hâlâ zoom'a izin veriyor.
- Tüm grafiklerde tutarlı olarak kapatılmalı (mobil UX).

## 4. Rezerv Değişim Grafiği — Ölçek Sorunu
- Ülkelerin ton ölçekleri çok farklı, üst üste binen çizgiler anlamsız.
- Varsayılan: ABD, Türkiye, Çin seçili olsun.
- Diğer ülkeler opsiyonel (checkbox/multiselect).

## 5. Tab Başlıkları Taşma Sorunu
- Grafik tabları (emoji + isim) uzun olduğunda yatay scroll gerektiriyor.
- Tab başlıkları ekrandan taşınca **alt satıra geçmeli** (wrap).

## 6. Tam Responsive Tasarım
- Tüm uygulama mobil/tablet/masaüstü ekranlarda düzgün görünmeli.
- Layout, font boyutu, grafik yüksekliği vb. ekran boyutuna uymalı.

## 7. ✅ ~~KRİTİK: Proje Dosyaları Karışmış — Temizlik Gerekli~~ (TAMAMLANDI)
- ~~`altins1_analiz` (geliştirme) ile `ALTINS1_StrCloud` (cloud deploy) arasındaki farklar tespit edildi.~~
- ~~Cloud sürümü 18 dosya, +1616 satır güncelleme ile senkronize edildi.~~
- ~~Lokal `ALTINS1_StrCloud` klasörü zaten mevcut değildi (sadece GitHub'da).~~
- **Durum**: `altins1_analiz` = geliştirme ortamı | `ALTINS1_StrCloud` (GitHub) = Streamlit Cloud deploy
- **Tamamlanma**: 11 Nisan 2026

## 8. MD Dosyalarını Klasöre Taşıma
- Kök dizindeki tüm `.md` dosyaları (ISLEMLER, CHANGELOG, TALIMATLAR, YAPILACAKLAR, README, HATA_RAPORU vb.) `docs/` gibi bir klasöre taşınsın.
- Dosya yapısı net ve anlaşılır olsun.
- `.github/copilot-instructions.md` yerinde kalabilir (VS Code bunu oradan okur).

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
