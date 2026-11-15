"""Shared Flask extensions."""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
csrf = CSRFProtect()


def utcnow():
    """Return a naive UTC datetime for existing database DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

