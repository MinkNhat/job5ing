from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import Post, Recruiter, Application, Company, db
from app.main.services import require_logged_in_user
from sqlalchemy import func
from datetime import datetime
from app.main.constants import EXPERIENCE_OPTIONS, SALARY_OPTIONS
from .service import (
    get_dashboard_stats,
    get_current_recruiter,
    get_company_info,
    update_company_info,
)
from . import recruiter_bp

@recruiter_bp.before_request
def restrict_to_recruiter():
    # Only allow access to recruiters
    # Some endpoints might need to be open if they are shared, but here they are all under /recruiter/
    recruiter = get_current_recruiter()
    if not recruiter:
        # Check if the user is logged in but not an approved recruiter
        user = require_logged_in_user()
        if not user or not user.is_employer:
            flash("Bạn cần đăng nhập với quyền nhà tuyển dụng.", "danger")
            return redirect(url_for('main.login'))
        
        # Check if they have a recruiter record
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

    # 1. Thống kê (Stats)
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

    # 2. Tìm kiếm và Lọc
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').upper()
    page = request.args.get('page', 1, type=int)

    query = Post.query.join(Recruiter).filter(Recruiter.company_id == company_id)

    if q:
        query = query.filter(Post.title.ilike(f'%{q}%'))
    if status_filter:
        query = query.filter(Post.status == status_filter)

    pagination = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    jobs = pagination.items

    # 3. Mapping trạng thái bài đăng
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
                           stats={
                               'total_apps': total_apps,
                               'active_jobs': active_jobs_count,
                               'pending_apps': pending_apps
                           },
                           experience_options=EXPERIENCE_OPTIONS,
                           salary_options=SALARY_OPTIONS)

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
            "skills": job.skills,
            "experience": job.experience,
            "salary_range": job.salary_range,
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
        job.skills = data.get('skills')
        job.experience = data.get('experience')
        job.salary_range = data.get('salary_range')
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
            skills=data.get('skills'),
            experience=data.get('experience'),
            salary_range=data.get('salary_range'),
            deadline=deadline,
            status='ACTIVE'
        )
        db.session.add(job)
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
                "location": request.form.get("location"),
                "website": request.form.get("website"),
                "scale": request.form.get("scale"),
                "description": request.form.get("description"),
            }
            update_company_info(company.id, recruiter.user_id, data, logo_file)
            flash("Cập nhật thông tin công ty thành công.", "success")
            return redirect(url_for("recruiter.company"))
        except PermissionError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "danger")

    return render_template("recruiter/company.html", company=company, recruiter=recruiter)
