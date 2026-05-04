import re
from app import db
from app.models import Application, Post, CV, ApplicationStatusHistory

from services.smtp_service import send_application_status_email

def calculate_ai_score(cv_id, post_id):
    """
    Tính điểm phù hợp giữa CV và Tin tuyển dụng dựa trên từ khóa kỹ năng.
    Sử dụng CVSkill và PostSkill để lấy danh sách kỹ năng chuẩn xác.
    """
    cv = db.session.get(CV, cv_id)
    post = db.session.get(Post, post_id)
    
    if not cv or not post:
        return 0

    def normalize(text):
        if not text: return ""
        # Giữ lại các ký tự đặc biệt phổ biến trong kỹ năng công nghệ: +, #, ., /
        return re.sub(r'[^\w\s,+#./-]', '', text.lower())

    def get_skill_names(skills_obj):
        if not skills_obj: return []
        return [s.skill_name for s in skills_obj]

    required_skills = get_skill_names(post.skills)
    if not required_skills:
        return 0

    cv_skills = get_skill_names(cv.skills)
    cv_text = normalize(f"{' '.join(cv_skills)} {cv.experience or ''} {cv.summary or ''} {cv.cv_content or ''}")

    matches = 0
    for skill in required_skills:
        skill_norm = skill.lower().strip()
        if not skill_norm: continue
        
        # Tạo pattern tìm kiếm thông minh
        escaped_skill = re.escape(skill_norm)
        
        # Boundary ở phía trước: Nếu bắt đầu bằng ký tự từ (\w), dùng \b. 
        # Nếu bắt đầu bằng ký tự đặc biệt (như .net), không dùng \b.
        prefix = r'\b' if re.match(r'^\w', skill_norm) else r''
        
        # Boundary ở phía sau: Nếu kết thúc bằng ký tự từ (\w), dùng \b.
        # Nếu kết thúc bằng ký tự đặc biệt (như c++), không dùng \b.
        suffix = r'\b' if re.search(r'\w$', skill_norm) else r''
        
        pattern = prefix + escaped_skill + suffix
            
        if re.search(pattern, cv_text, re.IGNORECASE):
            matches += 1

    score = int((matches / len(required_skills)) * 100)
    return min(score, 100)

def get_applications_for_post(post_id, status_filter=None, sort_by_ai=False):
    """
    Lấy danh sách ứng viên cho một bài đăng cụ thể.
    """
    query = Application.query.filter_by(post_id=post_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    if sort_by_ai:
        query = query.order_by(Application.ai_score.desc())
    else:
        query = query.order_by(Application.applied_at.desc())
        
    return query

def update_application_status(application_id, new_status, changed_by_id=None):
    app = db.session.get(Application, application_id)
    if app:
        old_status = app.status
        if old_status == new_status:
            return True
            
        app.status = new_status
        
        # Ghi lại lịch sử thay đổi trạng thái
        history = ApplicationStatusHistory(
            application_id=app.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id
        )
        db.session.add(history)
        
        db.session.commit()
        
        # Gửi email thông báo nếu trạng thái thay đổi
        try:
            candidate = app.cv.user
            job_title = app.post.title
            company_name = app.post.recruiter.company.name
            
            send_application_status_email(
                user_email=candidate.email,
                user_name=f"{candidate.last_name or ''} {candidate.first_name or ''}".strip(),
                job_title=job_title,
                company_name=company_name,
                new_status=new_status
            )
        except Exception as e:
            print(f"Lỗi khi gửi mail thông báo trạng thái: {e}")
                
        return True
    return False
