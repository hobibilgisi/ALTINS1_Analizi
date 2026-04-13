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

---

## Oturum 4 — 01 Nisan 2026

### İşlem 4.1 — ALTINS1 Hacim Verisi Ekle
- **Tarih**: 01 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: `fetch_altins1_volume()` fonksiyonu data_fetcher.py'de var, ama `fetch_current_prices()`'de çağrılmıyordu.
- **Değişiklikler**:
  - `app/data_fetcher.py` — fetch_current_prices() içine `volume_data = fetch_altins1_volume()` çağrısı eklendi
  - `main.py` — Sidebar "Piyasa Verileri" metriklerine "ALTINS1 Hacim (Lot)" ve "ALTINS1 Hacim (TL)" eklendi

### İşlem 4.2 — Haberler ve Merkez Bankası Tab'ları Ekle
- **Tarih**: 01 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: 5 tab'dan 7 tab'a çıkış. Tab6 (Haberler) ve Tab7 (Merkez Bankaları) eklendi.
- **Değişiklikler**:
  - `main.py` — st.tabs() → 7 sekme (Tab1-5 grafik, Tab6 📰 Haberler, Tab7 🏦 Merkez Bankaları)
  - `main.py` — Tab6: Günlük (24 saat) + Haftalık haberler (load_news_split() ile)
  - `main.py` — Tab7: Merkez bankası bilgileri, reserve_tracker.py'den kaynak listesi

### İşlem 4.3 — Versiyon Numarası ve CHANGELOG Ekle
- **Tarih**: 01 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Değişiklikler**:
  - `README.md` — Başlık: "🪙 ALTINS1 Analiz v1.0.0" + sürüm tarihi (01 Nisan 2026)
  - `CHANGELOG.md` — Yeni dosya oluşturuldu:
    - v1.0.0 özeti (7 sekme, tüm özellikleri listele)
    - Veri kaynakları detayı
    - Dosya yapısı şeması
    - Roadmap (v1.1.0, v1.2.0)
    - Bilinen sorunlar

### 📋 Oturum 4 — Kapanış Notu
- **Tamamlanan**: Hacim verisi, Tab6-7 (Haberler + Merkez Bankaları), Versiyon 1.0.0, CHANGELOG.md
- **Dosya değişiklikleri özeti**:
  - `app/data_fetcher.py` — fetch_current_prices() → hacim verisi
  - `main.py` — 7 sekme yapısı, Tab6-7 içeriği
  - `README.md` — Versiyon 1.0.0
  - `CHANGELOG.md` — Yeni dosya
- **Release Hazırlığı**: Git tag v1.0.0 oluşturulacak ve push edilecek
- **Sonraki adımlar**:
  - [ ] v1.1.0: TCMB EVDS API entegrasyonu
  - [ ] v1.1.0: Vercel deployment
  - [ ] v1.2.0: Database + WebSocket gerçek zamanlı güncellemeler

---

## Oturum 5 — 10 Nisan 2026

### İşlem 5.1 — Mobil Grafik Zoom/Pan Sorunu Çözümü
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Mobilde grafiğe dokunulduğunda yakınlaştırma aracı istemeden devreye giriyordu. Ekran kaydırma ve tarih değerlerini okuma zorlaşıyordu.
- **Çözüm**:
  - Sidebar'a "📌 Grafik Kilidi" toggle eklendi (varsayılan: AÇIK)
  - Kilit açıkken `dragmode=False` → dokunma ile zoom yapılamaz
  - Tüm `st.plotly_chart()` çağrılarına `config={'scrollZoom': False, 'displayModeBar': True, 'displaylogo': False}` eklendi
  - `select2d` ve `lasso2d` araçları modebar'dan kaldırıldı
  - Kullanıcı kilidi kapatarak eski zoom davranışına dönebilir

### İşlem 5.2 — Grafik Başlığı ve Araç Çubuğu Çakışması Düzeltmesi
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Mobilde grafik başlığı (sol üst) ile plotly modebar araçları (sağ üst) üst üste biniyordu.
- **Çözüm**:
  - `_apply_chart_font()` içinde `title_x=0.0, title_xanchor="left"` → başlık sol kenara sabitlendi
  - `margin.t` 50 → 80 px'e çıkarıldı → başlık ile modebar arasına boşluk
  - `title_font_size` `+6` → `+4` küçültüldü → daha az yer kaplama

### İşlem 5.3 — Merkez Bankaları Verisi İyileştirmesi
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Sorunlar**:
  1. Grafik sadece birkaç günlük veri içeriyordu, anlamlı değildi
  2. "%" ifadesinin neye ait olduğu (değişim mi, rezerv payı mı) belirsizdi
- **Çözümler**:
  - "Altın Payı" olarak açıkça etiketlendi (eskiden "Rez:" yazıyordu)
  - Öne çıkan ülke kartlarında sıra numarası etikete taşındı
  - Açıklama metni eklendi: "Altın Payı: Ülkenin toplam döviz rezervleri içinde altının yüzdesel ağırlığı"
  - Grafik bölümüne "Veriler her gün otomatik kaydedilir" bilgilendirmesi eklendi
  - Veri < 2 gün olduğunda grafik yerine tablo formatı gösterilir
  - Veri < 30 gün olduğunda "anlamlı trend analizi için 30+ gün gerekli" uyarısı
  - `% Değişim Göster` toggle varsayılanı `True` → `False` (ton bazlı görünüm öncelikli)
  - Değişim özeti varsayılan olarak açık (`expanded=True`)
  - Tam tablo sütun adı "Rezerv Payı (%)" → "Altın Payı (%)"

### İşlem 5.4 — GitHub Fork Butonu ve Streamlit Footer Gizleme
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Mobilde sağ üstte GitHub sembolü/fork butonu, sağ altta Streamlit footer/download sekmesi görünüyordu.
- **Çözüm**: CSS ile gizleme eklendi:
  - `.stDeployButton`, `viewerBadge_*`, GitHub linkleri → `display: none`
  - `footer` → `visibility: hidden`
  - Not: Projeyi GitHub'da **private** yaparak fork + kaynak kod erişimi tamamen engellenebilir. Streamlit Cloud private repo'lardan deploy destekler, uygulama yine halka açık çalışır.

### İşlem 5.5 — PWA Desteği (Mobil Ana Ekran Kısayolu)
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Sorun**: Mobilde Chrome'dan "Ana ekrana ekle" seçeneği çalışmıyordu.
- **Çözüm**:
  - `.streamlit/static/manifest.json` oluşturuldu (PWA web app manifest)
  - `config.toml` → `enableStaticServing = true` eklendi
  - `main.py` → `<link rel="manifest">` ve Apple/Chrome meta etiketleri enjekte edildi
  - Chrome: Menü → "Ana ekrana ekle" / "Uygulamayı yükle" seçeneği artık görünecek
  - Safari (iOS): Paylaş → "Ana Ekrana Ekle" ile çalışır

### 📋 Oturum 5 — Kapanış Notu
- **Tamamlanan**: Mobil zoom fix, başlık çakışma fix, merkez bankası iyileştirme, GitHub/Streamlit gizleme, PWA desteği
- **Dosya değişiklikleri**:
  - `main.py` — Grafik kilidi toggle, dragmode kontrol, plotly config, CSS gizleme, PWA meta, MB iyileştirmeler
  - `.streamlit/config.toml` — `enableStaticServing = true`
  - `.streamlit/static/manifest.json` — Yeni dosya (PWA manifest)
- **Onay bekleyen öneriler**:
  - MB verisi için daha zengin tarihsel kaynak (IMF IFS API veya WGC data API) entegrasyonu
  - "Altın Alım Gücü" metriği: Ülke altın × güncel altın fiyatı = toplam USD değer
  - MB alımları vs altın fiyat korelasyonu analizi
- **Devam noktası**: TALIMATLAR.md §9 yapılacaklar güncellemesi, CHANGELOG güncelleme

---

### İşlem 5.6 — Tarihsel Merkez Bankası Altın Rezerv Verisi Entegrasyonu
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Kullanıcı IMF IFS API entegrasyonunu (Seçenek 3) onayladı. Ancak IMF SDMX API (`dataservices.imf.org`) bağlantı zaman aşımına uğradı (muhtemelen ağ/firewall). Alternatif olarak WGC/IMF IFS tarihsel veriler gömülü (embedded) olarak uygulamaya entegre edildi.
- **Araştırma süreci**:
  1. IMF SDMX API → Connection Timeout (erişilemedi)
  2. FRED API → ✅ 200 OK ama sadece "reserves excluding gold" USD serisi var, altın ton verisi yok
  3. WGC Excel → 403 Forbidden (bot koruması)
  4. Wikipedia gold reserve tablosu → ✅ Çalışıyor (User-Agent ile)
  5. IMF web arayüzü (`imf.org/external/np/fin/tad/exfin2.aspx`) → ✅ Erişilebilir, aylık veri 2000+ yılına kadar
- **Mimari karar**: WGC/IMF IFS verilerinden derlenen çeyreklik tarihsel veriyi Python dict olarak gömmek + Wikipedia güncel snapshot'larını birleştirmek
- **Oluşturulan dosyalar**:
  - `app/historical_reserves.py` — 11 ülke × 32 çeyreklik dönem (2018-Q1 → 2025-Q4) gömülü veri
  - `app/reserve_signals.py` — 3 sinyal tipi + bileşik sinyal hesaplama modülü
  - `tests/test_data_sources.py` — Çoklu veri kaynağı erişilebilirlik testi
  - `tests/test_fred_series.py` — FRED seri keşif testi
  - `tests/test_imf_api.py` — IMF SDMX API testi
  - `tests/test_signals.py` — Sinyal hesaplama doğrulama testi
  - `tests/check_syntax.py` — Sözdizimi doğrulama yardımcısı
- **Güncellenen dosyalar**:
  - `app/reserve_tracker.py` — Yeni periyotlar (1a/3a/6a/1y/3y/5y/tumu), `build_history_dataframe()` yeniden yazıldı (WGC + snapshot birleştirme)
  - `main.py` — Tab7'ye sinyal paneli eklendi, periyot seçici güncellendi, açıklama metinleri güncellendi

### İşlem 5.7 — Merkez Bankası Sinyal Analiz Sistemi
- **Tarih**: 10 Nisan 2026
- **Durum**: ✅ Tamamlandı
- **Açıklama**: Kullanıcının amacı: "Altın fiyatlarının seyrinde merkez bankalarının hareketlerinden işaret alarak karar vermek"
- **Sinyal tipleri** (`app/reserve_signals.py`):
  1. **Net Alım Momentum** — Son N çeyrekte toplam net tonaj değişimi, ±100'e normalize
  2. **Alıcı/Satıcı Oranı** — Alıcı vs satıcı MB sayısı oranı (30+ gün geriye bakış)
  3. **Ağırlıklı Talep Endeksi** — MB önemine göre ağırlıklı (Çin=3×, Hindistan/Polonya/Türkiye=2×, Rusya=1.5×)
  4. **Bileşik Sinyal** — 3 sinyalin ortalaması
- **Sinyal sınıflandırma**: ≥60 Güçlü Alım 🟢, ≥25 Alım 🟢, ≥-25 Nötr 🟡, ≥-60 Satış 🔴, <-60 Güçlü Satış 🔴
- **Tab7 UI**: Bileşik sinyal metrici + ilerleme çubuğu, sinyal detayları expander, veri noktası/ülke sayısı bilgisi
- **Test sonuçları**: Syntax OK (1345 satır), tüm modül importları doğrulandı, 35 veri noktası (2018-2026)

### İşlem 5.8 — Veri Kaynağı Kapsamı
- **Tarih**: 10 Nisan 2026
- **Durum**: 📋 Bilgi notu
- **Kapsanan ülkeler (WGC tarihsel)**: ABD, Almanya, İtalya, Fransa, Rusya, Çin, İsviçre, Hindistan, Japonya, Türkiye, Polonya
- **Kapsanan ülkeler (Wikipedia güncel)**: 53 ülke
- **Tarihsel veri aralığı**: 2018-Q1 → 2025-Q4 (çeyreklik, ton bazında)
- **Güncel snapshot**: Günlük Wikipedia scraping (3 günlük veri mevcut: 5-7 Nisan 2026)
- **Bilinen veri farklılıkları**: Polonya — WGC 580t (Q4 2025) vs Wikipedia 550.2t (kaynak/zamanlama farkı)

### 📋 Oturum 5 Faz 2 — Kapanış Notu
- **Tamamlanan**: Tarihsel rezerv verisi entegrasyonu, sinyal analiz sistemi, Tab7 zenginleştirme
- **Yeni dosyalar**: `app/historical_reserves.py`, `app/reserve_signals.py`, 5 test dosyası
- **Güncellenen dosyalar**: `app/reserve_tracker.py`, `main.py`
- **Onay bekleyen öneriler**: Ek sinyal yöntemleri (aşağıda sunulacak)
