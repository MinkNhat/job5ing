import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    """
    Hàm gửi email cơ bản sử dụng SMTP.
    Cần cấu hình các biến môi trường: MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
    """
    mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(os.getenv("MAIL_PORT", 587))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_from_name = os.getenv("MAIL_FROM_NAME", "Job5ing Team")

    if not all([mail_username, mail_password]):
        print("Lỗi: Chưa cấu hình MAIL_USERNAME hoặc MAIL_PASSWORD trong .env")
        return False

    message = MIMEMultipart()
    message["From"] = f"{mail_from_name} <{mail_username}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")
        return False

def send_approval_email(user_email, company_name):
    subject = f"Thông báo: Công ty {company_name} đã được phê duyệt"
    body = f"""
    <html>
        <body>
            <h3>Chúc mừng!</h3>
            <p>Hồ sơ công ty <strong>{company_name}</strong> của bạn đã được quản trị viên Job5ing phê duyệt.</p>
            <p>Bây giờ bạn có thể đăng tin tuyển dụng và tìm kiếm ứng viên trên nền tảng của chúng tôi.</p>
            <br>
            <p>Trân trọng,<br>Đội ngũ Job5ing</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body)
