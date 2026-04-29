import re
from app import db
from app.models import Application, Post, CV

from services.smtp_service import send_application_status_email

def calculate_ai_score(cv_id, post_id):
    """
    Tính điểm phù hợp giữa CV và Tin tuyển dụng dựa trên từ khóa kỹ năng.
    Trả về số nguyên từ 0-100.
    """
    cv = db.session.get(CV, cv_id)
    post = db.session.get(Post, post_id)
    
    if not cv or not post:
        return 0
        
    # Chuẩn hóa văn bản: chuyển thành chữ thường, xóa ký tự đặc biệt
    def normalize(text):
        if not text: return ""
        return re.sub(r'[^\w\s,]', '', text.lower())

    cv_text = normalize(f"{cv.skills} {cv.experience} {cv.summary}")
    post_skills = normalize(post.skills).split(',')
    
    # Làm sạch danh sách kỹ năng yêu cầu
    required_skills = [s.strip() for s in post_skills if s.strip()]
    if not required_skills:
        return 0
        
    matches = 0
    for skill in required_skills:
        # Tìm chính xác từ khóa trong CV
        if re.search(r'\b' + re.escape(skill) + r'\b', cv_text):
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

def update_application_status(application_id, new_status):
    app = db.session.get(Application, application_id)
    if app:
        old_status = app.status
        app.status = new_status
        db.session.commit()
        
        # Gửi email thông báo nếu trạng thái thay đổi
        if old_status != new_status:
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
