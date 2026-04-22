import os
import tempfile
import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User
from app.main.services import (
    validate_email,
    validate_password_strength,
    validate_phone,
    validate_required_fields,
    create_account,
    login_with_password
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
            self.seed_users()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        os.close(self.db_fd)
        os.unlink(self.db_path)

    def seed_users(self):
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

    # --- UNIT TESTS FOR SERVICES ---

    def test_service_validate_email(self):
        self.assertTrue(validate_email("test@example.com")[0])
        self.assertFalse(validate_email("invalid-email")[0])
        self.assertFalse(validate_email("test@domain")[0])

    def test_service_validate_password_strength(self):
        # Yêu cầu: 8+ ký tự, hoa, thường, số, đặc biệt
        self.assertTrue(validate_password_strength("Strong123!")[0])
        self.assertFalse(validate_password_strength("weak")[0])
        self.assertFalse(validate_password_strength("NoSpecial123")[0])
        self.assertFalse(validate_password_strength("noshowcase123!")[0])

    def test_service_validate_phone(self):
        self.assertTrue(validate_phone("0912345678")[0])
        self.assertTrue(validate_phone("+84912345678")[0])
        self.assertFalse(validate_phone("12345")[0])

    def test_service_validate_required_fields(self):
        form = {"email": "test@example.com", "password": ""}
        fields = [("email", "Email"), ("password", "Mật khẩu")]
        is_valid, msg = validate_required_fields(form, fields)
        self.assertFalse(is_valid)
        self.assertIn("Mật khẩu", msg)

    # --- INTEGRATION TESTS FOR ROUTES ---

    def test_register_success_candidate(self):
        response = self.client.post(
            "/register",
            data={
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "first_name": "New",
                "last_name": "User",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đăng ký tài khoản thành công", response.get_data(as_text=True))
        
        with self.app.app_context():
            user = User.query.filter_by(email="new@example.com").first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_employer)

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

    def test_register_password_mismatch(self):
        response = self.client.post(
            "/register",
            data={
                "email": "mismatch@example.com",
                "password": "Password123!",
                "confirm_password": "WrongPassword",
            },
            follow_redirects=True,
        )
        self.assertIn("Mật khẩu xác nhận không khớp", response.get_data(as_text=True))

    def test_login_success(self):
        response = self.client.post(
            "/login",
            data={
                "email": "active@example.com",
                "password": "Password123!",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đăng nhập thành công", response.get_data(as_text=True))
        
        with self.client.session_transaction() as sess:
            self.assertIn("user_id", sess)

    def test_login_invalid_password(self):
        response = self.client.post(
            "/login",
            data={
                "email": "active@example.com",
                "password": "WrongPassword",
            },
            follow_redirects=True,
        )
        self.assertIn("Email hoặc mật khẩu không chính xác", response.get_data(as_text=True))

    def test_login_inactive_account(self):
        response = self.client.post(
            "/login",
            data={
                "email": "inactive@example.com",
                "password": "Password123!",
            },
            follow_redirects=True,
        )
        self.assertIn("Tài khoản của bạn đang bị khóa", response.get_data(as_text=True))

    def test_logout(self):
        # Login
        self.client.post(
            "/login",
            data={"email": "active@example.com", "password": "Password123!"}
        )
        # Logout
        response = self.client.post("/logout", follow_redirects=True)
        self.assertIn("Bạn đã đăng xuất", response.get_data(as_text=True))
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)

if __name__ == "__main__":
    unittest.main()
