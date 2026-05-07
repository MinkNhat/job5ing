import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for, jsonify
from itsdangerous import BadSignature, BadTimeSignature
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case
from .services import (
    build_google_redirect_uri,
    build_google_state_token,
    create_account,
    fetch_google_tokens,
    fetch_google_userinfo,
    inject_public_auth_context,
    login_with_google_profile,
    login_with_password,
    require_logged_in_user,
    update_account_profile,
    validate_google_state_token,
    get_user_cv,
    preview_resume,
    save_resume,
    validate_tax_code,
    submit_post_report,
)
from app.models import (
    Company, Post, Recruiter, User, Application, Notification, CV,
    ApplicationStatusHistory, Location, CompanyScale, ExperienceOption, SalaryOption
)

from app import db
main_bp = Blueprint("main", __name__)

@main_bp.app_context_processor
def provide_public_context():
    return inject_public_auth_context()

@main_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword", "").strip()
    location_id = request.args.get("location", type=int)
    experience_id = request.args.get("experience", type=int)
    salary_id = request.args.get("salary", type=int)
    sort_by = request.args.get("sort_by", "relevance")

    query = Post.query.filter(Post.status.in_(["ACTIVE", "PINNED"])).join(Recruiter).join(Company)

    if keyword:
        query = query.filter(
            (Post.title.ilike(f"%{keyword}%")) | (Company.name.ilike(f"%{keyword}%"))
        )
    if location_id:
        query = query.filter(Company.city_id == location_id)
    if experience_id:
        query = query.filter(Post.experience_id == experience_id)
    if salary_id:
        query = query.filter(Post.salary_id == salary_id)
    if sort_by == "salary_desc":
        query = query.order_by(Post.salary_id.desc(), Post.created_at.desc())
    elif sort_by == "experience_desc":
        query = query.order_by(Post.experience_id.desc(), Post.created_at.desc())
    elif sort_by == "newest":
        query = query.order_by(Post.created_at.desc())
    else:
        query = query.order_by(
            Post.status.desc(),
            Post.created_at.desc()
        )

    # Fetch pinned posts for the VIP section (limit to 4)
    pinned_posts = Post.query.filter_by(status='PINNED').order_by(Post.created_at.desc()).limit(4).all()

    pagination = query.paginate(page=page, per_page=9, error_out=False)

    return render_template(
        "public/index.html",
        pagination=pagination,
        pinned_posts=pinned_posts,
        all_locations=Location.query.all(),
        all_experiences=ExperienceOption.query.all(),
        all_salaries=SalaryOption.query.all(),
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


@main_bp.route("/switch-mode/<mode>")
def switch_mode(mode):
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    args = request.args.to_dict()

    if mode == "company":
        if not user.is_employer:
            flash("Hãy đăng ký trở thành nhà tuyển dụng để mở khóa tính năng này.", "info")
            return redirect(url_for("main.recruiter_request"))
        
        recruiter = Recruiter.query.get(user.id)
        if not recruiter:
            flash("Bạn cần đăng ký thông tin nhà tuyển dụng trước.", "warning")
            return redirect(url_for("main.recruiter_request"))
            
        if not recruiter.is_approved:
            session["show_approval_modal"] = "recruiter"
            return redirect(url_for("main.index", **args))
            
        company = Company.query.get(recruiter.company_id)
        if not company or not company.is_approved:
            session["show_approval_modal"] = "company"
            return redirect(url_for("main.index", **args))

        session["view_mode"] = "company"
        return redirect(url_for("recruiter.dashboard", **args))
    else:
        session["view_mode"] = "personal"
        return redirect(url_for("main.index", **args))

@main_bp.route("/recruiter-request", methods=["GET"])
def recruiter_request():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=url_for("main.recruiter_request", **request.args)))
    
    if user.is_employer:
        # If already an employer, maybe they want to post a job
        if request.args.get("action") == "post_job":
            return redirect(url_for("main.switch_mode", mode="company", action="post_job"))
        return redirect(url_for("recruiter.dashboard"))

    # Nếu là ứng viên chưa đăng ký employer
    flash("Hãy đăng ký trở thành nhà tuyển dụng để mở khóa tính năng này.", "info")

    companies = Company.query.all()
    return render_template("auth/recruiter_request.html",
                           companies=companies)
@main_bp.route("/submit-join-request", methods=["POST"])
def submit_join_request():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
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
        user.is_employer = True
        db.session.commit()
        session["user_role"] = "employer"
        flash("Yêu cầu của bạn đã được gửi đi, vui lòng chờ admin của công ty phê duyệt.", "success")
        return redirect(url_for("main.index"))
    except SQLAlchemyError:
        db.session.rollback()
        flash("Có lỗi xảy ra, vui lòng thử lại.", "danger")
        return redirect(url_for("main.recruiter_request"))

@main_bp.route("/register-company", methods=["POST"])
def register_company():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    existing_recruiter = Recruiter.query.get(user.id)
    if existing_recruiter:
        try:
            db.session.delete(existing_recruiter)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Không thể cập nhật yêu cầu cũ. Vui lòng thử lại sau.", "danger")
            return redirect(url_for("main.recruiter_request"))

    name = request.form.get("name")
    tax_code = request.form.get("taxCode")
    city_id = request.form.get("city")
    address = request.form.get("address")
    website = request.form.get("website")
    establish_date_str = request.form.get("establishDate")
    scale_id = request.form.get("scale")
    position = request.form.get("position")
    
    if not name or not tax_code:
        flash("Vui lòng điền tên công ty và mã số thuế.", "danger")
        return redirect(url_for("main.recruiter_request"))
    is_valid, error_msg = validate_tax_code(tax_code)
    if not is_valid:
        flash(error_msg, "danger")
        return redirect(url_for("main.recruiter_request"))
    if Company.query.filter_by(tax_code=tax_code.strip()).first():
        flash("Mã số thuế này đã được đăng ký trên hệ thống.", "danger")
        return redirect(url_for("main.recruiter_request"))
    city_obj = db.session.get(Location, city_id)
    city_name = city_obj.name if city_obj else ""
    location = f"{address}, {city_name}" if address else city_name
    avatar_file = request.files.get("avatar")
    license_file = request.files.get("businessLicense")
    
    business_license_path = "pending"
    if license_file and license_file.filename:
        business_license_path = license_file.filename
    from datetime import datetime
    establish_date = None
    if establish_date_str:
        try:
            establish_date = datetime.strptime(establish_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    new_company = Company(
        name=name,
        tax_code=tax_code.strip(),
        location=location,
        city_id=city_id,
        website=website,
        establish_date=establish_date,
        scale_id=scale_id,
        is_approved=False,
        business_license=business_license_path,
        avatar_url=avatar_file.filename if avatar_file and avatar_file.filename else None
    )
    
    try:
        db.session.add(new_company)
        db.session.flush()
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
        session["user_name"] = f"{user.last_name or ''} {user.first_name or ''}".strip() or user.email
        flash("Yêu cầu của bạn đã được gửi đi, vui lòng chờ admin phê duyệt công ty.", "success")
        return redirect(url_for("main.index"))
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"DEBUG DB ERROR: {str(e)}")
        flash(f"Lỗi hệ thống: {str(e)[:100]}...", "danger")
        return redirect(url_for("main.recruiter_request"))
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG GENERAL ERROR: {str(e)}")
        flash("Có lỗi bất ngờ xảy ra, vui lòng thử lại.", "danger")
        return redirect(url_for("main.recruiter_request"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next")
    if request.method == "GET" and next_url:
        flash("Bạn cần đăng nhập để tiếp tục chức năng này.", "warning")

    if request.method == "POST":
        success, message = login_with_password(request.form)
        if success:
            flash(message, "success")
            return redirect(next_url or url_for("main.index"))
        flash(message, "danger")

    return render_template(
        "auth/login.html",
        next_url=next_url,
        google_login_ready=bool(
            current_app.config.get("GOOGLE_CLIENT_ID")
            and current_app.config.get("GOOGLE_CLIENT_SECRET")
        ),
    )

@main_bp.route("/login/google")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google đăng nhập chưa được cấu hình. Hãy thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET.", "warning")
        return redirect(url_for("main.login"))

    next_url = request.args.get("next")
    if request.args.get("is_employer") == "true":
        session["google_is_employer"] = True
    else:
        session.pop("google_is_employer", None)

    state = build_google_state_token(next_url=next_url)
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
        state_payload = validate_google_state_token(returned_state)
        next_url = state_payload.get("next")
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
        target_is_employer = session.pop("google_is_employer", False)
        success, message = login_with_google_profile(profile)

        if success:
            user = User.query.filter_by(email=profile.get("email").lower()).first()
            if target_is_employer and user:
                user.is_employer = True
                db.session.commit()
                session["user_role"] = "employer"
                flash("Đăng ký tài khoản nhà tuyển dụng qua Google thành công.", "success")
                return redirect(url_for("main.recruiter_request"))

            flash(message, "success")
            if user and user.is_admin:
                return redirect(next_url or url_for("admin_panel.index"))
            return redirect(next_url or url_for("main.index"))

        flash(message, "danger")
        return redirect(url_for("main.login", next=next_url))
    except Exception as e:
        print(f"GOOGLE LOGIN ERROR: {str(e)}")
        db.session.rollback()
        flash(f"Không thể hoàn tất đăng nhập Google lúc này: {str(e)}", "danger")
        return redirect(url_for("main.login", next=next_url))

@main_bp.route("/account", methods=["GET", "POST"])
def account():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))

    if request.method == "POST":
        success, message = update_account_profile(user, request.form, request.files)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("main.account"))

    return render_template("public/account.html", user=user)

@main_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("main.index"))

@main_bp.route("/api/clear-approval-session", methods=["POST"])
def clear_approval_session():
    session.pop("show_approval_modal", None)
    return "", 204


from .recruiter_services import calculate_ai_score, get_applications_for_post, update_application_status

@main_bp.route("/my-company/posts")
def recruiter_posts():
    user = require_logged_in_user()
    if not user or not user.is_employer:
        flash("Bạn cần quyền nhà tuyển dụng để truy cập trang này.", "danger")
        return redirect(url_for("main.login"))

    recruiter = Recruiter.query.filter_by(user_id=user.id).first()
    if not recruiter or not recruiter.company_id:
        flash("Tài khoản của bạn chưa liên kết với công ty nào.", "warning")
        return redirect(url_for("main.recruiter_request"))
    posts = Post.query.filter(Post.recruiter.has(company_id=recruiter.company_id)).order_by(Post.created_at.desc()).all()

    return render_template("public/company_posts.html", posts=posts, company=recruiter.company)

@main_bp.route("/manage-candidates/<int:post_id>")
def manage_candidates(post_id):
    user = require_logged_in_user()
    if not user or not user.is_employer:
        flash("Bạn cần quyền nhà tuyển dụng để truy cập trang này.", "danger")
        return redirect(url_for("main.login"))

    post = Post.query.get_or_404(post_id)
    current_recruiter = Recruiter.query.filter_by(user_id=user.id).first()
    post_recruiter = Recruiter.query.filter_by(user_id=post.recruiter_id).first()
    if not current_recruiter or not post_recruiter or current_recruiter.company_id != post_recruiter.company_id:
        flash("Bạn không có quyền quản lý tin này (không thuộc cùng công ty).", "danger")
        return redirect(url_for("main.index"))

    status_filter = request.args.get("status")
    sort_by_ai = request.args.get("sort_by_ai") == "1"
    page = request.args.get("page", 1, type=int)

    query = get_applications_for_post(post_id, status_filter, sort_by_ai)
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    stats = {
        "all": Application.query.filter_by(post_id=post_id).count(),
        "received": Application.query.filter_by(post_id=post_id, status='RECEIVED').count(),
        "interview": Application.query.filter_by(post_id=post_id, status='INTERVIEW').count(),
        "approved": Application.query.filter_by(post_id=post_id, status='APPROVED').count(),
        "reject": Application.query.filter_by(post_id=post_id, status='REJECT').count(),
    }

    return render_template(
        "public/manage_candidates.html",
        post=post,
        pagination=pagination,
        stats=stats,
        current_status=status_filter,
        is_sorted_ai=sort_by_ai
    )

@main_bp.route("/api/calculate-scores/<int:post_id>", methods=["POST"])
def run_ai_screening(post_id):
    user = require_logged_in_user()
    if not user or not user.is_employer:
        return {"error": "Unauthorized"}, 401

    post = Post.query.get_or_404(post_id)
    for app in post.applications:
        app.ai_score = calculate_ai_score(app.cv_id, post_id)
    db.session.commit()
    flash("Đã hoàn tất sàng lọc hồ sơ bằng AI.", "success")
    return redirect(url_for("main.manage_candidates", post_id=post_id, sort_by_ai=1))

@main_bp.route("/api/update-app-status", methods=["POST"])
def change_app_status():
    app_id = request.form.get("application_id")
    new_status = request.form.get("status")
    if update_application_status(app_id, new_status):
        flash("Cập nhật trạng thái thành công.", "success")
    else:
        flash("Lỗi khi cập nhật trạng thái.", "danger")
    return redirect(request.referrer)

@main_bp.route("/manage-candidates/view-cv/<int:application_id>")
def view_candidate_cv(application_id):
    user = require_logged_in_user()
    if not user or not user.is_employer:
        flash("Bạn cần quyền nhà tuyển dụng để truy cập trang này.", "danger")
        return redirect(url_for("main.login"))

    application = Application.query.get_or_404(application_id)
    if application.post.recruiter_id != user.id:
        flash("Bạn không có quyền xem hồ sơ này.", "danger")
        return redirect(url_for("main.index"))

    return render_template("public/view_cv.html", application=application)

@main_bp.route("/posts/<int:post_id>/report", methods=["POST"])
def report_post(post_id):
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    reason = request.form.get("reason")
    description = request.form.get("description", "").strip()

    if not reason:
        flash("Vui lòng chọn lý do báo cáo.", "danger")
        return redirect(url_for("main.index"))

    success, message = submit_post_report(user, post_id, reason, description)
    flash(message, "success" if success else "danger")
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
                "title": cv_data.get("title"),
                "summary": cv_data.get("summary"),
                "skills": cv_data.get("skills") or [],
                "experience": cv_data.get("experience") or [],
                "education": cv_data.get("education") or []
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500


@main_bp.route("/resume", methods=["GET", "POST"])
def resume():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    cv_id = request.args.get("cv_id", type=int)
    action = request.args.get("action")

    if request.method == "POST":
        if user.is_employer:
            flash("Nhà tuyển dụng không thể tạo hoặc cập nhật CV mới.", "warning")
            return redirect(url_for("main.resume_management"))
        success, message = save_resume(user, request.form)
        flash(message, "success" if success else "danger")
        return redirect(url_for("main.resume_management"))

    if action == "create":
        if user.is_employer:
            flash("Nhà tuyển dụng không thể tạo CV mới.", "warning")
            return redirect(url_for("main.resume_management"))
        cv = CV(user_id=user.id)
    elif cv_id:
        cv = CV.query.filter_by(id=cv_id, user_id=user.id).first_or_404()
    else:
        cv = get_user_cv(user)
        
    return render_template("candidate/resume.html", user=user, cv=cv)
@main_bp.route("/company/<int:company_id>")
def company_details(company_id):
    company = Company.query.get_or_404(company_id)
    posts = Post.query.join(Recruiter).filter(
        Recruiter.company_id == company_id,
        Post.status.in_(["ACTIVE", "PINNED"])
    ).order_by(
        Post.status.desc(),
        Post.last_modified.desc()
    ).all()
    return render_template("public/company_details.html", company=company, posts=posts)
@main_bp.route("/post/<int:post_id>")
def post_details(post_id):
    post = Post.query.get_or_404(post_id)
    related_posts = Post.query.filter(
        Post.status.in_(["ACTIVE", "PINNED"]),
        Post.id != post_id
    ).join(Recruiter).filter(
        Recruiter.company_id == post.recruiter.company_id
    ).limit(3).all()

    has_applied = False
    cv = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user and not user.is_employer:
            cv = CV.query.filter_by(user_id=user.id).first()
            if cv:
                has_applied = Application.query.filter_by(cv_id=cv.id, post_id=post.id).first() is not None

    return render_template("public/post_details.html", post=post, related_posts=related_posts, has_applied=has_applied, cv=cv)

@main_bp.route("/post/<int:post_id>/apply", methods=["POST"])
def apply_job(post_id):
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    if user.is_employer:
        flash("Nhà tuyển dụng không thể ứng tuyển.", "warning")
        return redirect(url_for("main.post_details", post_id=post_id))
        
    post = Post.query.get_or_404(post_id)
    new_phone = request.form.get("phone")
    if new_phone and new_phone != user.phone:
        user.phone = new_phone
    
    cv = get_user_cv(user)
    if 'new_cv' in request.files and request.files['new_cv'].filename != '':
        new_cv_file = request.files['new_cv']
        ext = ("." + new_cv_file.filename.rsplit(".", 1)[1].lower()) if "." in new_cv_file.filename else ""
        if ext in [".pdf", ".doc", ".docx"]:
            try:
                import cloudinary.uploader
                upload_result = cloudinary.uploader.upload(
                    new_cv_file,
                    folder="job5ing/resumes",
                    resource_type="auto"
                )
                cv.cv_url = upload_result.get("secure_url")
                cv.title = new_cv_file.filename
            except Exception as e:
                flash(f"Lỗi khi tải CV lên: {str(e)}", "danger")
                return redirect(url_for("main.post_details", post_id=post_id))

    if not cv or (not cv.cv_url and not cv.cv_content):
        flash("Vui lòng cập nhật hồ sơ CV (tải lên file hoặc điền thông tin) trước khi ứng tuyển.", "warning")
        return redirect(url_for("main.resume"))
    existing_app = Application.query.filter_by(cv_id=cv.id, post_id=post.id).first()
    if existing_app:
        flash("Bạn đã ứng tuyển vào vị trí này rồi.", "info")
        return redirect(url_for("main.post_details", post_id=post_id))
        
    cover_letter = request.form.get("cover_letter")
    application = Application(cv_id=cv.id, post_id=post.id, cover_letter=cover_letter)
    db.session.add(application)
    db.session.flush()
    history = ApplicationStatusHistory(
        application_id=application.id,
        new_status='RECEIVED',
        notes="Ứng viên nộp hồ sơ trực tuyến."
    )
    db.session.add(history)
    notification = Notification(
        user_id=post.recruiter_id,
        content=f"Có ứng viên mới ứng tuyển vào vị trí {post.title}.",
        type='NEW_APPLICATION'
    )
    db.session.add(notification)
    
    try:
        db.session.commit()
        flash("Ứng tuyển thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Có lỗi xảy ra, vui lòng thử lại.", "danger")
        
    return redirect(url_for("main.post_details", post_id=post_id))

@main_bp.route("/applied-jobs")
def applied_jobs():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    cv = CV.query.filter_by(user_id=user.id).first()
    
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').upper()
    page = request.args.get("page", 1, type=int)

    query = Application.query.filter_by(cv_id=cv.id) if cv else Application.query.filter_by(id=-1)
    
    if q:
        query = query.join(Post).filter(Post.title.ilike(f'%{q}%'))
    if status_filter:
        query = query.filter(Application.status == status_filter)

    pagination = query.order_by(Application.applied_at.desc()).paginate(page=page, per_page=10, error_out=False)
        
    return render_template("candidate/applied_jobs.html", pagination=pagination)

@main_bp.route("/resume-management")
def resume_management():
    user = require_logged_in_user()
    if not user:
        return redirect(url_for("main.login", next=request.url))
    q = request.args.get('q', '').strip()
    page = request.args.get("page", 1, type=int)

    query = CV.query.filter_by(user_id=user.id)
    if q:
        query = query.filter(CV.title.ilike(f'%{q}%'))

    pagination = query.order_by(CV.last_modified.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template("candidate/resume_management.html", pagination=pagination)
