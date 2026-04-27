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
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        return {"current_user": user}

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    from app.recruiter import recruiter_bp
    app.register_blueprint(recruiter_bp)
    return app
