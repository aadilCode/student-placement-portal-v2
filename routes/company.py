from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import PlacementDrive, Application
from datetime import datetime

company_bp = Blueprint('company', __name__)


@company_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))

    active_drives = PlacementDrive.query.filter(
        PlacementDrive.company_id == current_user.id,
        PlacementDrive.status != 'Closed'
    ).all()

    closed_drives = PlacementDrive.query.filter_by(
        company_id=current_user.id, status='Closed'
    ).all()

    return render_template('company/dashboard.html',
                           active_drives=active_drives,
                           closed_drives=closed_drives)


@company_bp.route('/drive/create', methods=['GET', 'POST'])
@login_required
def create_drive():
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        deadline_str = request.form.get('deadline')
        deadline     = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

        drive = PlacementDrive(
            company_id  = current_user.id,
            job_title   = request.form['job_title'],
            description = request.form['description'],
            eligibility = request.form['eligibility'],
            salary      = request.form['salary'],
            location    = request.form['location'],
            deadline    = deadline,
            status      = 'Pending'
        )
        db.session.add(drive)
        db.session.commit()
        flash('Drive submitted for admin approval.', 'info')
        return redirect(url_for('company.dashboard'))

    return render_template('company/create_drive.html')


@company_bp.route('/drive/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_drive(id):
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != current_user.id:
        flash('Not your drive.', 'danger')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        drive.job_title   = request.form['job_title']
        drive.description = request.form['description']
        drive.eligibility = request.form['eligibility']
        drive.salary      = request.form['salary']
        drive.location    = request.form['location']
        drive.status      = 'Pending'
        db.session.commit()
        flash('Drive updated and sent for re-approval.', 'info')
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_drive.html', drive=drive)


@company_bp.route('/drive/<int:id>/close')
@login_required
def close_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        flash('Not your drive.', 'danger')
        return redirect(url_for('company.dashboard'))
    drive.status = 'Closed'
    db.session.commit()
    flash('Drive closed.', 'info')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/drive/<int:id>/delete')
@login_required
def delete_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        flash('Not your drive.', 'danger')
        return redirect(url_for('company.dashboard'))
    db.session.delete(drive)
    db.session.commit()
    flash('Drive deleted.', 'info')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/drive/<int:id>/applicants')
@login_required
def view_applicants(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        flash('Not your drive.', 'danger')
        return redirect(url_for('company.dashboard'))
    applications = Application.query.filter_by(drive_id=id).all()
    return render_template('company/applicants.html', drive=drive, applications=applications)


@company_bp.route('/application/<int:id>/update', methods=['POST'])
@login_required
def update_application(id):
    application = Application.query.get_or_404(id)
    application.status  = request.form['status']
    application.remarks = request.form.get('remarks', '')
    db.session.commit()
    flash('Application status updated.', 'success')
    return redirect(url_for('company.view_applicants', id=application.drive_id))


@company_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name       = request.form['name']
        current_user.hr_contact = request.form['hr_contact']
        current_user.phone      = request.form['phone']
        current_user.website    = request.form['website']
        current_user.overview   = request.form['overview']
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('company.dashboard'))
    return render_template('company/edit_profile.html')
