from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import PlacementDrive, Application

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))

    open_drives     = PlacementDrive.query.filter_by(status='Approved').all()
    my_applications = Application.query.filter_by(student_id=current_user.id)\
                                       .order_by(Application.applied_on.desc()).all()
    applied_drive_ids = {app.drive_id for app in my_applications}

    return render_template('student/dashboard.html',
                           open_drives=open_drives,
                           my_applications=my_applications,
                           applied_drive_ids=applied_drive_ids)


@student_bp.route('/drive/<int:id>')
@login_required
def view_drive(id):
    drive   = PlacementDrive.query.get_or_404(id)
    already = Application.query.filter_by(student_id=current_user.id, drive_id=id).first()
    return render_template('student/drive_detail.html', drive=drive, already_applied=already)


@student_bp.route('/drive/<int:id>/apply')
@login_required
def apply(id):
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(id)

    if drive.status != 'Approved':
        flash('This drive is not open for applications.', 'warning')
        return redirect(url_for('student.dashboard'))

    already = Application.query.filter_by(student_id=current_user.id, drive_id=id).first()
    if already:
        flash('You have already applied to this drive.', 'warning')
        return redirect(url_for('student.dashboard'))

    application = Application(student_id=current_user.id, drive_id=id)
    db.session.add(application)
    db.session.commit()
    flash(f'Successfully applied to {drive.job_title}!', 'success')
    return redirect(url_for('student.dashboard'))


@student_bp.route('/history')
@login_required
def history():
    applications = Application.query.filter_by(student_id=current_user.id)\
                                    .order_by(Application.applied_on.desc()).all()
    return render_template('student/history.html', applications=applications)


@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name        = request.form['name']
        current_user.department  = request.form['department']
        current_user.phone       = request.form['phone']
        current_user.cgpa        = request.form.get('cgpa') or None
        current_user.grad_year   = request.form.get('grad_year') or None
        current_user.skills      = request.form['skills']
        current_user.resume_link = request.form['resume_link']
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('student.dashboard'))
    return render_template('student/edit_profile.html')
