import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from itsdangerous import BadSignature, BadTimeSignature
from sqlalchemy.exc import SQLAlchemyError

from .constants import HOME_FEATURED_JOBS, HOME_LOCATIONS, COMPANY_SCALE_OPTIONS
from .services import (
    fetch_google_tokens,
    fetch_google_userinfo,
    inject_public_auth_context,
    login_with_google_profile,
    login_with_password,
    require_logged_in_user,
    update_account_profile,
    create_account,
    build_google_redirect_uri,
    build_google_state_token,
    validate_google_state_token,
)

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template(
        "public/index.html",
        featured_jobs=HOME_FEATURED_JOBS,
        locations=HOME_LOCATIONS,
    )

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        is_employer = request.form.get("is_employer") == "on"
        success, message = create_account(request.form)
        flash(message, "success" if success else "danger")
        if success:
            if is_employer:
                return redirect(url_for("main.recruiter_request"))
            return redirect(url_for("main.login"))

    return render_template("auth/register.html")


from app.models import Company, Recruiter, User
from app import db

@main_bp.route("/recruiter-request", methods=["GET"])
def recruiter_request():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login"))
    
    companies = Company.query.all()
    return render_template("auth/recruiter_request.html", 
                           companies=companies, 
                           scale_options=COMPANY_SCALE_OPTIONS)

@main_bp.route("/submit-join-request", methods=["POST"])
def submit_join_request():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login"))
    
    company_id = request.form.get("company_id")
    position = request.form.get("position")
    
    if not company_id or not position:
        flash("Vui lòng điền đầy đủ thông tin.", "danger")
        return redirect(url_for("main.recruiter_request"))
    
    # Tạo recruiter mới
    recruiter = Recruiter(
        user_id=user.id,
        company_id=company_id,
        position=position,
        is_approved=False,
        is_company_admin=False
    )
    
    try:
        db.session.add(recruiter)
        user.is_employer = True # Đảm bảo user có flag employer
        db.session.commit()
        session["user_role"] = "employer"
        flash("Yêu cầu gia nhập công ty đã được gửi và đang chờ duyệt.", "success")
        return redirect(url_for("main.index"))
    except SQLAlchemyError:
        db.session.rollback()
        flash("Có lỗi xảy ra, vui lòng thử lại.", "danger")
        return redirect(url_for("main.recruiter_request"))

@main_bp.route("/register-company", methods=["POST"])
def register_company():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login"))
    
    name = request.form.get("name")
    tax_code = request.form.get("taxCode")
    location = request.form.get("location")
    website = request.form.get("website")
    establish_date_str = request.form.get("establishDate")
    scale = request.form.get("scale")
    position = request.form.get("position")
    
    if not name or not tax_code:
        flash("Vui lòng điền tên công ty và mã số thuế.", "danger")
        return redirect(url_for("main.recruiter_request"))

    from datetime import datetime
    establish_date = None
    if establish_date_str:
        try:
            establish_date = datetime.strptime(establish_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
            
    # Tạo công ty mới
    new_company = Company(
        name=name,
        tax_code=tax_code,
        location=location,
        website=website,
        establish_date=establish_date,
        scale=scale, # Lưu trực tiếp giá trị được chọn (ví dụ: "201-500 nhân viên")
        is_approved=False,
        business_license="pending"
    )
    
    try:
        db.session.add(new_company)
        db.session.flush()
        
        # Tạo recruiter cho user này
        recruiter = Recruiter(
            user_id=user.id,
            company_id=new_company.id,
            position=position or "Quản trị viên",
            is_approved=True,
            is_company_admin=True
        )
        db.session.add(recruiter)
        user.is_employer = True
        db.session.commit()
        session["user_role"] = "employer"
        flash("Đăng ký công ty thành công. Công ty đang chờ hệ thống phê duyệt.", "success")
        return redirect(url_for("main.index"))
    except SQLAlchemyError:
        db.session.rollback()
        flash("Có lỗi xảy ra khi đăng ký công ty.", "danger")
        return redirect(url_for("main.recruiter_request"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        success, message = login_with_password(request.form)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("main.index"))

    return render_template(
        "auth/login.html",
        google_login_ready=bool(
            current_app.config.get("GOOGLE_CLIENT_ID")
            and current_app.config.get("GOOGLE_CLIENT_SECRET")
        ),
    )


@main_bp.route("/account", methods=["GET", "POST"])
def account():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        success, message = update_account_profile(user, request.form)
        flash(message, "success" if success else "danger")
        return redirect(url_for("main.account"))

    return render_template("public/account.html", user=user)


@main_bp.route("/login/google")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google đăng nhập chưa được cấu hình. Hãy thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET.", "warning")
        return redirect(url_for("main.login"))

    # Lưu trạng thái nhà tuyển dụng vào session để xử lý sau khi callback
    if request.args.get("is_employer") == "true":
        session["google_is_employer"] = True
    else:
        session.pop("google_is_employer", None)

    state = build_google_state_token()

    query = {
        "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
        "redirect_uri": build_google_redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }

    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query)}")


@main_bp.route("/login/google/callback")
def google_callback():
    returned_state = request.args.get("state")
    if not returned_state:
        flash("Không nhận được thông tin xác thực Google. Vui lòng thử lại.", "danger")
        return redirect(url_for("main.login"))

    try:
        validate_google_state_token(returned_state)
    except (BadSignature, BadTimeSignature):
        flash("Phiên đăng nhập Google không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.", "danger")
        return redirect(url_for("main.login"))

    error = request.args.get("error")
    if error:
        flash(f"Google đăng nhập bị từ chối: {error}.", "danger")
        return redirect(url_for("main.login"))

    code = request.args.get("code")
    if not code:
        flash("Không nhận được mã xác thực từ Google.", "danger")
        return redirect(url_for("main.login"))

    try:
        token_data = fetch_google_tokens(code)
        profile = fetch_google_userinfo(token_data["access_token"])
        
        # Kiểm tra xem user có muốn đăng ký làm recruiter không (lấy từ session đã lưu ở route google_login)
        target_is_employer = session.pop("google_is_employer", False)
        
        success, message = login_with_google_profile(profile)
        
        if success and target_is_employer:
            from app.models import User
            from app import db
            user = User.query.filter_by(email=profile.get("email").lower()).first()
            if user:
                user.is_employer = True
                db.session.commit()
                # Cập nhật lại session role
                session["user_role"] = "employer"
                flash("Đăng ký tài khoản nhà tuyển dụng qua Google thành công.", "success")
                return redirect(url_for("main.recruiter_request"))

        flash(message, "success" if success else "danger")
        return redirect(url_for("main.index" if success else "main.login"))
    except (HTTPError, URLError, KeyError, SQLAlchemyError, json.JSONDecodeError):
        from app import db
        db.session.rollback()
        flash("Không thể hoàn tất đăng nhập Google lúc này. Vui lòng kiểm tra lại cấu hình và thử lại.", "danger")
        return redirect(url_for("main.login"))


@main_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("main.index"))
