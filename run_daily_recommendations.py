from app import create_app
from app.main.services import send_daily_job_recommendations
import sys

def run():
    app = create_app()
    # Cấu hình SERVER_NAME để url_for có thể tạo URL tuyệt đối ngoài request context
    # Nếu chạy local dùng localhost:5000, nếu lên server hãy dùng domain thật
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    with app.app_context():
        print("🚀 Bắt đầu gửi gợi ý việc làm hàng ngày...")
        try:
            send_daily_job_recommendations()
            print("✅ Hoàn thành gửi gợi ý việc làm.")
        except Exception as e:
            print(f"❌ Lỗi khi gửi gợi ý: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run()
