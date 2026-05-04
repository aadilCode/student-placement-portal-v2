from flask import Flask
from extensions import db, login_manager
from models import Admin

app = Flask(__name__)

app.config['SECRET_KEY']              = 'aadilsecret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

db.init_app(app)
login_manager.init_app(app)

from routes.auth    import auth_bp
from routes.admin   import admin_bp
from routes.company import company_bp
from routes.student import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp,   url_prefix='/admin')
app.register_blueprint(company_bp, url_prefix='/company')
app.register_blueprint(student_bp, url_prefix='/student')

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin = Admin(username='admin', email='admin@college.edu', name='Admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin created → username: admin | password: admin123')

if __name__ == '__main__':
    app.run(debug=True)
