from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Admin, Company, Student

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.role + '.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.role + '.dashboard'))

    if request.method == 'POST':
        role     = request.form['role']
        username = request.form['username']
        password = request.form['password']

        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        elif role == 'company':
            user = Company.query.filter_by(username=username).first()
        else:
            user = Student.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Wrong username or password.', 'danger')
            return render_template('auth/login.html')

        if role == 'company' and not user.is_approved:
            flash('Your account is pending admin approval.', 'warning')
            return render_template('auth/login.html')

        if hasattr(user, 'is_blacklisted') and user.is_blacklisted:
            flash('Your account has been blacklisted. Contact admin.', 'danger')
            return render_template('auth/login.html')

        session['role'] = role
        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for(role + '.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.role + '.dashboard'))

    if request.method == 'POST':
        role     = request.form['role']
        name     = request.form['name']
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']

        username_taken = Company.query.filter_by(username=username).first() \
                      or Student.query.filter_by(username=username).first()

        if username_taken:
            flash('That username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        if role == 'company':
            new_user = Company(username=username, email=email, name=name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Company registered! Wait for admin approval before logging in.', 'info')
        else:
            new_user = Student(username=username, email=email, name=name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registered successfully! You can now log in.', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
