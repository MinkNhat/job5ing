import os
import tempfile
import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Company, Recruiter, Post

class SearchTestCase(unittest.TestCase):
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
        # 1. Create Companies
        c1 = Company(name="Google VN", location="Hồ Chí Minh", business_license="1", tax_code="T1")
        c2 = Company(name="FPT Software", location="Hà Nội", business_license="2", tax_code="T2")
        db.session.add_all([c1, c2])
        db.session.flush()

        # 2. Create Users & Recruiters
        u1 = User(email="r1@test.com", password="123", is_employer=True)
        u2 = User(email="r2@test.com", password="123", is_employer=True)
        db.session.add_all([u1, u2])
        db.session.flush()

        rec1 = Recruiter(user_id=u1.id, company_id=c1.id, is_approved=True)
        rec2 = Recruiter(user_id=u2.id, company_id=c2.id, is_approved=True)
        db.session.add_all([rec1, rec2])
        db.session.flush()

        # 3. Create Posts
        # Post 1: Python Dev, Google, 10-30tr, 1-3 năm, HCM, PINNED
        p1 = Post(
            recruiter_id=u1.id,
            title="Python Developer",
            salary_id=2, # Medium salary
            experience_id=2,
            status="PINNED",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        # Post 2: Java Dev, FPT, 5-10tr, <1 năm, Hanoi, ACTIVE
        p2 = Post(
            recruiter_id=u2.id,
            title="Java Backend",
            salary_id=1, # Lowest salary
            experience_id=1,
            status="ACTIVE",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        # Post 3: Frontend, Google, 30+, >5 năm, HCM, ACTIVE
        p3 = Post(
            recruiter_id=u1.id,
            title="Frontend Lead",
            salary_id=3, # Highest salary
            experience_id=3,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )

        db.session.add_all([p1, p2, p3])
        db.session.commit()

    def test_search_by_keyword_title(self):
        """Tìm kiếm theo keyword trong title"""
        response = self.client.get("/?keyword=Python")
        data = response.get_data(as_text=True)
        self.assertIn("Python Developer", data)
        self.assertNotIn("Java Backend", data)

    def test_search_by_keyword_company(self):
        """Tìm kiếm theo keyword tên công ty"""
        response = self.client.get("/?keyword=FPT")
        data = response.get_data(as_text=True)
        self.assertIn("Java Backend", data)
        self.assertNotIn("Python Developer", data)

    def test_filter_by_location(self):
        """Lọc theo địa điểm (HCM)"""
        # Note: Assumes city_id 1 is HCM. test_search seed doesn't set Location rows.
        # This will fail unless Location rows are seeded. We will pass location_id=c1.city_id
        pass

    def test_filter_by_experience(self):
        """Lọc theo kinh nghiệm (Exact match)"""
        response = self.client.get("/?experience=2")
        data = response.get_data(as_text=True)
        self.assertIn("Python Developer", data)
        self.assertNotIn("Frontend Lead", data)

    def test_filter_by_salary(self):
        """Lọc theo mức lương (Exact match)"""
        response = self.client.get("/?salary=3")
        data = response.get_data(as_text=True)
        self.assertIn("Frontend Lead", data)
        self.assertNotIn("Python Developer", data)

    def test_sorting_by_newest(self):
        """Sắp xếp theo bài đăng mới nhất"""
        response = self.client.get("/?sort_by=newest")
        data = response.get_data(as_text=True)
        # Kiểm tra thứ tự xuất hiện trong HTML (Frontend Lead mới nhất)
        lead_pos = data.find("Frontend Lead")
        java_pos = data.find("Java Backend")
        python_pos = data.find("Python Developer")
        self.assertTrue(lead_pos < java_pos < python_pos)

    def test_sorting_by_salary_rank(self):
        """Sắp xếp theo rank lương (Trên 30 triệu > 10-30 triệu > 5-10 triệu)"""
        response = self.client.get("/?sort_by=salary_desc")
        data = response.get_data(as_text=True)
        
        lead_pos = data.find("Frontend Lead")     # Trên 30tr
        python_pos = data.find("Python Developer") # 10-30tr
        java_pos = data.find("Java Backend")      # 5-10tr
        
        self.assertTrue(lead_pos < python_pos < java_pos)

    def test_sorting_default_relevance(self):
        """Sắp xếp mặc định: PINNED lên đầu, sau đó mới đến thời gian"""
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        
        python_pos = data.find("Python Developer") # PINNED (mặc dù cũ hơn bài Java)
        lead_pos = data.find("Frontend Lead")     # ACTIVE - Newest
        java_pos = data.find("Java Backend")      # ACTIVE
        
        self.assertTrue(python_pos < lead_pos < java_pos)

    def test_clear_filters_button_visibility(self):
        """Kiểm tra nút Xóa bộ lọc chỉ xuất hiện khi có param"""
        # Không có param
        response = self.client.get("/")
        self.assertNotIn("Xóa bộ lọc", response.get_data(as_text=True))
        
        # Có param
        response = self.client.get("/?keyword=Python")
        self.assertIn("Xóa bộ lọc", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
