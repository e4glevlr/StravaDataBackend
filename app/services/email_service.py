# app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


async def send_verification_email(to_email: str, verification_code: str):
    """Gửi email xác nhận đến người dùng"""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Xác nhận tài khoản Strava Integration"
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email

    # Tạo nội dung email
    text = f"""
    Cảm ơn bạn đã đăng ký tài khoản!
    Mã xác nhận của bạn là: {verification_code}
    Vui lòng sử dụng mã này để xác nhận tài khoản của bạn.
    """

    html = f"""
    <html>
    <body>
        <h2>Cảm ơn bạn đã đăng ký tài khoản!</h2>
        <p>Mã xác nhận của bạn là: <strong>{verification_code}</strong></p>
        <p>Vui lòng sử dụng mã này để xác nhận tài khoản của bạn.</p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Gửi email
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())