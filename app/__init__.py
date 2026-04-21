from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    return app
