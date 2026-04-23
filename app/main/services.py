import json
import re
import secrets
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app, flash, session, url_for
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import cloudinary.uploader

from app import db
from app.models import User

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PASSWORD_STRENGTH_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$"
)
PHONE_PATTERN = re.compile(r"^(?:\+84|0)\d{9,10}$")


def inject_public_auth_context():
    return {"current_user": get_logged_in_user()}


def get_logged_in_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def require_logged_in_user():
    user = get_logged_in_user()
    if not user:
        flash("Vui lòng đăng nhập để tiếp tục.", "warning")
        return None
    return user


def validate_required_fields(form_data, fields):
    missing_labels = [label for key, label in fields if not (form_data.get(key) or "").strip()]
    if missing_labels:
        return False, "Vui lòng nhập đầy đủ: " + ", ".join(missing_labels) + "."
    return True, None


def validate_email(email):
    if not EMAIL_PATTERN.match(email or ""):
        return False, "Email không đúng định dạng."
    return True, None


def validate_phone(phone):
    if not PHONE_PATTERN.match(phone or ""):
        return False, "Số điện thoại không hợp lệ. Hãy dùng số Việt Nam như 09xxxxxxxx hoặc +84xxxxxxxxx."
    return True, None


def validate_password_strength(password):
    if not PASSWORD_STRENGTH_PATTERN.match(password or ""):
        return (
            False,
            "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt.",
        )
    return True, None


def get_display_name(user):
    return f"{user.last_name or ''} {user.first_name or ''}".strip() or user.email


def sync_authenticated_session(user):
    session["user_id"] = user.id
    session["user_name"] = get_display_name(user)
    session["user_role"] = "employer" if user.is_employer else "candidate"
    session.permanent = True


def parse_date_input(raw_value):
    raw_value = (raw_value or "").strip()
    if not raw_value:
        return True, None, None

    try:
        return True, datetime.strptime(raw_value, "%Y-%m-%d").date(), None
    except ValueError:
        return False, None, "Ngày sinh không đúng định dạng."


def update_account_profile(user, form_data, files=None):
    required_fields = [
        ("first_name", "tên"),
        ("last_name", "họ"),
    ]
    is_valid, error_message = validate_required_fields(form_data, required_fields)
    if not is_valid:
        return False, error_message

    phone = (form_data.get("phone") or "").strip()
    avatar_url = user.avatar_url

    if phone:
        is_valid, error_message = validate_phone(phone)
        if not is_valid:
            return False, error_message

    is_valid, date_of_birth, error_message = parse_date_input(form_data.get("date_of_birth"))
    if not is_valid:
        return False, error_message

    # Handle avatar upload
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

    user.first_name = (form_data.get("first_name") or "").strip() or None
    user.last_name = (form_data.get("last_name") or "").strip() or None
    user.phone = phone or None
    user.address = (form_data.get("address") or "").strip() or None
    user.sex = (form_data.get("sex") or "").strip() or None
    user.avatar_url = avatar_url
    user.date_of_birth = date_of_birth

    try:
        db.session.commit()
        sync_authenticated_session(user)
        return True, "Cập nhật hồ sơ thành công."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể cập nhật hồ sơ lúc này. Vui lòng thử lại."


def create_account(form_data):
    required_fields = [
        ("email", "email"),
        ("password", "mật khẩu"),
        ("confirm_password", "xác nhận mật khẩu"),
    ]
    is_valid, error_message = validate_required_fields(form_data, required_fields)
    if not is_valid:
        return False, error_message

    email = (form_data.get("email") or "").strip().lower()
    password = form_data.get("password") or ""
    confirm_password = form_data.get("confirm_password") or ""
    first_name = (form_data.get("first_name") or "").strip() or None
    last_name = (form_data.get("last_name") or "").strip() or None
    phone = (form_data.get("phone") or "").strip() or None
    role = "employer" if form_data.get("is_employer") == "on" else "candidate"

    is_valid, error_message = validate_email(email)
    if not is_valid:
        return False, error_message

    if User.query.filter_by(email=email).first():
        return False, "Email này đã tồn tại."

    is_valid, error_message = validate_password_strength(password)
    if not is_valid:
        return False, error_message

    if password != confirm_password:
        return False, "Mật khẩu xác nhận không khớp."

    user = User(
        email=email,
        password=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        is_active=True,
        is_admin=False,
        is_employer=role == "employer",
        created_at=datetime.utcnow(),
    )

    try:
        db.session.add(user)
        db.session.commit()
        return True, "Đăng ký tài khoản thành công. Bạn có thể đăng nhập bằng email hoặc Google nếu dùng cùng email này."
    except SQLAlchemyError:
        db.session.rollback()
        return False, "Không thể tạo tài khoản lúc này. Vui lòng thử lại."


def login_with_password(form_data):
    required_fields = [
        ("email", "email"),
        ("password", "mật khẩu"),
    ]
    is_valid, error_message = validate_required_fields(form_data, required_fields)
    if not is_valid:
        return False, error_message, None

    email = (form_data.get("email") or "").strip().lower()
    password = form_data.get("password") or ""

    is_valid, error_message = validate_email(email)
    if not is_valid:
        return False, error_message, None

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return False, "Email hoặc mật khẩu không chính xác.", None

    if not user.is_active:
        return False, "Tài khoản của bạn đang bị khóa.", None

    finalize_login(user)
    return True, "Đăng nhập thành công.", user


def finalize_login(user):
    user.last_login = datetime.utcnow()
    sync_authenticated_session(user)
    db.session.commit()


def build_google_redirect_uri():
    configured_uri = current_app.config.get("GOOGLE_REDIRECT_URI")
    if configured_uri:
        return configured_uri
    return url_for("main.google_callback", _external=True)


def build_google_state_token():
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    payload = {
        "nonce": secrets.token_urlsafe(16),
        "issued_at": int(datetime.utcnow().timestamp()),
    }
    return serializer.dumps(payload, salt="google-oauth-state")


def validate_google_state_token(state):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(state, salt="google-oauth-state", max_age=600)


def fetch_google_tokens(code):
    payload = urlencode(
        {
            "code": code,
            "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
            "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": build_google_redirect_uri(),
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request_obj = Request(
        "https://oauth2.googleapis.com/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request_obj, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_google_userinfo(access_token):
    request_obj = Request(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urlopen(request_obj, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def login_with_google_profile(profile):
    email = (profile.get("email") or "").strip().lower()
    if not email:
        return False, "Google không trả về email cho tài khoản này.", None

    if not profile.get("email_verified", False):
        return False, "Email Google chưa được xác minh.", None

    user = User.query.filter_by(email=email).first()
    if not user:
        full_name = (profile.get("name") or "").strip().split()
        user = User(
            email=email,
            password=generate_password_hash(secrets.token_urlsafe(24)),
            first_name=(profile.get("given_name") or (full_name[-1] if full_name else "")).strip() or None,
            last_name=(profile.get("family_name") or (" ".join(full_name[:-1]) if len(full_name) > 1 else "")).strip() or None,
            avatar_url=(profile.get("picture") or "").strip() or None,
            is_active=True,
            is_admin=False,
            is_employer=False,
            created_at=datetime.utcnow(),
        )
        db.session.add(user)

    if not user.is_active:
        db.session.rollback()
        return False, "Tài khoản của bạn đang bị khóa.", None

    if profile.get("picture"):
        user.avatar_url = profile.get("picture")

    finalize_login(user)
    return True, "Đăng nhập Google thành công.", user

