# ALTINS1 ANALİZ - İŞLEMLER GÜNLÜĞÜ

> Bu dosya, projede yapılan tüm işlemleri kronolojik olarak kaydeder.
> Her oturum başında bu dosya okunarak bağlam korunmalıdır.

---

## Oturum 1 — 27 Mart 2026

### İşlem 1.1 — Proje Tanımı ve Planlama
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Kullanıcı proje gereksinimlerini tanımladı
- **Kararlar**:
  - Arayüz: Streamlit (modern, sade, kolay geliştirilebilir)
  - Veri: yfinance (birincil) + tvDatafeed (yedek) + TCMB EVDS
  - Doğruluk: %100 doğru veri şartı
  - Haber: RSS + merkez bankası altın rezerv takibi
  - Merkez bankaları: Çin (PBoC), ABD (Treasury), Avrupa (ECB), TC (TCMB)

### İşlem 1.2 — Proje İskeleti Oluşturma
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Oluşturulan dosyalar**:
  - `altins1_analiz/TALIMATLAR.md` — Proje talimat dosyası
  - `altins1_analiz/ISLEMLER.md` — Bu dosya (işlem günlüğü)
  - `altins1_analiz/requirements.txt` — Python bağımlılıkları
  - `altins1_analiz/README.md` — Proje açıklaması
  - `altins1_analiz/main.py` — Streamlit giriş noktası (iskelet)
  - `altins1_analiz/app/__init__.py` — Paket başlatma
  - `altins1_analiz/app/config.py` — Konfigürasyon ayarları
  - `altins1_analiz/app/data_fetcher.py` — Veri çekme modülü (iskelet)
  - `altins1_analiz/app/calculator.py` — Hesaplama modülü (iskelet)
  - `altins1_analiz/app/signal_engine.py` — Sinyal motoru (iskelet)
  - `altins1_analiz/app/news_fetcher.py` — Haber modülü (iskelet)
  - `altins1_analiz/app/reserve_tracker.py` — Rezerv takip modülü (iskelet)
  - `altins1_analiz/app/charts.py` — Grafik modülü (iskelet)
  - `altins1_analiz/tests/__init__.py` — Test paketi

### İşlem 1.3 — Veri Kaynağı Kapsamlı Test (Tamamlandı)
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: 10+ veri kaynağı sistematik olarak test edildi

#### Test Sonuçları:

| Kaynak | Sembol | Sonuç | Detay |
|--------|--------|-------|-------|
| yfinance | GC=F (Ons Altın) | ✅ ÇALIŞIYOR | 4453.60 USD |
| yfinance | USDTRY=X | ✅ ÇALIŞIYOR | 44.4554 TL |
| yfinance | ALTINS1.IS | ❌ BAŞARISIZ | "possibly delisted" — Yahoo'da yok |
| tvDatafeed | OANDA:XAUUSD | ✅ ÇALIŞIYOR | 4426.19 USD (nologin) |
| tvDatafeed | FX_IDC:USDTRY | ✅ ÇALIŞIYOR | 44.4579 TL (nologin) |
| tvDatafeed | BIST:ALTINS1 | ❌ TIMEOUT | BIST sertifika verisi login gerektirebilir |
| truncgil API | GRA (Gram Altın) | ✅ ÇALIŞIYOR | 6326 TL (Alış/Satış) |
| truncgil API | USD (Dolar/TL) | ✅ ÇALIŞIYOR | 44.4556 TL |
| truncgil API | HAS, ÇEY, YAR, TAM | ✅ ÇALIŞIYOR | Tüm altın çeşitleri |
| doviz.com | ALTINS1 | ❌ 404 | Sayfa bulunamadı |
| isyatirim API | ALTINS1 | ❌ 401 | Unauthorized |
| haremaltin.com | Altın fiyatları | ❌ 403 | Forbidden |
| borsaistanbul.com | ALTINS1 | ❌ Connection reset | Bağlantı reddedildi |
| bigpara | Hisse listesi | ⚠️ Yüzeysel | ALTINS1'e özgü değil |
| collectapi | Altın | ❌ 401 | Ücretli API anahtarı gerekli |

#### Mimari Karar:
- **Birincil (Anlık)**: `finans.truncgil.com/v4/today.json` — Ücretsiz, auth gerektirmez, gerçek zamanlı
  - GRA = Gram Altın piyasa fiyatı (ALTINS1'in izlediği referans)
  - USD = Dolar/TL
  - 80+ altın/döviz türü
- **Birincil (Tarihsel)**: yfinance — GC=F (ons altın) ve USDTRY=X
- **Yedek (Tarihsel)**: tvDatafeed (nologin) — OANDA:XAUUSD, FX_IDC:USDTRY
- **ALTINS1 BIST fiyatı**: İleride tvDatafeed login veya BIST API ile eklenecek
- **Doğrulama**: Hesaplanan gram altın = (Ons × USDTRY) / 31.1035 vs truncgil GRA çapraz kontrol

### İşlem 1.4 — Kod Güncellemesi (Veri kaynağı mimarisine göre)
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Güncellenen dosyalar**:
  - `app/config.py` — TRUNCGIL_API_URL, TRUNCGIL_KEYS, YF_SYMBOLS, TV_SYMBOLS eklendi
  - `app/data_fetcher.py` — Tam yeniden yazım: truncgil API + yfinance + tvDatafeed hibrit yapı
  - `main.py` — Yeni data_fetcher arayüzü, gram altın piyasa/hesaplanan karşılaştırma, deprecation fix
  - `requirements.txt` — tvdatafeed eklendi

### İşlem 1.5 — Uygulama Test Çalıştırması
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sonuç**: `streamlit run main.py` → http://localhost:8501 başarıyla çalışıyor
- **Doğrulanan bileşenler**:
  - ✅ truncgil API: Gram Altın 6348.11 TL, Dolar/TL 44.4554
  - ✅ yfinance: Ons Altın 4452.90 USD, USD/TRY 44.4584
  - ✅ Tarihsel veri: GC=F 253 satır, USDTRY=X 258 satır
  - ✅ Hesaplanan Gram Altın TL: 6365.41 TL (çapraz doğrulama OK)
  - ✅ RSS Haberler: Bloomberg HT 20, Dünya 20, Investing.com 10 → 15 ilgili haber
  - ✅ Merkez bankası kaynak tablosu görüntüleniyor
  - ✅ Sinyal motoru çalışıyor (piyasa vs hesaplanan makas)

---

## Sonraki Adımlar
- [x] ~~Mesai dışı görüntüleme~~ → Oturum 2'de tamamlandı
- [ ] Merkez bankası altın rezerv verilerini otomatik çekme (Aşama 5)
- [ ] Bildirim sistemi (Aşama 6)

---

## Oturum 2 — 28-29 Mart 2026

### İşlem 2.1 — Sanal Ortam Düzeltme
- **Tarih**: 28-29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: `.venv` pip launcher'ı başka projenin Python yolunu referans alıyordu (Billing_Project). Sanal ortam yeniden oluşturuldu, tüm bağımlılıklar yüklendi.

### İşlem 2.2 — Mesai Dışı Veri Görüntüleme
- **Tarih**: 28-29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Değişiklikler**:
  - `app/config.py` — BIST seans saatleri sabitleri eklendi (10:00-18:10), `price_cache_file` ayarı eklendi
  - `app/data_fetcher.py` — `is_bist_open()`, `save_prices_to_cache()`, `load_prices_from_cache()` fonksiyonları eklendi. `fetch_current_prices()` başarılı veri çektiğinde otomatik disk cache'e yazar.
  - `main.py` — Seans durumu banner'ı: Kapalıyken "BIST seansı kapalı" bilgi mesajı + son güncelleme zamanı. Canlı veri çekilemezse cache fallback.
- **Cache dosyası**: `data/cache/last_prices.json`
- **Test**: Saat 00:40 (hafta sonu) — Seans kapalı, veri cache'den okundu, doğrulandı.

### İşlem 2.3 — Tarihsel Makas Tarih Örtüşme Düzeltmesi
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: ALTINS1 (Mynet) gün bazlı tarih, yfinance saat bilgili datetime index — `intersection` boş dönüyordu
- **Çözüm**: `main.py`'de tüm tarihsel serilerin index'leri `normalize()` ile date-only yapıldı, çift tarihler `duplicated(keep="last")` ile temizlendi
- **Ek**: Ortak tarih aralığı bilgisi (gün sayısı, tarih aralığı) grafik üstüne caption olarak eklendi

### İşlem 2.4 — TALIMATLAR.md §3.2 Güncelleme
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Veri kaynakları tablosu güncel mimariye güncellendi (Mynet, truncgil, yfinance, cache)

### Oturum 2 Kapanış Notu
- **Tamamlanan**: Sanal ortam düzeltme, mesai dışı görüntüleme, tarih örtüşme fix, §3.2 güncelleme
- **Tamamlanmamış**: Yok — tüm öncelikli maddeler tamamlandı
- **Devam noktası**: TALIMATLAR.md §9 "Orta Vadeli" maddeler (merkez bankası rezerv, bildirim sistemi)
- [ ] Tarihsel makas veri aralığı eşleştirme iyileştirmesi
- [ ] Merkez bankası altın rezerv verilerini otomatik çekme (Aşama 5)
- [ ] Bildirim sistemi ve otomatik yenileme (Aşama 6)

---

## Oturum 2 — 27 Mart 2026

### İşlem 2.1 — ALTINS1 BIST Fiyat Kaynağı Araştırması
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: 15+ kaynak test edildi. Çoğu 401/403/404 döndü.
- **Sonuç**: **Mynet Finans** (`finans.mynet.com/borsa/hisseler/altins1-altin-sertifikasi/`) çalışıyor!
  - Güncel fiyat: 82.33 TL (`unit-price` CSS class ile parse)
  - Tarihsel veri: 419 bar (Kasım 2022 – Mart 2026), `initChartData()` JSON'dan parse
  - Google Finance ALTINS1:IST = 22,328 TL → yanlış veri (güvenilmez)

### İşlem 2.2 — Makas Formülü Güncelleme
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Yeni Formül**:
  - ALTINS1 = 0.01 gram altın sertifikası
  - Beklenen ALTINS1 = Gram Altın TL × 0.01
  - Makas (%) = (Gerçek ALTINS1 - Beklenen) / Beklenen × 100
  - Güncel: 82.33 / 63.97 = **%28.7 prim**
- **Sinyal Eşikleri**: Güçlü Alım ≤%5, Alım ≤%15, Satım ≥%35, Güçlü Satım ≥%50

### İşlem 2.3 — Kod Güncellemeleri (Tam ALTINS1 Entegrasyonu)
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Güncellenen dosyalar**:
  - `app/config.py` — ALTINS1_GRAM_KATSAYI=0.01, MYNET_ALTINS1_URL, SignalThresholds (5/15/35/50)
  - `app/data_fetcher.py` — fetch_altins1_mynet() eklendi, fetch_current_prices() ALTINS1 entegrasyonu, truncgil JSON fix
  - `app/calculator.py` — calculate_expected_altins1(), calculate_spread() beklenen fiyat bazlı, calculate_spread_series() güncellendi
  - `app/charts.py` — create_spread_chart() 4 eşik çizgili, create_altins1_vs_expected_chart(), create_overlay_chart() (normalize)
  - `main.py` — Tamamen yeniden tasarlandı: ALTINS1 makas odaklı, 5 metrik, 4 sekme (vs Beklenen, Makas Tarihsel, Normalize Karşılaştırma, Ons Altın)

### İşlem 2.4 — Test ve Doğrulama
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sonuçlar**:
  - Tüm import'lar OK
  - fetch_current_prices(): altins1_fiyat=82.35, gram_altin_tl=6397.09, beklenen=63.97, makas=%28.73
  - Streamlit dashboard çalışıyor (localhost:8502)
  - Deprecation uyarıları (`use_container_width` → `width="stretch"`) düzeltildi

### İşlem 2.5 — Talimat ve İş Akışı Güncelleme
- **Tarih**: 27 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Eklenenler**:
  - TALIMATLAR.md §8: "Her Oturum Başında Yapılacaklar" — zorunlu kontrol listesi
  - TALIMATLAR.md §9: "Yapılacaklar Listesi" — öncelikli, orta vadeli, tamamlanan maddeler
  - Repo memory güncellendi — oturum başı iş akışı varsayılan olarak tanımlandı

### 📋 Oturum 2 — Kapanış Notu
- **Tamamlanan**: ALTINS1 kaynak bulma, makas formülü, tam kod entegrasyonu (5 dosya), test, talimat sistemi
- **Tamamlanmamış / Yarım Kalan İşler**:
  1. **Mesai dışı veri görüntüleme** — Henüz kodlanmadı. Seans kapandığında uygulama ALTINS1 fiyatını alamıyor veya boş gösteriyor. Son geçerli kapanış verisi cache'lenip gösterilmeli.
  2. **Tarihsel makas grafiği veri örtüşmesi** — ALTINS1 (mynet, Kasım 2022'den) ile gram altın TL (yfinance, seçilen periyoda göre) tarih aralıkları tam eşleşmiyor. İnterpolasyon veya ortak aralık genişletme yapılmalı.
  3. **TALIMATLAR.md §3.2 tablosu** — Veri kaynakları tablosu hâlâ eski (yfinance ALTINS1.IS diyor). Mynet + truncgil + yfinance mimarisine göre güncellenmeli.
- **Devam Noktası**: Sonraki oturum öncelikle §9'daki "Mesai dışı veri görüntüleme" maddesiyle başlamalı.
- **Bilinen Sorunlar**: Mynet Finans scraping'i site değişikliğine duyarlı — HTML yapısı değişirse parse kırılır.

---

## Oturum 3 — 29 Mart 2026

### İşlem 3.1 — Timezone Uyumsuzluğu Düzeltmesi
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: yfinance tz-aware index döndürüyor, ALTINS1 (Mynet) tz-naive. Tarihsel makas hesabında `intersection()` boş geliyordu.
- **Çözüm**: Tüm tarihsel serilere `tz_localize(None).normalize()` uygulandı. 240 ortak iş günü doğrulandı.

### İşlem 3.2 — Normalize Grafiğinde Gram Altın Görünürlük Düzeltmesi
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Gram Altın TL ve Ons Altın TL normalize edilince aynı eğriyi veriyor (ikisi de ons×USDTRY'den türer).
- **Çözüm**: Ons altın her zaman USD olarak gösterilir — 3 ayrı çizgi: ALTINS1 (TL), Gram Altın (TL), Ons Altın (USD).

### İşlem 3.3 — TL/USD Para Birimi Seçeneği
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Tab1 (ALTINS1 vs Beklenen) ve Tab3 (Normalize) sekmelerine `st.radio` ile TL/USD toggle eklendi. USD seçildiğinde seriler USDTRY'ye bölünerek dönüştürülüyor.

### İşlem 3.4 — Makas Grafiğine Kümülatif Ortalama
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: `create_spread_chart()` → `expanding().mean()` ile kümülatif ortalama trace eklendi (mavi, dashdot).

### İşlem 3.5 — ALTINS1 vs Beklenen Grafik Sadeleştirme
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Kullanıcı isteğiyle gram altın ve ons altın serileri bu grafikten kaldırıldı. Sadece ALTINS1 Gerçek + Beklenen ALTINS1 çizgileri kalıyor.

### İşlem 3.6 — Grafik Stili Düzeltmeleri
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Değişiklikler**:
  - Normalize grafiğinde Y ekseni etiketleri ve "Değişim (%)" başlığı kaldırıldı
  - Tüm çizgiler sürekli (solid) yapıldı — kesikli çizgiler kaldırıldı
  - Beklenen ALTINS1 çizgisi sürekli yapıldı

### İşlem 3.7 — Dinamik Alım Eşikleri
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Alım eşiği artık tarihsel makas ortalamasına bağlı:
  - `buy_th = round(avg_spread, 1)` → ortalama makas
  - `strong_buy_th = round(avg_spread - 5.0, 1)` → ortalama - 5
- **Yapısal değişiklik**: `main.py` yeniden düzenlendi — veri hazırlığı sidebar'dan önce, spread hesabı ortada, eşik gösterimi sidebar'ın altında.

### İşlem 3.8 — Haber HTML/CSS Temizliği
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Dünya Gazetesi RSS içeriklerinde `<style>`, `<img>` gibi HTML etiketleri görünüyordu.
- **Çözüm**: `news_fetcher.py` → `_strip_html()` fonksiyonu eklendi (regex ile `<style>`, `<img>`, tüm HTML tagları temizlenir).

### İşlem 3.9 — Günlük & Haftalık Haber Bölümleri
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Değişiklikler**:
  - `news_fetcher.py` → `get_daily_and_weekly_news()` fonksiyonu eklendi (son 24 saat + 7 gün ayrımı)
  - `config.py` → `NEWS_KEYWORDS_WEEKLY` listesi eklendi (30+ anahtar kelime: jeopolitik, ekonomi, forex)
  - `main.py` → Haber bölümü günlük (15 haber) ve haftalık (20 haber) olmak üzere ikiye ayrıldı

### İşlem 3.10 — Gümüş ve GLDTR Fonu Entegrasyonu
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Yeni veri kaynakları** (`config.py` → `YF_SYMBOLS`):
  - `"ons_gumus_usd": "SI=F"` — Gümüş Vadeli İşlem (COMEX)
  - `"gldtr": "GLDTR.IS"` — BIST Altın Fonu (TL)
- **Yeni serimler** (`main.py` veri hazırlığı):
  - `ons_silver_usd_hist_series` — Ons gümüş USD
  - `gram_silver_hist_series` — Gram gümüş TL = (SI=F × USDTRY) / 31.1035
  - `gldtr_hist_series` — GLDTR fon kapanış serisi
- **Yeni sekmeler** (4 → 7 sekme):
  - Tab5: 🥇🥈 Ons Altın vs Ons Gümüş — dual Y-axis USD karşılaştırma + güncel oran
  - Tab6: ⚖️ Gram Altın vs Gram Gümüş — dual Y-axis TL/USD toggle
  - Tab7: 🔗 Altın / Gümüş Oranı — Gold/Silver ratio + dönem ortalaması (hline)
- **Normalize sekmesi güncellendi** (Tab3): GLDTR Fon serisi eklendi (yeşil çizgi)
- **Yeni grafik fonksiyonları** (`charts.py`):
  - `create_ons_gold_silver_chart()` — Ons Au vs Ag dual Y-axis
  - `create_gram_gold_silver_chart()` — Gram Au vs Ag dual Y-axis, TL/USD destekli
  - `create_overlay_chart()` → `gldtr_series` parametresi eklendi

### İşlem 3.11 — Grafik Checkbox Kontrolleri
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Tüm 7 sekmede her grafik çizgisi için renkli emoji etiketli checkbox eklendi. Kullanıcı istediği çizgiyi kapatabilir.
- **Uygulama**: `fig.data` üzerinde trace adına göre `_tr.visible = False` ile gizleme. Tab3'te checkbox'a bağlı olarak serilerin `_norm_visible` dict'e alınması.

| Sekme | Checkbox'lar |
|---|---|
| Tab1 | 🔵 ALTINS1 Gerçek, 🟠 Beklenen ALTINS1 |
| Tab2 | 🟠 Makas (%), 🔵 Kümülatif Ortalama |
| Tab3 | 🔵 ALTINS1, 🟠 Gram Altın, 🟣 Ons Altın (USD), 🟢 GLDTR Fon |
| Tab4 | 🟢 Fiyat, 🔵 Hacim |
| Tab5 | 🟡 Ons Altın, ⚪ Ons Gümüş |
| Tab6 | 🟡 Gram Altın, ⚪ Gram Gümüş |
| Tab7 | 🟡 Altın/Gümüş Oranı, 🔵 Ortalama |

### İşlem 3.12 — Günlük E-posta Bildirim Sistemi
- **Tarih**: 29 Mart 2026
- **Durum**: ✅ Tamamlandı
- **Yeni dosya**: `app/email_notifier.py`
- **Özellikler**:
  - Günlük sinyal özeti oluşturma (`generate_daily_summary()`)
  - SMTP ile HTML e-posta gönderme (`send_email()`)
  - Birden fazla alıcıya gönderim desteği
  - Sinyal tipine göre renkli HTML şablonu
- **Konfigürasyon** (`config.py`):
  - `EmailConfig` dataclass: smtp_server, smtp_port, sender_email, sender_password, recipients
  - SMTP kimlik bilgileri ortam değişkenlerinden okunur (güvenlik)
- **main.py entegrasyonu**: Sidebar'da "📧 E-posta Bildirim" bölümü — alıcı yönetimi, test gönderimi, günlük otomatik gönderim

### 📋 Oturum 3 — Kapanış Notu
- **Tamamlanan**: Timezone fix, normalize fix, TL/USD toggle, kümülatif ortalama, grafik sadeleştirme, grafik stili, dinamik eşikler, haber HTML temizliği, günlük/haftalık haberler, gümüş+GLDTR entegrasyonu (3 yeni sekme), checkbox kontrolleri, e-posta bildirim sistemi
- **Dosya değişiklikleri özeti**:
  - `app/config.py` — YF_SYMBOLS'e SI=F + GLDTR.IS eklendi, NEWS_KEYWORDS_WEEKLY eklendi, EmailConfig eklendi
  - `app/charts.py` — 2 yeni fonksiyon (ons/gram gold-silver), overlay'e GLDTR, tüm çizgiler solid
  - `app/news_fetcher.py` — `_strip_html()`, `_parse_pub_date()`, `get_daily_and_weekly_news()`
  - `app/email_notifier.py` — Yeni dosya: SMTP e-posta gönderimi + günlük özet
  - `main.py` — 690 satır, 7 sekme, checkbox'lar, dinamik eşikler, günlük/haftalık haberler, e-posta sidebar
- **Sonraki adımlar**:
  - [ ] Vercel'e web deployment hazırlığı (Streamlit → web uyumluluk)
  - [ ] Merkez bankası altın rezerv verilerini otomatik çekme
  - [ ] Otomatik periyodik yenileme
