import os
import tempfile
import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User
from app.main.services import (
    validate_required_fields,
    validate_phone,
    parse_date_input,
)


class UserAccountServiceTestCase(unittest.TestCase):
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
                first_name="User",
                last_name="Yue",
                email="user@example.com",
                phone="0912345678",
                password=generate_password_hash("Pass1234!"),
                is_active=True,
                created_at=datetime.utcnow(),
            ),
            User(
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                password=generate_password_hash("Pass1234!"),
                is_active=True,
                created_at=datetime.utcnow(),
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

    def test_validate_required_fields_success(self):
        form = {"first_name": "User", "last_name": "Yue"}
        fields = [("first_name", "tên"), ("last_name", "họ")]
        is_valid, msg = validate_required_fields(form, fields)

        self.assertTrue(is_valid)
        self.assertIsNone(msg)

    def test_validate_required_fields_missing(self):
        form = {"first_name": "", "last_name": "Yue"}
        fields = [("first_name", "tên"), ("last_name", "họ")]
        is_valid, msg = validate_required_fields(form, fields)

        self.assertFalse(is_valid)
        self.assertIn("tên", msg)

    def test_validate_phone_valid_formats(self):
        self.assertTrue(validate_phone("0912345678")[0])
        self.assertTrue(validate_phone("0987654321")[0])
        self.assertTrue(validate_phone("+84912345678")[0])
        self.assertTrue(validate_phone("+84987654321")[0])

    def test_validate_phone_invalid_formats(self):
        self.assertFalse(validate_phone("123")[0])
        self.assertFalse(validate_phone("abcdefghij")[0])
        self.assertFalse(validate_phone("12345678901")[0])

    def test_parse_date_input_valid(self):
        is_valid, parsed_date, error = parse_date_input("1990-05-15")

        self.assertTrue(is_valid)
        self.assertEqual(str(parsed_date), "1990-05-15")
        self.assertIsNone(error)

    def test_parse_date_input_empty(self):
        is_valid, parsed_date, error = parse_date_input("")

        self.assertTrue(is_valid)
        self.assertIsNone(parsed_date)
        self.assertIsNone(error)

    def test_parse_date_input_invalid_format(self):
        is_valid, parsed_date, error = parse_date_input("15-05-1990")

        self.assertFalse(is_valid)
        self.assertIsNone(parsed_date)
        self.assertIn("Ngày sinh", error)


if __name__ == "__main__":
    unittest.main()
