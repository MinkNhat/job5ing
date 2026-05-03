from flask import session
from sqlalchemy import and_
import cloudinary.uploader
from app import db
from app.models import User, Recruiter, Post, Application, Company, Location, CompanyScale
def get_current_recruiter():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if user:
        recruiter = db.session.get(Recruiter, user_id)
        if recruiter and recruiter.is_approved:
            return recruiter
    return None
def get_dashboard_stats(recruiter_id):
    total_posts = Post.query.filter_by(recruiter_id=recruiter_id).count()
    active_posts = Post.query.filter(
        and_(
            Post.recruiter_id == recruiter_id,
            Post.status.in_(['ACTIVE', 'PINNED'])
        )
    ).count()
    total_candidates = db.session.query(Application).join(
        Post, Application.post_id == Post.id
    ).filter(Post.recruiter_id == recruiter_id).count()
    new_candidates = db.session.query(Application).join(
        Post, Application.post_id == Post.id
    ).filter(
        and_(
            Post.recruiter_id == recruiter_id,
            Application.status == 'RECEIVED'
        )
    ).count()
    approved_candidates = db.session.query(Application).join(
        Post, Application.post_id == Post.id
    ).filter(
        and_(
            Post.recruiter_id == recruiter_id,
            Application.status == 'APPROVED'
        )
    ).count()
    return {
        "total_posts": total_posts,
        "active_posts": active_posts,
        "total_candidates": total_candidates,
        "new_candidates": new_candidates,
        "approved_candidates": approved_candidates,
    }
def get_company_members(company_id):
    return db.session.query(Recruiter, User).join(User, Recruiter.user_id == User.id).filter(Recruiter.company_id == company_id).all()
def approve_member(recruiter_id, company_id):
    recruiter = db.session.get(Recruiter, recruiter_id)
    if recruiter and recruiter.company_id == company_id:
        recruiter.is_approved = True
        db.session.commit()
        return True
    return False
def delete_member(recruiter_id, company_id):
    recruiter = db.session.get(Recruiter, recruiter_id)
    if recruiter and recruiter.company_id == company_id:
        db.session.delete(recruiter)
        db.session.commit()
        return True
    return False
def toggle_member_admin(recruiter_id, company_id):
    recruiter = db.session.get(Recruiter, recruiter_id)
    if recruiter and recruiter.company_id == company_id:
        recruiter.is_company_admin = not recruiter.is_company_admin
        db.session.commit()
        return True, recruiter.is_company_admin
    return False, None
def get_company_info(company_id):
    return db.session.get(Company, company_id)
def update_company_info(company_id, recruiter_id, data, logo_file=None):
    recruiter = db.session.get(Recruiter, recruiter_id)
    if not recruiter or recruiter.company_id != company_id or not recruiter.is_company_admin:
        raise PermissionError("Bạn không có quyền cập nhật thông tin công ty")
    company = db.session.get(Company, company_id)
    if not company:
        raise ValueError("Công ty không tồn tại")
    if logo_file and logo_file.filename:
        try:
            result = cloudinary.uploader.upload(
                logo_file,
                folder="job5ing/company_logos",
                resource_type="auto",
                overwrite=True,
                unique_filename=False
            )
            company.avatar_url = result.get("secure_url")
        except Exception as e:
            raise Exception(f"Không thể upload logo lên. Vui lòng thử lại. ({str(e)})")
    if "name" in data and data["name"]:
        company.name = data["name"]
    if "city_id" in data and data["city_id"]:
        company.city_id = data["city_id"]
        address = data.get("address", "")
        city_obj = db.session.get(Location, company.city_id)
        city_name = city_obj.name if city_obj else ""
        company.location = f"{address}, {city_name}" if address else city_name
    elif "location" in data and data["location"]:
        company.location = data["location"]
    if "website" in data and data["website"]:
        company.website = data["website"]
    if "scale_id" in data and data["scale_id"]:
        company.scale_id = data["scale_id"]
    if "description" in data and data["description"]:
        company.description = data["description"]
    db.session.commit()
    return company