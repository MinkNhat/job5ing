from flask import Blueprint, flash, redirect, render_template, request, url_for

from .service import (
    get_dashboard_stats,
    get_current_recruiter,
    get_company_info,
    update_company_info,
)

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")


@recruiter_bp.before_request
def restrict_to_recruiter():
    recruiter = get_current_recruiter()
    if not recruiter:
        flash("Bạn không có quyền truy cập vào khu vực này.", "danger")
        return redirect(url_for("main.login"))


@recruiter_bp.app_context_processor
def inject_recruiter_context():
    return {"current_recruiter": get_current_recruiter()}


@recruiter_bp.route("/")
def index():
    recruiter = get_current_recruiter()
    stats = get_dashboard_stats(recruiter.user_id)
    return render_template("recruiter/index.html", stats=stats, recruiter=recruiter)


@recruiter_bp.route("/company", methods=["GET", "POST"])
def company():
    recruiter = get_current_recruiter()
    company = get_company_info(recruiter.company_id)
    
    if not company:
        flash("Thông tin công ty không tồn tại.", "danger")
        return redirect(url_for("recruiter.index"))
    
    if request.method == "POST":
        if not recruiter.is_company_admin:
            flash("Bạn không có quyền chỉnh sửa thông tin công ty.", "danger")
            return redirect(url_for("recruiter.company"))
        
        try:
            logo_file = None
            if "logo" in request.files:
                logo_file = request.files["logo"]
                if not logo_file.filename:
                    logo_file = None
            
            data = {
                "name": request.form.get("name"),
                "location": request.form.get("location"),
                "website": request.form.get("website"),
                "scale": request.form.get("scale"),
                "description": request.form.get("description"),
            }
            update_company_info(company.id, recruiter.user_id, data, logo_file)
            flash("Cập nhật thông tin công ty thành công.", "success")
        except PermissionError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "danger")
    
    return render_template("recruiter/company.html", company=company, recruiter=recruiter)
