from flask import Blueprint, flash, redirect, render_template, request, url_for

from .service import (
    approve_company,
    delete_company,
    delete_post,
    delete_user,
    get_companies,
    get_company_by_id,
    get_current_admin,
    get_dashboard_stats,
    get_post_by_id,
    get_posts,
    get_user_by_id,
    get_users,
    toggle_user_status,
    update_admin_profile,
    update_post_status,
    update_user,
    get_post_reports,
    dismiss_post_reports,
)

admin_bp = Blueprint("admin_panel", __name__, url_prefix="/admin")


@admin_bp.before_request
def restrict_to_admin():
    admin = get_current_admin()
    if not admin:
        flash("Bạn không có quyền truy cập vào khu vực này.", "danger")
        return redirect(url_for("main.login"))


@admin_bp.app_context_processor
def inject_admin_context():
    return {"current_admin": get_current_admin()}


@admin_bp.route("/")
def index():
    admin = get_current_admin()
    stats = get_dashboard_stats(admin.id)
    return render_template("admin/index.html", stats=stats)


@admin_bp.route("/notifications/delete", methods=["POST"])
def delete_notifications():
    admin = get_current_admin()
    notification_ids = request.form.getlist("notification_ids")
    
    from .service import delete_admin_notifications
    success, message = delete_admin_notifications(admin.id, notification_ids)
    
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.index"))


@admin_bp.route("/accounts")
def accounts():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword")
    role = request.args.get("role")
    status = request.args.get("status")

    users = get_users(page, keyword, role, status)

    return render_template("admin/accounts.html", users=users)


@admin_bp.route("/profile", methods=["GET", "POST"])
def profile():
    user = get_current_admin()
    if not user:
        flash("Chưa có tài khoản quản trị viên trong hệ thống.", "warning")
        return redirect(url_for("admin_panel.accounts"))

    if request.method == "POST":
        success, message = update_admin_profile(user, request.form, request.files)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("admin_panel.profile"))

    return render_template("admin/profile.html", user=user)


@admin_bp.route("/accounts/<int:user_id>/edit", methods=["GET", "POST"])
def edit_account(user_id):
    user = get_user_by_id(user_id)
    next_url = request.args.get("next") or request.form.get("next")
    if not user:
        flash("Không tìm thấy tài khoản.", "danger")
        return redirect(url_for("admin_panel.accounts"))

    if request.method == "POST":
        success, message = update_user(user, request.form)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(next_url or url_for("admin_panel.accounts"))

    return render_template("admin/account_edit.html", user=user, next_url=next_url)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
def toggle_account(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Không tìm thấy tài khoản.", "danger")
        return redirect(url_for("admin_panel.accounts"))

    success, message = toggle_user_status(user)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.accounts", **request.args))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_account(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Không tìm thấy tài khoản.", "danger")
        return redirect(url_for("admin_panel.accounts"))

    success, message = delete_user(user)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.accounts", **request.args))


@admin_bp.route("/posts")
def posts():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword")
    status = request.args.get("status")
    is_reported = request.args.get("is_reported")

    if is_reported == "1":
        is_reported = True
    elif is_reported == "0":
        is_reported = False
    else:
        is_reported = None

    posts = get_posts(page, keyword, status, is_reported)

    return render_template("admin/posts.html", posts=posts)


@admin_bp.route("/posts/<int:post_id>/status", methods=["POST"])
def change_post_status(post_id):
    post = get_post_by_id(post_id)
    if not post:
        flash("Không tìm thấy tin tuyển dụng.", "danger")
        return redirect(url_for("admin_panel.posts"))

    new_status = request.form.get("status")
    success, message = update_post_status(post, new_status)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.posts", **request.args))


@admin_bp.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_route(post_id):
    post = get_post_by_id(post_id)
    if not post:
        flash("Không tìm thấy tin tuyển dụng.", "danger")
        return redirect(url_for("admin_panel.posts"))

    success, message = delete_post(post)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.posts", **request.args))


@admin_bp.route("/companies")
def companies():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword")
    status = request.args.get("status", "all")

    companies = get_companies(page, keyword, status)

    return render_template("admin/companies.html", companies=companies)


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
def approve_company_route(company_id):
    company = get_company_by_id(company_id)
    if not company:
        flash("Không tìm thấy thông tin công ty.", "danger")
        return redirect(url_for("admin_panel.companies"))

    success, message = approve_company(company)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.companies", **request.args))


@admin_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company_route(company_id):
    company = get_company_by_id(company_id)
    if not company:
        flash("Không tìm thấy thông tin công ty.", "danger")
        return redirect(url_for("admin_panel.companies"))

    success, message = delete_company(company)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.companies", **request.args))


@admin_bp.route("/posts/<int:post_id>/reports")
def view_post_reports(post_id):
    post = get_post_by_id(post_id)
    if not post:
        flash("Không tìm thấy tin tuyển dụng.", "danger")
        return redirect(url_for("admin_panel.posts"))

    reports = get_post_reports(post_id)
    return render_template("admin/post_reports.html", post=post, reports=reports)


@admin_bp.route("/posts/<int:post_id>/dismiss_reports", methods=["POST"])
def dismiss_reports(post_id):
    success, message = dismiss_post_reports(post_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin_panel.posts", **request.args))
