from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import Company, Student, PlacementDrive, Application

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    stats = {
        'total_students'  : Student.query.count(),
        'total_companies' : Company.query.count(),
        'total_drives'    : PlacementDrive.query.count(),
        'total_apps'      : Application.query.count(),
    }

    pending_companies = Company.query.filter_by(is_approved=False, is_blacklisted=False).all()
    pending_drives    = PlacementDrive.query.filter_by(status='Pending').all()
    all_companies     = Company.query.filter_by(is_blacklisted=False).all()
    all_students      = Student.query.filter_by(is_blacklisted=False).all()
    all_applications  = Application.query.order_by(Application.applied_on.desc()).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           pending_companies=pending_companies,
                           pending_drives=pending_drives,
                           all_companies=all_companies,
                           all_students=all_students,
                           all_applications=all_applications)


@admin_bp.route('/search')
@login_required
def search():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    query       = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'student')
    results     = []

    if query:
        if search_type == 'student':
            results = Student.query.filter(
                Student.name.ilike(f'%{query}%') |
                Student.email.ilike(f'%{query}%')
            ).all()
        else:
            results = Company.query.filter(
                Company.name.ilike(f'%{query}%')
            ).all()

    return render_template('admin/search.html', results=results, query=query, search_type=search_type)


@admin_bp.route('/company/<int:id>/approve')
@login_required
def approve_company(id):
    company = Company.query.get_or_404(id)
    company.is_approved = True
    db.session.commit()
    flash(f'{company.name} has been approved.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/company/<int:id>/reject')
@login_required
def reject_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('Company registration rejected and removed.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/company/<int:id>/blacklist')
@login_required
def blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.is_blacklisted = True
    for drive in company.drives:
        drive.status = 'Closed'
    db.session.commit()
    flash(f'{company.name} has been blacklisted and all their drives closed.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/company/<int:id>/unblacklist')
@login_required
def unblacklist_company(id):
    company = Company.query.get_or_404(id)
    company.is_blacklisted = False
    db.session.commit()
    flash(f'{company.name} has been unblacklisted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/company/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    company = Company.query.get_or_404(id)
    if request.method == 'POST':
        company.name       = request.form['name']
        company.hr_contact = request.form['hr_contact']
        company.phone      = request.form['phone']
        company.website    = request.form['website']
        db.session.commit()
        flash('Company updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_company.html', company=company)


@admin_bp.route('/company/<int:id>/delete')
@login_required
def delete_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('Company deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/drive/<int:id>/approve')
@login_required
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" approved.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/drive/<int:id>/reject')
@login_required
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    db.session.delete(drive)
    db.session.commit()
    flash('Drive rejected and removed.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/student/<int:id>/blacklist')
@login_required
def blacklist_student(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = True
    db.session.commit()
    flash(f'{student.name} has been blacklisted.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/student/<int:id>/unblacklist')
@login_required
def unblacklist_student(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = False
    db.session.commit()
    flash(f'{student.name} has been unblacklisted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/student/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name       = request.form['name']
        student.department = request.form['department']
        student.phone      = request.form['phone']
        student.cgpa       = request.form['cgpa'] or None
        db.session.commit()
        flash('Student updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_student.html', student=student)


@admin_bp.route('/student/<int:id>/delete')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('admin.dashboard'))
