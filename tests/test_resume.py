import os
import tempfile
import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, CV
from app.main.services import (
    get_user_cv,
)


class ResumeServiceTestCase(unittest.TestCase):
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
        os.unlink(self.db_path)

    def seed_data(self):
        users = [
            User(
                first_name="Resume",
                last_name="User",
                email="resume@example.com",
                password=generate_password_hash("Pass1234!"),
                is_active=True,
                created_at=datetime.utcnow(),
            ),
            User(
                first_name="Another",
                last_name="User",
                email="another@example.com",
                password=generate_password_hash("Pass1234!"),
                is_active=True,
                created_at=datetime.utcnow(),
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

    def test_get_user_cv_creates_new_if_not_exists(self):
        with self.app.app_context():
            user = User.query.filter_by(email="resume@example.com").first()

            cv = get_user_cv(user)

            self.assertIsNotNone(cv)
            self.assertEqual(cv.user_id, user.id)

    def test_get_user_cv_returns_existing(self):
        with self.app.app_context():
            user = User.query.filter_by(email="resume@example.com").first()

            cv1 = get_user_cv(user)
            cv1_id = cv1.id

            cv2 = get_user_cv(user)

            self.assertEqual(cv1_id, cv2.id)

    def test_cv_user_relationship(self):
        with self.app.app_context():
            user = User.query.filter_by(email="resume@example.com").first()
            cv = get_user_cv(user)

            self.assertEqual(cv.user_id, user.id)
            self.assertIn(cv, user.cvs)

    def test_cv_has_correct_fields(self):
        with self.app.app_context():
            user = User.query.filter_by(email="resume@example.com").first()
            cv = get_user_cv(user)

            self.assertTrue(hasattr(cv, 'id'))
            self.assertTrue(hasattr(cv, 'user_id'))
            self.assertTrue(hasattr(cv, 'title'))
            self.assertTrue(hasattr(cv, 'summary'))
            self.assertTrue(hasattr(cv, 'skills'))
            self.assertTrue(hasattr(cv, 'experience'))
            self.assertTrue(hasattr(cv, 'education'))
            self.assertTrue(hasattr(cv, 'cv_url'))
            self.assertTrue(hasattr(cv, 'cv_content'))
            self.assertTrue(hasattr(cv, 'created_at'))
            self.assertTrue(hasattr(cv, 'last_modified'))

    def test_cv_timestamps_are_set(self):
        with self.app.app_context():
            user = User.query.filter_by(email="resume@example.com").first()
            cv = get_user_cv(user)

            self.assertIsNotNone(cv.created_at)
            self.assertIsNotNone(cv.last_modified)

    def test_multiple_users_have_separate_cvs(self):
        with self.app.app_context():
            user1 = User.query.filter_by(email="resume@example.com").first()
            user2 = User.query.filter_by(email="another@example.com").first()

            cv1 = get_user_cv(user1)
            cv2 = get_user_cv(user2)

            self.assertNotEqual(cv1.id, cv2.id)
            self.assertEqual(cv1.user_id, user1.id)
            self.assertEqual(cv2.user_id, user2.id)


if __name__ == "__main__":
    unittest.main()
