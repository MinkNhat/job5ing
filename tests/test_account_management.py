import os
import tempfile
import unittest
from datetime import datetime

from app import create_app, db
from app.models import User


class AccountManagementTestCase(unittest.TestCase):
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
        
        self.login_admin()

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1 # ID của AdminPham từ seed_users
            sess['user_role'] = 'admin'

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
                first_name="Admin",
                last_name="Pham",
                email="admin@job5ing.com",
                password="123",
                is_active=True,
                is_admin=True,
                is_employer=False,
                created_at=datetime(2026, 4, 19, 15, 29, 8),
            ),
            User(
                first_name="Huy",
                last_name="Tran",
                email="huy@gmail.com",
                password="123",
                is_active=True,
                is_admin=False,
                is_employer=False,
                created_at=datetime(2026, 4, 19, 15, 29, 8),
            ),
            User(
                first_name="Anh",
                last_name="Company",
                email="anh@company.com",
                password="123",
                is_active=True,
                is_admin=False,
                is_employer=True,
                created_at=datetime(2026, 4, 19, 15, 29, 8),
            ),
            User(
                first_name="Linh",
                last_name="Nguyen",
                email="linh@gmail.com",
                password="123",
                is_active=False,
                is_admin=False,
                is_employer=False,
                created_at=datetime(2026, 4, 19, 15, 29, 8),
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

    def test_accounts_page_loads(self):
        response = self.client.get("/admin/accounts")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Danh sách tài khoản", response.get_data(as_text=True))

    def test_accounts_filter_by_admin_role(self):
        response = self.client.get("/admin/accounts?role=admin")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("admin@job5ing.com", page)
        self.assertNotIn("huy@gmail.com", page)
        self.assertNotIn("anh@company.com", page)

    def test_accounts_filter_by_inactive_status(self):
        response = self.client.get("/admin/accounts?status=inactive")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("linh@gmail.com", page)
        self.assertNotIn("admin@job5ing.com", page)

    def test_edit_account_updates_role_and_status(self):
        with self.app.app_context():
            user = User.query.filter_by(email="huy@gmail.com").first()
            user_id = user.id

        response = self.client.post(
            f"/admin/accounts/{user_id}/edit",
            data={
                "email": "huy.updated@gmail.com",
                "first_name": "Huy",
                "last_name": "Tran",
                "phone": "0909000000",
                "address": "TP.HCM",
                "sex": "Nam",
                "role": "admin",
                "is_active": "0",
                "next": "/admin/accounts",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cập nhật tài khoản thành công.", response.get_data(as_text=True))

        with self.app.app_context():
            updated_user = db.session.get(User, user_id)
            self.assertEqual(updated_user.email, "huy.updated@gmail.com")
            self.assertTrue(updated_user.is_admin)
            self.assertFalse(updated_user.is_employer)
            self.assertFalse(updated_user.is_active)

    def test_toggle_account_switches_active_status(self):
        with self.app.app_context():
            user = User.query.filter_by(email="linh@gmail.com").first()
            user_id = user.id

        response = self.client.post(
            f"/admin/users/{user_id}/toggle",
            data={},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã mở khóa tài khoản.", response.get_data(as_text=True))

        with self.app.app_context():
            updated_user = db.session.get(User, user_id)
            self.assertTrue(updated_user.is_active)

    def test_delete_account_removes_user(self):
        with self.app.app_context():
            user = User.query.filter_by(email="anh@company.com").first()
            user_id = user.id

        response = self.client.post(
            f"/admin/users/{user_id}/delete",
            data={},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã xóa tài khoản.", response.get_data(as_text=True))

        with self.app.app_context():
            deleted_user = db.session.get(User, user_id)
            self.assertIsNone(deleted_user)

    def test_profile_updates_current_admin_information(self):
        response = self.client.post(
            "/admin/profile",
            data={
                "email": "admin.updated@job5ing.com",
                "first_name": "Super",
                "last_name": "Admin",
                "phone": "0988888888",
                "sex": "Khác",
                "avatar_url": "https://example.com/avatar.png",
                "address": "Da Nang",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã cập nhật hồ sơ quản trị viên.", response.get_data(as_text=True))

        with self.app.app_context():
            admin_user = User.query.filter_by(is_admin=True).order_by(User.id.asc()).first()
            self.assertEqual(admin_user.email, "admin.updated@job5ing.com")
            self.assertEqual(admin_user.first_name, "Super")
            self.assertEqual(admin_user.last_name, "Admin")
            self.assertEqual(admin_user.phone, "0988888888")
            self.assertEqual(admin_user.sex, "Khác")
            self.assertEqual(admin_user.avatar_url, "https://example.com/avatar.png")
            self.assertEqual(admin_user.address, "Da Nang")


if __name__ == "__main__":
    unittest.main()
