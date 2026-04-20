from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import User

def get_users(page=1, keyword=None, role=None, status=None):
    query = User.query
    if keyword:
        query = query.filter(User.email.contains(keyword))

    if role:
        role = role.strip().lower()
        if role != "all":
            if role in ("admin", "quản trị", "quan-tri"):
                query = query.filter(User.is_admin.is_(True))
            elif role in ("employer", "recruiter", "nhà tuyển dụng", "nha-tuyen-dung"):
                query = query.filter(User.is_employer.is_(True))
            elif role in ("user", "candidate", "ứng viên", "ung-vien"):
                query = query.filter(
                    User.is_admin.is_(False),
                    User.is_employer.is_(False)
                )

    if status:
        status = status.strip().lower()
        if status != "all":
            if status in ("active", "hoạt động", "hoat-dong"):
                query = query.filter(User.is_active.is_(True))
            elif status in ("inactive", "locked", "blocked", "khóa", "khoa"):
                query = query.filter(User.is_active.is_(False))

    return query.order_by(User.id.desc()).paginate(page=page, per_page=5)


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


def get_current_admin():
    return User.query.filter(User.is_admin.is_(True)).order_by(User.id.asc()).first()


def update_user(user, form_data):
    email = (form_data.get("email") or "").strip()
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


def update_admin_profile(user, form_data):
    email = (form_data.get("email") or "").strip()
    first_name = (form_data.get("first_name") or "").strip() or None
    last_name = (form_data.get("last_name") or "").strip() or None
    phone = (form_data.get("phone") or "").strip() or None
    address = (form_data.get("address") or "").strip() or None
    sex = (form_data.get("sex") or "").strip() or None
    avatar_url = (form_data.get("avatar_url") or "").strip() or None

    if not email:
        return False, "Email không được để trống."

    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        return False, "Email này đã tồn tại."

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
