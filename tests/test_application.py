import os
import tempfile
import unittest
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Company, Recruiter, Post, CV, Application

class ApplicationTestCase(unittest.TestCase):
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
            business_license="test_license.pdf"
        )
        db.session.add(company)
        db.session.flush()

        # Create recruiters
        recruiter_user = User(
            email="recruiter@example.com",
            password=generate_password_hash("Password123!"),
            is_active=True,
            is_employer=True
        )
        recruiter_user2 = User(
            email="recruiter2@example.com",
            password=generate_password_hash("Password123!"),
            is_active=True,
            is_employer=True
        )
        db.session.add_all([recruiter_user, recruiter_user2])
        db.session.flush()

        recruiter = Recruiter(
            user_id=recruiter_user.id,
            company_id=company.id,
            position="HR Manager",
            is_approved=True
        )
        recruiter2 = Recruiter(
            user_id=recruiter_user2.id,
            company_id=company.id,
            position="HR Assistant",
            is_approved=True
        )
        db.session.add_all([recruiter, recruiter2])
        db.session.flush()

        # Create post (by recruiter 1)
        post = Post(
            title="Senior Python Developer",
            description="Looking for an expert Python developer.",
            status="ACTIVE",
            recruiter_id=recruiter.user_id
        )
        db.session.add(post)
        db.session.flush()
        
        # Create candidate user
        candidate = User(
            email="candidate@example.com",
            password=generate_password_hash("Password123!"),
            is_active=True,
            is_employer=False
        )
        db.session.add(candidate)
        db.session.commit()

    def login(self, email, password="Password123!"):
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True
        )

    def test_recruiter_view_application_same_company(self):
        """Test recruiter can view application for a post created by another recruiter in the same company"""
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            cv = CV(user_id=candidate.id, title="My CV", cv_content='{"skills": "Python"}')
            db.session.add(cv)
            post = Post.query.first()
            application = Application(cv_id=cv.id, post_id=post.id)
            db.session.add(application)
            db.session.commit()
            app_id = application.id

        # Login as recruiter 2 (who didn't create the post)
        self.login("recruiter2@example.com")
        response = self.client.get(f"/manage-candidates/view-cv/{app_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Chi tiết hồ sơ", response.get_data(as_text=True))
        self.assertNotIn("Bạn không có quyền xem hồ sơ này", response.get_data(as_text=True))

    def test_apply_job_success(self):
        """Test candidate applying with valid CV"""
        self.login("candidate@example.com")
        
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            cv = CV(user_id=candidate.id, title="My CV", cv_content='{"skills": "Python"}')
            db.session.add(cv)
            db.session.commit()
            cv_id = cv.id
            
            post = Post.query.first()
            post_id = post.id
            
        response = self.client.post(f"/post/{post_id}/apply", data={
            "cv_id": cv_id,
            "phone": "0901234567",
            "cover_letter": "I am very interested in this position."
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        self.assertIn("Ứng tuyển thành công", data)
        
        with self.app.app_context():
            app_count = Application.query.count()
            self.assertEqual(app_count, 1)
            app = Application.query.first()
            self.assertEqual(app.cover_letter, "I am very interested in this position.")
            user = User.query.filter_by(email="candidate@example.com").first()
            self.assertEqual(user.phone, "0901234567")

    def test_apply_job_saves_phone_to_profile(self):
        """Test that applying for a job saves the provided phone number to the user profile if missing"""
        self.login("candidate@example.com")
        
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            candidate.phone = None # Ensure it's missing
            db.session.commit()
            
            cv = CV(user_id=candidate.id, title="My CV", cv_content='{"skills": "Python"}')
            db.session.add(cv)
            db.session.commit()
            
            post = Post.query.first()
            post_id = post.id
            
        # Submit application with a phone number
        response = self.client.post(f"/post/{post_id}/apply", data={
            "phone": "0888999000",
            "cover_letter": "Saving my phone number."
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ứng tuyển thành công", response.get_data(as_text=True))
        
        # Verify phone is saved to User profile
        with self.app.app_context():
            user = User.query.filter_by(email="candidate@example.com").first()
            self.assertEqual(user.phone, "0888999000")

    def test_apply_job_already_applied(self):
        """Test applying to the same job twice"""
        self.login("candidate@example.com")
        
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            cv = CV(user_id=candidate.id, title="My CV", cv_content='{"skills": "Python"}')
            db.session.add(cv)
            
            post = Post.query.first()
            application = Application(cv_id=cv.id, post_id=post.id)
            db.session.add(application)
            db.session.commit()
            
            post_id = post.id
            
        response = self.client.post(f"/post/{post_id}/apply", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        # Check for message in the data-message attribute of the flash-data div
        self.assertIn('data-message="Bạn đã ứng tuyển vào vị trí này bằng CV này rồi."', data)
        
        with self.app.app_context():
            app_count = Application.query.count()
            self.assertEqual(app_count, 1)

    def test_apply_job_as_employer(self):
        """Test employer cannot apply to a job"""
        self.login("recruiter@example.com")
        
        with self.app.app_context():
            post = Post.query.first()
            post_id = post.id
            
        response = self.client.post(f"/post/{post_id}/apply", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        self.assertIn("Nhà tuyển dụng không thể ứng tuyển", data)

    def test_applied_jobs_list(self):
        """Test candidate can view their applied jobs list"""
        self.login("candidate@example.com")
        
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            cv = CV(user_id=candidate.id, title="My CV", cv_content='{"skills": "Python"}')
            db.session.add(cv)
            
            post = Post.query.first()
            application = Application(cv_id=cv.id, post_id=post.id, status='INTERVIEW')
            db.session.add(application)
            db.session.commit()
            
            post_title = post.title
            
        response = self.client.get("/applied-jobs")
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        self.assertIn("Việc làm đã ứng tuyển", data)
        self.assertIn(post_title, data)
        self.assertIn("Phỏng vấn", data)

if __name__ == "__main__":
    unittest.main()
