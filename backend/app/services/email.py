import logging
import os
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM_EMAIL", "noreply@arthemiz.com.br")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")


def _smtp_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def _send(to: str, subject: str, body: str) -> None:
    if not _smtp_configured():
        logger.info("[DEV] Email to=%s subject=%s\n%s", to, subject, body)
        return

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, to, msg.as_string())


def send_verification_email(to: str, token: str) -> None:
    link = f"{FRONTEND_URL}/verify-email?token={token}"
    body = f"""
    <h2>Verifique seu e-mail</h2>
    <p>Clique no link abaixo para verificar sua conta no PROMOVE:</p>
    <p><a href="{link}">{link}</a></p>
    <p>Se você não criou esta conta, ignore este e-mail.</p>
    """
    _send(to, "PROMOVE — Verificação de e-mail", body)


def send_password_reset_email(to: str, token: str) -> None:
    link = f"{FRONTEND_URL}/reset-password?token={token}"
    body = f"""
    <h2>Redefinir senha</h2>
    <p>Clique no link abaixo para redefinir sua senha no PROMOVE:</p>
    <p><a href="{link}">{link}</a></p>
    <p>Este link expira em 30 minutos.</p>
    <p>Se você não solicitou a redefinição, ignore este e-mail.</p>
    """
    _send(to, "PROMOVE — Redefinição de senha", body)
