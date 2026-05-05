from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import (
    User, Post, PostSkill, Recruiter, Application, Company, db, 
    ExperienceOption, SalaryOption, CompanyScale, Location
)
from app.main.services import require_logged_in_user
from sqlalchemy import func
from datetime import datetime
from .service import (
    get_dashboard_stats,
    get_current_recruiter,
    get_company_info,
    update_company_info,
    get_company_members,
    approve_member,
    delete_member,
    toggle_member_admin,
)
from . import recruiter_bp
@recruiter_bp.before_request
def restrict_to_recruiter():
    recruiter = get_current_recruiter()
    if not recruiter:
        user = require_logged_in_user()
        if not user or not user.is_employer:
            flash("Bạn cần đăng nhập với quyền nhà tuyển dụng.", "danger")
            return redirect(url_for('main.login'))
        recruiter = Recruiter.query.get(user.id)
        if not recruiter or not recruiter.is_approved:
            flash("Tài khoản của bạn chưa được duyệt quyền nhà tuyển dụng hoặc chưa liên kết công ty.", "warning")
            return redirect(url_for('main.index'))
    return None
@recruiter_bp.app_context_processor
def inject_recruiter_context():
    return {"current_recruiter": get_current_recruiter()}
@recruiter_bp.route("/")
def index():
    recruiter = get_current_recruiter()
    stats = get_dashboard_stats(recruiter.user_id)
    return render_template("recruiter/index.html", stats=stats, recruiter=recruiter)
@recruiter_bp.route('/dashboard')
def dashboard():
    recruiter = get_current_recruiter()
    company_id = recruiter.company_id
    total_apps = db.session.query(func.count(Application.id))\
        .join(Post)\
        .join(Recruiter)\
        .filter(Recruiter.company_id == company_id).scalar() or 0
    active_jobs_count = Post.query.join(Recruiter)\
        .filter(Recruiter.company_id == company_id, Post.status == 'ACTIVE').count()
    pending_apps = db.session.query(func.count(Application.id))\
        .join(Post)\
        .join(Recruiter)\
        .filter(Recruiter.company_id == company_id, Application.status == 'RECEIVED').scalar() or 0
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').upper()
    experience_id = request.args.get('experience', type=int)
    salary_id = request.args.get('salary', type=int)
    page = request.args.get('page', 1, type=int)
    query = Post.query.join(Recruiter).filter(Recruiter.company_id == company_id)
    if q:
        query = query.filter(Post.title.ilike(f'%{q}%'))
    if status_filter:
        query = query.filter(Post.status == status_filter)
    if experience_id:
        query = query.filter(Post.experience_id == experience_id)
    if salary_id:
        query = query.filter(Post.salary_id == salary_id)
    pagination = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    jobs = pagination.items
    total_company_jobs = Post.query.join(Recruiter).filter(Recruiter.company_id == company_id).count()
    status_map = {
        'ACTIVE': ('Đang hiển thị', 'badge-status-active'),
        'PINNED': ('Đang ghim', 'badge-status-active'),
        'OVERDUE': ('Hết hạn', 'badge-status-inactive'),
        'CLOSED': ('Đã đóng', 'badge-status-inactive'),
        'BLOCKED': ('Bị khóa', 'badge-role-gray')
    }
    for job in jobs:
        job.candidate_count = Application.query.filter_by(post_id=job.id).count()
        label, css_class = status_map.get(job.status, (job.status, 'badge-role-gray'))
        job.status_vn = label
        job.status_class = css_class
    return render_template('recruiter/company_post_management.html',
                           jobs=jobs,
                           pagination=pagination,
                           total_company_jobs=total_company_jobs,
                           stats={
                               'total_apps': total_apps,
                               'active_jobs': active_jobs_count,
                               'pending_apps': pending_apps
                           },
                           experience_options=ExperienceOption.query.all(),
                           salary_options=SalaryOption.query.all())
@recruiter_bp.route('/job/<int:job_id>', methods=['GET'])
def get_job(job_id):
    recruiter = get_current_recruiter()
    job = Post.query.get_or_404(job_id)
    if job.recruiter.company_id != recruiter.company_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify({
        "success": True,
        "job": {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "skills": ", ".join([s.skill_name for s in job.skills]),
            "experience_id": job.experience_id,
            "salary_id": job.salary_id,
            "deadline": job.deadline.isoformat() if job.deadline else None,
            "status": job.status
        }
    })
@recruiter_bp.route('/job/manage', methods=['POST'])
@recruiter_bp.route('/job/manage/<int:job_id>', methods=['POST'])
def manage_job(job_id=None):
    recruiter = get_current_recruiter()
    data = request.form
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.strptime(data.get('deadline'), '%Y-%m-%d').date()
        except ValueError:
            pass
    if job_id:
        job = Post.query.get_or_404(job_id)
        if job.recruiter.company_id != recruiter.company_id:
            flash("Không có quyền.", "danger")
            return redirect(url_for('recruiter.dashboard'))
        job.title = data.get('title')
        job.description = data.get('description')
        
        # Handle skills relationship
        job.skills = data.get('skills')

        job.experience_id = data.get('experience', type=int)
        job.salary_id = data.get('salary', type=int)
        job.deadline = deadline
        new_status = data.get('status')
        if new_status and new_status != 'BLOCKED':
            job.status = new_status
        msg = "Cập nhật tin thành công."
    else:
        job = Post(
            recruiter_id=recruiter.user_id,
            title=data.get('title'),
            description=data.get('description'),
            experience_id=data.get('experience', type=int),
            salary_id=data.get('salary', type=int),
            deadline=deadline,
            status='ACTIVE'
        )
        db.session.add(job)
        db.session.flush() # Get job.id for update_skills

        # Handle skills relationship
        job.skills = data.get('skills')

        msg = "Đăng tin mới thành công."
    db.session.commit()
    flash(msg, "success")
    return redirect(url_for('recruiter.dashboard'))
@recruiter_bp.route('/job/close/<int:job_id>', methods=['POST'])
def close_job(job_id):
    recruiter = get_current_recruiter()
    job = Post.query.get_or_404(job_id)
    if job.recruiter.company_id != recruiter.company_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    job.status = 'CLOSED'
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({"success": True, "message": "Đã đóng tin tuyển dụng."})
    flash("Đã đóng tin tuyển dụng.", "success")
    return redirect(url_for('recruiter.dashboard'))
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
                "city_id": request.form.get("city_id", type=int),
                "address": request.form.get("address"),
                "website": request.form.get("website"),
                "scale_id": request.form.get("scale_id", type=int),
                "description": request.form.get("description"),
            }
            update_company_info(company.id, recruiter.user_id, data, logo_file)
            flash("Cập nhật thông tin công ty thành công.", "success")
            return redirect(url_for("recruiter.company"))
        except PermissionError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "danger")
    return render_template("recruiter/company.html", 
                           company=company, 
                           recruiter=recruiter)
@recruiter_bp.route("/members")
def manage_members():
    recruiter = get_current_recruiter()
    if not recruiter.is_company_admin:
        flash("Bạn không có quyền truy cập chức năng này.", "danger")
        return redirect(url_for("recruiter.dashboard"))
    q = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "")
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Recruiter, User)\
        .join(User, Recruiter.user_id == User.id)\
        .filter(Recruiter.company_id == recruiter.company_id)
    if q:
        query = query.filter((User.first_name.ilike(f"%{q}%")) | (User.last_name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%")))
    if role_filter == "admin":
        query = query.filter(Recruiter.is_company_admin == True)
    elif role_filter == "staff":
        query = query.filter(Recruiter.is_company_admin == False)
    if status_filter == "approved":
        query = query.filter(Recruiter.is_approved == True)
    elif status_filter == "pending":
        query = query.filter(Recruiter.is_approved == False)
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template("recruiter/manage_members.html", pagination=pagination, recruiter=recruiter)
@recruiter_bp.route("/members/approve/<int:user_id>", methods=["POST"])
def approve_company_member(user_id):
    recruiter = get_current_recruiter()
    if not recruiter.is_company_admin:
        flash("Bạn không có quyền thực hiện hành động này.", "danger")
        return redirect(url_for("recruiter.dashboard"))
    if approve_member(user_id, recruiter.company_id):
        flash("Đã phê duyệt thành viên.", "success")
    else:
        flash("Không thể phê duyệt thành viên này.", "danger")
    return redirect(url_for("recruiter.manage_members"))
@recruiter_bp.route("/members/delete/<int:user_id>", methods=["POST"])
def delete_company_member(user_id):
    recruiter = get_current_recruiter()
    if not recruiter.is_company_admin:
        flash("Bạn không có quyền thực hiện hành động này.", "danger")
        return redirect(url_for("recruiter.dashboard"))
    if user_id == recruiter.user_id:
        other_admins = Recruiter.query.filter_by(company_id=recruiter.company_id, is_company_admin=True).filter(Recruiter.user_id != user_id).count()
        if other_admins == 0:
            flash("Bạn là quản trị viên duy nhất. Vui lòng chỉ định người khác làm quản trị viên trước khi rời khỏi công ty.", "warning")
            return redirect(url_for("recruiter.manage_members"))
    if delete_member(user_id, recruiter.company_id):
        flash("Đã xóa thành viên khỏi công ty.", "success")
        if user_id == recruiter.user_id:
            return redirect(url_for("main.index"))
    else:
        flash("Không thể xóa thành viên này.", "danger")
    return redirect(url_for("recruiter.manage_members"))
@recruiter_bp.route("/members/toggle-admin/<int:user_id>", methods=["POST"])
def toggle_admin(user_id):
    recruiter = get_current_recruiter()
    if not recruiter.is_company_admin:
        flash("Bạn không có quyền thực hiện hành động này.", "danger")
        return redirect(url_for("recruiter.dashboard"))
    if user_id == recruiter.user_id:
        flash("Bạn không thể tự thay đổi quyền quản trị của chính mình.", "warning")
        return redirect(url_for("recruiter.manage_members"))
    success, is_admin = toggle_member_admin(user_id, recruiter.company_id)
    if success:
        role_name = "Quản trị viên" if is_admin else "Nhân viên thường"
        flash(f"Đã thay đổi quyền thành {role_name}.", "success")
    else:
        flash("Không thể thay đổi quyền thành viên này.", "danger")
    return redirect(url_for("recruiter.manage_members"))