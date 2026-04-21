import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
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
        success, message = update_account_profile(user, request.form)
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