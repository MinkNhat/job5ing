from flask import Blueprint, render_template, request
from .service import get_users

admin_bp = Blueprint("admin_panel", __name__, url_prefix="/admin")


@admin_bp.route("/accounts")
def accounts():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword")
    role = request.args.get("role")
    status = request.args.get("status")

    users = get_users(page, keyword, role, status)

    return render_template("admin/accounts.html", users=users)