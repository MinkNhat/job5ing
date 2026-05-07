from app import db
from werkzeug.security import generate_password_hash, check_password_hash
class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    companies = db.relationship('Company', backref='city', lazy=True)

class CompanyScale(db.Model):
    __tablename__ = 'company_scale'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    companies = db.relationship('Company', backref='scale_ref', lazy=True)

class ExperienceOption(db.Model):
    __tablename__ = 'experience_option'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='experience_ref', lazy=True)

class SalaryOption(db.Model):
    __tablename__ = 'salary_option'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='salary_ref', lazy=True)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    city_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    website = db.Column(db.String(255))
    establish_date = db.Column(db.Date)
    scale_id = db.Column(db.Integer, db.ForeignKey('company_scale.id'), nullable=True)
    tax_code = db.Column(db.String(15), unique=True)
    description = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(255))
    business_license = db.Column(db.String(255), nullable=True)
    recruiters = db.relationship('Recruiter', backref='company', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    sex = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_employer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime)
    avatar_url = db.Column(db.String(255))
    cvs = db.relationship('CV', backref='user', lazy=True, cascade="all, delete-orphan")
    recruiter_profile = db.relationship('Recruiter', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Recruiter(db.Model):
    __tablename__ = 'recruiter'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company.id', ondelete='SET NULL')
    )
    position = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    is_company_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='recruiter', lazy=True)

class CV(db.Model):
    __tablename__ = 'cv'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    cv_url = db.Column(db.String(255))
    cv_content = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.now())
    last_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    applications = db.relationship('Application', backref='cv', lazy=True)
    skills_list = db.relationship('CVSkill', backref='cv', lazy=True, cascade="all, delete-orphan")
    education_list = db.relationship('CVEducation', backref='cv', lazy=True, cascade="all, delete-orphan")
    experience_list = db.relationship('CVExperience', backref='cv', lazy=True, cascade="all, delete-orphan")

    @property
    def skills(self):
        return ", ".join([s.skill_name for s in self.skills_list])

    @skills.setter
    def skills(self, value):
        self.skills_list = []
        if value:
            names = [s.strip() for s in value.split(',') if s.strip()]
            for name in names:
                self.skills_list.append(CVSkill(skill_name=name))

    @property
    def education(self):
        result = []
        for e in self.education_list:
            text = f"{e.school or ''}"
            if e.major:
                text += f" - {e.major}"
            if e.start_date:
                text += f" ({e.start_date.strftime('%m/%Y')}"
                if e.end_date:
                    text += f" - {e.end_date.strftime('%m/%Y')}"
                else:
                    text += " - Hiện tại"
                text += ")"
            result.append(text.strip())
        return "\n".join(result)

    @property
    def experience(self):
        result = []
        for e in self.experience_list:
            text = f"{e.job_title or ''}"
            if e.company_name:
                text += f" - {e.company_name}"
            if e.position:
                text += f" ({e.position})"
            if e.start_date:
                text += f" ({e.start_date.strftime('%m/%Y')}"
                if e.end_date:
                    text += f" - {e.end_date.strftime('%m/%Y')}"
                else:
                    text += " - Hiện tại"
                text += ")"
            result.append(text.strip())
            if e.description:
                result.append(f"  {e.description}")
        return "\n".join(result)
    
    def get_education_json(self):
        result = []
        for e in self.education_list:
            result.append({
                "school": e.school or "",
                "major": e.major or "",
                "start_date": e.start_date.isoformat() if e.start_date else "",
                "end_date": e.end_date.isoformat() if e.end_date else ""
            })
        return result
    
    def get_experience_json(self):
        result = []
        for e in self.experience_list:
            result.append({
                "job_title": e.job_title or "",
                "company_name": e.company_name or "",
                "position": e.position or "",
                "description": e.description or "",
                "start_date": e.start_date.isoformat() if e.start_date else "",
                "end_date": e.end_date.isoformat() if e.end_date else ""
            })
        return result

class CVSkill(db.Model):
    __tablename__ = 'cv_skill'
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)

class CVEducation(db.Model):
    __tablename__ = 'cv_education'
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id', ondelete='CASCADE'), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    major = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)  # NULL = present

class CVExperience(db.Model):
    __tablename__ = 'cv_experience'
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)  # NULL = present

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey('recruiter.user_id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    experience_id = db.Column(db.Integer, db.ForeignKey('experience_option.id'), nullable=True)
    salary_id = db.Column(db.Integer, db.ForeignKey('salary_option.id'), nullable=True)
    deadline = db.Column(db.Date)
    status = db.Column(
        db.Enum('ACTIVE', 'OVERDUE', 'CLOSED', 'PINNED', 'BLOCKED'),
        default='ACTIVE'
    )
    is_reported = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    applications = db.relationship('Application', backref='post', lazy=True)
    reports = db.relationship('PostReport', backref='post', lazy=True, cascade="all, delete-orphan")
    skills_list = db.relationship('PostSkill', backref='post', lazy=True, cascade="all, delete-orphan")

    @property
    def skills(self):
        return ", ".join([s.skill_name for s in self.skills_list])

    @skills.setter
    def skills(self, value):
        self.skills_list = []
        if value:
            names = [s.strip() for s in value.split(',') if s.strip()]
            for name in names:
                self.skills_list.append(PostSkill(skill_name=name))

class PostSkill(db.Model):
    __tablename__ = 'post_skill'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)

class PostReport(db.Model):
    __tablename__ = 'post_report'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_resolved = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='reports_sent')

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(
        db.Integer,
        db.ForeignKey('cv.id', ondelete='CASCADE'),
        nullable=False
    )
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False
    )
    applied_at = db.Column(db.DateTime, default=db.func.now())
    ai_score = db.Column(db.Integer, default=0)
    status = db.Column(
        db.Enum('RECEIVED', 'INTERVIEW', 'APPROVED', 'REJECT'),
        default='RECEIVED'
    )
    cover_letter = db.Column(db.Text)
    __table_args__ = (
        db.UniqueConstraint('cv_id', 'post_id', name='uq_app_cv_post'),
    )
    history = db.relationship('ApplicationStatusHistory', backref='application', lazy=True, cascade="all, delete-orphan")

class ApplicationStatusHistory(db.Model):
    __tablename__ = 'application_status_history'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey('application.id', ondelete='CASCADE'),
        nullable=False
    )
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=db.func.now())
    changed_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    notes = db.Column(db.Text)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    content = db.Column(db.Text)
    type = db.Column(
        db.Enum(
            'APPLICATION_STATUS_CHANGED',
            'INTERVIEW_INVITATION',
            'NEW_APPLICATION',
            'ACCOUNT_APPROVED',
            'POST_BLOCKED'
        )
    )
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_read = db.Column(db.Boolean, default=False)