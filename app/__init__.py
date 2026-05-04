from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from flask import session
    from app.models import User

    @app.context_processor
    def inject_user_context():
        from app.models import User, Recruiter
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        recruiter = Recruiter.query.get(user_id) if user_id else None
        view_mode = session.get("view_mode", "personal")
        return {
            "current_user": user,
            "current_recruiter": recruiter,
            "view_mode": view_mode
        }

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    from app.recruiter import recruiter_bp
    app.register_blueprint(recruiter_bp)
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    from app.models import Location, CompanyScale, ExperienceOption, SalaryOption
    @app.context_processor
    def inject_global_options():
        return {
            'all_locations': Location.query.all(),
            'all_scales': CompanyScale.query.all(),
            'all_experiences': ExperienceOption.query.all(),
            'all_salaries': SalaryOption.query.all()
        }

    return app
