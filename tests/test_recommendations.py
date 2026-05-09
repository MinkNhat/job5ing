import os
import tempfile
import unittest
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from unittest.mock import patch

from app import create_app, db
from app.models import (
    User, CV, Post, Recruiter, Company, Location, 
    ExperienceOption, SalaryOption, CVSkill, CVExperience
)
from app.main.services import get_recommended_jobs, send_daily_job_recommendations

class RecommendationTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.db_path}",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "test-secret",
                "SERVER_NAME": "localhost:5000",
                "PREFERRED_URL_SCHEME": "http"
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
        # Create base options
        loc = Location(name="Hồ Chí Minh")
        exp_opt = ExperienceOption(name="1-3 năm")
        sal_opt = SalaryOption(name="10-20 triệu")
        db.session.add_all([loc, exp_opt, sal_opt])
        db.session.commit()

        # Create Company & Recruiter
        company = Company(name="Tech Corp", location="HCM", is_approved=True)
        db.session.add(company)
        db.session.commit()

        employer_user = User(
            email="employer@example.com",
            password=generate_password_hash("Pass1234!"),
            is_employer=True
        )
        db.session.add(employer_user)
        db.session.commit()

        recruiter = Recruiter(user_id=employer_user.id, company_id=company.id, is_approved=True)
        db.session.add(recruiter)
        db.session.commit()

        # Create Posts
        post1 = Post(
            title="Python Developer",
            skills="python, flask, sql",
            description="python developer with flask experience",
            status="ACTIVE",
            recruiter_id=employer_user.id,
            experience_id=exp_opt.id,
            salary_id=sal_opt.id
        )
        post2 = Post(
            title="Java Developer",
            skills="java, spring",
            description="java backend developer",
            status="ACTIVE",
            recruiter_id=employer_user.id,
            experience_id=exp_opt.id,
            salary_id=sal_opt.id
        )
        db.session.add_all([post1, post2])
        db.session.commit()

        # Create Candidate
        candidate = User(
            email="candidate@example.com",
            password=generate_password_hash("Pass1234!"),
            is_employer=False,
            is_active=True
        )
        db.session.add(candidate)
        db.session.commit()

        cv = CV(
            user_id=candidate.id,
            title="Backend Engineer",
            summary="I am a python fan"
        )
        db.session.add(cv)
        db.session.commit()

        # Add skills and experience via related tables
        db.session.add(CVSkill(cv_id=cv.id, skill_name="python"))
        db.session.add(CVSkill(cv_id=cv.id, skill_name="sql"))
        db.session.add(CVExperience(
            cv_id=cv.id, 
            job_title="Developer", 
            company_name="Old Co", 
            description="Worked with python and sql for 2 years"
        ))
        db.session.commit()

    @patch('app.main.recruiter_services.calculate_ai_score')
    def test_get_recommended_jobs(self, mock_calculate_score):
        with self.app.app_context():
            # Mock scores: Python = 90, Java = 10
            def side_effect(cv_id, post_id):
                post = db.session.get(Post, post_id)
                if "Python" in post.title:
                    return 90
                return 10
            mock_calculate_score.side_effect = side_effect
            
            candidate = User.query.filter_by(email="candidate@example.com").first()
            recommendations = get_recommended_jobs(candidate.id)
            
            self.assertEqual(len(recommendations), 2)
            self.assertEqual(recommendations[0]['post'].title, "Python Developer")
            self.assertEqual(recommendations[0]['score'], 90)

    @patch('app.main.services.get_recommended_jobs')
    @patch('services.smtp_service.send_email')
    def test_send_daily_job_recommendations(self, mock_send_email, mock_get_recs):
        with self.app.app_context():
            candidate = User.query.filter_by(email="candidate@example.com").first()
            post = Post.query.filter_by(title="Python Developer").first()
            
            mock_get_recs.return_value = [{'post': post, 'score': 95}]
            mock_send_email.return_value = True
            
            send_daily_job_recommendations()
            
            self.assertTrue(mock_send_email.called)
            args, kwargs = mock_send_email.call_args
            self.assertEqual(args[0], "candidate@example.com")
            self.assertIn("Python Developer", args[2])
            self.assertIn("95% phù hợp", args[2])

if __name__ == "__main__":
    unittest.main()
