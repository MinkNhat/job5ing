import os
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime

from app import create_app, db
from app.models import User, Company, Recruiter, Notification


class CompanyManagementTestCase(unittest.TestCase):
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
        # Create companies
        c1 = Company(name="Pending Corp", tax_code="111", is_approved=False)
        c2 = Company(name="Approved Inc", tax_code="222", is_approved=True)
        db.session.add_all([c1, c2])
        db.session.flush()

        # Create a recruiter for Pending Corp
        u1 = User(email="hr@pending.com", password="123", is_employer=True)
        db.session.add(u1)
        db.session.flush()
        
        r1 = Recruiter(user_id=u1.id, company_id=c1.id)
        db.session.add(r1)
        db.session.commit()

    def test_companies_page_loads(self):
        response = self.client.get("/admin/companies")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Quản lý doanh nghiệp", response.get_data(as_text=True))

    def test_companies_filter_pending(self):
        response = self.client.get("/admin/companies?status=pending")
        page = response.get_data(as_text=True)
        self.assertIn("Pending Corp", page)
        self.assertNotIn("Approved Inc", page)

    @patch('app.admin.service.send_approval_email')
    def test_approve_company(self, mock_send_email):
        mock_send_email.return_value = True
        
        with self.app.app_context():
            company = Company.query.filter_by(name="Pending Corp").first()
            company_id = company.id

        response = self.client.post(
            f"/admin/companies/{company_id}/approve",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã phê duyệt công ty Pending Corp và gửi thông báo", response.get_data(as_text=True))

        with self.app.app_context():
            updated_company = db.session.get(Company, company_id)
            self.assertTrue(updated_company.is_approved)
            
            # Kiểm tra thông báo trong app
            notification = Notification.query.filter_by(user_id=updated_company.recruiters[0].user_id).first()
            self.assertIsNotNone(notification)
            self.assertEqual(notification.type, 'ACCOUNT_APPROVED')
            
            # Kiểm tra xem hàm gửi mail có được gọi không
            mock_send_email.assert_called_once_with("hr@pending.com", "Pending Corp")

    def test_delete_company(self):
        with self.app.app_context():
            company = Company.query.filter_by(name="Approved Inc").first()
            company_id = company.id

        response = self.client.post(
            f"/admin/companies/{company_id}/delete",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã xóa thông tin công ty.", response.get_data(as_text=True))

        with self.app.app_context():
            deleted_company = db.session.get(Company, company_id)
            self.assertIsNone(deleted_company)


if __name__ == "__main__":
    unittest.main()
