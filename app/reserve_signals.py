"""
ALTINS1 Analiz — Merkez Bankası Altın Rezerv Sinyal Analizi

Merkez bankalarının altın alım/satım hareketlerinden
altın fiyat yönü için sinyaller üretir.

Yöntemler:
1. Net Alım Trendi (Momentum) — Son çeyreklerdeki toplam değişim
2. Alıcı Sayısı Oranı — Alım yapan MB sayısı / Toplam MB sayısı
3. Ağırlıklı Alım Endeksi — Büyük MB'lerin alımlarına ağırlık veren endeks
4. Momentum Hızlanması — Net alımdaki ivmelenme (ikinci türev)
5. Çin Öncü Göstergesi — PBoC alımı tek başına öncü sinyal
6. Alım Konsantrasyonu (HHI) — Alımın kaç ülkeye dağıldığı
7. Altın Payı Trendi — Altın/toplam rezerv oranı değişimi
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ReserveSignal:
    """Tek bir sinyal sonucu."""

    name: str  # Sinyal adı
    value: float  # Sinyal değeri (-100 ile +100 arası normalize)
    label: str  # İnsan okunur etiket ("Güçlü Alım", "Nötr" vb.)
    emoji: str  # 🟢🟡🔴
    detail: str  # Açıklama metni


def _classify_signal(value: float) -> Tuple[str, str]:
    """Sinyal değerini etiket ve emojiye çevirir."""
    if value >= 60:
        return "Güçlü Alım Sinyali", "🟢"
    elif value >= 25:
        return "Alım Eğilimi", "🟢"
    elif value >= -25:
        return "Nötr", "🟡"
    elif value >= -60:
        return "Satış Eğilimi", "🔴"
    else:
        return "Güçlü Satış Sinyali", "🔴"


def compute_net_change_momentum(
    df: pd.DataFrame,
    quarters: int = 4,
) -> Optional[ReserveSignal]:
    """Net Alım Momentum Sinyali.

    Son N çeyrekteki toplam tonaj değişimini hesaplar.
    Tüm takip edilen ülkelerin toplamını kullanır.

    Pozitif = MB'ler net alıcı → altın için yükseliş sinyali
    Negatif = MB'ler net satıcı → altın için düşüş sinyali
    """
    if df is None or len(df) < 2:
        return None

    # Son N çeyreğe denk gelen satır sayısı
    n_rows = min(quarters + 1, len(df))
    recent = df.iloc[-n_rows:]

    # Her ülke için toplam değişim (son - ilk)
    changes = recent.iloc[-1] - recent.iloc[0]
    total_change = changes.sum()

    # Normalize: ±500 ton = ±100 puan (tarihsel büyük hareket referansı)
    normalized = max(min(total_change / 5.0, 100), -100)

    label, emoji = _classify_signal(normalized)

    # Detay: en çok alan ve satan ülkeler
    top_buyers = changes.nlargest(3)
    top_sellers = changes.nsmallest(3)

    detail_parts = [f"Son {quarters} çeyrekte toplam net değişim: {total_change:+.1f} ton"]
    buyer_parts = []
    for country, change in top_buyers.items():
        if change > 0:
            buyer_parts.append(f"{country} (+{change:.1f}t)")
    if buyer_parts:
        detail_parts.append("En çok alan: " + ", ".join(buyer_parts))

    seller_parts = []
    for country, change in top_sellers.items():
        if change < 0:
            seller_parts.append(f"{country} ({change:.1f}t)")
    if seller_parts:
        detail_parts.append("En çok satan: " + ", ".join(seller_parts))

    return ReserveSignal(
        name="Net Alım Momentum",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=" | ".join(detail_parts),
    )


def compute_buyer_ratio(df: pd.DataFrame) -> Optional[ReserveSignal]:
    """Alıcı Sayısı Oranı Sinyali.

    Son anlamlı değişim periyodundaki altın stoğunu artıran MB sayısı /
    toplam takip edilen MB sayısı.

    Gerçek değişim görmek için en az 30 gün arayla iki noktayı karşılaştırır.

    Oran > %60 → güçlü alım sinyali
    Oran < %30 → satış sinyali
    """
    if df is None or len(df) < 2:
        return None

    # Son veri noktası
    last = df.iloc[-1]

    # En az 30 gün önceki son veri noktasını bul
    last_date = df.index[-1]
    prev = None
    for i in range(len(df) - 2, -1, -1):
        if (last_date - df.index[i]).days >= 30:
            prev = df.iloc[i]
            break

    if prev is None:
        # 30 gün önceki veri yoksa ilk veriyi al
        prev = df.iloc[0]
        if (last_date - df.index[0]).days < 7:
            return None  # Yeterli süre geçmemiş

    changes = last - prev
    total_countries = len(changes.dropna())
    if total_countries == 0:
        return None

    buyers = (changes > 0.1).sum()  # 0.1 ton eşiği (yuvarlama hatalarını yoksay)
    sellers = (changes < -0.1).sum()
    unchanged = total_countries - buyers - sellers

    ratio = buyers / total_countries * 100

    # Normalize: %50 = nötr (0 puan), %100 = +100, %0 = -100
    normalized = (ratio - 50) * 2

    label, emoji = _classify_signal(normalized)

    detail = (
        f"Alıcı: {buyers} | Satıcı: {sellers} | Değişimsiz: {unchanged} "
        f"(Toplam {total_countries} MB) → Alıcı oranı: %{ratio:.0f}"
    )

    return ReserveSignal(
        name="Alıcı/Satıcı Oranı",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


def compute_weighted_demand_index(df: pd.DataFrame) -> Optional[ReserveSignal]:
    """Ağırlıklı Talep Endeksi.

    Büyük merkez bankalarının (Çin, Hindistan, Polonya, Türkiye, Rusya)
    son hareketlerine daha fazla ağırlık verir, çünkü bu ülkeler
    son yıllarda piyasayı yönlendiren aktif alıcılardır.

    Ağırlıklar:
    - Çin: 3x (en büyük aktif alıcı)
    - Hindistan: 2x
    - Polonya: 2x
    - Türkiye: 2x
    - Rusya: 1.5x
    - Diğer: 1x
    """
    if df is None or len(df) < 2:
        return None

    WEIGHTS = {
        "Çin": 3.0,
        "Hindistan": 2.0,
        "Polonya": 2.0,
        "Türkiye": 2.0,
        "Rusya": 1.5,
    }

    # En az 30 gün arayla iki noktayı karşılaştır
    last_date = df.index[-1]
    prev_idx = 0
    for i in range(len(df) - 2, -1, -1):
        if (last_date - df.index[i]).days >= 30:
            prev_idx = i
            break

    if prev_idx == len(df) - 1:
        prev_idx = 0
        if (last_date - df.index[0]).days < 7:
            return None

    changes = df.iloc[-1] - df.iloc[prev_idx]

    weighted_sum = 0.0
    total_weight = 0.0
    detail_parts = []

    for country in df.columns:
        change = changes.get(country)
        if pd.isna(change):
            continue
        w = WEIGHTS.get(country, 1.0)
        weighted_sum += change * w
        total_weight += abs(change) * w if abs(change) > 0.1 else w * 0.1

        if abs(change) > 0.1:
            sign = "+" if change > 0 else ""
            detail_parts.append(f"{country}({sign}{change:.1f}t, x{w})")

    if total_weight == 0:
        return None

    # Normalize: ağırlıklı net değişim / referans
    normalized = max(min(weighted_sum / 3.0, 100), -100)

    label, emoji = _classify_signal(normalized)

    detail = "Ağırlıklı hareketler: " + (", ".join(detail_parts) if detail_parts else "değişim yok")

    return ReserveSignal(
        name="Ağırlıklı Talep Endeksi",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


# ── A) Momentum Hızlanması (Acceleration) ──────────────────────


def compute_momentum_acceleration(
    df: pd.DataFrame,
    window: int = 4,
) -> Optional[ReserveSignal]:
    """Momentum Hızlanması — Net alımın ivmelendiğini/yavaşladığını ölçer.

    Son N çeyrekteki net değişim ile ondan önceki N çeyrekteki net değişimi
    karşılaştırır. Fark pozitifse alımlar hızlanıyor, negatifse yavaşlıyor.

    Bu, 'değişimin değişimi' (ikinci türev) olduğu için pivot noktalarını
    mevcut momentum sinyalinden daha ERKEN yakalar.
    """
    # En az 2*window+1 veri noktası gerekli (ör: window=4 → 9 nokta)
    min_rows = 2 * window + 1
    if df is None or len(df) < min_rows:
        return None

    # Toplam tonaj serisi (tüm ülkelerin toplamı)
    totals = df.sum(axis=1)

    # Son periyot net değişimi
    recent_change = totals.iloc[-1] - totals.iloc[-(window + 1)]
    # Önceki periyot net değişimi
    prior_change = totals.iloc[-(window + 1)] - totals.iloc[-(2 * window + 1)]

    acceleration = recent_change - prior_change

    # Normalize: ±200 ton ivme = ±100 puan
    normalized = max(min(acceleration / 2.0, 100), -100)
    label, emoji = _classify_signal(normalized)

    if acceleration > 0:
        trend_word = "hızlanıyor 📈"
    elif acceleration < -5:
        trend_word = "yavaşlıyor 📉"
    else:
        trend_word = "sabit ↔️"

    detail = (
        f"Son {window}Ç net: {recent_change:+.0f}t | "
        f"Önceki {window}Ç net: {prior_change:+.0f}t | "
        f"İvme: {acceleration:+.0f}t → Alım {trend_word}"
    )

    return ReserveSignal(
        name="Alım İvmesi",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


# ── C) Çin Öncü Göstergesi ─────────────────────────────────────


def compute_china_leading_indicator(
    df: pd.DataFrame,
    quarters: int = 4,
) -> Optional[ReserveSignal]:
    """Çin (PBoC) Öncü Göstergesi.

    PBoC 2023'ten bu yana küresel altın talebinin en büyük sürücüsü.
    Çin'in tek başına alım/satım yönü, genel fiyat trendini 1-2 çeyrek
    önceden işaret etme eğiliminde.

    Sadece Çin verisine odaklanarak basit ama etkili bir öncü sinyal üretir.
    """
    if df is None or "Çin" not in df.columns or len(df) < 2:
        return None

    china = df["Çin"].dropna()
    if len(china) < 2:
        return None

    n_rows = min(quarters + 1, len(china))
    recent_china = china.iloc[-n_rows:]
    change = recent_china.iloc[-1] - recent_china.iloc[0]

    # Ayrıca son 1 çeyrekteki hız
    if len(china) >= 2:
        last_q_change = china.iloc[-1] - china.iloc[-2]
    else:
        last_q_change = change

    # Normalize: ±100 ton Çin alımı = ±100 puan
    normalized = max(min(change / 1.0, 100), -100)
    label, emoji = _classify_signal(normalized)

    # Yön değerlendirmesi
    if change > 5 and last_q_change > 0:
        direction = "Çin aktif alıcı — altın talebi güçlü"
    elif change > 5 and last_q_change <= 0:
        direction = "Çin alımları duraklıyor — dikkat"
    elif change < -5:
        direction = "Çin net satıcı — talep baskısı azalıyor"
    else:
        direction = "Çin nötr, belirgin hareket yok"

    detail = (
        f"PBoC son {quarters}Ç: {change:+.1f}t | "
        f"Son çeyrek: {last_q_change:+.1f}t | "
        f"{direction}"
    )

    return ReserveSignal(
        name="Çin Öncü Göstergesi",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


# ── D) Alım Konsantrasyonu (HHI) ───────────────────────────────


def compute_buying_concentration(
    df: pd.DataFrame,
    quarters: int = 4,
) -> Optional[ReserveSignal]:
    """Alım Konsantrasyonu — Herfindahl-Hirschman benzeri endeks.

    Alımın kaç ülkeye dağıldığını ölçer:
    - Geniş tabanlı alım (çok ülke alıyor) = sürdürülebilir talep → güçlü sinyal
    - Konsantre alım (1-2 ülke) = kırılgan talep → zayıf sinyal

    HHI düşükse ve toplam alım pozitifse → en güçlü alım sinyali
    HHI yüksekse → tek ülkeye bağımlı, dikkatli olunmalı
    """
    if df is None or len(df) < 2:
        return None

    n_rows = min(quarters + 1, len(df))
    changes = df.iloc[-1] - df.iloc[-n_rows]

    # Sadece alıcıları hesapla (>0.1 ton eşiği)
    buyers = changes[changes > 0.1]
    total_buying = buyers.sum()

    if total_buying <= 0:
        # Net alım yok → sinyal negatif
        seller_count = (changes < -0.1).sum()
        return ReserveSignal(
            name="Alım Dağılımı",
            value=-50.0,
            label="Satış Eğilimi",
            emoji="🔴",
            detail=f"Son {quarters} çeyrekte net alıcı yok, {seller_count} satıcı",
        )

    buyer_count = len(buyers)
    # Her alıcının payını hesapla ve HHI hesapla
    shares = (buyers / total_buying * 100)
    hhi = (shares ** 2).sum()  # Max: 10000 (tek alıcı), Min ≈ 10000/N

    # Normalize: HHI < 1500 → çok dağınık (iyi), HHI > 5000 → çok konsantre (riskli)
    # Düşük HHI + pozitif toplam = güçlü sinyal
    if hhi < 1500:
        concentration_score = 80  # Geniş tabanlı
    elif hhi < 2500:
        concentration_score = 50  # Orta dağılım
    elif hhi < 5000:
        concentration_score = 20  # Konsantre
    else:
        concentration_score = -20  # Çok konsantre

    # Toplam alım büyüklüğüne göre ayarla
    size_multiplier = min(total_buying / 200.0, 1.5)  # 200+ ton = 1.5x
    normalized = max(min(concentration_score * size_multiplier, 100), -100)
    label, emoji = _classify_signal(normalized)

    # En büyük alıcılar
    top = buyers.nlargest(3)
    top_parts = [f"{c} ({v:+.0f}t, %{s:.0f})" for c, v, s in zip(top.index, top.values, shares[top.index])]

    detail = (
        f"Alıcı: {buyer_count} ülke, toplam {total_buying:+.0f}t | "
        f"HHI: {hhi:.0f} ({'dağınık' if hhi < 2500 else 'konsantre'}) | "
        f"Büyük alıcılar: {', '.join(top_parts)}"
    )

    return ReserveSignal(
        name="Alım Dağılımı",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


# ── E) Altın Payı Trendi ───────────────────────────────────────


def compute_gold_share_trend(
    reserves_data: list,
) -> Optional[ReserveSignal]:
    """Altın / Toplam Döviz Rezervi Payı Trendi.

    Ülkelerin altın paylarının ağırlıklı ortalamasına bakar.
    Bu pay artıyorsa → yapısal de-dolarizasyon → uzun vadeli altın talebi güçlü.

    Not: Bu sinyal güncel snapshot verisine dayanır (Wikipedia).
    Tarihsel karşılaştırma için sonraki sürümlerde geçmiş paylar eklenecek.
    Şimdilik sadece mevcut durumun değerlendirmesini yapar.
    """
    if not reserves_data:
        return None

    # Önemli ülkelerin altın paylarını değerlendir
    KEY_COUNTRIES = {
        "Rusya", "Çin", "Hindistan", "Polonya", "Türkiye",
        "Macaristan", "Singapur", "Tayland", "Çek Cumhuriyeti",
    }

    total_weight = 0.0
    weighted_pct = 0.0
    details = []

    for r in reserves_data:
        if r.country_tr in KEY_COUNTRIES and r.pct_of_reserves:
            w = 2.0 if r.country_tr in ("Çin", "Rusya", "Hindistan") else 1.0
            weighted_pct += r.pct_of_reserves * w
            total_weight += w
            details.append(f"{r.country_tr} %{r.pct_of_reserves:.0f}")

    if total_weight == 0:
        return None

    avg_pct = weighted_pct / total_weight

    # Referans: gelişmekte olan ülkelerin tarihsel altın payı
    # 2018: ortalama ~%5, 2025: ortalama ~%10-15
    # %15+ → güçlü yapısal talep, %5-10 → büyüme alanı var, <%5 → düşük
    if avg_pct >= 20:
        normalized = 70  # Çok yüksek pay → yapısal talep güçlü
    elif avg_pct >= 12:
        normalized = 50  # Yükseliş trendi devam
    elif avg_pct >= 7:
        normalized = 25  # Büyüme alanı var
    else:
        normalized = 0  # Henüz erken aşama

    label, emoji = _classify_signal(normalized)

    detail = (
        f"Kilit ülkelerin ağırlıklı altın payı: %{avg_pct:.1f} | "
        f"Katılımcılar: {', '.join(details[:6])}"
    )

    return ReserveSignal(
        name="Altın Payı Değerlendirmesi",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


# ── B) MB Alım vs Altın Fiyat Korelasyonu ──────────────────────


def compute_price_correlation(
    df: pd.DataFrame,
    gold_prices_quarterly: Optional[pd.Series] = None,
) -> Optional[ReserveSignal]:
    """MB toplam net alımı ile aynı dönem altın fiyat değişimi arasındaki korelasyon.

    gold_prices_quarterly: Tarih indeksli, çeyreklik ortalama ons altın USD fiyatı.
    Eğer None verilirse sinyal üretilemez.
    """
    if df is None or len(df) < 6 or gold_prices_quarterly is None:
        return None

    # Toplam tonaj serisi
    totals = df.sum(axis=1)
    # Çeyreklik değişimler
    reserve_changes = totals.diff().dropna()

    # Altın fiyatındaki çeyreklik değişimler
    price_changes = gold_prices_quarterly.pct_change().dropna() * 100

    # Ortak tarihleri bul (en yakın çeyreğe yuvarla)
    reserve_q = reserve_changes.copy()
    reserve_q.index = reserve_q.index.to_period("Q").to_timestamp()
    price_q = price_changes.copy()
    price_q.index = price_q.index.to_period("Q").to_timestamp()

    common = reserve_q.index.intersection(price_q.index)
    if len(common) < 4:
        return None

    r_vals = reserve_q.loc[common]
    p_vals = price_q.loc[common]

    corr = r_vals.corr(p_vals)
    if pd.isna(corr):
        return None

    # Normalize: korelasyon -1..+1 → -100..+100
    normalized = corr * 100
    label, emoji = _classify_signal(normalized)

    detail = (
        f"Korelasyon: {corr:.2f} ({len(common)} çeyrek) | "
        f"{'MB alımları fiyatla aynı yönde' if corr > 0.3 else 'Zayıf/ters ilişki' if corr < -0.3 else 'Belirsiz ilişki'}"
    )

    return ReserveSignal(
        name="Fiyat Korelasyonu",
        value=round(normalized, 1),
        label=label,
        emoji=emoji,
        detail=detail,
    )


def compute_all_signals(
    df: pd.DataFrame,
    reserves_data: Optional[list] = None,
    gold_prices_quarterly: Optional[pd.Series] = None,
) -> List[ReserveSignal]:
    """Tüm sinyal türlerini hesapla ve döndür."""
    signals = []

    s = compute_net_change_momentum(df)
    if s:
        signals.append(s)

    s = compute_momentum_acceleration(df)
    if s:
        signals.append(s)

    s = compute_buyer_ratio(df)
    if s:
        signals.append(s)

    s = compute_weighted_demand_index(df)
    if s:
        signals.append(s)

    s = compute_china_leading_indicator(df)
    if s:
        signals.append(s)

    s = compute_buying_concentration(df)
    if s:
        signals.append(s)

    if reserves_data:
        s = compute_gold_share_trend(reserves_data)
        if s:
            signals.append(s)

    if gold_prices_quarterly is not None:
        s = compute_price_correlation(df, gold_prices_quarterly)
        if s:
            signals.append(s)

    return signals


def compute_composite_signal(signals: List[ReserveSignal]) -> Optional[ReserveSignal]:
    """Tüm sinyallerin ortalamasını alarak bileşik sinyal üretir."""
    if not signals:
        return None

    avg = sum(s.value for s in signals) / len(signals)
    label, emoji = _classify_signal(avg)

    details = [f"{s.name}: {s.value:+.0f}" for s in signals]

    return ReserveSignal(
        name="Bileşik MB Sinyali",
        value=round(avg, 1),
        label=label,
        emoji=emoji,
        detail=" | ".join(details),
    )
