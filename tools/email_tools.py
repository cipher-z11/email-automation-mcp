# fix: implement SMTP send_email tool
# last_updated: 2026-05-07 09:56
"""
Core email tool implementations using IMAP/SMTP.
Supports Gmail, Outlook, and any standard email provider.
"""
import smtplib
import imaplib
import email
import os
import ssl
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Use App Password for Gmail


def _get_smtp_connection():
    context = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.ehlo()
    server.starttls(context=context)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    return server


def _get_imap_connection():
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    return mail


async def send_email(to: str, subject: str, body: str, cc: str = "") -> dict:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        if cc:
            msg["Cc"] = cc

        # Support both plain text and HTML
        if body.strip().startswith("<"):
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        recipients = [r.strip() for r in to.split(",")]
        if cc:
            recipients += [r.strip() for r in cc.split(",")]

        with _get_smtp_connection() as server:
            server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())

        return {
            "status": "success",
            "message": f"Email sent successfully to {to}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def send_email_with_attachment(
    to: str, subject: str, body: str, file_path: str, cc: str = ""
) -> dict:
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        if cc:
            msg["Cc"] = cc

        msg.attach(MIMEText(body, "plain"))

        # Attach file
        mime_type, _ = mimetypes.guess_type(file_path)
        main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)

        with open(file_path, "rb") as f:
            part = MIMEBase(main_type, sub_type)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

        recipients = [r.strip() for r in to.split(",")]
        if cc:
            recipients += [r.strip() for r in cc.split(",")]

        with _get_smtp_connection() as server:
            server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())

        return {
            "status": "success",
            "message": f"Email with attachment sent to {to}",
            "file": os.path.basename(file_path),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def list_emails(folder: str = "INBOX", limit: int = 10) -> list[dict]:
    try:
        mail = _get_imap_connection()
        mail.select(folder)
        _, msg_ids = mail.search(None, "ALL")
        ids = msg_ids[0].split()[-limit:]

        result = []
        for msg_id in reversed(ids):
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            result.append({
                "id": msg_id.decode(),
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "subject": msg.get("Subject", ""),
                "date": msg.get("Date", ""),
            })

        mail.logout()
        return result
    except Exception as e:
        return [{"error": str(e)}]


async def search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> list[dict]:
    try:
        mail = _get_imap_connection()
        mail.select(folder)

        # Build IMAP search criteria
        search_criteria = f'(TEXT "{query}")'
        _, msg_ids = mail.search(None, search_criteria)
        ids = msg_ids[0].split()[-limit:]

        result = []
        for msg_id in reversed(ids):
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            result.append({
                "id": msg_id.decode(),
                "from": msg.get("From", ""),
                "subject": msg.get("Subject", ""),
                "date": msg.get("Date", ""),
            })

        mail.logout()
        return result
    except Exception as e:
        return [{"error": str(e)}]


async def get_email_by_id(message_id: str) -> dict:
    try:
        mail = _get_imap_connection()
        mail.select("INBOX")
        _, msg_data = mail.fetch(message_id.encode(), "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

        mail.logout()
        return {
            "id": message_id,
            "from": msg.get("From", ""),
            "to": msg.get("To", ""),
            "subject": msg.get("Subject", ""),
            "date": msg.get("Date", ""),
            "body": body,
        }
    except Exception as e:
        return {"error": str(e)}


async def create_draft(to: str, subject: str, body: str) -> dict:
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))

        mail = _get_imap_connection()
        mail.append("[Gmail]/Drafts", "", imaplib.Time2Internaldate(datetime.now()), msg.as_bytes())
        mail.logout()

        return {"status": "success", "message": "Draft saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Implement SMTP send_email tool

# Final testing and documentation
