import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from config import SMTP_CONFIG


class EmailSender:
    def __init__(self, config=None):
        self.config = config or SMTP_CONFIG

    def send(self, to_email, subject, body, attachments=None):
        if not self.config["user"] or not self.config["password"]:
            raise ValueError("Email SMTP nao configurado. Configure SMTP_USER e SMTP_PASSWORD no .env")

        msg = MIMEMultipart()
        msg["From"] = self.config["user"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html", "utf-8"))

        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if path.exists():
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{path.name}"',
                    )
                    msg.attach(part)

        with smtplib.SMTP(self.config["host"], self.config["port"]) as server:
            server.starttls()
            server.login(self.config["user"], self.config["password"])
            server.send_message(msg)
        return True

    def is_configured(self):
        return bool(self.config["user"] and self.config["password"])


email_sender = EmailSender()
