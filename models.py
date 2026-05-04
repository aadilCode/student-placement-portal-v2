from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Admin(UserMixin, db.Model):
    id       = db.Column(db.Integer,     primary_key=True)
    username = db.Column(db.String(50),  unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    name     = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role     = 'admin'

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class Company(UserMixin, db.Model):
    id             = db.Column(db.Integer,     primary_key=True)
    username       = db.Column(db.String(50),  unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    name           = db.Column(db.String(150), nullable=False)
    hr_contact     = db.Column(db.String(100))
    phone          = db.Column(db.String(20))
    website        = db.Column(db.String(200))
    overview       = db.Column(db.Text)
    password       = db.Column(db.String(256), nullable=False)
    is_approved    = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    joined_on      = db.Column(db.DateTime, default=datetime.utcnow)
    role           = 'company'

    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all, delete-orphan')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)



class Student(UserMixin, db.Model):
    id             = db.Column(db.Integer,     primary_key=True)
    username       = db.Column(db.String(50),  unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    name           = db.Column(db.String(100), nullable=False)
    department     = db.Column(db.String(100))
    cgpa           = db.Column(db.Float)
    phone          = db.Column(db.String(20))
    grad_year      = db.Column(db.Integer)
    skills         = db.Column(db.Text)
    resume_link    = db.Column(db.String(300))
    password       = db.Column(db.String(256), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    joined_on      = db.Column(db.DateTime, default=datetime.utcnow)
    role           = 'student'

    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)



class PlacementDrive(db.Model):
    id          = db.Column(db.Integer,     primary_key=True)
    company_id  = db.Column(db.Integer,     db.ForeignKey('company.id'), nullable=False)
    job_title   = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text,        nullable=False)
    eligibility = db.Column(db.Text)
    salary      = db.Column(db.String(50))
    location    = db.Column(db.String(100))
    deadline    = db.Column(db.Date)
    status      = db.Column(db.String(20),  default='Pending')
    created_on  = db.Column(db.DateTime,    default=datetime.utcnow)

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

class Application(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'),         nullable=False)
    drive_id   = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status     = db.Column(db.String(20), default='Applied')
    remarks    = db.Column(db.String(300))

    
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id'),)
