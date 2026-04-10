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
