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
    validate_required_fields,
    validate_tax_code
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
            tax_code="1234567890",
            business_license="test_license.pdf",
            scale_id=1
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

    # --- 1. VALIDATION TESTS ---

    def test_service_validate_tax_code(self):
        # Hợp lệ (10 hoặc 13 số)
        self.assertTrue(validate_tax_code("0100109106")[0])
        self.assertTrue(validate_tax_code("0100109106-001")[0])
        self.assertTrue(validate_tax_code("0100109106001")[0])
        # Không hợp lệ
        self.assertFalse(validate_tax_code("12345")[0])
        self.assertFalse(validate_tax_code("123456789012")[0])
        self.assertFalse(validate_tax_code("abc1234567")[0])

    def test_service_validate_email(self):
        self.assertTrue(validate_email("test@example.com")[0])
        self.assertFalse(validate_email("invalid-email")[0])

    # --- 2. REGISTRATION TESTS ---

    def test_register_success_candidate(self):
        """Đăng ký ứng viên thành công"""
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
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["user_role"], "candidate")

    def test_register_employer_initial_state(self):
        """Đăng ký tích chọn nhà tuyển dụng: ban đầu vẫn là candidate cho đến khi xác nhận cty"""
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
        # Bị đẩy sang trang recruiter-request
        self.assertIn("Xác nhận Công ty trực thuộc", response.get_data(as_text=True))
        
        with self.client.session_transaction() as sess:
            # Vẫn là candidate vì chưa xác nhận công ty
            self.assertEqual(sess["user_role"], "candidate")

    # --- 3. RECRUITER & COMPANY LOGIC TESTS ---

    def test_submit_join_request_updates_role(self):
        """Gửi yêu cầu gia nhập công ty -> Trở thành employer ngay"""
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        
        with self.app.app_context():
            company_id = Company.query.first().id

        response = self.client.post(
            "/submit-join-request",
            data={"company_id": company_id, "position": "HR"},
            follow_redirects=True
        )
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["user_role"], "employer")
        
        with self.app.app_context():
            user = User.query.filter_by(email="active@example.com").first()
            self.assertTrue(user.is_employer)

    def test_register_company_updates_role(self):
        """Đăng ký công ty mới -> Trở thành employer ngay"""
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        
        response = self.client.post(
            "/register-company",
            data={
                "name": "New Tech Corp",
                "taxCode": "0100109106", # MST hợp lệ (10 số)
                "position": "CEO",
                "city": "Hà Nội",
                "address": "123 Láng",
                "scale": "1-50 nhân viên"
            },
            follow_redirects=True
        )
        self.assertIn("Yêu cầu của bạn đã được gửi đi", response.get_data(as_text=True))
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["user_role"], "employer")

    def test_register_company_duplicate_tax_code(self):
        """Không cho phép trùng mã số thuế"""
        self.client.post("/login", data={"email": "active@example.com", "password": "Password123!"})
        
        response = self.client.post(
            "/register-company",
            data={
                "name": "Another Corp",
                "taxCode": "1234567890", # Trùng MST trong seed_data
                "city": "Hà Nội",
                "scale": "1-50 nhân viên"
            },
            follow_redirects=True
        )
        self.assertIn("Mã số thuế này đã được đăng ký", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
