import os
import tempfile
import unittest
from datetime import datetime, date

from app import create_app, db
from app.models import User, Company, Recruiter, Post


class PostManagementTestCase(unittest.TestCase):
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
        # Create a company
        company = Company(name="FPT Software", location="Hanoi", tax_code="123456")
        db.session.add(company)
        db.session.flush()

        # Create a recruiter user
        recruiter_user = User(
            first_name="Recruiter",
            last_name="One",
            email="recruiter@fpt.com",
            password="123",
            is_employer=True
        )
        db.session.add(recruiter_user)
        db.session.flush()

        # Create recruiter profile
        recruiter = Recruiter(user_id=recruiter_user.id, company_id=company.id, position="HR Manager")
        db.session.add(recruiter)
        db.session.flush()

        # Create posts
        posts = [
            Post(
                recruiter_id=recruiter_user.id,
                title="Python Developer",
                description="Looking for Python devs",
                skills="Python, Flask",
                status='ACTIVE',
                is_reported=False,
                created_at=datetime(2026, 4, 1, 10, 0, 0)
            ),
            Post(
                recruiter_id=recruiter_user.id,
                title="Frontend React",
                description="Need React expert",
                skills="React, JS",
                status='BLOCKED',
                is_reported=True,
                created_at=datetime(2026, 4, 2, 10, 0, 0)
            ),
            Post(
                recruiter_id=recruiter_user.id,
                title="Java Backend",
                description="Spring boot master",
                skills="Java, Spring",
                status='CLOSED',
                is_reported=False,
                created_at=datetime(2026, 4, 3, 10, 0, 0)
            ),
        ]
        db.session.add_all(posts)
        db.session.commit()

    def test_posts_page_loads(self):
        response = self.client.get("/admin/posts")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Quản lý tin tuyển dụng", response.get_data(as_text=True))
        self.assertIn("Python Developer", response.get_data(as_text=True))

    def test_posts_filter_by_keyword(self):
        response = self.client.get("/admin/posts?keyword=React")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Frontend React", page)
        self.assertNotIn("Python Developer", page)

    def test_posts_filter_by_status(self):
        response = self.client.get("/admin/posts?status=BLOCKED")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Frontend React", page)
        self.assertNotIn("Java Backend", page)

    def test_posts_filter_by_reported(self):
        response = self.client.get("/admin/posts?is_reported=1")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Frontend React", page)
        self.assertIn("Bị báo cáo", page)
        self.assertNotIn("Python Developer", page)

    def test_change_post_status(self):
        with self.app.app_context():
            post = Post.query.filter_by(title="Python Developer").first()
            post_id = post.id

        response = self.client.post(
            f"/admin/posts/{post_id}/status",
            data={"status": "PINNED"},
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã cập nhật trạng thái tin tuyển dụng thành PINNED", response.get_data(as_text=True))

        with self.app.app_context():
            updated_post = db.session.get(Post, post_id)
            self.assertEqual(updated_post.status, "PINNED")

    def test_delete_post(self):
        with self.app.app_context():
            post = Post.query.filter_by(title="Java Backend").first()
            post_id = post.id

        response = self.client.post(
            f"/admin/posts/{post_id}/delete",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã xóa tin tuyển dụng thành công.", response.get_data(as_text=True))

        with self.app.app_context():
            deleted_post = db.session.get(Post, post_id)
            self.assertIsNone(deleted_post)


if __name__ == "__main__":
    unittest.main()
