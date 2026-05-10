# Job5ing - Job Search & Recruitment Platform

Nền tảng kết nối ứng viên và nhà tuyển dụng với các tính năng thông minh hỗ trợ bởi AI. Dự án được xây dựng trên nền tảng Flask.

## Sản phẩm dùng để làm gì?

- **Đối với ứng viên:** Tìm kiếm việc làm, quản lý CV chuyên nghiệp, trích xuất thông tin CV tự động bằng Gemini AI và nhận gợi ý việc làm phù hợp hàng ngày qua Email.
- **Đối với nhà tuyển dụng:** Đăng tin tuyển dụng, quản lý công ty, phê duyệt thành viên và quản lý danh sách ứng viên ứng tuyển với hệ thống chấm điểm độ phù hợp AI.
- **Đối với Admin:** Quản lý tài khoản, phê duyệt yêu cầu tham gia công ty, quản lý bài đăng và xử lý báo cáo vi phạm.

## Các giao diện chính

- **Trang chủ:** `app/main/routes.py` (Tìm kiếm việc làm, Tin tuyển dụng nổi bật)
- **Đăng nhập/Đăng ký:** `/login`, `/register` (Hỗ trợ Google OAuth 2.0)
- **Hồ sơ ứng viên:** `/resume` (Quản lý thông tin cá nhân, kỹ năng, kinh nghiệm)
- **Quản lý CV:** `/resume-management` (Tạo CV, Upload và trích xuất thông tin bằng Gemini AI)
- **Chi tiết việc làm:** `/post/<int:post_id>` (Xem thông tin chi tiết và ứng tuyển)
- **Công việc đã ứng tuyển:** `/applied-jobs` (Theo dõi trạng thái hồ sơ)
- **Quản lý nhà tuyển dụng:** `/recruiter/` (Bảng điều khiển dành cho doanh nghiệp)
- **Quản lý ứng viên:** `/manage-candidates/<int:post_id>` (Chấm điểm AI và cập nhật trạng thái ứng tuyển)
- **Trang quản trị (Admin):** `/admin/` (Quản lý toàn bộ hệ thống)

## Công nghệ sử dụng

- **Backend:** Python 3.11.9, Flask
- **Database:** PostgreSQL (hoặc SQLite cho local development), SQLAlchemy ORM, Flask-Migrate
- **AI Integration:** Google Generative AI (Gemini 2.5-flash) để phân tích CV và tính điểm độ phù hợp
- **Media:** Cloudinary (Lưu trữ ảnh avatar, ảnh công ty và file CV)
- **Email:** SMTP Service (Gửi thông báo và gợi ý việc làm hàng ngày)
- **Authentication:** Flask-Session, Google OAuth 2.0

## Cài đặt & Chạy (local)

### 1. Yêu cầu hệ thống
- Python 3.11.9
- pip 24.0

### 2. Thiết lập môi trường
1. Tạo và kích hoạt môi trường ảo (venv):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Cài đặt các thư viện cần thiết:
   ```powershell
   pip install -r requirements.txt
   ```

3. Tạo cơ sở dữ liệu:
   - Tạo một database trống tên là `job5ing` trên PostgreSQL (hoặc cấu hình SQLite trong .env).

4. Cấu hình biến môi trường:
   - Tạo file `.env` tại thư mục gốc (cùng cấp với `.example.env`).
   - Sao chép nội dung từ `.example.env` sang `.env` và điền các giá trị tương ứng:
     ```env
     SECRET_KEY=your_secret_key
     SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/job5ing
     GEMINI_API_KEY=your_gemini_api_key
     CLOUDINARY_URL=your_cloudinary_url
     MAIL_USERNAME=your_email
     MAIL_PASSWORD=your_app_password
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     SERVER_NAME=localhost:5000
     PREFERRED_URL_SCHEME=http
     ```

### 3. Khởi tạo Database & Chạy dự án
1. Thực hiện migration:
   ```powershell
   flask db upgrade
   ```

2. (Tùy chọn) Seed dữ liệu mẫu:
   ```powershell
   python run_seed.py
   ```

3. Chạy server phát triển:
   ```powershell
   flask run
   # hoặc
   python run.py
   ```

4. Mở trình duyệt và truy cập: `http://localhost:5000`

## Ghi chú

- **Tính năng AI:** Cần có `GEMINI_API_KEY` hợp lệ để sử dụng tính năng trích xuất thông tin CV và tính điểm phù hợp.
- **Gửi Email hàng ngày:** Bạn có thể chạy script `python run_daily_recommendations.py` để gửi email gợi ý việc làm cho toàn bộ ứng viên.
- **Google Login:** Cần cấu hình `GOOGLE_REDIRECT_URI` trong Google Cloud Console trùng với URL của bạn.
