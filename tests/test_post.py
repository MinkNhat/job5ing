import os
import tempfile
import unittest
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Company, Recruiter, Post

class PostTestCase(unittest.TestCase):
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
        # Create company
        company = Company(
            name="Job5ing Corp",
            tax_code="1234567890",
            location="Hồ Chí Minh",
            scale_id=1,
            website="https://job5ing.com",
            business_license="test_license.pdf"
        )
        db.session.add(company)
        db.session.flush()

        # Create user/recruiter
        user = User(
            email="recruiter@example.com",
            password=generate_password_hash("Password123!"),
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_employer=True
        )
        db.session.add(user)
        db.session.flush()

        recruiter = Recruiter(
            user_id=user.id,
            company_id=company.id,
            position="HR Manager",
            is_approved=True
        )
        db.session.add(recruiter)
        db.session.flush()

        # Create posts
        post1 = Post(
            title="Senior Python Developer",
            description="Looking for an expert Python developer.",
            skills="Python, Flask, SQLAlchemy",
            experience_id=1,
            salary_id=1,
            deadline=(datetime.now() + timedelta(days=30)).date(),
            status="ACTIVE",
            recruiter_id=recruiter.user_id
        )
        
        post2 = Post(
            title="Junior Frontend Developer",
            description="Looking for a React developer.",
            skills="React, CSS, HTML",
            experience_id=1,
            salary_id=1,
            deadline=(datetime.now() + timedelta(days=15)).date(),
            status="ACTIVE",
            recruiter_id=recruiter.user_id
        )
        
        post_inactive = Post(
            title="Ghost Job",
            description="This job is not active.",
            status="CLOSED",
            recruiter_id=recruiter.user_id
        )

        db.session.add_all([post1, post2, post_inactive])
        db.session.commit()

    def test_post_details_success(self):
        """Test viewing an existing post successfully"""
        with self.app.app_context():
            post = Post.query.filter_by(title="Senior Python Developer").first()
            post_id = post.id

        response = self.client.get(f"/post/{post_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        self.assertIn("Senior Python Developer", data)
        self.assertIn("Job5ing Corp", data)
        self.assertIn("Thỏa thuận", data)
        self.assertIn("Không yêu cầu", data)
        self.assertIn("Python, Flask, SQLAlchemy", data)
        self.assertIn("Hồ Chí Minh", data)

    def test_post_details_404(self):
        """Test viewing a non-existent post returns 404"""
        response = self.client.get("/post/9999")
        self.assertEqual(response.status_code, 404)

    def test_related_jobs_display(self):
        """Test that related jobs from the same company are displayed"""
        with self.app.app_context():
            post1 = Post.query.filter_by(title="Senior Python Developer").first()
            post2 = Post.query.filter_by(title="Junior Frontend Developer").first()
            post1_id = post1.id
            post2_title = post2.title

        response = self.client.get(f"/post/{post1_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        # Should contain the current job and the related job
        self.assertIn("Senior Python Developer", data)
        self.assertIn("Công việc liên quan", data)
        self.assertIn(post2_title, data)

    def test_inactive_post_details(self):
        """Test that even inactive posts can be viewed via direct link (or 404 if business logic requires)"""
        # Current implementation uses get_or_404(post_id), so it will show regardless of status
        # unless we add status check in the route.
        with self.app.app_context():
            post = Post.query.filter_by(status="CLOSED").first()
            post_id = post.id

        response = self.client.get(f"/post/{post_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ghost Job", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
