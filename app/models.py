from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# COMPANY
# =========================
class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    website = db.Column(db.String(255))
    establish_date = db.Column(db.Date)
    scale = db.Column(db.String(50))
    tax_code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(255))
    business_license = db.Column(db.String(255), nullable=False)

    recruiters = db.relationship('Recruiter', backref='company', lazy=True)


# =========================
# USERS
# =========================
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

    # Relationships
    cvs = db.relationship('CV', backref='user', lazy=True, cascade="all, delete-orphan")
    recruiter_profile = db.relationship('Recruiter', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# =========================
# RECRUITER
# =========================
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


# =========================
# CV
# =========================
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

    created_at = db.Column(db.DateTime, default=db.func.now())
    last_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    applications = db.relationship('Application', backref='cv', lazy=True)


# =========================
# POST
# =========================
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
    skills = db.Column(db.Text)
    experience = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    deadline = db.Column(db.Date)

    status = db.Column(
        db.Enum('ACTIVE', 'OVERDUE', 'CLOSED', 'PINNED', 'BLOCKED'),
        default='ACTIVE'
    )

    is_reported = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
    last_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    applications = db.relationship('Application', backref='post', lazy=True)


# =========================
# APPLICATION
# =========================
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

    status = db.Column(
        db.Enum('RECEIVED', 'INTERVIEW', 'APPROVED', 'REJECT'),
        default='RECEIVED'
    )

    __table_args__ = (
        db.UniqueConstraint('cv_id', 'post_id', name='uq_app_cv_post'),
    )


# =========================
# NOTIFICATION
# =========================
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
