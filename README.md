# 🎓 College Placement Portal

A full-stack web application built with **Flask** that manages the entire college placement process — from company registration and drive creation to student applications and admin oversight.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [User Roles](#user-roles)
- [How It Works — The Full Flow](#how-it-works--the-full-flow)
- [All Routes Reference](#all-routes-reference)
- [Installation & Running](#installation--running)
- [Default Admin Credentials](#default-admin-credentials)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

The College Placement Portal connects three types of users — **Admin**, **Companies**, and **Students** — on a single platform. Companies post placement drives, students apply to them, and the admin oversees and controls every step of the process.

Every action requires approval:
- A company must be **approved by admin** before they can log in
- A placement drive must be **approved by admin** before students can see it
- Students can then apply, and companies update each application's status

---

## Features

### Admin
- View a dashboard with live stats (total students, companies, drives, applications)
- Approve or reject new company registrations
- Approve or reject placement drives submitted by companies
- Blacklist / unblacklist companies and students
- Edit or delete any company or student record
- Search students and companies by name or email

### Company
- Register and wait for admin approval
- Create placement drives (job title, description, eligibility, salary, location, deadline)
- Edit drives (re-submits for admin approval automatically)
- View all applicants for each drive
- Update each application status: Applied → Shortlisted → Selected / Rejected
- Add remarks to applications
- Close or delete drives
- Edit company profile

### Student
- Register and log in immediately (no approval needed)
- View all approved placement drives
- Apply to drives (one application per drive enforced)
- View full drive details before applying
- Track all past applications and their statuses
- Edit personal profile (CGPA, skills, resume link, department, etc.)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Flask (Python) |
| Database ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Password Security | Werkzeug (PBKDF2 hashing) |
| Database | SQLite (`portal.db`) |
| Templating | Jinja2 (HTML templates) |
| Session Management | Flask session (server-side cookie) |

---

## Project Structure

```
placement_portal/
│
├── app.py                  ← App factory: config, blueprints, DB init, admin seed
├── extensions.py           ← db and login_manager objects (prevents circular imports)
├── models.py               ← All 5 database models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← /login  /register  /logout
│   ├── admin.py            ← /admin/...  (all admin actions)
│   ├── company.py          ← /company/...  (drives, applicants, profile)
│   └── student.py          ← /student/...  (dashboard, apply, history, profile)
│
├── templates/
│   ├── base.html           ← Shared layout (navbar, flash messages)
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── edit_company.html
│   │   ├── edit_student.html
│   │   └── search.html
│   ├── company/
│   │   ├── dashboard.html
│   │   ├── create_drive.html
│   │   ├── edit_drive.html
│   │   ├── edit_profile.html
│   │   └── applicants.html
│   └── student/
│       ├── dashboard.html
│       ├── drive_detail.html
│       ├── edit_profile.html
│       └── history.html
│
└── instance/
    └── portal.db           ← SQLite database file (auto-created on first run)
```

---

## Database Schema

The application uses **5 tables** in SQLite.

### `admin`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| username | String(50) | Unique, Not Null |
| email | String(120) | Unique, Not Null |
| name | String(100) | Not Null |
| password | String(256) | Not Null (hashed) |

### `company`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| username | String(50) | Unique, Not Null |
| email | String(120) | Unique, Not Null |
| name | String(150) | Not Null |
| hr_contact | String(100) | |
| phone | String(20) | |
| website | String(200) | |
| overview | Text | |
| password | String(256) | Not Null (hashed) |
| is_approved | Boolean | Default: False |
| is_blacklisted | Boolean | Default: False |
| joined_on | DateTime | Default: now |

### `student`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| username | String(50) | Unique, Not Null |
| email | String(120) | Unique, Not Null |
| name | String(100) | Not Null |
| department | String(100) | |
| cgpa | Float | |
| phone | String(20) | |
| grad_year | Integer | |
| skills | Text | |
| resume_link | String(300) | |
| password | String(256) | Not Null (hashed) |
| is_blacklisted | Boolean | Default: False |
| joined_on | DateTime | Default: now |

### `placement_drive`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| company_id | Integer | Foreign Key → company.id |
| job_title | String(150) | Not Null |
| description | Text | Not Null |
| eligibility | Text | |
| salary | String(50) | |
| location | String(100) | |
| deadline | Date | |
| status | String(20) | Default: `'Pending'` |
| created_on | DateTime | Default: now |

**Drive status lifecycle:** `Pending` → `Approved` → `Closed`

### `application`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| student_id | Integer | Foreign Key → student.id |
| drive_id | Integer | Foreign Key → placement_drive.id |
| applied_on | DateTime | Default: now |
| status | String(20) | Default: `'Applied'` |
| remarks | String(300) | |

**Application status lifecycle:** `Applied` → `Shortlisted` → `Selected` or `Rejected`

**Unique constraint:** `(student_id, drive_id)` — prevents a student from applying to the same drive twice.

### Relationships

```
Admin       ──────────────── (no relationships, standalone)

Company     ──< PlacementDrive   (one company → many drives)
                     │
PlacementDrive ──< Application   (one drive → many applications)
                     │
Student     ──< Application      (one student → many applications)
```

Cascade rules: deleting a Company deletes all its drives. Deleting a drive or student deletes all related applications.

---

## User Roles

| Role | Registration | Login Condition | Prefix |
|---|---|---|---|
| Admin | Auto-created on first run | Always allowed | `/admin` |
| Company | Self-register via `/register` | Only after admin approval | `/company` |
| Student | Self-register via `/register` | Immediately after registration | `/student` |

Role is stored in `session['role']` on login, which allows Flask-Login's `user_loader` to load the correct model (Admin / Company / Student) for each request.

---

## How It Works — The Full Flow

```
1. First run
   └── app.py creates all tables and seeds the admin account
       (username: admin | password: admin123)

2. Company registers at /register
   └── Account created with is_approved = False
   └── Cannot log in yet

3. Admin logs in → sees pending companies on dashboard
   └── Clicks Approve → is_approved = True
   └── Company can now log in

4. Company logs in → creates a Placement Drive
   └── Drive created with status = 'Pending'
   └── Students cannot see it yet

5. Admin sees pending drives on dashboard
   └── Clicks Approve → status = 'Approved'
   └── Drive is now visible to all students

6. Student registers → logs in → sees all Approved drives
   └── Clicks Apply → Application row created
       (student_id, drive_id, status='Applied')

7. Company views applicants for their drive
   └── Updates application status:
       Applied → Shortlisted → Selected / Rejected
   └── Can add remarks to each application

8. Student checks /student/history
   └── Sees all applications and their current statuses

9. Admin can at any time:
   └── Blacklist a company → all their drives closed
   └── Blacklist a student → they cannot log in
   └── Delete any user or drive
   └── Edit company/student details directly
```

---

## All Routes Reference

### Auth (`auth_bp` — no prefix)
| Method | URL | Description |
|---|---|---|
| GET | `/` | Redirects to dashboard if logged in, else to login |
| GET/POST | `/login` | Login page for all roles |
| GET/POST | `/register` | Registration for students and companies |
| GET | `/logout` | Logs out and clears session |

### Admin (`admin_bp` — prefix: `/admin`)
| Method | URL | Description |
|---|---|---|
| GET | `/admin/dashboard` | Main admin dashboard with stats and all data |
| GET | `/admin/search` | Search students or companies by name/email |
| GET | `/admin/company/<id>/approve` | Approve a pending company |
| GET | `/admin/company/<id>/reject` | Reject and delete a pending company |
| GET | `/admin/company/<id>/blacklist` | Blacklist company and close all their drives |
| GET | `/admin/company/<id>/unblacklist` | Remove blacklist from company |
| GET/POST | `/admin/company/<id>/edit` | Edit company details |
| GET | `/admin/company/<id>/delete` | Permanently delete a company |
| GET | `/admin/drive/<id>/approve` | Approve a pending drive |
| GET | `/admin/drive/<id>/reject` | Reject and delete a pending drive |
| GET | `/admin/student/<id>/blacklist` | Blacklist a student |
| GET | `/admin/student/<id>/unblacklist` | Remove blacklist from student |
| GET/POST | `/admin/student/<id>/edit` | Edit student details |
| GET | `/admin/student/<id>/delete` | Permanently delete a student |

### Company (`company_bp` — prefix: `/company`)
| Method | URL | Description |
|---|---|---|
| GET | `/company/dashboard` | Company dashboard (active + closed drives) |
| GET/POST | `/company/drive/create` | Create a new placement drive |
| GET/POST | `/company/drive/<id>/edit` | Edit a drive (resets to Pending status) |
| GET | `/company/drive/<id>/close` | Close a drive |
| GET | `/company/drive/<id>/delete` | Delete a drive |
| GET | `/company/drive/<id>/applicants` | View all applicants for a drive |
| POST | `/company/application/<id>/update` | Update application status and remarks |
| GET/POST | `/company/profile/edit` | Edit company profile |

### Student (`student_bp` — prefix: `/student`)
| Method | URL | Description |
|---|---|---|
| GET | `/student/dashboard` | View all open drives and own applications |
| GET | `/student/drive/<id>` | View full details of a drive |
| GET | `/student/drive/<id>/apply` | Apply to a drive |
| GET | `/student/history` | View full application history |
| GET/POST | `/student/profile/edit` | Edit student profile |

---

## Installation & Running

### 1. Clone or extract the project
```bash
cd placement_portal
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

On first run, the database (`instance/portal.db`) is created automatically and the admin account is seeded.

---

## Default Admin Credentials

```
Username : admin
Password : admin123
Role     : admin
```

> ⚠️ Change the `SECRET_KEY` in `app.py` before deploying to production.

---

## Key Design Decisions

**Why `extensions.py`?**
`db` and `login_manager` are created in a separate file to avoid circular imports. `models.py` needs `db`, `routes/` need models, and `app.py` needs routes — if `db` lived in `app.py`, every file would import from `app.py` creating a circular dependency chain.

**Why Blueprints?**
Routes are split into 4 blueprints (`auth`, `admin`, `company`, `student`) so each file only contains related logic. URL prefixes (`/admin`, `/company`, `/student`) are applied at registration in `app.py`, keeping route definitions clean.

**Why `session['role']`?**
All three user types (Admin, Company, Student) share the same login page but live in different database tables. The role stored in the session tells Flask-Login's `user_loader` which model to query when identifying the current user on each request.

**Why password hashing?**
Passwords are never stored in plain text. `generate_password_hash()` uses PBKDF2-SHA256, a slow one-way algorithm. Even if the database is stolen, passwords cannot be recovered. `check_password_hash()` is used at login to verify without ever decrypting.

**Why `cascade='all, delete-orphan'`?**
Ensures referential integrity automatically. Deleting a Company deletes all its drives. Deleting a drive or student deletes all related applications. No orphaned records are left in the database.
