from datetime import datetime, date, timedelta
import random
from app import create_app, db
from app.models import (
    Location, CompanyScale, ExperienceOption, SalaryOption,
    Company, User, Recruiter, CV, CVSkill, CVEducation, CVExperience, Post, PostSkill,
    Application, ApplicationStatusHistory, PostReport, Notification
)
from app.main.recruiter_services import calculate_ai_score


def seed_data():
    # Luôn reset database để dữ liệu đồng bộ và mới nhất cho demo
    db.drop_all()
    db.create_all()

    try:
        print("🚀 Đang khởi tạo bộ dữ liệu mẫu SIÊU CẤP (Mega Demo Seed)...")

        # 1. Cấu hình cơ bản
        locations = [
            Location(id=1, name='TP. Hồ Chí Minh'),
            Location(id=2, name='Hà Nội'),
            Location(id=3, name='Đà Nẵng'),
            Location(id=4, name='Cần Thơ'),
            Location(id=5, name='Hải Phòng'),
            Location(id=6, name='Bình Dương'),
        ]
        db.session.add_all(locations)

        scales = [
            CompanyScale(id=1, name='1-50 nhân viên'),
            CompanyScale(id=2, name='51-200 nhân viên'),
            CompanyScale(id=3, name='201-500 nhân viên'),
            CompanyScale(id=4, name='501-1000 nhân viên'),
            CompanyScale(id=5, name='1000+ nhân viên'),
        ]
        db.session.add_all(scales)

        experiences = [
            ExperienceOption(id=1, name='Không yêu cầu'),
            ExperienceOption(id=2, name='<1 năm'),
            ExperienceOption(id=3, name='1-3 năm'),
            ExperienceOption(id=4, name='3-5 năm'),
            ExperienceOption(id=5, name='>5 năm'),
            ExperienceOption(id=6, name='Cấp Quản lý'),
        ]
        db.session.add_all(experiences)

        salaries = [
            SalaryOption(id=1, name='Không lương'),
            SalaryOption(id=2, name='1-3 triệu'),
            SalaryOption(id=3, name='3-5 triệu'),
            SalaryOption(id=4, name='5-10 triệu'),
            SalaryOption(id=5, name='10-20 triệu'),
            SalaryOption(id=6, name='20-30 triệu'),
            SalaryOption(id=7, name='Trên 30 triệu'),
            SalaryOption(id=8, name='Thỏa thuận'),
        ]
        db.session.add_all(salaries)
        db.session.flush()

        # 2. Người dùng (Users) - Giữ nguyên 10 user gốc
        admin_pass = 'scrypt:32768:8:1$DBfLeANMNIhwOcCg$b25e8284c507670c1c0be1e025d35c9412f7b9f6debe8a37710f62f94dbabc139a4bf578da24c45ec987818b72271e54a8a3bd4b9502be953a59203b49116d28'

        users = [
            User(id=1, password=admin_pass, first_name='Admin', last_name='System',
                 email='admin@testjob5ing.com', phone='0901234567',
                 address='Tòa nhà Admin, Quận 1, TP.HCM', date_of_birth=date(1990, 1, 1),
                 sex='Male', is_active=True, is_admin=True, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=admin'),
            User(id=2, password=admin_pass, first_name='Huy', last_name='Tran',
                 email='huy@testjob5ing.com', phone='0912345678',
                 address='Quận Cầu Giấy, Hà Nội', date_of_birth=date(1992, 5, 12),
                 sex='Male', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=huy'),
            User(id=3, password=admin_pass, first_name='Anh', last_name='Pham',
                 email='anh@testjob5ing.com', phone='0923456789',
                 address='Quận 3, TP.HCM', date_of_birth=date(1995, 8, 20),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=anh'),
            User(id=4, password=admin_pass, first_name='Long', last_name='Nguyen',
                 email='long@testjob5ing.com', phone='0934567890',
                 address='Quận Hải Châu, Đà Nẵng', date_of_birth=date(1988, 11, 5),
                 sex='Male', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=long'),
            User(id=5, password=admin_pass, first_name='Khanh', last_name='Le',
                 email='khanh@testjob5ing.com', phone='0945678901',
                 address='Quận Ninh Kiều, Cần Thơ', date_of_birth=date(1994, 2, 14),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=khanh'),
            User(id=6, password=admin_pass, first_name='Linh', last_name='Nguyen',
                 email='linh@testjob5ing.com', phone='0956789012',
                 address='Quận 7, TP.HCM', date_of_birth=date(1991, 9, 30),
                 sex='Female', is_active=True, is_admin=False, is_employer=True,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=linh'),
            User(id=7, password=admin_pass, first_name='Minh', last_name='Le',
                 email='minh@testjob5ing.com', phone='0967890123',
                 address='Quận Tân Bình, TP.HCM', date_of_birth=date(1998, 4, 25),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 3, 18, 49, 35),
                 avatar_url='https://i.pravatar.cc/150?u=minh'),
            User(id=8, password=admin_pass, first_name='Tuan', last_name='Vo',
                 email='tuan@testjob5ing.com', phone='0978901234',
                 address='Quận Đống Đa, Hà Nội', date_of_birth=date(2000, 12, 10),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=tuan'),
            User(id=9, password=admin_pass, first_name='Trang', last_name='Pham',
                 email='trang@testjob5ing.com', phone='0989012345',
                 address='Quận Sơn Trà, Đà Nẵng', date_of_birth=date(1999, 7, 7),
                 sex='Female', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=trang'),
            User(id=10, password=admin_pass, first_name='Nam', last_name='Hoang',
                 email='nam@testjob5ing.com', phone='0990123456',
                 address='Quận 10, TP.HCM', date_of_birth=date(1997, 3, 18),
                 sex='Male', is_active=True, is_admin=False, is_employer=False,
                 created_at=datetime(2026, 5, 4, 1, 11, 12), last_login=datetime(2026, 5, 4, 1, 11, 12),
                 avatar_url='https://i.pravatar.cc/150?u=nam'),
        ]

        # Thêm 100 User mới để demo quy mô lớn
        vn_last = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ',
                   'Ngô', 'Dương']
        vn_mid = ['Văn', 'Thị', 'Minh', 'Anh', 'Ngọc', 'Quang', 'Xuân', 'Đức', 'Trọng', 'Kim', 'Thanh', 'Hải']
        vn_first = ['Hùng', 'Tuấn', 'Dũng', 'Lan', 'Hương', 'Linh', 'Thành', 'Bảo', 'Long', 'Tiến', 'Việt', 'Nam',
                    'Trang', 'Mai', 'Chi', 'An', 'Bình']

        all_candidate_ids = list(range(7, 11))
        all_user_ids = list(range(1, 11))
        for i in range(11, 121):
            is_emp = i > 105  # Các user cuối làm employer
            fname, lname = f"{random.choice(vn_mid)} {random.choice(vn_first)}", random.choice(vn_last)
            u = User(id=i, password=admin_pass, first_name=fname, last_name=lname, email=f'user{i}@demo.com',
                     phone=f'09{random.randint(10000000, 99999999)}', address=f'Số {i}, Đường ABC, TP.HCM',
                     is_active=True, is_admin=False, is_employer=is_emp,
                     date_of_birth=date(1985 + random.randint(0, 20), 1, 1), sex=random.choice(['Male', 'Female']))
            users.append(u)
            all_user_ids.append(i)
            if not is_emp:
                all_candidate_ids.append(i)

        db.session.add_all(users)
        db.session.flush()

        # 3. Công ty (Companies) - 15 Công ty với thông tin đầy đủ
        company_specs = [
            ('FPT Software', 'fpt.com',
             'Tập đoàn công nghệ hàng đầu Việt Nam, chuyên cung cấp các giải pháp chuyển đổi số toàn cầu và dịch vụ CNTT chất lượng cao cho thị trường Nhật, Mỹ, Âu.'),
            ('VNG Corporation', 'vng.com.vn',
             'Công ty internet hàng đầu Việt Nam, sở hữu hệ sinh thái Zing, Zalo, ZaloPay và hàng loạt tựa game nổi tiếng toàn cầu.'),
            ('VNPay', 'vnpay.vn',
             'Đơn vị đi đầu trong lĩnh vực Fintech tại Việt Nam với mạng lưới thanh toán QR Code phủ khắp cả nước và các giải pháp ngân hàng số hiện đại.'),
            ('MoMo', 'momo.vn',
             'Siêu ứng dụng thanh toán số 1 Việt Nam, phục vụ hàng chục triệu người dùng với các dịch vụ tài chính, giải trí và mua sắm tiện lợi.'),
            ('Tiki', 'tiki.vn',
             'Hệ sinh thái thương mại điện tử "All-in-one" uy tín nhất Việt Nam với hệ thống Logistics hiện đại và dịch vụ khách hàng tận tâm.'),
            ('Viettel Tech', 'viettel.vn',
             'Khối công nghệ và viễn thông thuộc tập đoàn Viettel, doanh nghiệp viễn thông lớn nhất Việt Nam và top đầu khu vực.'),
            ('Grab Vietnam', 'grab.com',
             'Siêu ứng dụng đa dịch vụ hàng đầu Đông Nam Á, cung cấp các giải pháp di chuyển, giao hàng và tài chính cho mọi người.'),
            ('Shopee Vietnam', 'shopee.vn',
             'Nền tảng thương mại điện tử phổ biến nhất Việt Nam, thuộc tập đoàn SEA Limited, mang lại trải nghiệm mua sắm dễ dàng.'),
            ('Techcombank IT', 'techcombank.com',
             'Khối công nghệ của ngân hàng tư nhân lớn nhất Việt Nam, tiên phong trong hành trình chuyển đổi số ngành tài chính.'),
            ('VinTech', 'vin-tech.net',
             'Đơn vị nghiên cứu và phát triển công nghệ cao thuộc tập đoàn Vingroup, tập trung vào AI, Big Data và Robot.'),
            ('CMC Global', 'cmcglobal.com.vn',
             'Công ty cung cấp giải pháp phần mềm và dịch vụ CNTT quốc tế hàng đầu, đối tác tin cậy của nhiều doanh nghiệp lớn trên thế giới.'),
            ('Vietcombank Digital', 'vietcombank.com.vn',
             'Trung tâm chuyển đổi số của ngân hàng Vietcombank, xây dựng các hệ thống ngân hàng thế hệ mới cho hàng triệu khách hàng.'),
            ('NashTech', 'nashtechglobal.com',
             'Tư vấn và phát triển giải pháp phần mềm toàn cầu, có môi trường làm việc chuyên nghiệp chuẩn quốc tế.'),
            ('KMS Technology', 'kms-technology.com',
             'Công ty phát triển phần mềm chất lượng cao từ Mỹ, chuyên cung cấp các sản phẩm và dịch vụ công nghệ cho thị trường toàn cầu.'),
            ('Amanotes', 'amanotes.com',
             'Công ty game âm nhạc (Music Games) hàng đầu thế giới, sở hữu hàng tỷ lượt tải trên các kho ứng dụng di động.')
        ]

        companies = []
        for i, (name, site, desc) in enumerate(company_specs):
            c = Company(id=i + 1, name=name, location=f'Tòa nhà {name}, Quận 1, TP.HCM',
                        city_id=random.randint(1, 4), website=site,
                        establish_date=date(1995 + random.randint(0, 25), 1, 1),
                        scale_id=random.randint(1, 5), tax_code=f'TAX{i + 1:05d}', description=desc,
                        is_approved=True, avatar_url=f'https://logo.clearbit.com/{site}',
                        business_license=f'license_{i + 1}.pdf')
            companies.append(c)
        db.session.add_all(companies)
        db.session.flush()

        # 4. Nhà tuyển dụng (Recruiters)
        recruiters = []
        # Users 2-6 là HR cho các công ty đầu
        for i in range(2, 7):
            r = Recruiter(user_id=i, company_id=i - 1, position='HR Manager', is_approved=True, is_company_admin=True)
            recruiters.append(r)

        # Thêm HR cho các công ty còn lại từ các user mới
        for i in range(106, 121):
            cid = (i - 106) % 15 + 1
            r = Recruiter(user_id=i, company_id=cid, position='Lead Recruiter', is_approved=True, is_company_admin=True)
            recruiters.append(r)
        db.session.add_all(recruiters)
        db.session.flush()

        # 5. Bài đăng (Posts) - 60+ Tin với mô tả chi tiết
        stacks = {
            'Java': 'Java, Spring Boot, MySQL, Docker, Microservices, Hibernate, Kafka, Redis',
            'Python': 'Python, FastAPI, Django, PostgreSQL, Docker, Redis, Celery, MongoDB',
            'Frontend': 'ReactJS, TypeScript, Next.js, Tailwind CSS, HTML5, CSS3, Redux, Figma',
            'DevOps': 'AWS, Kubernetes, CI/CD, Terraform, Linux, Ansible, Docker, Jenkins',
            'QA': 'Manual Test, Automation Test, Selenium, JIRA, SQL, Cypress, Appium',
            'Mobile': 'Flutter, Dart, Firebase, SQLite, Clean Architecture, Android, iOS',
            'Bridge': 'Java, Project Management, Japanese N2, Communication, Bridge SE',
            'AI': 'Python, PyTorch, TensorFlow, Computer Vision, Machine Learning, NLP'
        }

        all_posts = []
        today = date.today()
        for i in range(1, 61):
            stack_name = random.choice(list(stacks.keys()))
            skills_str = stacks[stack_name]
            p = Post(
                id=i, recruiter_id=random.choice(recruiters).user_id,
                title=f"{stack_name} Developer - {random.choice(['Senior', 'Junior', 'Middle'])}",
                description=f"### MÔ TẢ CÔNG VIỆC\n- Thiết kế và phát triển hệ thống {stack_name} quy mô lớn, đảm bảo tính sẵn sàng và hiệu năng cao.\n- Tham gia vào toàn bộ vòng đời phát triển phần mềm từ ý tưởng, thiết kế đến triển khai.\n- Phối hợp chặt chẽ với team thiết kế và quản lý sản phẩm để đưa ra giải pháp tốt nhất.\n\n### YÊU CẦU\n- Thành thạo: {skills_str}.\n- Có tư duy lập trình tốt, am hiểu về cấu trúc dữ liệu và giải thuật.\n- Khả năng làm việc độc lập và kỹ năng làm việc nhóm hiệu quả.\n\n### QUYỀN LỢI\n- Mức lương cạnh tranh, tương xứng với năng lực.\n- Thưởng tháng lương 13, 14 và các khoản thưởng hiệu quả kinh doanh.\n- Được tham gia các khóa đào tạo chuyên sâu và lộ trình thăng tiến rõ ràng.",
                experience_id=random.randint(2, 5), salary_id=random.randint(4, 7),
                deadline=today + timedelta(days=random.randint(15, 120)),
                status='PINNED' if i <= 6 else 'ACTIVE'
            )
            db.session.add(p)
            db.session.flush()
            p.skills = skills_str
            all_posts.append(p)

            # Thêm PostSkill (cho backward compatibility nếu dùng bảng này)
            for s in skills_str.split(', '):
                db.session.add(PostSkill(post_id=p.id, skill_name=s))

        # 6. CVs (Đầy đủ hồ sơ cho 100+ ứng viên)
        cvs = []
        for i, uid in enumerate(all_candidate_ids, 1):
            stack_name = random.choice(list(stacks.keys()))
            is_match = random.random() < 0.7  # 70% khớp hoàn toàn để demo AI
            my_skills = stacks[stack_name] if is_match else "Giao tiếp, Tin học văn phòng, Anh văn cơ bản"

            cv = CV(
                id=i, user_id=uid, title=f"Kỹ sư {stack_name} - Chuyên gia hệ thống",
                summary=f"Tôi là một lập trình viên {stack_name} với niềm đam mê xây dựng những sản phẩm công nghệ tuyệt vời. Tôi đã có kinh nghiệm làm việc trong các dự án quy mô vừa và lớn, luôn hướng tới việc tối ưu hóa mã nguồn và mang lại giá trị cao nhất cho doanh nghiệp.",
                cv_url=f"https://job5ing.s3.amazonaws.com/cvs/cv_{i}.pdf",
                cv_content=f"Thông tin chi tiết của ứng viên {uid}.\nKỹ năng chuyên môn: {my_skills}.\nKinh nghiệm làm việc: 5 năm tại các công ty lớn."
            )
            cv.skills = my_skills  # Trigger setter để thêm vào CVSkill table
            db.session.add(cv)
            db.session.flush()

            # Thêm Education detail
            db.session.add(CVEducation(cv_id=i, school='Đại học Bách Khoa', major='Công nghệ Thông tin',
                                       start_date=date(2018, 9, 1), end_date=date(2022, 6, 30)))
            # Thêm Experience detail
            db.session.add(
                CVExperience(cv_id=i, job_title=f'{stack_name} Developer', company_name='Global Software Co.',
                             position='Senior Engineer',
                             description='Chịu trách nhiệm thiết kế và triển khai các tính năng quan trọng.',
                             start_date=date(2022, 7, 1)))
            cvs.append(cv)

        # 7. Đơn ứng tuyển (Applications) - 350+ Đơn với AI Score thực tế
        print("📝 Đang tạo 350+ đơn ứng tuyển...")
        applied_pairs = set()
        count = 0
        while count < 350:
            p = random.choice(all_posts)
            cv = random.choice(cvs)
            if (p.id, cv.id) not in applied_pairs:
                applied_pairs.add((p.id, cv.id))
                score = calculate_ai_score(cv.id, p.id)
                status = random.choice(['RECEIVED', 'INTERVIEW', 'APPROVED', 'REJECT'])
                app = Application(cv_id=cv.id, post_id=p.id, ai_score=score, status=status,
                                  applied_at=datetime.now() - timedelta(days=random.randint(0, 20)),
                                  cover_letter=f"Kính gửi bộ phận tuyển dụng, tôi là {cv.user.first_name}, tôi tin rằng kinh nghiệm {cv.skills} của tôi rất phù hợp với vị trí {p.title} của quý công ty.")
                db.session.add(app)
                db.session.flush()

                # Thêm History
                if status != 'RECEIVED':
                    db.session.add(
                        ApplicationStatusHistory(application_id=app.id, old_status='RECEIVED', new_status=status,
                                                 notes='Hồ sơ đạt yêu cầu sơ loại.'))
                count += 1

        # 8. Báo cáo & Thông báo
        for _ in range(15):
            db.session.add(PostReport(post_id=random.randint(1, 60), user_id=random.choice(all_candidate_ids),
                                      reason='Spam', description='Nội dung tin tuyển dụng trùng lặp.',
                                      is_resolved=False))

        for i in range(60):
            db.session.add(
                Notification(user_id=random.choice(all_user_ids), content=f'Thông báo hệ thống về hồ sơ số {i + 1}',
                             type=random.choice(['NEW_APPLICATION', 'APPLICATION_STATUS_CHANGED'])))

        db.session.commit()
        print(f"THÀNH CÔNG! Đã khởi tạo {count} đơn ứng tuyển và bộ dữ liệu SIÊU CẤP cho Demo.")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi seed dữ liệu: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main_app = create_app()
    with main_app.app_context():
        seed_data()
