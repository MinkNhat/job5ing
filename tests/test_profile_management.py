import unittest
from app import create_app, db
from app.models import User, CV
from app.main.services import update_account_profile

class ProfileManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test-secret'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Tạo user test
        self.user = User(
            email="test@gmail.com",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_update_profile_success(self):
        """Kiểm tra cập nhật thông tin User thành công."""
        form_data = {
            "first_name": "Nguyen",
            "last_name": "Van A",
            "phone": "0912345678",
            "address": "Hanoi, Vietnam",
            "sex": "Nam",
            "date_of_birth": "1995-01-01"
        }
        
        # Giả lập session vì hàm sync_authenticated_session có dùng session
        with self.app.test_request_context():
            from flask import session
            success, message = update_account_profile(self.user, form_data)
            
            self.assertTrue(success)
            self.assertEqual(message, "Cập nhật hồ sơ thành công.")
            
            # Kiểm tra dữ liệu User
            updated_user = db.session.get(User, self.user.id)
            self.assertEqual(updated_user.first_name, "Nguyen")
            self.assertEqual(updated_user.phone, "0912345678")

    def test_update_profile_missing_required(self):
        """Kiểm tra báo lỗi khi thiếu trường bắt buộc."""
        form_data = {
            "first_name": "", # Thiếu tên
            "last_name": "Van A"
        }
        success, message = update_account_profile(self.user, form_data)
        self.assertFalse(success)
        self.assertIn("Vui lòng nhập đầy đủ", message)

    def test_update_profile_invalid_phone(self):
        """Kiểm tra báo lỗi khi số điện thoại sai định dạng."""
        form_data = {
            "first_name": "Nguyen",
            "last_name": "Van A",
            "phone": "123" # Sai định dạng
        }
        success, message = update_account_profile(self.user, form_data)
        self.assertFalse(success)
        self.assertIn("Số điện thoại không hợp lệ", message)

if __name__ == '__main__':
    unittest.main()
