"""
ALTINS1 Analiz — E-posta Bildirim Modülü
Günlük sinyal özeti oluşturur ve SMTP ile birden fazla alıcıya gönderir.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from app.config import EmailConfig
from app.signal_engine import SignalType

logger = logging.getLogger(__name__)

# ── Sinyal renk haritası (HTML) ────────────────────────────────
_SIGNAL_COLORS: Dict[SignalType, str] = {
    SignalType.STRONG_BUY: "#00c853",
    SignalType.BUY: "#7cb342",
    SignalType.NEUTRAL: "#78909c",
    SignalType.SELL: "#ff9800",
    SignalType.STRONG_SELL: "#d50000",
}

_SIGNAL_EMOJI: Dict[SignalType, str] = {
    SignalType.STRONG_BUY: "🟢",
    SignalType.BUY: "🟡",
    SignalType.NEUTRAL: "⚪",
    SignalType.SELL: "🟠",
    SignalType.STRONG_SELL: "🔴",
}


def generate_daily_summary(
    signal_type: SignalType,
    signal_msg: str,
    prices: Dict[str, Optional[float]],
    thresholds_info: Dict[str, float],
) -> str:
    """Günlük sinyal özetini HTML formatında oluşturur.

    Args:
        signal_type: Güncel sinyal tipi
        signal_msg: Sinyal mesajı (generate_signal_message çıktısı)
        prices: Fiyat bilgileri dict'i {'altins1_fiyat', 'gram_altin_tl',
                'beklenen_altins1', 'makas_pct', 'ons_altin_usd', 'dolar_tl'}
        thresholds_info: Eşik bilgileri {'strong_buy', 'buy', 'sell', 'strong_sell', 'avg_spread'}

    Returns:
        HTML formatında e-posta gövdesi
    """
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    color = _SIGNAL_COLORS.get(signal_type, "#78909c")
    emoji = _SIGNAL_EMOJI.get(signal_type, "⚪")

    altins1 = prices.get("altins1_fiyat")
    gram_tl = prices.get("gram_altin_tl")
    beklenen = prices.get("beklenen_altins1")
    makas = prices.get("makas_pct")
    ons_usd = prices.get("ons_altin_usd")
    dolar = prices.get("dolar_tl")

    def _fmt(val: Optional[float], prefix: str = "₺", decimals: int = 2) -> str:
        if val is None:
            return "—"
        return f"{prefix}{val:,.{decimals}f}"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 12px; padding: 24px;">
        <h2 style="text-align: center; margin-top: 0;">🪙 ALTINS1 Günlük Sinyal Özeti</h2>
        <p style="text-align: center; color: #aaa; font-size: 13px;">{now}</p>

        <!-- Sinyal kutusu -->
        <div style="padding: 16px; border-radius: 10px; background: {color};
                    color: white; font-size: 18px; text-align: center; margin: 16px 0;">
            {emoji} {signal_type.value}
        </div>
        <p style="text-align: center; font-size: 14px; color: #ccc;">{signal_msg}</p>

        <!-- Fiyat tablosu -->
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr style="border-bottom: 1px solid #333;">
                <td style="padding: 8px; color: #aaa;">ALTINS1 (BIST)</td>
                <td style="padding: 8px; text-align: right; font-weight: bold;">{_fmt(altins1)}</td>
            </tr>
            <tr style="border-bottom: 1px solid #333;">
                <td style="padding: 8px; color: #aaa;">Beklenen ALTINS1</td>
                <td style="padding: 8px; text-align: right;">{_fmt(beklenen)}</td>
            </tr>
            <tr style="border-bottom: 1px solid #333;">
                <td style="padding: 8px; color: #aaa;">Makas</td>
                <td style="padding: 8px; text-align: right; font-weight: bold; color: {color};">
                    %{f'{makas:.1f}' if makas else '—'}
                </td>
            </tr>
            <tr style="border-bottom: 1px solid #333;">
                <td style="padding: 8px; color: #aaa;">Gram Altın TL</td>
                <td style="padding: 8px; text-align: right;">{_fmt(gram_tl)}</td>
            </tr>
            <tr style="border-bottom: 1px solid #333;">
                <td style="padding: 8px; color: #aaa;">Ons Altın USD</td>
                <td style="padding: 8px; text-align: right;">{_fmt(ons_usd, "$")}</td>
            </tr>
            <tr>
                <td style="padding: 8px; color: #aaa;">Dolar/TL</td>
                <td style="padding: 8px; text-align: right;">{_fmt(dolar)}</td>
            </tr>
        </table>

        <!-- Eşik bilgileri -->
        <div style="background: #0f3460; border-radius: 8px; padding: 12px; margin-top: 12px;">
            <p style="margin: 4px 0; font-size: 13px;">
                📊 Ort. Tarihsel Makas: <b>%{thresholds_info.get('avg_spread', 0):.1f}</b>
            </p>
            <p style="margin: 4px 0; font-size: 13px;">
                🟢 Güçlü Alım: ≤%{thresholds_info.get('strong_buy', 0):.1f} &nbsp;|&nbsp;
                🟡 Alım: ≤%{thresholds_info.get('buy', 0):.1f} &nbsp;|&nbsp;
                🟠 Satım: ≥%{thresholds_info.get('sell', 0):.1f} &nbsp;|&nbsp;
                🔴 Güçlü Satım: ≥%{thresholds_info.get('strong_sell', 0):.1f}
            </p>
        </div>

        <p style="text-align: center; color: #666; font-size: 11px; margin-top: 20px;">
            ALTINS1 Analiz | Yalnızca bilgi amaçlıdır, yatırım tavsiyesi değildir.
        </p>
    </div>
</body>
</html>"""
    return html


def send_email(
    email_config: EmailConfig,
    subject: str,
    html_body: str,
    recipients: Optional[List[str]] = None,
) -> bool:
    """SMTP ile HTML e-posta gönderir.

    Args:
        email_config: EmailConfig nesnesi (smtp bağlantı bilgileri)
        subject: E-posta konusu
        html_body: HTML formatında e-posta gövdesi
        recipients: Alıcı listesi (None ise config'den alınır)

    Returns:
        True ise başarılı, False ise hata oluştu
    """
    to_list = recipients or email_config.recipients
    if not to_list:
        logger.warning("E-posta alıcısı belirtilmedi.")
        return False

    if not email_config.sender_email or not email_config.sender_password:
        logger.warning("SMTP kimlik bilgileri eksik.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_config.sender_email
    msg["To"] = ", ".join(to_list)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email_config.sender_email, email_config.sender_password)
            server.sendmail(email_config.sender_email, to_list, msg.as_string())
        logger.info("E-posta başarıyla gönderildi: %s", ", ".join(to_list))
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP kimlik doğrulama hatası. Şifre veya uygulama parolasını kontrol edin.")
        return False
    except smtplib.SMTPException as exc:
        logger.error("SMTP hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Bağlantı hatası: %s", exc)
        return False


def send_daily_signal_email(
    email_config: EmailConfig,
    signal_type: SignalType,
    signal_msg: str,
    prices: Dict[str, Optional[float]],
    thresholds_info: Dict[str, float],
    recipients: Optional[List[str]] = None,
) -> bool:
    """Günlük sinyal özeti e-postası gönderir.

    Args:
        email_config: SMTP config
        signal_type: Güncel sinyal
        signal_msg: Sinyal mesajı
        prices: Fiyat dict'i
        thresholds_info: Eşik bilgileri
        recipients: Opsiyonel alıcı listesi

    Returns:
        Gönderim başarılı mı
    """
    today = datetime.now().strftime("%d.%m.%Y")
    subject = f"ALTINS1 Sinyal — {signal_type.value} ({today})"
    html = generate_daily_summary(signal_type, signal_msg, prices, thresholds_info)
    return send_email(email_config, subject, html, recipients)
