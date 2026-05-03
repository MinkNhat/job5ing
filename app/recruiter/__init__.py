from flask import Blueprint
recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')
from . import routes