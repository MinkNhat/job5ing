from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import User, Company, Post, PostSkill, Application, Notification, PostReport
from services.smtp_service import send_approval_email

def get_dashboard_stats(admin_id):
    total_users = User.query.count()
    total_companies = Company.query.count()
    total_posts = Post.query.count()
    total_applications = Application.query.count()

    active_posts = Post.query.filter_by(status='ACTIVE').count()
    pending_companies = Company.query.filter_by(is_approved=False).count()
    notifications = Notification.query.filter_by(user_id=admin_id)\
        .order_by(Notification.created_at.desc()).all()

    return {
        "total_users": total_users,
        "total_companies": total_companies,
        "total_posts": total_posts,
        "total_applications": total_applications,
        "active_posts": active_posts,
        "pending_companies": pending_companies,
        "notifications": notifications
    }

def delete_admin_notifications(admin_id, notification_ids):
    if not notification_ids:
        return False, "Chưa chọn thông báo nào."
    
    try:
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == admin_id
        ).delete(synchronize_session=False)
        db.session.commit()
        return True, "Đã xóa thông báo thành công."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Lỗi khi xóa thông báo."

def get_users(page=1, keyword=None, role=None, status=None):
    query = User.query

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                User.email.ilike(keyword_filter),
                User.first_name.ilike(keyword_filter),
                User.last_name.ilike(keyword_filter),
                User.phone.ilike(keyword_filter)
            )
        )

    if role and role != "all":
        role = role.strip().lower()
        if role == "admin":
            query = query.filter(User.is_admin.is_(True))
        elif role == "employer":
            query = query.filter(User.is_employer.is_(True))
        elif role == "user":
            query = query.filter(
                User.is_admin.is_(False),
                User.is_employer.is_(False)
            )

    if status and status != "all":
        status = status.strip().lower()
        if status in ("active", "1"):
            query = query.filter(User.is_active.is_(True))
        elif status in ("inactive", "0"):
            query = query.filter(User.is_active.is_(False))

    return query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


from flask import session

def get_current_admin():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if user and user.is_admin:
        return user
    return None


def update_user(user, form_data):
    email = (form_data.get("email") or "").strip()
    password = form_data.get("password")
    first_name = (form_data.get("first_name") or "").strip() or None
    last_name = (form_data.get("last_name") or "").strip() or None
    phone = (form_data.get("phone") or "").strip() or None
    address = (form_data.get("address") or "").strip() or None
    sex = (form_data.get("sex") or "").strip() or None
    role = (form_data.get("role") or "user").strip().lower()
    is_active = form_data.get("is_active") == "1"

    if not email:
        return False, "Email không được để trống."

    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        return False, "Email này đã tồn tại."

    user.email = email
    if password:
        user.set_password(password)
        
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone
    user.address = address
    user.sex = sex
    user.is_active = is_active

    user.is_admin = role == "admin"
    user.is_employer = role == "employer"

    try:
        db.session.commit()
        return True, "Cập nhật tài khoản thành công."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể cập nhật tài khoản. Vui lòng thử lại."


import cloudinary.uploader

def update_admin_profile(user, form_data, files=None):
    email = (form_data.get("email") or "").strip()
    first_name = (form_data.get("first_name") or "").strip() or None
    last_name = (form_data.get("last_name") or "").strip() or None
    phone = (form_data.get("phone") or "").strip() or None
    address = (form_data.get("address") or "").strip() or None
    sex = (form_data.get("sex") or "").strip() or None
    avatar_url = (form_data.get("avatar_url") or "").strip() or user.avatar_url

    if not email:
        return False, "Email không được để trống."

    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        return False, "Email này đã tồn tại."

    if files and "avatar" in files:
        avatar_file = files["avatar"]
        if avatar_file and avatar_file.filename:
            try:
                result = cloudinary.uploader.upload(
                    avatar_file,
                    folder="job5ing/avatars",
                    resource_type="auto",
                    overwrite=True,
                    unique_filename=False
                )
                avatar_url = result.get("secure_url")
            except Exception as e:
                return False, f"Không thể upload ảnh lên. Vui lòng thử lại. ({str(e)})"

    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone
    user.address = address
    user.sex = sex
    user.avatar_url = avatar_url

    try:
        db.session.commit()
        return True, "Đã cập nhật hồ sơ quản trị viên."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể cập nhật hồ sơ. Vui lòng thử lại."


def toggle_user_status(user):
    user.is_active = not user.is_active

    try:
        db.session.commit()
        if user.is_active:
            return True, "Đã mở khóa tài khoản."
        return True, "Đã khóa tài khoản."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể thay đổi trạng thái tài khoản."


def delete_user(user):
    try:
        db.session.delete(user)
        db.session.commit()
        return True, "Đã xóa tài khoản."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể xóa tài khoản. Tài khoản có thể đang liên kết với dữ liệu khác."


def get_posts(page=1, keyword=None, status=None, is_reported=None):
    query = Post.query

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Post.title.ilike(keyword_filter),
                Post.description.ilike(keyword_filter),
                Post.skills_list.any(PostSkill.skill_name.ilike(keyword_filter))
            )
        )

    if status and status != "all":
        query = query.filter(Post.status == status)

    if is_reported is not None:
        query = query.filter(Post.is_reported == is_reported)

    return query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)


def get_post_by_id(post_id):
    return db.session.get(Post, post_id)


def update_post_status(post, new_status):
    if new_status not in ['ACTIVE', 'OVERDUE', 'CLOSED', 'PINNED', 'BLOCKED']:
        return False, "Trạng thái không hợp lệ."

    post.status = new_status
    try:
        db.session.commit()
        return True, f"Đã cập nhật trạng thái tin tuyển dụng thành {new_status}."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể cập nhật trạng thái tin tuyển dụng."


def delete_post(post):
    try:
        db.session.delete(post)
        db.session.commit()
        return True, "Đã xóa tin tuyển dụng thành công."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể xóa tin tuyển dụng."


def get_companies(page=1, keyword=None, status=None):
    query = Company.query

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Company.name.ilike(keyword_filter),
                Company.tax_code.ilike(keyword_filter),
                Company.location.ilike(keyword_filter)
            )
        )

    if status == "approved":
        query = query.filter(Company.is_approved.is_(True))
    elif status == "pending":
        query = query.filter(Company.is_approved.is_(False))

    return query.order_by(Company.id.desc()).paginate(page=page, per_page=10)


def get_company_by_id(company_id):
    return db.session.get(Company, company_id)


def approve_company(company):
    if company.is_approved:
        return False, "Công ty này đã được duyệt trước đó."

    company.is_approved = True
    for recruiter in company.recruiters:
        notification = Notification(
            user_id=recruiter.user_id,
            content=f"Công ty {company.name} của bạn đã được phê duyệt.",
            type='ACCOUNT_APPROVED'
        )
        db.session.add(notification)
        if recruiter.user and recruiter.user.email:
            send_approval_email(recruiter.user.email, company.name)

    try:
        db.session.commit()
        return True, f"Đã phê duyệt công ty {company.name} và gửi thông báo."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể phê duyệt công ty. Vui lòng thử lại."


def delete_company(company):
    try:
        db.session.delete(company)
        db.session.commit()
        return True, "Đã xóa thông tin công ty."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể xóa công ty do có dữ liệu liên quan."


def get_post_reports(post_id):
    return PostReport.query.filter_by(post_id=post_id, is_resolved=False).all()


def dismiss_post_reports(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return False, "Không tìm thấy tin tuyển dụng."
    
    try:
        PostReport.query.filter_by(post_id=post_id).update({"is_resolved": True})
        post.is_reported = False
        db.session.commit()
        return True, "Đã gỡ bỏ báo cáo cho tin này."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Lỗi khi xử lý gỡ báo cáo."
