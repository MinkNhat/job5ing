import os
import tempfile
import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


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

    # --- Test Registration ---

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

    def test_register_success_employer(self):
        response = self.client.post(
            "/register",
            data={
                "email": "employer@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "first_name": "Employer",
                "last_name": "User",
                "is_employer": "on",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đăng ký tài khoản thành công", response.get_data(as_text=True))
        
        with self.app.app_context():
            user = User.query.filter_by(email="employer@example.com").first()
            self.assertIsNotNone(user)
            self.assertTrue(user.is_employer)

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

    def test_register_weak_password(self):
        response = self.client.post(
            "/register",
            data={
                "email": "weak@example.com",
                "password": "123",
                "confirm_password": "123",
            },
            follow_redirects=True,
        )
        self.assertIn("Mật khẩu phải có ít nhất 8 ký tự", response.get_data(as_text=True))

    # --- Test Login ---

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
            self.assertEqual(sess.get("user_id"), 1) # active@example.com is first seeded

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

    def test_login_nonexistent_user(self):
        response = self.client.post(
            "/login",
            data={
                "email": "nonexistent@example.com",
                "password": "Password123!",
            },
            follow_redirects=True,
        )
        self.assertIn("Email hoặc mật khẩu không chính xác", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
