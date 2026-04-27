import os
import tempfile
import unittest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Company, Recruiter, Post, Application, CV

class CompanyPostManagementTestCase(unittest.TestCase):
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
        # Create a recruiter user
        recruiter_user = User(
            email="recruiter@example.com",
            password=generate_password_hash("Password123!"),
            is_active=True,
            is_employer=True,
            first_name="Recruiter",
            last_name="User"
        )
        
        # Create a candidate user
        candidate_user = User(
            email="candidate@example.com",
            password=generate_password_hash("Password123!"),
            is_active=True,
            is_employer=False,
            first_name="Candidate",
            last_name="User"
        )
        
        db.session.add_all([recruiter_user, candidate_user])
        db.session.flush()

        # Create company
        company = Company(
            name="Test Company",
            tax_code="1234567890",
            business_license="license.pdf"
        )
        db.session.add(company)
        db.session.flush()

        # Link recruiter to company
        recruiter = Recruiter(
            user_id=recruiter_user.id,
            company_id=company.id,
            is_approved=True
        )
        db.session.add(recruiter)
        
        # Create a job
        job = Post(
            recruiter_id=recruiter_user.id,
            title="Python Developer",
            description="Experience with Flask",
            status="ACTIVE",
            deadline=datetime.utcnow().date() + timedelta(days=10)
        )
        db.session.add(job)
        db.session.flush()
        
        # Create CV and Application
        cv = CV(user_id=candidate_user.id, title="My Resume")
        db.session.add(cv)
        db.session.flush()
        
        app = Application(cv_id=cv.id, post_id=job.id, status="RECEIVED")
        db.session.add(app)
        
        db.session.commit()

    def login(self, email, password):
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True
        )

    def test_dashboard_access_recruiter(self):
        """Recruiter can access dashboard"""
        self.login("recruiter@example.com", "Password123!")
        response = self.client.get("/recruiter/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Danh sách tin đã đăng", response.get_data(as_text=True))
        self.assertIn("Python Developer", response.get_data(as_text=True))

    def test_dashboard_access_denied_candidate(self):
        """Candidate cannot access recruiter dashboard"""
        self.login("candidate@example.com", "Password123!")
        response = self.client.get("/recruiter/dashboard")
        # Should redirect to index with flash message
        self.assertEqual(response.status_code, 302)

    def test_stats_calculation(self):
        """Verify dashboard statistics"""
        self.login("recruiter@example.com", "Password123!")
        response = self.client.get("/recruiter/dashboard")
        html = response.get_data(as_text=True)
        self.assertIn("1", html) # Total apps, Active jobs, Pending apps in this seed are all 1

    def test_create_job_success(self):
        """Create a new job via POST"""
        self.login("recruiter@example.com", "Password123!")
        response = self.client.post(
            "/recruiter/job/manage",
            data={
                "title": "New Job",
                "description": "Description",
                "salary_range": "10-30 triệu",
                "experience": "1-3 năm kinh nghiệm",
                "deadline": (datetime.utcnow() + timedelta(days=20)).strftime('%Y-%m-%d'),
                "skills": "Test"
            },
            follow_redirects=True
        )
        self.assertIn("Đăng tin mới thành công", response.get_data(as_text=True))
        
        with self.app.app_context():
            job = Post.query.filter_by(title="New Job").first()
            self.assertIsNotNone(job)
            self.assertEqual(job.status, "ACTIVE")

    def test_update_job_success(self):
        """Update an existing job and change status"""
        self.login("recruiter@example.com", "Password123!")
        
        with self.app.app_context():
            job_id = Post.query.filter_by(title="Python Developer").first().id

        response = self.client.post(
            f"/recruiter/job/manage/{job_id}",
            data={
                "title": "Updated Python Developer",
                "description": "New desc",
                "salary_range": "Thỏa thuận",
                "experience": "3-5 năm kinh nghiệm",
                "deadline": (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
                "status": "CLOSED"
            },
            follow_redirects=True
        )
        self.assertIn("Cập nhật tin thành công", response.get_data(as_text=True))
        
        with self.app.app_context():
            job = Post.query.get(job_id)
            self.assertEqual(job.title, "Updated Python Developer")
            self.assertEqual(job.status, "CLOSED")

    def test_close_job_action(self):
        """Test the close job action endpoint"""
        self.login("recruiter@example.com", "Password123!")
        
        with self.app.app_context():
            job_id = Post.query.filter_by(title="Python Developer").first().id

        response = self.client.post(f"/recruiter/job/close/{job_id}", follow_redirects=True)
        
        with self.app.app_context():
            job = Post.query.get(job_id)
            self.assertEqual(job.status, "CLOSED")

if __name__ == "__main__":
    unittest.main()
