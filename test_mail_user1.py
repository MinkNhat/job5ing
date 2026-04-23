from app import create_app, db
from app.models import User, Company
from services.smtp_service import send_email, send_approval_email

app = create_app()

def test_send_to_user_1():
    with app.app_context():
        # 1. Tìm User có ID = 1
        user = db.session.get(User, 1)
        
        if not user:
            print("Lỗi: Không tìm thấy User có ID = 1 trong database.")
            return

        if not user.email:
            print(f"Lỗi: User {user.id} không có địa chỉ email.")
            return

        print(f"Đang chuẩn bị gửi mail thử tới: {user.email} (Tên: {user.first_name} {user.last_name})")

        # 2. Thử gửi một email nội dung bất kỳ
        subject = "Kiểm tra hệ thống gửi mail Job5ing"
        body = f"Chào {user.first_name}, đây là email kiểm tra từ hệ thống quản trị."
        
        success = send_email(user.email, subject, body)
        
        if success:
            print("--- KẾT QUẢ: Gửi email kiểm tra THÀNH CÔNG! ---")
        else:
            print("--- KẾT QUẢ: Gửi email THẤT BẠI. Vui lòng kiểm tra cấu hình .env và log lỗi. ---")

        # 3. Thử gửi email theo mẫu phê duyệt công ty (nếu user là recruiter)
        if user.is_employer:
            print("\nĐang thử gửi mail mẫu phê duyệt doanh nghiệp...")
            company_name = "Công ty TNHH Thử Nghiệm"
            if user.recruiter_profile and user.recruiter_profile.company:
                company_name = user.recruiter_profile.company.name
            
            success_appr = send_approval_email(user.email, company_name)
            if success_appr:
                print("--- KẾT QUẢ: Gửi mail phê duyệt THÀNH CÔNG! ---")
            else:
                print("--- KẾT QUẢ: Gửi mail phê duyệt THẤT BẠI. ---")

if __name__ == "__main__":
    test_send_to_user_1()
