import os
import tempfile
import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Company, Recruiter
from app.main.services import (
    validate_email,
    validate_password_strength,
    validate_phone,
    validate_required_fields
)

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.db_path}",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "test-secret",
            }
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.seed_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def seed_data(self):
        # Tạo công ty mẫu
        company = Company(
            name="Công ty Cổ phần Job5ing",
            tax_code="123456789",
            business_license="test_license.pdf",
            scale="1-50 nhân viên"
        )
        db.session.add(company)

        # Tạo người dùng mẫu
        users = [
            User(
                email="active@example.com",
                password=generate_password_hash("Password123!"),
                is_active=True,
                first_name="Active",
                last_name="User",
                created_at=datetime.utcnow(),
            ),
            User(
                email="inactive@example.com",
                password=generate_password_hash("Password123!"),
                is_active=False,
                first_name="Inactive",
                last_name="User",
                created_at=datetime.utcnow(),
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

    # --- 1. UNIT TESTS CHO VALIDATION SERVICES (Đơn giản) ---

    def test_service_validate_email(self):
        self.assertTrue(validate_email("test@example.com")[0])
        self.assertFalse(validate_email("invalid-email")[0])

    def test_service_validate_password_strength(self):
        self.assertTrue(validate_password_strength("Strong123!")[0])
        self.assertFalse(validate_password_strength("weak")[0])

    def test_service_validate_phone(self):
        self.assertTrue(validate_phone("0912345678")[0])
        self.assertFalse(validate_phone("12345")[0])

    def test_service_validate_required_fields(self):
        form = {"email": "test@example.com", "password": ""}
        fields = [("email", "Email"), ("password", "Mật khẩu")]
        is_valid, msg = validate_required_fields(form, fields)
        self.assertFalse(is_valid)
        self.assertIn("Mật khẩu", msg)

    # --- 2. REGISTRATION TESTS (Tự động đăng nhập & Điều hướng vai trò) ---

    def test_register_success_candidate(self):
        """Đăng ký ứng viên thành công và tự động đăng nhập"""
        response = self.client.post(
            "/register",
            data={
                "email": "candidate@test.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "first_name": "New",
                "last_name": "Candidate",
            },
            follow_redirects=True,
        )
        self.assertIn("Đăng ký tài khoản thành công", response.get_data(as_text=True))
        
        # Kiểm tra tự động đăng nhập (session)
        with self.client.session_transaction() as sess:
            self.assertIn("user_id", sess)
            self.assertEqual(sess["user_role"], "candidate")

    def test_register_success_employer(self):
        """Đăng ký nhà tuyển dụng: tự động đăng nhập và redirect tới recruiter-request"""
        response = self.client.post(
            "/register",
            data={
                "email": "employer@test.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "is_employer": "on",
                "first_name": "New",
                "last_name": "Employer",
            },
            follow_redirects=True,
        )
        # Kiểm tra điều hướng tới trang xác nhận công ty
        self.assertIn("Xác nhận Công ty trực thuộc", response.get_data(as_text=True))
        
        with self.client.session_transaction() as sess:
            self.assertIn("user_id", sess)
            self.assertEqual(sess["user_role"], "employer")

    def test_register_duplicate_email(self):
        response = self.client.post(
            "/register",
            data={
                "email": "active@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=True,
        )
        self.assertIn("Email này đã tồn tại", response.get_data(as_text=True))

    # --- 3. LOGIN & LOGOUT TESTS ---

    def test_login_success(self):
        response = self.client.post(
            "/login",
            data={"email": "active@example.com", "password": "Password123!"},
            follow_redirects=True,
        )
        self.assertIn("Đăng nhập thành công", response.get_data(as_text=True))
        with self.client.session_transaction() as sess:
            self.assertIn("user_id", sess)

    def test_login_inactive_account(self):
        response = self.client.post(
            "/login",
            data={"email": "inactive@example.com", "password": "Password123!"},
            follow_redirects=True,
        )
        self.assertIn("Tài khoản của bạn đang bị khóa", response.get_data(as_text=True))

    def test_logout(self):
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        response = self.client.post("/logout", follow_redirects=True)
        self.assertIn("Bạn đã đăng xuất", response.get_data(as_text=True))
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)

    # --- 4. RECRUITER & COMPANY LOGIC TESTS (Phức tạp) ---

    def test_recruiter_request_access_denied_if_not_logged_in(self):
        """Truy cập recruiter-request khi chưa đăng nhập phải bị redirect"""
        response = self.client.get("/recruiter-request", follow_redirects=True)
        self.assertIn("Vui lòng đăng nhập để tiếp tục", response.get_data(as_text=True))

    def test_submit_join_request_success(self):
        """Gửi yêu cầu gia nhập công ty hiện có thành công"""
        # Đăng nhập trước
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        
        with self.app.app_context():
            company = Company.query.first()
            company_id = company.id

        response = self.client.post(
            "/submit-join-request",
            data={
                "company_id": company_id,
                "position": "Trưởng phòng nhân sự"
            },
            follow_redirects=True
        )
        self.assertIn("Yêu cầu gia nhập công ty đã được gửi", response.get_data(as_text=True))
        
        with self.app.app_context():
            user = User.query.filter_by(email="active@example.com").first()
            recruiter = Recruiter.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(recruiter)
            self.assertEqual(recruiter.company_id, company_id)
            self.assertFalse(recruiter.is_approved)
            self.assertFalse(recruiter.is_company_admin)
            self.assertTrue(user.is_employer)

    def test_register_company_success(self):
        """Đăng ký công ty mới thành công, tạo đồng thời recruiter admin"""
        # Đăng nhập trước
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        
        response = self.client.post(
            "/register-company",
            data={
                "name": "Công ty Công nghệ Mới",
                "taxCode": "987654321",
                "position": "Giám đốc điều hành",
                "location": "Hà Nội",
                "scale": "51-200 nhân viên"
            },
            follow_redirects=True
        )
        self.assertIn("Đăng ký công ty thành công", response.get_data(as_text=True))
        
        with self.app.app_context():
            company = Company.query.filter_by(tax_code="987654321").first()
            self.assertIsNotNone(company)
            self.assertEqual(company.scale, "51-200 nhân viên")
            self.assertFalse(company.is_approved) # Chờ admin phê duyệt
            
            user = User.query.filter_by(email="active@example.com").first()
            recruiter = Recruiter.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(recruiter)
            self.assertEqual(recruiter.company_id, company.id)
            self.assertTrue(recruiter.is_company_admin) # Người tạo cty là admin
            self.assertTrue(recruiter.is_approved) # Được phê duyệt recruiter ngay
            self.assertTrue(user.is_employer)

if __name__ == "__main__":
    unittest.main()
