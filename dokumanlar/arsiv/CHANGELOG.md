# Changelog — ALTINS1 Analiz

Tüm önemli değişiklikler bu dosyada kaydedilir.
Versiyon formatı: **SemVer** (MAJOR.MINOR.PATCH)

> **MAJOR sürümler** = Projenin temel dönüm noktaları
> 1 = ALTINS1 veri çekme | 2 = Makas/ortalama grafiği | 3 = Sinyal üretme | 4 = Web'e taşıma | 5 = Mail/Telegram botu

---

## MAJOR 4 — Web'e Taşıma (Streamlit Cloud)

### [4.4.0] — 2026-04-13 ← Güncel
- **Tab modül refactoring**: 8 tab `app/tabs/` paketine çıkarıldı, `TabContext` dataclass
- **altins1_app.py**: ~1,700 → 555 satır (%67 azalma), saf orkestratör
- **Type hints**: `ui_helpers.py` ve tüm tab modüllerine eklendi
- **SemVer versiyon sistemi**: `APP_VERSION` + footer güncelleme notu paneli
- **Dokümantasyon**: `MIMARI_RAPOR.md`, MD dosyaları `dokumanlar/` klasörüne taşındı

### [4.3.0] — 2026-04-10
- **Tarihsel MB Rezerv Verisi**: WGC/IMF IFS 11 ülke × 32 çeyrek (2018–2025) gömülü veri
- **MB Sinyal Analiz Paneli**: Net Alım Momentum, Alıcı/Satıcı Oranı, Ağırlıklı Talep Endeksi, Bileşik Sinyal
- **Yeni periyotlar**: 1a/3a/6a/1y/3y/5y/tümü
- Yeni dosyalar: `historical_reserves.py`, `reserve_signals.py`, 5 test dosyası

### [4.2.0] — 2026-04-10
- **Grafik Kilidi**: Sidebar toggle, mobilde zoom engelleme (varsayılan: AÇIK)
- **Grafik başlık fix**: `title_x=0`, modebar çakışması giderildi, `margin.t` 50→80px
- **Merkez bankası UX**: "Altın Payı" etiketleme, yetersiz veri tablo fallback
- **PWA desteği**: Web App Manifest, Ana Ekrana Ekle
- **CSS gizleme**: GitHub badge, fork butonu, Streamlit footer

### [4.1.0] — 2026-04-10
- **Merkez bankası altın rezervleri** (Tab7): Wikipedia scraping, 53 ülke
- **Öne çıkan ülke kartları**: Çin, ABD, Avrupa, Türkiye
- **Günlük snapshot kaydetme**: `data/cache/` altında otomatik tarihsel birikim

### [4.0.0] — 2026-04-01
- **Streamlit Cloud deployment**: `hobibilgisi/ALTINS1_Analizi` repo, `main` push → otomatik deploy
- **ALTINS1 hacim verisi**: Mynet Finans'tan gerçek zamanlı lot + TL hacim
- **Tab6 (Haberler)** ve **Tab7 (Merkez Bankaları)** eklendi → 7 tab

---

## MAJOR 3 — Sinyal Üretme Sistemi

### [3.3.0] — 2026-03-29
- **E-posta bildirim sistemi**: Günlük sinyal özeti SMTP ile HTML gönderim
- **EmailConfig** dataclass, birden fazla alıcı desteği

### [3.2.0] — 2026-03-29
- **Günlük + haftalık haber bölümleri**: RSS (Bloomberg HT, Dünya, Investing.com)
- **Haber HTML temizliği**: `_strip_html()`, genişletilmiş anahtar kelimeler (30+)

### [3.1.0] — 2026-03-29
- **Gümüş (SI=F) + GLDTR.IS** entegrasyonu → 4 tab'dan 7 tab'a
- **TL/USD toggle** (Tab1, Tab3, Tab6)
- **EMA desteği**: 20/50/100/200 günlük hareketli ortalamalar
- **Checkbox kontrolleri**: Her sekmede çizgi göster/gizle
- **Kümülatif makas ortalaması** (expanding mean)

### [3.0.0] — 2026-03-29
- **5 seviyeli sinyal motoru**: Güçlü Alım → Güçlü Satım (`signal_engine.py`)
- **Dinamik alım eşikleri**: Tarihsel makas ortalamasına bağlı otomatik kalibrasyon
- **Sidebar sinyal eşik slider'ları**: Kullanıcı ayarlayabilir

---

## MAJOR 2 — Makas/Ortalama Grafiği

### [2.0.1] — 2026-03-29
- Mesai dışı veri görüntüleme (disk cache fallback)
- Timezone uyumsuzluğu düzeltmesi (tz-aware → tz-naive normalize)
- Tarihsel makas tarih örtüşme düzeltmesi

### [2.0.0] — 2026-03-27
- **Makas formülü**: (Gerçek – Beklenen) / Beklenen × 100
- **ALTINS1 vs Beklenen** karşılaştırma grafiği
- **Normalize karşılaştırma**: ALTINS1, Gram Altın, Ons Altın
- **4 tab dashboard**: ALTINS1 vs Beklenen, Makas, Normalize, Ons Altın
- ALTINS1 BIST fiyat kaynağı: **Mynet Finans** (anlık + 419 bar tarihsel)

---

## MAJOR 1 — ALTINS1 Veri Çekme

### [1.0.0] — 2026-03-27
- **Proje iskeleti** oluşturuldu (12 dosya)
- **10+ veri kaynağı** test edildi (yfinance, tvDatafeed, truncgil, doviz.com, isyatirim, vb.)
- **Mimari karar**: truncgil (anlık) + yfinance (tarihsel) + tvDatafeed (yedek)
- İlk Streamlit çalışma testi başarılı (localhost:8501)

---

## Gelecek Sürümler

### 5.0.0 — Mail / Telegram Botu (Planlı)
- [ ] Otomatik günlük sinyal e-postası (zamanlayıcı ile)
- [ ] Telegram bot entegrasyonu
- [ ] Slack webhook desteği
- [ ] Eşik aşımı anlık bildirim

### 4.x — Devam Eden İyileştirmeler
- [ ] Türkçe tarih ekseni gözden geçirme
- [ ] TCMB EVDS API entegrasyonu
- [ ] Petrol (Brent) entegrasyonu
- [ ] Dark/Light tema seçeneği

---

## Bilinen Sorunlar
- Mynet Finans HTML yapısı değişikliğine duyarlı (site güncelleme → parse kırılması riski)
- BIST sertifika (ALTINS1) tvDatafeed nologin modunda erişim yok
- TCMB EVDS API şu an placeholder

---

**Son Güncelleme**: 2026-04-13
