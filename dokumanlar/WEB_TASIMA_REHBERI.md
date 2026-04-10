# 🌐 ALTINS1 Analiz — Web'e Taşıma Rehberi (Ders Notu)

> **Tarih:** 5 Nisan 2026  
> **Mevcut Durum:** Streamlit ile yerel çalışan Python uygulaması  
> **Hedef:** Uygulamayı internette yayınlamak (deploy etmek)  
> **Yaklaşım:** Hem öğrenme hem uygulama — her adım açıklamalı

---

## 📑 İÇİNDEKİLER

1. [Mevcut Projenin Analizi](#1-mevcut-projenin-analizi)
2. [Temel Kavramlar (Öğrenme Notu)](#2-temel-kavramlar)
3. [Web'e Taşıma Yöntemleri — Karşılaştırma Tablosu](#3-webe-taşıma-yöntemleri)
4. [Yöntem 1: Streamlit Community Cloud (En Kolay)](#yöntem-1-streamlit-community-cloud)
5. [Yöntem 2: VPS + Docker (En Esnek)](#yöntem-2-vps--docker)
6. [Yöntem 3: Vercel + Supabase (Modern Full-Stack)](#yöntem-3-vercel--supabase)
7. [Yöntem 4: Railway / Render (Orta Yol)](#yöntem-4-railway--render)
8. [Yöntem 5: Ev Sunucusu — Kendi PC veya Raspberry Pi](#yöntem-5-ev-sunucusu--kendi-pc-veya-raspberry-pi)
9. [Veritabanı Seçenekleri](#5-veritabanı-seçenekleri)
10. [Domain (Alan Adı) Rehberi](#6-domain-alan-adı-rehberi)
11. [Önerilen Yol Haritası](#7-önerilen-yol-haritası)
12. [Sözlük](#8-sözlük)

---

## 1. MEVCUT PROJENİN ANALİZİ

### Kullanılan Teknolojiler
| Bileşen | Teknoloji | Web'e Etkisi |
|---------|-----------|--------------|
| Arayüz | Streamlit | Zaten web tabanlı (localhost:8501) |
| Veri Çekme | requests, yfinance, BeautifulSoup | Sunucuda çalışmalı |
| Grafikler | Plotly | Tarayıcıda render edilir ✅ |
| Veri İşleme | Pandas, NumPy | Sunucuda çalışır |
| Cache | JSON dosya (data/cache/) | Sunucuda dosya sistemi gerekir |
| E-posta | SMTP | Sunucuda çalışır |
| Veritabanı | ❌ Yok | Şu anda dosya tabanlı cache |
| Kimlik Doğrulama | ❌ Yok | Web'de gerekebilir |

### Web'e Taşırken Dikkat Edilecekler
1. **Streamlit zaten bir web framework** — `streamlit run main.py` aslında bir web sunucusu başlatır
2. **Veri çekme sunucu tarafında olmalı** — API key'ler, scraping kodları sunucuda kalmalı
3. **Cache mekanizması** değişebilir — dosya sistemi her yerde olmayabilir
4. **Ortam değişkenleri** — API key'ler, e-posta şifreleri env variable olarak saklanmalı

---

## 2. TEMEL KAVRAMLAR

### 🔑 Frontend vs Backend
```
┌─────────────┐     HTTP      ┌─────────────┐
│  FRONTEND   │ ◄──────────►  │   BACKEND    │
│ (Tarayıcı)  │   İstekler    │  (Sunucu)    │
│             │               │              │
│ HTML/CSS/JS │               │ Python/Node  │
│ React/Vue   │               │ Flask/Django  │
│ Kullanıcı   │               │ Veri İşleme  │
│ arayüzü     │               │ API'ler      │
└─────────────┘               └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │  VERİTABANI  │
                              │ PostgreSQL   │
                              │ SQLite       │
                              └──────────────┘
```

**Streamlit'in farkı:** Streamlit hem frontend hem backend'i tek bir Python dosyasında yönetir.
Normal web uygulamalarında bunlar ayrıdır. Bu avantaj (kolay) ama dezavantaj (özelleştirme kısıtlı).

### 🔑 Deploy (Yayınlama) Nedir?
Kodunu bir sunucuya yükleyip, herkesin erişebileceği bir URL'den çalıştırmaktır.

### 🔑 Sunucu Türleri
| Tür | Açıklama | Örnek |
|-----|----------|-------|
| **Shared Hosting** | Aynı sunucuyu başkalarıyla paylaşırsın | Turhost, GoDaddy |
| **VPS** (Virtual Private Server) | Sanal ama sana özel sunucu | DigitalOcean, Hetzner, Contabo |
| **PaaS** (Platform as a Service) | Sadece kodu yükle, altyapıyı platform yönetir | Heroku, Railway, Render |
| **Serverless** | Sunucu yok, fonksiyon çalışır | Vercel, AWS Lambda, Cloudflare Workers |
| **Container Hosting** | Docker container'ını çalıştırır | Fly.io, Railway, Google Cloud Run |

### 🔑 Docker Nedir?
```
┌──────────────────────────────────────┐
│           Docker Container           │
│  ┌────────────────────────────┐      │
│  │  Senin Uygulaman           │      │
│  │  + Python 3.11             │      │
│  │  + Tüm kütüphaneler       │      │
│  │  + Sistem bağımlılıkları   │      │
│  └────────────────────────────┘      │
│  Hangi sunucuda çalışırsa çalışsın,  │
│  aynı şekilde davranır              │
└──────────────────────────────────────┘
```
- **Ne yapar?** Uygulamanı, bağımlılıklarını ve ortamını tek bir "kutu" (container) içine paketler
- **Neden?** "Benim bilgisayarımda çalışıyor" sorununu ortadan kaldırır
- **Nasıl?** Bir `Dockerfile` yazarsın, `docker build` ile image oluşturursun, `docker run` ile çalıştırırsın
- **Analoji:** Bir taşınma kolisi gibi düşün — her şeyi kutunun içine koyarsın, nereye taşırsan taşı aynı şekilde açılır

### 🔑 DNS ve Domain
```
kullanıcı "altins1.com" yazar
         │
         ▼
┌─────────────┐     IP: 123.45.67.89     ┌─────────────┐
│  DNS Sunucu │ ──────────────────────►  │ Senin Sunucu │
│  (Rehber)   │                          │              │
└─────────────┘                          └──────────────┘
```
- **Domain:** İnsan okunabilir adres (örn: altins1analiz.com)
- **DNS:** Domain'i IP adresine çeviren sistem (telefon rehberi gibi)
- **SSL/TLS:** Adresi `https://` yapan güvenlik sertifikası

### 🔑 Ortam Değişkeni (Environment Variable)
```bash
# .env dosyası (GİT'E EKLENMEZ!)
EMAIL_PASSWORD=gizli_sifre_123
SMTP_SERVER=smtp.gmail.com
API_KEY=abc123xyz
```
Hassas bilgileri (şifreler, API anahtarları) kodun içine yazmak yerine ortam değişkenlerinde saklarsın.

---

## 3. WEB'E TAŞIMA YÖNTEMLERİ

### Karşılaştırma Tablosu

| Özellik              | Streamlit Cloud| VPS + Docker          | Vercel + Supabase     | Railway / Render | Ev Sunucusu (PC/RPi) |
| **Zorluk**           | ⭐ Çok Kolay  | ⭐⭐⭐⭐ Zor         | ⭐⭐⭐⭐⭐ En Zor | ⭐⭐ Kolay        | ⭐⭐⭐ Orta-Zor |
| **Maliyet**          | Ücretsiz       | ~$4-10/ay             | Ücretsiz başlar       | Ücretsiz başlar   | Sadece elektrik (~₺30-80/ay) |
| **Kod Değişikliği**  | Yok            | Az (Dockerf ile)      | Tamamen yeniden yaz   | Az (Dockerfile)   | Az (Docker) |
| **Özelleştirme**     | Düşük          | Çok Yüksek            | Çok Yüksek            | Orta              | Çok Yüksek |
| **Öğrenme Değeri**   | Düşük          | Çok Yüksek            | Çok Yüksek            | Orta              | En Yüksek |
| **Performans**       | Orta           | Yüksek                | Yüksek                | Orta-İyi          | RPi: Orta / PC: Yüksek |
| **Ölçeklenebilirlik**| Düşük          | Manuel                | Otomatik              | Otomatik          | Manuel |
| **Domain Desteği**   | Hayır          | Evet                  | Evet                  | Evet              | Evet (DDNS) |
| **Veritabanı**       | Dosya (geçici) | İstediğin             | Supabase (PostgreSQL) | Eklenti ile       | İstediğin |
| **SSL (HTTPS)**      | Otomatik       | Manuel (Let's Encrypt) | Otomatik             | Otomatik          | Manuel |
| **Streamlit Uyumlu** | ✅ Doğrudan    | ✅ Docker ile         | ❌ Yeniden yazılmalı | ✅ Docker ile    | ✅ Docker ile |

### Hangi Yöntemi Seçmeliyim?

> **💰 Maliyet Tercihi:** Aylık sabit ücret ödenmeyecek.
> VPS (~€4.5/ay) ve Railway ücretli planları **elendi**. Rehberde referans olarak duruyorlar
> ama aktif değerlendirme dışındalar. Odak: ücretsiz + kendi donanım.

```
Soru 1: Streamlit arayüzünden memnun musun?
  ├─ EVET → Soru 2
  └─ HAYIR → Vercel + Supabase (ücretsiz tier, ama yeniden yazma gerekir)
  
 Soru 2: Nasıl yayınlamak istiyorsun?
  ├─ HIZLI (5 dk)     → Streamlit Cloud (ücretsiz, sıfır değişiklik)
  ├─ KALICI + ÖğREN  → Raspberry Pi 4 + Docker (✅ ÖNERİLEN — donanım zaten var!)
  └─ İKSİ DE         → Önce Streamlit Cloud, sonra RPi'ye geç

✅ Önerilen yol: Streamlit Cloud (hemen) → RPi + Docker (kalıcı çözüm)
❌ Elenen: VPS (aylık ücret), Railway/Render ücretli planlar
ℹ️ Referans: VPS ve Railway bölümleri rehberde bilgi amaçlı duruyor
```

---

## YÖNTEM 1: Streamlit Community Cloud

### Ne? 
Streamlit'in kendi ücretsiz hosting platformu. GitHub repo'ndan direkt deploy.

### Avantajları ✅
- **Sıfır değişiklik** — mevcut kodu olduğu gibi deploy edersin
- **5 dakikada yayında** — GitHub bağla, repo seç, çalıştır
- **Ücretsiz** — Community plan tamamen bedava
- **Otomatik güncelleme** — GitHub'a push = otomatik redeploy
- **SSL dahil** — https:// ile çalışır
- **Secrets yönetimi** — Ortam değişkenleri için panel var

### Dezavantajları ❌
- **Özel domain yok** — `*.streamlit.app` adresi alırsın
- **Uyku modu** — Kullanılmadığında uyur, ilk açılış yavaş (30-60 sn)
- **Sınırlı kaynak** — 1 GB RAM, yoğun işlemlerde yavaşlar
- **Dosya sistemi geçici** — Uygulama uyandığında cache dosyaları silinir
- **Özelleştirme kısıtlı** — Arka plan görevleri, cron job çalıştıramazsın
- **Tek uygulama görünümü** — Sadece Streamlit arayüzü, başka sayfa ekleyemezsin

### Adım Adım Uygulama

#### Adım 1: GitHub'a Yükle
```bash
# Proje zaten GitHub'daysa bu adımı atla
cd altins1_analiz
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/KULLANICI_ADI/altins1-analiz.git
git push -u origin main
```

#### Adım 2: .gitignore Kontrol
```gitignore
# .gitignore dosyasında bunlar olmalı:
.env
__pycache__/
*.pyc
data/cache/
logs/
.venv/
```

#### Adım 3: secrets.toml Hazırla
```toml
# .streamlit/secrets.toml (YEREL — git'e ekleme!)
[email]
password = "uygulama_sifresi"
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender = "ornek@gmail.com"
```

#### Adım 4: Streamlit Cloud'a Deploy
1. https://share.streamlit.io adresine git
2. GitHub hesabınla giriş yap
3. "New app" → Repo seç → Branch: main → Main file: main.py
4. "Advanced settings" → Secrets kısmına yukarıdaki TOML'u yapıştır
5. "Deploy" butonuna bas

#### Adım 5: Test Et
- URL: `https://kullanici-adi-altins1-analiz-main-xxxxx.streamlit.app`
- İlk açılış biraz uzun sürer (cold start)
- Verilerin doğru geldiğini kontrol et

### ⚠️ Dikkat Edilecekler
- `data/cache/` klasörü geçici — uygulama uyandığında cache boş olur
- `requirements.txt` doğru ve eksiksiz olmalı
- `tvdatafeed` git bağımlılığı sorun çıkarabilir → alternatif düşünülmeli

---

## YÖNTEM 2: VPS + Docker

### Ne?
Kendi sanal sunucunu kiralayıp, Docker ile uygulamayı çalıştırmak.

### Avantajları ✅
- **Tam kontrol** — Sunucu sana ait, istediğini yaparsın
- **Sürekli çalışır** — Uyku modu yok, 7/24 aktif
- **Özel domain** — altins1analiz.com gibi adres kullanabilirsin
- **Veritabanı** — PostgreSQL, Redis, her şeyi kurabilirsin
- **Cron job** — Zamanlanmış görevler (günlük e-posta vs.)
- **Çok şey öğrenirsin** — Linux, Docker, Nginx, SSL, DNS
- **Birden fazla uygulama** — Aynı sunucuda başka projeler de çalıştırabilirsin
- **Dosya sistemi kalıcı** — Cache dosyaları silinmez

### Dezavantajları ❌
- **Aylık maliyet** — En ucuz ~$4/ay (Hetzner, Contabo)
- **Öğrenme eğrisi dik** — Linux, Docker, Nginx, SSL öğrenmen gerekir
- **Bakım senin işin** — Güvenlik güncellemeleri, yedekleme, izleme
- **Manuel ölçekleme** — Trafik artarsa sunucuyu büyütmen gerekir
- **İlk kurulum uzun** — İlk seferde 1-2 saat sürebilir

### Mimari
```
İnternet
    │
    ▼
┌────────────────────────────────────────────────┐
│              VPS Sunucu (Linux)                 │
│                                                │
│  ┌──────────┐    ┌──────────────────────┐      │
│  │  Nginx   │───►│  Docker Container    │      │
│  │  (Proxy) │    │  ┌────────────────┐  │      │
│  │  :80/:443│    │  │ Streamlit App  │  │      │
│  └──────────┘    │  │ main.py        │  │      │
│       │          │  │ :8501          │  │      │
│       │          │  └────────────────┘  │      │
│  ┌────▼─────┐    └──────────────────────┘      │
│  │SSL Cert  │                                  │
│  │Let's Enc.│    ┌──────────────────────┐      │
│  └──────────┘    │  PostgreSQL (opsiyonel)│     │
│                  │  :5432               │      │
│                  └──────────────────────┘      │
└────────────────────────────────────────────────┘
```

### Adım Adım Uygulama

#### Adım 1: VPS Seç ve Satın Al

| Sağlayıcı | En Ucuz Plan | RAM | Disk | Konum | Not |
|-----------|-------------|-----|------|-------|-----|
| **Hetzner** | ~€4.5/ay | 2 GB | 20 GB | Almanya/Finlandiya | En iyi fiyat/performans |
| **Contabo** | ~€5/ay | 4 GB | 50 GB | Almanya | Çok ucuz, daha yavaş |
| **DigitalOcean** | $6/ay | 1 GB | 25 GB | Hollanda/ABD | Kolay panel, iyi döküman |
| **Linode (Akamai)** | $5/ay | 1 GB | 25 GB | ABD/Avrupa | Güvenilir |
| **Oracle Cloud** | Ücretsiz! | 1 GB | 50 GB | ABD | Always Free tier (sınırlı) |

**Öneri:** Hetzner (CX22 plan) — €4.5/ay, 2 GB RAM, Avrupa lokasyon, mükemmel performans.

#### Adım 2: Dockerfile Yaz
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Veri ve log dizinleri
RUN mkdir -p data/cache logs

# Streamlit ayarları
RUN mkdir -p /root/.streamlit
RUN echo '[server]\nheadless = true\nport = 8501\nenableCORS = false\nenableXsrfProtection = false\n\n[browser]\nserverAddress = "0.0.0.0"\ngatherUsageStats = false' > /root/.streamlit/config.toml

EXPOSE 8501

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
```

#### Adım 3: docker-compose.yml Yaz
```yaml
# docker-compose.yml
version: '3.8'

services:
  altins1:
    build: .
    container_name: altins1-analiz
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data          # Cache verileri kalıcı
      - ./logs:/app/logs          # Log dosyaları kalıcı
    environment:
      - TZ=Europe/Istanbul
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    env_file:
      - .env
```

#### Adım 4: Sunucuya Bağlan ve Kur
```bash
# 1. SSH ile sunucuya bağlan
ssh root@SUNUCU_IP_ADRESI

# 2. Sistemi güncelle
apt update && apt upgrade -y

# 3. Docker kur
curl -fsSL https://get.docker.com | sh

# 4. Docker Compose kur (genelde Docker ile birlikte gelir)
docker compose version  # kontrol et

# 5. Git kur ve projeyi çek
apt install git -y
git clone https://github.com/KULLANICI_ADI/altins1-analiz.git
cd altins1-analiz

# 6. .env dosyası oluştur
nano .env
# İçine ortam değişkenlerini yaz

# 7. Docker ile başlat
docker compose up -d --build

# 8. Kontrol et
docker compose logs -f altins1
```

#### Adım 5: Nginx Reverse Proxy Kur (Opsiyonel ama Önerilen)
```bash
# 1. Nginx kur
apt install nginx -y

# 2. Konfigürasyon dosyası oluştur
nano /etc/nginx/sites-available/altins1
```

```nginx
# /etc/nginx/sites-available/altins1
server {
    listen 80;
    server_name altins1analiz.com www.altins1analiz.com;  # veya sunucu IP

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;  # WebSocket timeout
    }

    # Streamlit WebSocket desteği
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

```bash
# 3. Site'ı aktif et
ln -s /etc/nginx/sites-available/altins1 /etc/nginx/sites-enabled/
nginx -t  # Konfigürasyon kontrolü
systemctl restart nginx
```

#### Adım 6: SSL Sertifikası (HTTPS) — Let's Encrypt
```bash
# 1. Certbot kur
apt install certbot python3-certbot-nginx -y

# 2. SSL sertifikası al (domain gerekli!)
certbot --nginx -d altins1analiz.com -d www.altins1analiz.com

# Otomatik yenileme zaten ayarlanır (90 günde bir)
```

### 🧠 Docker Hakkında Öğrenme Notları

**Temel Docker Komutları:**
```bash
docker build -t altins1 .           # Image oluştur
docker run -d -p 8501:8501 altins1  # Container başlat
docker ps                            # Çalışan container'ları listele
docker logs altins1-analiz           # Logları gör
docker stop altins1-analiz           # Durdur
docker rm altins1-analiz             # Sil
docker compose up -d                 # Compose ile başlat
docker compose down                  # Compose ile durdur
docker compose logs -f               # Compose logları takip et
```

**Kavramlar:**
- **Image:** Uygulamanın fotoğrafı (blueprint)
- **Container:** Image'dan çalışan bir kopya (instance)
- **Volume:** Kalıcı veri alanı (container silinse bile veri kalır)
- **Port mapping:** `-p 8501:8501` → Sunucunun 8501 portunu container'ın 8501 portuna bağla

---

## YÖNTEM 3: Vercel + Supabase

### Ne?
Frontend'i Vercel'de (Next.js/React), backend API'yi Vercel Serverless Functions'da,
veritabanını Supabase'de (PostgreSQL) çalıştırmak.

### ⚠️ ÖNEMLİ UYARI
Bu yöntem **uygulamayı tamamen yeniden yazmayı** gerektirir. Streamlit yerine
React/Next.js frontend + Python/Node.js API yazılır. En çok öğrenilen ama en zor yöntem.

### Avantajları ✅
- **Ücretsiz tier** — Vercel ve Supabase'in cömert ücretsiz planları var
- **Otomatik ölçekleme** — Trafik artarsa Vercel otomatik ölçekler
- **Modern mimari** — Gerçek dünyada kullanılan teknolojiler
- **Hızlı** — CDN ile dünya genelinde hızlı (Edge Network)
- **En çok şey öğrenirsin** — React, API, veritabanı, modern web geliştirme
- **Özel domain** — Kolayca bağlanır
- **Otomatik SSL** — Vercel ücretsiz sağlar
- **Gerçek veritabanı** — Supabase = Hosted PostgreSQL + API

### Dezavantajları ❌
- **Tamamen yeniden yazım** — Streamlit kodu kullanılamaz
- **Çok fazla yeni teknoloji** — React, Next.js, TypeScript, Supabase, Vercel CLI
- **Öğrenme süresi uzun** — Aylar sürebilir
- **Serverless sınırları** — Fonksiyonlar max 10-60 sn çalışır (yfinance veri çekme sorun olabilir)
- **Cold start** — İlk istek yavaş olabilir
- **Python desteği sınırlı** — Vercel serverless Python destekler ama ekosistemi Node.js ağırlıklı

### Mimari
```
┌──────────────────────────────────────────────────┐
│                   Vercel                          │
│  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Next.js Frontend│  │ Serverless API   │      │
│  │  React Bileşenler│  │ /api/prices      │      │
│  │  Grafikler (Chart│  │ /api/signal      │      │
│  │  .js / Recharts) │  │ /api/news        │      │
│  │  Tailwind CSS    │  │ (Python/Node.js) │      │
│  └──────────────────┘  └────────┬─────────┘      │
│                                 │                │
└─────────────────────────────────┼────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │        Supabase             │
                    │  ┌──────────────────┐       │
                    │  │   PostgreSQL     │       │
                    │  │   - prices       │       │
                    │  │   - signals      │       │
                    │  │   - users        │       │
                    │  └──────────────────┘       │
                    │  ┌──────────────────┐       │
                    │  │  Auth (Kimlik)   │       │
                    │  │  Storage (Dosya) │       │
                    │  │  Realtime        │       │
                    │  └──────────────────┘       │
                    └────────────────────────────┘
```

### Supabase Nedir?
- **Açık kaynak Firebase alternatifi**
- PostgreSQL veritabanı + Auth + Storage + Realtime
- Ücretsiz plan: 500 MB veritabanı, 1 GB dosya depolama, 50K aylık aktif kullanıcı
- SQL yazabilirsin (Firebase'den farkı bu — gerçek SQL!)

### Vercel Nedir?
- **Frontend hosting + Serverless Functions platformu**
- Next.js'in yaratıcığı firmanın platformu (doğal entegrasyon)
- Her git push otomatik deploy
- Ücretsiz plan: Hobi projeleri için yeterli
- CDN (Content Delivery Network) ile dünya genelinde hızlı

### Bu Yöntemi Seçersen Öğrenmen Gerekenler
1. **JavaScript/TypeScript** (temel seviye yeterli)
2. **React** (bileşen mantığı)
3. **Next.js** (sayfa yönlendirme, API routes)
4. **Supabase client** (veritabanı CRUD işlemleri)
5. **CSS/Tailwind** (tasarım)
6. **Chart.js veya Recharts** (grafikler)

### Tahmini Geliştirme Süresi
- React/Next.js öğrenme: 2-4 hafta
- Uygulamayı yeniden yazma: 2-4 hafta
- **Toplam:** 1-2 ay (part-time çalışarak)

---

## YÖNTEM 4: Railway / Render

### Ne?
Docker veya doğrudan Python desteği olan PaaS platformları. 
GitHub repo'ndan otomatik deploy. Docker bilmesen de çalışır, bilsen daha iyi.

### Avantajları ✅
- **Kolay deploy** — GitHub bağla, otomatik çalışır
- **Docker desteği** — Dockerfile varsa kullanır, yoksa otomatik algılar
- **Ücretsiz tier** — Sınırlı ama başlangıç için yeterli (Railway: $5 kredi/ay)
- **Veritabanı eklentisi** — PostgreSQL, Redis ekleyebilirsin (Railway)
- **Özel domain** — Ücretsiz planda bile
- **SSL otomatik** — https:// dahil
- **Ortam değişkenleri** — Panel üzerinden kolay yönetim
- **Log görüntüleme** — Web panelden logları görebilirsin

### Dezavantajları ❌
- **Ücretsiz plan sınırlı** — Railway: $5/ay kredi (aşınca durur), Render: 750 saat/ay
- **Uyku modu** (Render ücretsiz) — 15 dk inaktivite sonrası uyur
- **Kaynak sınırlı** — Ücretsiz planlarda RAM/CPU düşük
- **Vendor lock-in riski** — Platforma bağımlılık (ama Docker ile azalır)

### Railway Adım Adım
```bash
# 1. https://railway.app adresine git, GitHub ile giriş yap
# 2. "New Project" → "Deploy from GitHub repo" 
# 3. altins1-analiz reposunu seç
# 4. Railway otomatik olarak Python algılar ve deploy eder
# 5. Settings → Environment Variables → .env değişkenlerini ekle
# 6. Settings → Domains → Generate Domain (veya özel domain bağla)
```

### Render Adım Adım
```bash
# 1. https://render.com adresine git, GitHub ile giriş yap  
# 2. "New" → "Web Service"
# 3. GitHub repo bağla → altins1-analiz seç
# 4. Runtime: Docker (veya Python)
# 5. Start Command: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
# 6. Environment Variables ekle
# 7. "Create Web Service"
```

---

## YÖNTEM 5: Ev Sunucusu — Kendi PC veya Raspberry Pi

### Ne?
Kendi bilgisayarını veya modeme bağlı bir Raspberry Pi'yi sunucu olarak kullanıp,
uygulamayı evinden internete açmak. VPS kiralamak yerine kendi donanımını kullanırsın.

### ⚡ İki Seçenek

| Özellik | Windows PC | Raspberry Pi 4 |
|---------|:----------:|:--------------:|
| **Donanım maliyeti** | Zaten var | ~₺3.000-5.000 (4GB/8GB model) |
| **Elektrik tüketimi** | 100-300W (~₺50-150/ay) | 5-15W (~₺5-15/ay) |
| **Performans** | Yüksek | Orta (yeterli) |
| **Gürültü** | Fan sesi var | Sessiz |
| **7/24 çalışma** | PC'yi kapatma şart yok ama yıpratır | Bunun için tasarlandı ✅ |
| **Güvenilirlik** | Windows güncellemeleri/restart riski | Linux, kararlı |
| **Taşınabilirlik** | Büyük | Avuç içi kadar |
| **Docker desteği** | ✅ Docker Desktop | ✅ Docker (ARM) |
| **OS** | Windows 10/11 | Raspberry Pi OS (Debian/Linux) |

### Avantajları ✅
- **Aylık maliyet yok** — VPS kirası ödemezsin (sadece elektrik)
- **Tam kontrol** — Donanım ve yazılım tamamen sende
- **Sınırsız kaynak** — PC: 16GB+ RAM; RPi: 4-8GB RAM (VPS'den fazla)
- **Kalıcı depolama** — Dosya sistemi kalıcı, disk alanı bol
- **Yerel ağda hızlı** — Evdeki cihazlardan anında erişim
- **Çok şey öğrenirsin** — Linux, ağ, port forwarding, güvenlik, Docker
- **Birden fazla proje** — Aynı cihazda istediğin kadar uygulama çalıştır
- **Veritabanı özgürlüğü** — PostgreSQL, SQLite, Redis... hepsi çalışır

### Dezavantajları ❌
- **İnternet hızına bağlı** — Evdeki upload hızın sınırlayıcı (Türkiye'de genelde 5-20 Mbps upload)
- **Dinamik IP sorunu** — ISP her gün IP'ni değiştirebilir → DDNS gerekir
- **ISP kısıtlamaları** — Bazı ISP'ler port 80/443'ü engelleyebilir
- **Elektrik kesintisi** — Elektrik giderse site de gider (UPS gerekebilir)
- **Modem ayarları** — Port forwarding yapman gerekir (ilk seferde zor gelebilir)
- **Güvenlik riski** — Ev ağını internete açıyorsun (doğru yapılmazsa risk)
- **Bakım senin işin** — Güncelleme, yedekleme, izleme hep sana ait
- **IP itibarı düşük** — Ev IP'leri e-posta gönderirken spam olarak işaretlenebilir

### 🏗️ Mimari (Ev Sunucusu)

```
İnternet
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│                    Modem/Router                               │
│  WAN IP: 85.xxx.xxx.xxx (dinamik)                            │
│  Port Forwarding: 80→RPi:80, 443→RPi:443                    │
└──────────────────────┬───────────────────────────────────────┘
                       │ LAN (192.168.1.x)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              Raspberry Pi 4 / Windows PC                     │
│              IP: 192.168.1.100 (sabit)                       │
│                                                              │
│  ┌──────────┐    ┌──────────────────────┐                    │
│  │  Nginx   │───►│  Docker Container    │                    │
│  │  :80/:443│    │  ┌────────────────┐  │                    │
│  │  + SSL   │    │  │ Streamlit App  │  │                    │
│  └──────────┘    │  │ main.py :8501  │  │                    │
│                  │  └────────────────┘  │                    │
│  ┌──────────┐   └──────────────────────┘                    │
│  │  DDNS    │   ┌──────────────────────┐                    │
│  │  Client  │   │  SQLite/PostgreSQL   │                    │
│  └──────────┘   └──────────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

---

### SEÇENEK A: Raspberry Pi 4 ile Sunucu

#### Neden Raspberry Pi?
- **7/24 çalışması için tasarlandı** — Az elektrik, sessiz, küçük
- **Linux tabanlı** — Gerçek sunucu deneyimi
- **GPIO pinleri** — İleride sensör/LED gibi donanım projeleri de yapabilirsin
- **Topluluk büyük** — Her sorunun cevabı internette var

#### Mevcut Donanım (İlker'in Elinde Olanlar) ✅
| Malzeme | Durum | Not |
|---------|:-----:|-----|
| Raspberry Pi 4 | ✅ Mevcut | Sunucu için yeterli |
| 512 GB SSD | ✅ Mevcut | SD kart yerine SSD kullanmak **çok daha iyi** (hız + ömür) |

#### Ek İhtiyaçlar (Varsa Kontrol Et)
| Malzeme | Tahmini Fiyat | Not |
|---------|:------------:|-----|
| USB 3.0 - SATA Adaptörü | ~₺150-250 | SSD'yi RPi'ye bağlamak için (USB 3.0 port kullan!) |
| USB-C Güç Adaptörü (5V/3A) | ~₺150 | Varsa gerek yok, orijinal RPi adaptörü önerilir |
| Ethernet Kablosu | ~₺30 | WiFi de olur ama kablo daha kararlı |
| Kasa (opsiyonel) | ~₺100-200 | Fanlı kasa ısınmayı önler |
| **Ek Maliyet** | **~₺0-400** | Çoğu zaten evde bulunur |

> **💡 SSD Avantajı:** MicroSD kart yerine 512 GB SSD kullanmak **devasa bir fark** yaratır:
> - **10-20x daha hızlı** okuma/yazma (Docker build, veri işleme, veritabanı)
> - **Çok daha uzun ömür** — SD kartlar yoğun yazma ile 6-12 ayda bozulabilir, SSD yıllarca dayanır
> - **512 GB alan** — Veritabanı, loglar, cache, yedekler için bol alan
> - Kısacası: SD kart ile çalıştırma, **direkt SSD'den boot et**

#### Adım 1: SSD'den Boot Etme (SD Kart Yerine)

```
⚠️ ÖNEMLİ: 512 GB SSD'n olduğu için SD kartsız, doğrudan SSD'den boot et.
   Bu hem hızlı hem de güvenilir olur.

Gerekli: USB 3.0 to SATA adaptörü (veya SSD kutusu)
         SSD'yi RPi'nin MAVİ USB 3.0 portuna bağla (siyah olanlar USB 2.0, yavaş!)
```

```bash
# 1. Raspberry Pi Imager'ı Windows'a indir:
#    https://www.raspberrypi.com/software/
#
# 2. SSD'yi USB adaptörle Windows PC'ye bağla
#
# 3. Imager'ı aç:
#    - Cihaz: Raspberry Pi 4
#    - OS: "Raspberry Pi OS Lite (64-bit)" 
#      (Desktop gereksiz, Lite yeterli — sunucu için)
#    - Depolama: SSD'yi seç (SD kartı DEĞİL!)
#
# 4. Ayarlar (⚙️ ikon):
#    - Hostname: altins1-server
#    - SSH: Aktif et (şifre ile)
#    - Kullanıcı adı: pi  |  Şifre: güçlü_bir_şifre
#    - WiFi: (opsiyonel, ethernet tercih et)
#    - Locale: Europe/Istanbul, TR klavye
#
# 5. "Write" butonuna bas → SSD'ye yazılacak
#
# 6. SSD'yi USB 3.0 adaptörle RPi'nin MAVİ (USB 3.0) portuna bağla
#    SD kart TAKMA — RPi otomatik olarak USB'den boot eder
#    (RPi 4 firmware'i varsayılan olarak USB boot destekler)
#
# 7. Ethernet kablosu bağla, güç ver
```

> **Not:** RPi 4 genelde kutudan USB boot destekler. Eğer boot etmezse:
> ```bash
> # Geçici olarak SD karta OS yaz, boot et, sonra şu komutları çalıştır:
> sudo raspi-config
> # Advanced Options → Boot Order → USB Boot → Finish → Reboot
> # Ardından SD kartı çıkar, SSD ile tekrar başlat
> ```

#### Adım 2: SSH ile Bağlan
```bash
# Windows PowerShell veya Terminal:
ssh pi@altins1-server.local
# veya IP ile:
ssh pi@192.168.1.XXX

# IP adresini bulmak için modem paneline bak (192.168.1.1)
# veya Windows'ta:
ping altins1-server.local
```

#### Adım 3: Sistemi Güncelle ve Docker Kur
```bash
# Sistemi güncelle
sudo apt update && sudo apt upgrade -y

# Docker kur (ARM destekli)
curl -fsSL https://get.docker.com | sh

# Docker'ı pi kullanıcısına ekle (sudo olmadan kullanmak için)
sudo usermod -aG docker pi

# Oturumu yenile (çıkış yap, tekrar bağlan)
exit
ssh pi@altins1-server.local

# Docker çalışıyor mu kontrol et
docker --version
docker compose version
```

#### Adım 4: Projeyi Çek ve Çalıştır
```bash
# Git kur (genelde yüklü gelir)
sudo apt install git -y

# Projeyi klonla
git clone https://github.com/KULLANICI_ADI/altins1-analiz.git
cd altins1-analiz

# .env dosyası oluştur
nano .env
# İçine ortam değişkenlerini yaz (EMAIL_PASSWORD vs.)

# Docker ile başlat
docker compose up -d --build

# ⚠️ İlk build ARM mimarisinde biraz uzun sürer (10-20 dk)
# Logları takip et:
docker compose logs -f
```

#### Adım 5: RPi'ye Sabit IP Ver
```bash
# Modem panelinden (192.168.1.1) RPi'nin MAC adresine sabit IP ata
# VEYA RPi üzerinde:
sudo nano /etc/dhcpcd.conf

# Dosyanın sonuna ekle:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=1.1.1.1 8.8.8.8

# Kaydet (Ctrl+O, Enter, Ctrl+X) ve yeniden başlat:
sudo reboot
```

---

### SEÇENEK B: Windows PC ile Sunucu

#### Adım 1: Docker Desktop Kur
```
1. https://www.docker.com/products/docker-desktop/ adresinden indir
2. Kur ve bilgisayarı yeniden başlat
3. Docker Desktop'ı aç, "WSL 2" backend'ini kullan (önerilir)
4. Terminal'den test et:
   docker --version
   docker compose version
```

#### Adım 2: Projeyi Docker ile Çalıştır
```powershell
# PowerShell'de proje klasörüne git
cd C:\Users\ilker\Documents\GitHub\Projects\altins1_analiz

# Docker ile başlat
docker compose up -d --build

# Tarayıcıda test et:
# http://localhost:8501
```

#### Adım 3: PC'ye Sabit Yerel IP Ver
```
1. Ayarlar → Ağ ve İnternet → Ethernet (veya WiFi)
2. IP ayarları → Düzenle → Manuel
3. IPv4: Açık
   - IP adresi: 192.168.1.100
   - Alt ağ maskesi: 255.255.255.0 (veya /24)
   - Ağ geçidi: 192.168.1.1
   - DNS: 1.1.1.1, 8.8.8.8
```

#### ⚠️ Windows PC ile Sunucu Kullanmanın Ekstra Riskleri
- **Windows Update** otomatik yeniden başlatır → Uygulama durur
  - Çözüm: Aktif saatleri ayarla, veya güncellemeleri erteleme
- **Uyku modu** → Bilgisayar uyursa site kapanır
  - Çözüm: Ayarlar → Güç → Asla uyuma
- **Firewall** → Windows Defender port'ları engelleyebilir
  - Çözüm: 8501 portunu Windows Firewall'da aç

---

### HER İKİ SEÇENEK İÇİN: İnternete Açma

#### Adım A: Modemde Port Forwarding (Port Yönlendirme)

```
Bu ne yapar?
Dışarıdan gelen istekleri modemin ev ağındaki doğru cihaza yönlendirir.

                    İnternet
                       │
              ┌────────▼────────┐
              │     MODEM       │
              │                 │
              │  Port 80  ──────┼──► 192.168.1.100:80  (Nginx)
              │  Port 443 ──────┼──► 192.168.1.100:443 (Nginx/SSL)
              │                 │
              └─────────────────┘
```

```
Adımlar:
1. Modem paneline gir: http://192.168.1.1 (veya modeminin adresi)
   - Kullanıcı adı/şifre: genelde modem etiketinde yazar
   - Türk Telekom: admin/ttnet veya modem üzerindeki etiket
   - Superonline: admin/admin veya modem etiketi

2. "Port Yönlendirme" / "Port Forwarding" / "NAT" bölümünü bul
   (Her modemde farklı yerde, genelde Gelişmiş Ayarlar altında)

3. Yeni kural ekle:
   ┌──────────────────────────────────────────────────┐
   │ Kural Adı: altins1-http                          │
   │ Protokol: TCP                                    │    
   │ Dış Port (External): 80                          │
   │ İç IP (Internal): 192.168.1.100                  │
   │ İç Port (Internal): 80                           │
   ├──────────────────────────────────────────────────┤
   │ Kural Adı: altins1-https                         │
   │ Protokol: TCP                                    │
   │ Dış Port (External): 443                         │
   │ İç IP (Internal): 192.168.1.100                  │
   │ İç Port (Internal): 443                          │
   └──────────────────────────────────────────────────┘

4. Kaydet ve modemi yeniden başlat (opsiyonel)
```

**⚠️ ISP Port Engeli Kontrolü:**
```bash
# Dışarıdan test etmek için (başka bir ağdan veya telefondan 4G ile):
# https://www.yougetsignal.com/tools/open-ports/
# IP'ni gir, port 80 ve 443'ü kontrol et

# Eğer ISP port 80/443'ü engelliyorsa:
# Alternatif port kullan (8080, 8443 gibi)
# VEYA Cloudflare Tunnel kullan (aşağıda anlatılıyor)
```

#### Adım B: Dinamik DNS (DDNS) Kurulumu

```
Sorun: Ev internet IP'n her gün değişebilir (dinamik IP).
Çözüm: DDNS servisi IP değişse bile aynı adresten erişim sağlar.

Nasıl çalışır?
┌──────────────┐                    ┌──────────────┐
│  RPi/PC'de   │  "IP'm değişti,   │  DDNS Sunucu │
│  DDNS Client │  yeni IP: 85.x"   │  (No-IP vs.) │
│              │ ──────────────────►│              │
└──────────────┘                    └──────┬───────┘
                                           │
                     altins1.ddns.net ──► 85.xxx.xxx.xxx
```

**Ücretsiz DDNS Servisleri:**

| Servis | Ücretsiz Domain | Not |
|--------|----------------|-----|
| **No-IP** | 3 hostname (30 günde bir onayla) | En popüler, kolay |
| **DuckDNS** | 5 subdomain | Tamamen ücretsiz, açık kaynak |
| **Dynu** | 4 hostname | DDNS + DNS hizmeti |
| **FreeDNS (afraid.org)** | 5 subdomain | Ücretsiz, topluluk destekli |

**DuckDNS Kurulumu (Önerilen — Tamamen Ücretsiz):**
```bash
# 1. https://www.duckdns.org adresine git, GitHub/Google ile giriş yap
# 2. Bir subdomain oluştur: altins1analiz.duckdns.org
# 3. Token'ını kopyala

# RPi veya Linux üzerinde:
mkdir -p ~/duckdns
nano ~/duckdns/duck.sh
```

```bash
# duck.sh dosyasının içeriği:
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=altins1analiz&token=SENIN_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

```bash
# Çalıştırılabilir yap ve cron'a ekle (her 5 dakikada güncelle):
chmod 700 ~/duckdns/duck.sh
crontab -e
# Açılan editöre bu satırı ekle:
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1

# Test et:
~/duckdns/duck.sh
cat ~/duckdns/duck.log  # "OK" yazmalı
```

#### Adım C: Nginx + SSL Kurulumu (Sunucu Üzerinde)

```bash
# Nginx kur
sudo apt install nginx certbot python3-certbot-nginx -y

# Nginx konfigürasyonu
sudo nano /etc/nginx/sites-available/altins1
```

```nginx
server {
    listen 80;
    server_name altins1analiz.duckdns.org;  # veya kendi domain'in

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

```bash
# Aktif et
sudo ln -s /etc/nginx/sites-available/altins1 /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# SSL sertifikası al (DDNS domain ile):
sudo certbot --nginx -d altins1analiz.duckdns.org
# E-posta gir, şartları kabul et, otomatik yönlendirme seç
```

---

### 🛡️ ALTERNATİF: Cloudflare Tunnel (Port Forwarding Gerektirmez!)

```
Modemde port açmak istemiyorsan veya ISP portları engelliyorsa,
Cloudflare Tunnel mükemmel bir alternatif:

┌─────────────┐      ┌───────────────┐      ┌──────────────┐
│  Kullanıcı  │─────►│  Cloudflare   │◄─────│  RPi/PC      │
│  (Tarayıcı) │ HTTPS│  CDN + Tunnel │ Tünel│  (cloudflared│
│             │      │               │      │   uygulaması)│
└─────────────┘      └───────────────┘      └──────────────┘

✅ Port forwarding gereksiz!
✅ Modem ayarlarına dokunmana gerek yok!
✅ Ücretsiz SSL sertifikası!
✅ DDoS koruması dahil!
✅ ISP port engeli sorun olmaz!
```

```bash
# 1. Cloudflare hesabı aç (ücretsiz): https://dash.cloudflare.com
# 2. Bir domain satın al veya mevcut domain'i Cloudflare'e taşı

# 3. cloudflared kur (RPi/Linux):
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

# Windows için:
# https://github.com/cloudflare/cloudflared/releases adresinden .exe indir

# 4. Cloudflare'e giriş yap:
cloudflared tunnel login
# Tarayıcı açılır, domain seç ve yetkilendir

# 5. Tunnel oluştur:
cloudflared tunnel create altins1-tunnel

# 6. Konfigürasyon dosyası:
nano ~/.cloudflared/config.yml
```

```yaml
# config.yml
tunnel: TUNNEL_ID_BURAYA
credentials-file: /home/pi/.cloudflared/TUNNEL_ID_BURAYA.json

ingress:
  - hostname: altins1.senindomain.com
    service: http://localhost:8501
  - service: http_status:404
```

```bash
# 7. DNS kaydı oluştur:
cloudflared tunnel route dns altins1-tunnel altins1.senindomain.com

# 8. Tunnel'ı başlat:
cloudflared tunnel run altins1-tunnel

# 9. Servis olarak kur (otomatik başlasın):
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

### 🔒 Ev Sunucusu Güvenlik Kontrol Listesi

```
⬜ Güçlü SSH şifresi veya SSH key kullan
⬜ Port 22 (SSH) dışarıya açık OLMAMALI (sadece yerel ağdan)
⬜ fail2ban kur (brute-force saldırılarına karşı)
⬜ UFW firewall aktif et (sadece gerekli portları aç)
⬜ Düzenli güncelleme yap (sudo apt update && upgrade)
⬜ Docker container'ları root olmayan kullanıcıyla çalıştır
⬜ Hassas veriler .env dosyasında, git'e ekleme
⬜ Cloudflare Tunnel kullanıyorsan port forwarding'i kapat
```

```bash
# Temel güvenlik kurulumu (RPi/Linux):

# fail2ban (SSH brute-force koruması)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban

# UFW firewall
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh          # Port 22 (sadece yerel ağdan eriş)
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw enable

# Otomatik güvenlik güncellemeleri
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

### 📊 Ev Sunucusu vs VPS Karşılaştırması

| Kriter | Ev Sunucusu (RPi) | VPS (Hetzner) |
|--------|:-----------------:|:-------------:|
| Aylık maliyet | ~₺10-15 (elektrik) | ~₺200 (~€4.5) |
| İlk yatırım | ~₺0-400 (zaten var! 🎉) | ₺0 |
| 1 yıllık toplam | ~₺180-580 | ~₺2.400 |
| 2 yıllık toplam | ~₺360-760 | ~₺4.800 |
| **İlk günden** | **Çok daha ucuz** ✅ | Daha pahalı |
| Upload hızı | 5-20 Mbps (ev) | 100+ Mbps |
| Uptime (çalışma süresi) | %95-99 (elektrik/internet) | %99.9+ |
| Bakım | Sen yaparsın | Sen yaparsın (ama uzaktan) |
| Öğrenme | Donanım + yazılım | Sadece yazılım |
| Fiziksel erişim | ✅ | ❌ (uzaktan) |

> **Sonuç:** RPi zaten elinde olduğu için VPS'e gerek yok — RPi her yönüyle daha uygun.
> VPS bilgisi rehberde referans olarak duruyor, ileride ihtiyaç olursa bakılabilir.

---

### 🧠 Raspberry Pi Öğrenme Notları

**Temel Linux Komutları (RPi üzerinde kullanacağın):**
```bash
ls -la              # Dosyaları listele
cd /klasor           # Dizin değiştir
pwd                  # Mevcut dizini göster  
nano dosya.txt       # Metin editörü
cat dosya.txt        # Dosya içeriğini göster
sudo                 # Yönetici olarak çalıştır
sudo reboot          # Yeniden başlat
sudo shutdown -h now  # Kapat
htop                 # Sistem kaynakları (CPU, RAM)
df -h               # Disk kullanımı
free -h             # RAM kullanımı
systemctl status nginx  # Servis durumu kontrol
journalctl -u nginx -f  # Servis loglarını takip et
```

**RPi Faydalı Komutlar:**
```bash
vcgencmd measure_temp    # CPU sıcaklığı (60°C altı iyi)
vcgencmd get_throttled   # Güç/ısı throttle durumu (0x0 = sorun yok)
pinout                   # GPIO pin haritası
```

---

## 5. VERİTABANI SEÇENEKLERİ

### Şu Anda: Dosya Tabanlı Cache (JSON)
Mevcut uygulama veritabanı kullanmıyor. `data/cache/` klasörüne JSON dosyaları yazıyor.
Bu yerel çalışırken sorun değil, ama web'de sorun olabilir (geçici dosya sistemi).

### Ne Zaman Veritabanı Gerekir?
| Senaryo | Gerekli mi? | Neden? |
|---------|:-----------:|--------|
| Sadece güncel veri göster | ❌ Hayır | Veriyi API'den çek, cache'le, göster |
| Tarihsel veriyi sakla | ✅ Evet | Her seferinde yfinance'dan çekmek yavaş |
| Kullanıcı hesabı | ✅ Evet | Kullanıcı bilgileri saklanmalı |
| Sinyal geçmişi | ✅ Evet | Geçmiş sinyalleri görmek istersen |
| E-posta abonelikleri | ✅ Evet | Kimin ne zaman bildirim istediği |

### Veritabanı Karşılaştırması

| Veritabanı | Tür | Maliyet | Zorluk | Ne Zaman Kullan? |
|-----------|-----|---------|--------|-----------------|
| **SQLite** | Dosya tabanlı SQL | Ücretsiz | ⭐ Kolay | Tek sunucu, düşük trafik |
| **PostgreSQL** | İlişkisel SQL | Ücretsiz-$7/ay | ⭐⭐ Orta | Ciddi uygulamalar, Supabase ile |
| **Supabase** | Hosted PostgreSQL | Ücretsiz başlar | ⭐⭐ Orta | Vercel ile kullanırken |
| **Redis** | Bellek içi (cache) | Ücretsiz başlar | ⭐⭐ Orta | Hızlı cache, geçici veri |
| **MongoDB** | Belge tabanlı (NoSQL) | Ücretsiz başlar | ⭐⭐ Orta | Esnek yapılı veri |
| **Firebase Firestore** | Bulut NoSQL | Ücretsiz başlar | ⭐ Kolay | Google ekosistemi |

### SQLite (En Basit, VPS İçin Uygun)
```python
# Mevcut JSON cache yerine SQLite kullanmak:
import sqlite3

conn = sqlite3.connect("data/prices.db")
cursor = conn.cursor()

# Tablo oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        altins1_fiyat REAL,
        gram_altin_tl REAL,
        ons_altin_usd REAL,
        dolar_tl REAL,
        makas_pct REAL
    )
""")

# Veri ekle
cursor.execute("""
    INSERT INTO price_cache (timestamp, altins1_fiyat, gram_altin_tl, ons_altin_usd, dolar_tl, makas_pct)
    VALUES (?, ?, ?, ?, ?, ?)
""", ("2026-04-05 14:30:00", 42.50, 3850.0, 2350.50, 38.45, 10.3))
conn.commit()
```

### Supabase (Vercel İçin Uygun)
```javascript
// JavaScript ile Supabase kullanımı (Next.js API)
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY
)

// Veri çek
const { data, error } = await supabase
    .from('price_history')
    .select('*')
    .order('timestamp', { ascending: false })
    .limit(100)

// Veri ekle
const { data, error } = await supabase
    .from('price_history')
    .insert({ altins1_fiyat: 42.50, gram_altin_tl: 3850.0 })
```

---

## 6. DOMAIN (ALAN ADI) REHBERİ

### Domain Nereden Alınır?

| Sağlayıcı | .com Fiyat | .com.tr Fiyat | Türkçe Panel | Not |
|-----------|-----------|---------------|:------------:|-----|
| **Namecheap** | ~$9/yıl | ❌ | ❌ | En popüler, WHOIS koruma ücretsiz |
| **Cloudflare** | ~$9/yıl | ❌ | ❌ | Maliyet fiyatına satar + ücretsiz CDN/DNS |
| **Google Domains** | ~$12/yıl | ❌ | ❌ | Temiz panel, Google entegrasyonu |
| **GoDaddy** | ~$12/yıl | ❌ | ✅ | Yaygın ama ek satışlar dikkat |
| **Natro** | ~₺99/yıl | ~₺89/yıl | ✅ | Türk şirketi, .com.tr desteği |
| **Turhost** | ~₺119/yıl | ~₺89/yıl | ✅ | Türk şirketi |
| **İsimtescil** | ~₺99/yıl | ~₺89/yıl | ✅ | Türk şirketi |

**Öneri:** 
- Uluslararası: **Cloudflare Registrar** (maliyet fiyatı + dahili DNS/CDN)
- Türkiye: **Natro** veya **İsimtescil** (.com.tr istersen)

### Domain'i Sunucuya Bağlama (DNS Ayarları)

```
Domain: altins1analiz.com
Sunucu IP: 123.45.67.89

DNS Kayıtları:
┌──────────┬───────────┬─────────────────┬────────┐
│ Tip      │ İsim      │ Değer           │ TTL    │
├──────────┼───────────┼─────────────────┼────────┤
│ A        │ @         │ 123.45.67.89    │ 3600   │  ← Ana domain
│ A        │ www       │ 123.45.67.89    │ 3600   │  ← www alt alanı
│ CNAME    │ www       │ altins1analiz.com│ 3600   │  ← Alternatif
└──────────┴───────────┴─────────────────┴────────┘
```

**Vercel İçin:**
```
CNAME  →  cname.vercel-dns.com
```

**Railway İçin:**
```
CNAME  →  railway tarafından verilen adres
```

### SSL/HTTPS
- **VPS:** Let's Encrypt (ücretsiz, `certbot` ile otomatik)
- **Vercel/Railway/Render:** Otomatik (hiçbir şey yapmanıza gerek yok)
- **Streamlit Cloud:** Otomatik (ama özel domain desteklemiyor)

---

## 7. ÖNERİLEN YOL HARİTASI

Hem öğrenmek hem uygulamak istediğin için **aşamalı bir plan** öneriyorum:

> **💰 Not:** Aylık ücretli seçenekler (VPS, Railway ücretli plan) elendi.
> Plan tamamen ücretsiz araçlar + mevcut donanım (RPi 4 + 512 GB SSD) üzerine kurulu.

### 🗓️ Aşama 1: Streamlit Cloud (1. Gün)
> **Hedef:** Uygulamayı hiç değiştirmeden internete çıkar, web deploy kavramını öğren

- [ ] GitHub reposunu hazırla (.gitignore, secrets)
- [ ] Streamlit Cloud'a deploy et
- [ ] URL'yi test et, paylaş
- [ ] **Öğrenilen:** Deploy kavramı, CI/CD (otomatik güncelleme), secrets yönetimi

### 🗓️ Aşama 2: Docker Öğren (1. Hafta)
> **Hedef:** Docker'ı kendi bilgisayarında öğren

- [ ] Docker Desktop kur (Windows)
- [ ] Dockerfile yaz
- [ ] `docker build` ve `docker run` ile yerel çalıştır
- [ ] `docker-compose` kurulumu yap
- [ ] **Öğrenilen:** Container kavramı, image, volume, port mapping

### 🗓️ Aşama 3: Raspberry Pi 4 Sunucu Kurulumu (2. Hafta) ⭐ ANA HEDEF
> **Hedef:** RPi 4 + 512 GB SSD ile kendi sunucunu kur, internete aç

- [ ] SSD'ye Raspberry Pi OS Lite yaz (SD kartsız boot)
- [ ] SSH ile bağlan, sistemi güncelle
- [ ] Docker kur, projeyi Docker ile çalıştır
- [ ] RPi'ye sabit yerel IP ver
- [ ] Modemde port forwarding yap VEYA Cloudflare Tunnel kur
- [ ] DDNS ayarla (DuckDNS — ücretsiz)
- [ ] Nginx + SSL kur
- [ ] Güvenlik önlemlerini uygula (fail2ban, UFW)
- [ ] **Öğrenilen:** Linux, Docker, ağ yönetimi, port forwarding, güvenlik

### 🗓️ Aşama 4: Veritabanı Ekle (3. Hafta)
> **Hedef:** JSON cache yerine SQLite/PostgreSQL kullan

- [ ] SQLite ile cache sistemi yaz
- [ ] Tarihsel veriyi veritabanına kaydet
- [ ] Sinyal geçmişi tablosu ekle
- [ ] **Öğrenilen:** SQL temelleri, veritabanı tasarımı

### 🗓️ Aşama 5 (İsteğe Bağlı): Modern Frontend (1-2 Ay)
> **Hedef:** Streamlit'ten bağımsız, özel arayüz

- [ ] Next.js + React öğren
- [ ] Supabase veritabanı kur
- [ ] Backend API yaz (FastAPI veya Vercel Functions)
- [ ] Frontend grafiklerini oluştur (Chart.js / Recharts)
- [ ] Vercel'e deploy et
- [ ] **Öğrenilen:** React, API geliştirme, modern frontend, Supabase

---

## 8. SÖZLÜK

| Terim | Açıklama |
|-------|----------|
| **Deploy** | Uygulamayı sunucuya yükleyip çalışır hale getirme |
| **CI/CD** | Continuous Integration / Continuous Deployment — Kod push'landığında otomatik test ve deploy |
| **Container** | İzole edilmiş uygulama ortamı (Docker) |
| **Image** | Container'ın şablonu (fotoğrafı) |
| **Volume** | Docker'da kalıcı veri alanı |
| **Reverse Proxy** | İstekleri arka plandaki uygulamaya yönlendiren aracı (Nginx) |
| **SSL/TLS** | HTTPS için güvenlik sertifikası |
| **DNS** | Domain adını IP adresine çeviren sistem |
| **CDN** | Content Delivery Network — İçeriği dünya genelinde dağıtan ağ |
| **Serverless** | Sunucu yönetimi olmadan kod çalıştırma |
| **PaaS** | Platform as a Service — Altyapıyı platform yönetir |
| **VPS** | Virtual Private Server — Sanal özel sunucu |
| **Cold Start** | Uyku modundan uyanma süresi |
| **Port** | Ağ iletişiminde servisin dinlediği numara (örn: 8501) |
| **SSH** | Secure Shell — Sunucuya güvenli uzaktan bağlantı |
| **Cron Job** | Zamanlanmış görev (her gün saat 09:00'da çalış gibi) |
| **CRUD** | Create, Read, Update, Delete — Temel veritabanı işlemleri |
| **API** | Application Programming Interface — Uygulamalar arası iletişim arayüzü |
| **REST API** | HTTP üzerinden çalışan API standardı (GET, POST, PUT, DELETE) |
| **WebSocket** | İki yönlü sürekli bağlantı (Streamlit bunu kullanır) |
| **Middleware** | İstek ve yanıt arasına giren ara katman |
| **ORM** | Object-Relational Mapping — Veritabanı işlemlerini nesne olarak yapma |
| **Migration** | Veritabanı şema değişikliklerini yönetme |
| **CORS** | Cross-Origin Resource Sharing — Farklı domainler arası erişim izni |
| **WHOIS** | Domain sahiplik bilgisi sorgulaması |
| **TTL** | Time To Live — DNS kaydının cache süresi |
| **DDNS** | Dynamic DNS — Değişen IP'yi sabit bir domain'e bağlama |
| **Port Forwarding** | Modemden gelen trafiği iç ağdaki cihaza yönlendirme |
| **NAT** | Network Address Translation — İç ve dış IP çevirisi |
| **Raspberry Pi** | Kredi kartı büyüklüğünde, ucuz, Linux çalıştıran mini bilgisayar |
| **ARM** | RPi ve telefonlarda kullanılan işlemci mimarisi (x86'dan farklı) |
| **UPS** | Kesintisiz Güç Kaynağı — Elektrik kesintisinde cihazı çalıştırır |
| **Cloudflare Tunnel** | Port açmadan, güvenli tünel ile siteyi internete açma |
| **fail2ban** | Brute-force saldırılarına karşı IP engelleyen güvenlik aracı |
| **UFW** | Uncomplicated Firewall — Kolay Linux güvenlik duvarı |

---

## 📌 NOTLAR

- Bu rehber **altins1_analiz** projesine özeldir ama kavramlar tüm web projeleri için geçerlidir
- Her aşamada sorun yaşarsan, o aşamada durup sorabiliriz
- En önemli prensip: **çalışan bir şeyi bozmadan, yeni şeyler eklemek**
- Mevcut Streamlit Cloud deploy'unu aktif bırakıp, VPS'te ayrı bir kopya çalıştırabilirsin
- Vercel + Supabase yolu çok değerli ama uzun vadeli bir hedef olarak düşün

---

> **Sonraki Adım:** Hangi aşamadan başlamak istediğine karar ver, birlikte adım adım yapalım.
