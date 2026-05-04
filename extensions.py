from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db            = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view             = 'auth.login'
login_manager.login_message          = 'Please log in first.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from flask import session
    from models import Admin, Company, Student

    role = session.get('role')

    if role == 'admin':
        return Admin.query.get(int(user_id))
    if role == 'company':
        return Company.query.get(int(user_id))
    if role == 'student':
        return Student.query.get(int(user_id))
