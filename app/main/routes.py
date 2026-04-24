import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for, jsonify
from itsdangerous import BadSignature, BadTimeSignature
from sqlalchemy.exc import SQLAlchemyError

from .constants import HOME_FEATURED_JOBS, HOME_LOCATIONS
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
    get_user_cv,
    preview_resume,
    save_resume,
)

main_bp = Blueprint("main", __name__)

@main_bp.app_context_processor
def provide_public_context():
    return inject_public_auth_context()

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
        success, message = create_account(request.form)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("main.login"))

    return render_template("auth/register.html")


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
        success, message = update_account_profile(user, request.form, request.files)
        flash(message, "success" if success else "danger")
        return redirect(url_for("main.account"))

    return render_template("public/account.html", user=user)


@main_bp.route("/login/google")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google đăng nhập chưa được cấu hình. Hãy thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET.", "warning")
        return redirect(url_for("main.login"))

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
        success, message = login_with_google_profile(profile)
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


@main_bp.route("/preview-resume", methods=["POST"])
def preview_resume_endpoint():
    user = require_logged_in_user()

    try:
        is_valid, cv_url, cv_data, error_message = preview_resume(request.files)
        if not is_valid:
            return jsonify({"success": False, "message": error_message}), 400

        return jsonify({
            "success": True,
            "message": "Preview CV thành công",
            "cv_url": cv_url,
            "cv_data": {
                "title": cv_data.get("title") or "",
                "summary": cv_data.get("summary") or "",
                "skills": cv_data.get("skills") or "",
                "experience": cv_data.get("experience") or "",
                "education": cv_data.get("education") or ""
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500


@main_bp.route("/resume", methods=["GET", "POST"])
def resume():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login"))

    if user.is_employer:
        flash("Chỉ ứng viên mới có thể quản lý CV.", "warning")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        success, message = save_resume(user, request.form)
        flash(message, "success" if success else "danger")
        return redirect(url_for("main.resume"))

    cv = get_user_cv(user)
    return render_template("public/resume.html", user=user, cv=cv)
