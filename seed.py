from datetime import datetime, date
from app import create_app, db
from app.models import (
    Location, CompanyScale, ExperienceOption, SalaryOption,
    Company, User, Recruiter, CV, CVSkill, Post, PostSkill,
    Application, ApplicationStatusHistory, PostReport, Notification
)

def seed_data():
    if User.query.first() is not None:
        print("Database already has data. Skipping seed.")
        return False

    try:
        locations = [
            Location(id=1, name='TP. Hồ Chí Minh'),
            Location(id=2, name='Hà Nội'),
            Location(id=3, name='Đà Nẵng'),
            Location(id=4, name='Cần Thơ'),
        ]
        for loc in locations:
            db.session.add(loc)

        scales = [
            CompanyScale(id=1, name='1-50 nhân viên'),
            CompanyScale(id=2, name='51-200 nhân viên'),
            CompanyScale(id=3, name='201-500 nhân viên'),
            CompanyScale(id=4, name='500+ nhân viên'),
        ]
        for scale in scales:
            db.session.add(scale)

        experiences = [
            ExperienceOption(id=1, name='Không yêu cầu kinh nghiệm'),
            ExperienceOption(id=2, name='<1 năm kinh nghiệm'),
            ExperienceOption(id=3, name='1-3 năm kinh nghiệm'),
            ExperienceOption(id=4, name='3-5 năm kinh nghiệm'),
            ExperienceOption(id=5, name='>5 năm kinh nghiệm'),
        ]
        for exp in experiences:
            db.session.add(exp)

        salaries = [
            SalaryOption(id=1, name='Không lương'),
            SalaryOption(id=2, name='1-3 triệu'),
            SalaryOption(id=3, name='3-5 triệu'),
            SalaryOption(id=4, name='5-10 triệu'),
            SalaryOption(id=5, name='10-30 triệu'),
            SalaryOption(id=6, name='Trên 30 triệu'),
            SalaryOption(id=7, name='Thỏa thuận'),
        ]
        for salary in salaries:
            db.session.add(salary)

        db.session.flush()

        users = [
            User(id=1, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Admin', last_name='System',
                 email='admin@testjob5ing.com', phone='0901234567',
                 address='Tòa nhà Admin, Quận 1, TP.HCM', date_of_birth=date(1990, 1, 1),
                 sex='Male', is_active=True, is_admin=True, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=2, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Huy', last_name='Tran',
                 email='huy@testjob5ing.com', phone='0912345678',
                 address='Quận Cầu Giấy, Hà Nội', date_of_birth=date(1992, 5, 12),
                 sex='Male', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=3, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Anh', last_name='Pham',
                 email='anh@testjob5ing.com', phone='0923456789',
                 address='Quận 3, TP.HCM', date_of_birth=date(1995, 8, 20),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=4, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Long', last_name='Nguyen',
                 email='long@testjob5ing.com', phone='0934567890',
                 address='Quận Hải Châu, Đà Nẵng', date_of_birth=date(1988, 11, 5),
                 sex='Male', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=5, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Khanh', last_name='Le',
                 email='khanh@testjob5ing.com', phone='0945678901',
                 address='Quận Ninh Kiều, Cần Thơ', date_of_birth=date(1994, 2, 14),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=6, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Linh', last_name='Nguyen',
                 email='linh@testjob5ing.com', phone='0956789012',
                 address='Quận 7, TP.HCM', date_of_birth=date(1991, 9, 30),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=7, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Minh', last_name='Le',
                 email='minh@testjob5ing.com', phone='0967890123',
                 address='Quận Tân Bình, TP.HCM', date_of_birth=date(1998, 4, 25),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 3, 18, 49, 35),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=8, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Tuan', last_name='Vo',
                 email='tuan@testjob5ing.com', phone='0978901234',
                 address='Quận Đống Đa, Hà Nội', date_of_birth=date(2000, 12, 10),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=9, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Trang', last_name='Pham',
                 email='trang@testjob5ing.com', phone='0989012345',
                 address='Quận Sơn Trà, Đà Nẵng', date_of_birth=date(1999, 7, 7),
                 sex='Female', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
            User(id=10, password='scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28', first_name='Nam', last_name='Hoang',
                 email='nam@testjob5ing.com', phone='0990123456',
                 address='Quận 10, TP.HCM', date_of_birth=date(1997, 3, 18),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://via.placeholder.com/150'),
        ]
        for user in users:
            db.session.add(user)

        db.session.flush()

        companies = [
            Company(id=1, name='FPT Software', location='Khu Công Nghệ Cao, Quận 9',
                   city_id=1, website='fpt.com', establish_date=date(1999, 1, 1),
                   scale_id=4, tax_code='TAX01', description='Tập đoàn công nghệ hàng đầu Việt Nam.',
                   is_approved=True, avatar_url='https://via.placeholder.com/200', business_license='license_fpt.pdf'),
            Company(id=2, name='VNG', location='Khu chế xuất Tân Thuận, Quận 7',
                   city_id=1, website='vng.com.vn', establish_date=date(2004, 9, 9),
                   scale_id=4, tax_code='TAX02', description='Kỳ lân công nghệ đầu tiên của Việt Nam.',
                   is_approved=True, avatar_url='https://via.placeholder.com/200', business_license='license_vng.pdf'),
            Company(id=3, name='VNPay', location='Tòa nhà VNPAY, Nam Từ Liêm',
                   city_id=2, website='vnpay.vn', establish_date=date(2007, 3, 1),
                   scale_id=3, tax_code='TAX03', description='Công ty Cổ phần Giải pháp Thanh toán Việt Nam.',
                   is_approved=True, avatar_url='https://via.placeholder.com/200', business_license='license_vnpay.pdf'),
            Company(id=4, name='MoMo', location='Tòa nhà Phú Mỹ Hưng, Quận 7',
                   city_id=1, website='momo.vn', establish_date=date(2007, 11, 15),
                   scale_id=3, tax_code='TAX04', description='Siêu ứng dụng thanh toán hàng đầu.',
                   is_approved=True, avatar_url='https://via.placeholder.com/200', business_license='license_momo.pdf'),
            Company(id=5, name='Tiki', location='Tòa nhà Viettel, Quận 10',
                   city_id=1, website='tiki.vn', establish_date=date(2010, 3, 1),
                   scale_id=4, tax_code='TAX05', description='Nền tảng thương mại điện tử đáng tin cậy.',
                   is_approved=True, avatar_url='https://via.placeholder.com/200', business_license='license_tiki.pdf'),
        ]
        for company in companies:
            db.session.add(company)

        db.session.flush()

        recruiters = [
            Recruiter(user_id=2, company_id=1, position='HR Manager', is_approved=True, is_company_admin=True),
            Recruiter(user_id=3, company_id=2, position='Recruitment Specialist', is_approved=True, is_company_admin=True),
            Recruiter(user_id=4, company_id=3, position='Talent Acquisition', is_approved=True, is_company_admin=True),
            Recruiter(user_id=5, company_id=4, position='HR Director', is_approved=True, is_company_admin=True),
            Recruiter(user_id=6, company_id=5, position='Tech Recruiter', is_approved=True, is_company_admin=True),
        ]
        for recruiter in recruiters:
            db.session.add(recruiter)

        db.session.flush()

        cvs = [
            CV(id=1, user_id=7, title='Java Backend Dev', summary='Kỹ sư phần mềm đam mê Backend',
               education='Đại học KHTN - CNTT', experience='2 năm tại công ty ABC',
               cv_url='aws.s3/cv1.pdf', cv_content='Nội dung text CV 1',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=2, user_id=7, title='Python Backend Dev', summary='Chuyên gia xây dựng API bằng Python',
               education='Đại học KHTN - CNTT', experience='2 năm kinh nghiệm backend',
               cv_url='aws.s3/cv2.pdf', cv_content='Nội dung text CV 2',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=3, user_id=8, title='ReactJS Frontend', summary='Yêu thích làm đẹp giao diện web',
               education='Đại học Bách Khoa', experience='1 năm frontend developer',
               cv_url='aws.s3/cv3.pdf', cv_content='Nội dung text CV 3',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=4, user_id=8, title='VueJS Frontend', summary='Cứng tay VueJS và Nuxt',
               education='Đại học Bách Khoa', experience='1 năm kinh nghiệm UI/UX',
               cv_url='aws.s3/cv4.pdf', cv_content='Nội dung text CV 4',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=5, user_id=9, title='Manual Tester', summary='Cẩn thận, tỉ mỉ, tìm bug nhanh',
               education='ĐH CNTT', experience='1 năm QA Tester',
               cv_url='aws.s3/cv5.pdf', cv_content='Nội dung text CV 5',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=6, user_id=9, title='Automation Tester', summary='Viết script automation chạy mượt',
               education='ĐH CNTT', experience='Thực tập sinh Automation',
               cv_url='aws.s3/cv6.pdf', cv_content='Nội dung text CV 6',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=7, user_id=10, title='DevOps Engineer', summary='Tối ưu CI/CD pipeline',
               education='Đại học FPT', experience='3 năm làm sysadmin/devops',
               cv_url='aws.s3/cv7.pdf', cv_content='Nội dung text CV 7',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            CV(id=8, user_id=10, title='AWS Cloud Engineer', summary='Chuyên thiết kế hạ tầng Cloud AWS',
               education='Đại học FPT', experience='3 năm kinh nghiệm Cloud',
               cv_url='aws.s3/cv8.pdf', cv_content='Nội dung text CV 8',
               created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
        ]
        for cv in cvs:
            db.session.add(cv)

        db.session.flush()

        cv_skills = [
            CVSkill(id=1, cv_id=1, skill_name='Java'),
            CVSkill(id=2, cv_id=1, skill_name='Spring Boot'),
            CVSkill(id=3, cv_id=1, skill_name='MySQL'),
            CVSkill(id=4, cv_id=2, skill_name='Python'),
            CVSkill(id=5, cv_id=2, skill_name='FastAPI'),
            CVSkill(id=6, cv_id=2, skill_name='Docker'),
            CVSkill(id=7, cv_id=3, skill_name='ReactJS'),
            CVSkill(id=8, cv_id=3, skill_name='CSS'),
            CVSkill(id=9, cv_id=3, skill_name='HTML'),
            CVSkill(id=10, cv_id=4, skill_name='Vue'),
            CVSkill(id=11, cv_id=4, skill_name='NuxtJS'),
            CVSkill(id=12, cv_id=4, skill_name='Tailwind'),
            CVSkill(id=13, cv_id=5, skill_name='Test Case'),
            CVSkill(id=14, cv_id=5, skill_name='JIRA'),
            CVSkill(id=15, cv_id=5, skill_name='SQL'),
            CVSkill(id=16, cv_id=6, skill_name='Selenium'),
            CVSkill(id=17, cv_id=6, skill_name='Python'),
            CVSkill(id=18, cv_id=6, skill_name='Cypress'),
            CVSkill(id=19, cv_id=7, skill_name='Jenkins'),
            CVSkill(id=20, cv_id=7, skill_name='Docker'),
            CVSkill(id=21, cv_id=7, skill_name='Kubernetes'),
            CVSkill(id=22, cv_id=8, skill_name='AWS EC2'),
            CVSkill(id=23, cv_id=8, skill_name='S3'),
            CVSkill(id=24, cv_id=8, skill_name='RDS'),
        ]
        for skill in cv_skills:
            db.session.add(skill)

        posts = [
            Post(id=1, recruiter_id=2, title='Senior Java Developer', description='Phát triển dự án Outsource thị trường Nhật',
                 experience_id=4, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=2, recruiter_id=2, title='Junior Python', description='Làm việc với framework FastAPI',
                 experience_id=2, salary_id=4, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=3, recruiter_id=2, title='BrSE (Kỹ sư cầu nối)', description='Giao tiếp khách hàng Nhật, review code',
                 experience_id=4, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=4, recruiter_id=2, title='Fresher Tester', description='Đào tạo từ đầu, có trợ cấp',
                 experience_id=1, salary_id=2, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=5, recruiter_id=3, title='Game Developer', description='Phát triển core game bằng C++',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=6, recruiter_id=3, title='Data Engineer', description='Xử lý big data cho nền tảng Zalo',
                 experience_id=4, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=7, recruiter_id=3, title='React Native Dev', description='Làm app di động cho hàng triệu user',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=8, recruiter_id=3, title='Security Engineer', description='Đảm bảo an toàn thông tin hệ thống',
                 experience_id=4, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=9, recruiter_id=4, title='Golang Developer', description='Xây dựng core thanh toán',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=10, recruiter_id=4, title='DevOps Engineer', description='Quản trị hệ thống server Linux',
                 experience_id=4, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=11, recruiter_id=4, title='Business Analyst', description='Phân tích yêu cầu nghiệp vụ ngân hàng',
                 experience_id=3, salary_id=4, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=12, recruiter_id=4, title='System Admin', description='Trực hệ thống 24/7',
                 experience_id=3, salary_id=4, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=13, recruiter_id=5, title='AI Engineer', description='Phát triển mô hình Recommender System',
                 experience_id=4, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=14, recruiter_id=5, title='Android Developer', description='Tối ưu hiệu năng app MoMo',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=15, recruiter_id=5, title='iOS Developer', description='Phát triển tính năng mới cho iOS',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=16, recruiter_id=5, title='QA Lead', description='Quản lý đội ngũ QA 10 người',
                 experience_id=5, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=17, recruiter_id=6, title='NodeJS Backend', description='Xây dựng hệ thống quản lý kho',
                 experience_id=3, salary_id=5, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=18, recruiter_id=6, title='Frontend VueJS', description='Làm trang chủ e-commerce',
                 experience_id=3, salary_id=4, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=19, recruiter_id=6, title='Data Analyst', description='Phân tích hành vi mua hàng',
                 experience_id=3, salary_id=4, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
            Post(id=20, recruiter_id=6, title='Product Manager', description='Định hướng sản phẩm cho Seller',
                 experience_id=5, salary_id=6, deadline=date(2026, 12, 31), status='ACTIVE', is_reported=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_modified=datetime(2026, 5, 4, 1, 11, 12)),
        ]
        for post in posts:
            db.session.add(post)

        db.session.flush()

        post_skills = [
            PostSkill(id=1, post_id=1, skill_name='Java'),
            PostSkill(id=2, post_id=1, skill_name='Spring Boot'),
            PostSkill(id=3, post_id=2, skill_name='Python'),
            PostSkill(id=4, post_id=3, skill_name='Japanese N2'),
            PostSkill(id=5, post_id=3, skill_name='IT background'),
            PostSkill(id=6, post_id=4, skill_name='Manual Testing'),
            PostSkill(id=7, post_id=5, skill_name='C++'),
            PostSkill(id=8, post_id=5, skill_name='Unity'),
            PostSkill(id=9, post_id=6, skill_name='Spark'),
            PostSkill(id=10, post_id=6, skill_name='Hadoop'),
            PostSkill(id=11, post_id=6, skill_name='Python'),
            PostSkill(id=12, post_id=7, skill_name='React Native'),
            PostSkill(id=13, post_id=8, skill_name='PenTest'),
            PostSkill(id=14, post_id=8, skill_name='CEH'),
            PostSkill(id=15, post_id=9, skill_name='Golang'),
            PostSkill(id=16, post_id=9, skill_name='Microservices'),
            PostSkill(id=17, post_id=10, skill_name='Docker'),
            PostSkill(id=18, post_id=10, skill_name='K8s'),
            PostSkill(id=19, post_id=10, skill_name='Linux'),
            PostSkill(id=20, post_id=11, skill_name='BPMN'),
            PostSkill(id=21, post_id=11, skill_name='UML'),
            PostSkill(id=22, post_id=11, skill_name='Finance'),
            PostSkill(id=23, post_id=12, skill_name='Network'),
            PostSkill(id=24, post_id=12, skill_name='CCNA'),
            PostSkill(id=25, post_id=13, skill_name='Python'),
            PostSkill(id=26, post_id=13, skill_name='Machine Learning'),
            PostSkill(id=27, post_id=14, skill_name='Kotlin'),
            PostSkill(id=28, post_id=14, skill_name='Android Studio'),
            PostSkill(id=29, post_id=15, skill_name='Swift'),
            PostSkill(id=30, post_id=16, skill_name='Automation Test'),
            PostSkill(id=31, post_id=16, skill_name='Leadership'),
            PostSkill(id=32, post_id=17, skill_name='NodeJS'),
            PostSkill(id=33, post_id=17, skill_name='Express'),
            PostSkill(id=34, post_id=17, skill_name='MongoDB'),
            PostSkill(id=35, post_id=18, skill_name='VueJS'),
            PostSkill(id=36, post_id=18, skill_name='CSS3'),
            PostSkill(id=37, post_id=19, skill_name='SQL'),
            PostSkill(id=38, post_id=19, skill_name='Tableau'),
            PostSkill(id=39, post_id=19, skill_name='Python'),
            PostSkill(id=40, post_id=20, skill_name='Agile'),
            PostSkill(id=41, post_id=20, skill_name='Scrum'),
            PostSkill(id=42, post_id=20, skill_name='UX/UI'),
        ]
        for skill in post_skills:
            db.session.add(skill)

        db.session.flush()

        applications = [
            Application(id=1, cv_id=1, post_id=1, applied_at=datetime(2026, 5, 4, 1, 11, 12),
                       ai_score=85, status='INTERVIEW', cover_letter='Em rất mong muốn được làm việc tại FPT'),
            Application(id=2, cv_id=2, post_id=2, applied_at=datetime(2026, 5, 4, 1, 11, 12),
                       ai_score=90, status='RECEIVED', cover_letter='Gửi công ty VNG bản CV Python của em'),
            Application(id=3, cv_id=3, post_id=7, applied_at=datetime(2026, 5, 4, 1, 11, 12),
                       ai_score=75, status='REJECT', cover_letter='Em đam mê React Native'),
            Application(id=4, cv_id=7, post_id=10, applied_at=datetime(2026, 5, 4, 1, 11, 12),
                       ai_score=95, status='APPROVED', cover_letter='Kinh nghiệm DevOps 3 năm xin ứng tuyển'),
        ]
        for app in applications:
            db.session.add(app)

        db.session.flush()

        histories = [
            ApplicationStatusHistory(id=1, application_id=1, old_status='RECEIVED', new_status='INTERVIEW',
                                    changed_at=datetime(2026, 5, 4, 1, 11, 13), changed_by_id=2,
                                    notes='Ứng viên tiềm năng, hẹn PV tuần sau'),
            ApplicationStatusHistory(id=2, application_id=4, old_status='RECEIVED', new_status='APPROVED',
                                    changed_at=datetime(2026, 5, 4, 1, 11, 13), changed_by_id=4,
                                    notes='Đã pass vòng kĩ thuật'),
        ]
        for history in histories:
            db.session.add(history)

        db.session.flush()

        reports = [
            PostReport(id=1, post_id=1, user_id=7, reason='Spam',
                      description='Tin tuyển dụng đăng lặp lại nhiều lần',
                      created_at=datetime(2026, 5, 4, 1, 11, 13), is_resolved=False),
            PostReport(id=2, post_id=12, user_id=8, reason='Lừa đảo',
                      description='Yêu cầu đóng phí trước khi phỏng vấn',
                      created_at=datetime(2026, 5, 4, 1, 11, 13), is_resolved=False),
        ]
        for report in reports:
            db.session.add(report)

        db.session.flush()

        notifications = [
            Notification(id=1, user_id=7, content='Bạn có lịch phỏng vấn với FPT',
                        type='INTERVIEW_INVITATION', created_at=datetime(2026, 5, 4, 1, 11, 13), is_read=False),
            Notification(id=2, user_id=10, content='Chúc mừng bạn đã trúng tuyển VNPay',
                        type='APPLICATION_STATUS_CHANGED', created_at=datetime(2026, 5, 4, 1, 11, 13), is_read=False),
            Notification(id=3, user_id=2, content='Tin tuyển dụng của bạn bị report',
                        type='POST_BLOCKED', created_at=datetime(2026, 5, 4, 1, 11, 13), is_read=False),
        ]
        for notif in notifications:
            db.session.add(notif)

        db.session.commit()
        print("Seed data completed successfully!")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding data: {str(e)}")
        raise


def main():
    app = create_app()
    with app.app_context():
        seed_data()


if __name__ == '__main__':
    main()
