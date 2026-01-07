import smtplib
from email.mime.text import MIMEText

class EmailService:
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> None:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'no-reply@example.com'
        msg['To'] = to

        with smtplib.SMTP('localhost') as server:
            server.sendmail('no-reply@example.com', [to], msg.as_string())