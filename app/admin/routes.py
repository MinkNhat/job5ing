from flask import Blueprint, flash, redirect, render_template, request, url_for

from .service import (
    delete_user,
    get_current_admin,
    get_user_by_id,
    get_users,
    toggle_user_status,
    update_admin_profile,
    update_user,
)

admin_bp = Blueprint("admin_panel", __name__, url_prefix="/admin")


@admin_bp.app_context_processor
def inject_admin_context():
    return {"current_admin": get_current_admin()}


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
        success, message = update_admin_profile(user, request.form)
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
