import os
import tempfile
import unittest
from datetime import date
from app import create_app, db
from app.models import User, Company, Recruiter

class RecruiterCompanyEditTestCase(unittest.TestCase):
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
        # Create company
        c = Company(name="Test Corp", is_approved=True)
        db.session.add(c)
        db.session.flush()

        # Create recruiter admin
        u = User(email="admin@testcorp.com", password="123", is_employer=True, is_active=True)
        db.session.add(u)
        db.session.flush()
        
        r = Recruiter(user_id=u.id, company_id=c.id, is_company_admin=True, is_approved=True)
        db.session.add(r)
        db.session.commit()
        self.recruiter_id = u.id
        self.company_id = c.id

    def login_recruiter(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.recruiter_id

    def test_edit_company_founding_date(self):
        self.login_recruiter()
        
        # Initial check
        with self.app.app_context():
            company = db.session.get(Company, self.company_id)
            self.assertIsNone(company.establish_date)
            self.assertIsNone(company.tax_code)
            self.assertIsNone(company.business_license)

        # Submit update
        response = self.client.post(
            "/recruiter/company",
            data={
                "name": "Updated Corp",
                "establish_date": "2020-01-01",
                "tax_code": "123456789",
                "business_license": "LICENSE-ABC",
                "description": "Updated description"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cập nhật thông tin công ty thành công", response.get_data(as_text=True))

        # Verify database
        with self.app.app_context():
            company = db.session.get(Company, self.company_id)
            self.assertEqual(company.name, "Updated Corp")
            self.assertEqual(company.establish_date, date(2020, 1, 1))
            self.assertEqual(company.tax_code, "123456789")
            self.assertEqual(company.business_license, "LICENSE-ABC")
            self.assertEqual(company.description, "Updated description")

if __name__ == "__main__":
    unittest.main()
