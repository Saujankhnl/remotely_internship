# Remotely - Internship Platform

A full-stack internship platform built with Django where companies can post internships and students can apply.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-cyan)

## 🎯 Project Overview

**Remotely** is a role-based internship platform that connects companies with students seeking internship opportunities.

### Key Features

| Feature | Description |
|---------|-------------|
| **Role-Based Access** | Separate dashboards for Companies and Students |
| **Internship Posting** | Companies can post paid/unpaid internships |
| **Application System** | Students can apply with CV upload |
| **Status Tracking** | Track applications (Pending → Accepted/Rejected) |
| **Search & Filter** | Find internships by skills, type, location |
| **Secure Authentication** | OTP-based password reset |

---

## 🏗️ Architecture

### Database Schema (ER Diagram)

```
┌─────────────────┐       ┌─────────────────┐
│   CustomUser    │       │   UserProfile   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──────>│ user (FK)       │
│ username        │       │ full_name       │
│ email           │       │ phone           │
│ password        │       │ skills          │
│ user_type       │       │ resume          │
│ (user/company)  │       │ linkedin        │
└────────┬────────┘       └─────────────────┘
         │
         │ (if company)
         v
┌─────────────────┐       ┌─────────────────┐
│ CompanyProfile  │       │   Internship    │
├─────────────────┤       ├─────────────────┤
│ user (FK)       │       │ id (PK)         │
│ company_name    │       │ company (FK)────┼───> CustomUser
│ industry        │       │ title           │
│ logo            │       │ description     │
└─────────────────┘       │ type (paid/     │
                          │      unpaid)    │
                          │ skills_required │
                          │ status (open/   │
                          │        closed)  │
                          └────────┬────────┘
                                   │
                                   v
                          ┌─────────────────┐
                          │  Application    │
                          ├─────────────────┤
                          │ internship (FK) │
                          │ applicant (FK)──┼───> CustomUser
                          │ full_name       │
                          │ cv (file)       │
                          │ status          │
                          │ applied_at      │
                          └─────────────────┘
```

### Key Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Profile | One-to-One | Each user has one profile |
| Company → Internships | One-to-Many | Company can post many internships |
| Internship → Applications | One-to-Many | Internship can receive many applications |
| User → Applications | One-to-Many | User can apply to many internships |
| User + Internship | Unique Together | User can apply only once per internship |

---

## 🔐 Security Features

### Role-Based Access Control

```python
# Decorators ensure only authorized users access views
@company_required  # Only companies can post internships
@user_required     # Only students can apply
```

### Data Protection

- ✅ Companies can only see their own internships and applicants
- ✅ Students can only see their own applications
- ✅ URL manipulation is prevented (e.g., changing `/application/5/` to `/application/6/`)
- ✅ Duplicate application prevention (database constraint)
- ✅ CV file validation (PDF/DOC only, max 5MB)
- ✅ OTP stored as hash (not plain text)

---

## 📊 Dashboard Features

### Company Dashboard
- Total Posts count (jobs + internships)
- Total Applications received and status breakdown
- Pending applications to review
- Total profile views and unread chat/notification alerts
- List of internships with application counts
- Quick actions: Post new, View applicants, view analytics, check messages/alerts

### Student Dashboard
- Total applications sent (jobs + internships)
- Pending/Accepted/Rejected counts plus interview requests
- Available internships and jobs to browse
- Saved jobs count
- Resumes created and quick resume builder
- Badges earned from assessments and link to skill tests
- Unread notifications and chat messages
- Recent applications with status

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/remotely-internship.git
cd remotely-internship

# 2. Create virtual environment
python -m venv env

# 3. Activate virtual environment
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (admin)
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

### Environment Variables (Optional)

```bash
# For email functionality (SendGrid)
set SENDGRID_API_KEY=your_api_key
set DEFAULT_FROM_EMAIL=your@email.com
```

---

## 📁 Project Structure

```
remotely_internship/
├── accounts/              # User authentication & profiles
│   ├── models.py          # CustomUser, UserProfile, CompanyProfile
│   ├── views.py           # Login, Register, Dashboard
│   ├── forms.py           # Registration & Profile forms
│   └── templates/         # Auth templates
│
├── internships/           # Core internship functionality
│   ├── models.py          # Internship, Application
│   ├── views.py           # CRUD operations
│   ├── forms.py           # Internship & Application forms
│   └── templates/         # Internship templates
│
├── theme/                 # TailwindCSS configuration
├── media/                 # User uploads (CVs, photos)
├── manage.py
└── README.md
```

---

## 🧪 Testing the Application

### Test Scenarios

1. **Register as Company** → Post internship → View applications
2. **Register as Student** → Browse internships → Apply → Track status
3. **Password Reset** → Enter email → Check terminal for OTP → Reset password

### Admin Panel

Access at: `http://127.0.0.1:8000/admin/`

---

## 📝 API Endpoints

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/` | GET | Public | Registration page |
| `/login/` | GET/POST | Public | Login |
| `/dashboard/` | GET | Auth | Role-based dashboard |
| `/internships/` | GET | Public | Browse internships |
| `/internships/create/` | POST | Company | Create internship |
| `/internships/<id>/apply/` | POST | Student | Apply to internship |
| `/internships/my-internships/` | GET | Company | My posted internships |
| `/internships/my-applications/` | GET | Student | My applications |

---

## 🎤 Interview Preparation

### How to Explain This Project

> "I built a full-stack internship platform using Django. It has two user roles - Companies and Students. Companies can post internships with required skills, and students can apply by uploading their CV. I implemented role-based access control, secure file uploads, and OTP-based password reset. The dashboard shows real-time statistics based on database queries."

### Key Technical Points to Mention

1. **Django ORM** - Used for database operations
2. **Role-Based Access** - Custom decorators for authorization
3. **File Upload Security** - Validated file types and size limits
4. **Database Constraints** - Prevented duplicate applications
5. **Responsive UI** - TailwindCSS for mobile-friendly design

### Common Interview Questions

**Q: How do you prevent a user from applying twice?**
> A: I used Django's `UniqueConstraint` on `(internship, applicant)` fields. This ensures the database rejects duplicate applications.

**Q: How do you handle different user roles?**
> A: I added a `user_type` field to the User model and created custom decorators (`@company_required`, `@user_required`) that check the user's role before allowing access.

**Q: How do you secure file uploads?**
> A: I validate file extension (PDF/DOC only), check file size (max 5MB), and store files in a protected media directory.

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💻 Author

Built as a learning project to demonstrate full-stack Django development.
