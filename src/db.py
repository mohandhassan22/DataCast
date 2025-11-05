# db.py: Database object for SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

# from yourapplication.models import *  # noqa: F401,
