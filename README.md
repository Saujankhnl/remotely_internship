# Remotely - Internship & Job Platform

A full-stack platform built with Django where companies can post jobs/internships and candidates can apply, chat, and get AI-screened.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-cyan)
![CI](https://github.com/saujankhnl/remotely_internship/actions/workflows/ci.yml/badge.svg)

---

## 🎯 Features

| Module | Features |
|--------|----------|
| **Auth** | Registration, Login, OTP password reset, Google/LinkedIn social login |
| **Jobs & Internships** | Create, edit, search, filter, bookmark, premium listings |
| **Applications** | Apply with CV, status tracking, structured remarks, rejection/acceptance tags |
| **ATS Screening** | Auto-screening with weighted scoring, ranked applicants, screening analytics |
| **Chat** | Real-time messaging (WebSocket + AJAX fallback), file attachments |
| **Interviews** | Schedule, reschedule, cancel, complete with notes |
| **Assessments** | Timed skill tests, MCQ, verified badges, attempt limits |
| **Resume Builder** | Generate PDF resumes from profile data (multiple templates) |
| **Notifications** | In-app notifications with real-time count, mark read |
| **Analytics** | Job views, application funnels, company dashboard, screening analytics |
| **Advanced Search** | Smart query parsing, skill matching, saved searches, trending searches |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone
git clone https://github.com/saujankhnl/remotely_internship.git
cd remotely_internship

# Virtual environment
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your values (optional for development)

# Database
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

### Environment Variables

Copy `.env.example` to `.env`. All variables have sensible defaults for development. See [.env.example](.env.example) for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Production | Django secret key |
| `DJANGO_DEBUG` | No | `True` (default) or `False` |
| `SENDGRID_API_KEY` | For emails | SendGrid API key |
| `GOOGLE_CLIENT_ID` | For social login | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | For social login | Google OAuth secret |

---

## 📁 Project Structure

```
remotely_internship/
├── accounts/              # Auth, profiles, admin dashboard
├── internships/           # Jobs, internships, applications, ATS, analytics
├── chat/                  # Real-time messaging (WebSocket + AJAX)
├── notifications/         # In-app notification system
├── resume/                # PDF resume builder
├── assessments/           # Skill assessments & badges
├── theme/                 # TailwindCSS configuration
├── remotely_internship/   # Django project settings
├── docs/                  # Documentation
│   └── DATABASE.md        # Database schema & setup guide
├── .github/workflows/     # CI/CD pipeline
│   └── ci.yml             # Tests, linting on push/PR
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── manage.py
```

---

## 🗄️ Database

- **Development**: SQLite (zero config)
- **Production**: PostgreSQL recommended

See [docs/DATABASE.md](docs/DATABASE.md) for full schema documentation, setup instructions, and common commands.

---

## 🔐 Security

- Environment-based secrets (`SECRET_KEY`, API keys)
- Role-based access (`@company_required`, `@user_required`, `@company_approved_required`)
- Rate-limited OTP requests and brute-force protection
- Django password validators enforced on registration and reset
- Server-side file upload validation (type, size)
- CSRF protection on all forms
- Secure cookie settings auto-enabled in production
- HSTS, SSL redirect, content-type sniffing protection

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
```

CI runs automatically on push/PR to `main` via GitHub Actions.

---

## 📊 Admin Panel

Access at `http://127.0.0.1:8000/admin/`

- Manage users, companies, approval workflows
- Bulk approve/reject/suspend companies
- View all jobs, internships, applications
- Manage skill assessments and questions

---

## 📝 API Endpoints

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/` | GET | Public | Registration |
| `/login/` | POST | Public | Login |
| `/dashboard/` | GET | Auth | Role-based dashboard |
| `/internships/` | GET | Public | Browse internships |
| `/internships/jobs/` | GET | Public | Browse jobs |
| `/internships/search/` | GET | Public | Advanced search |
| `/internships/create/` | POST | Company | Post internship |
| `/internships/jobs/create/` | POST | Company | Post job |
| `/chat/` | GET | Auth | Chat list |
| `/assessments/` | GET | User | Skill assessments |
| `/resume/` | GET | User | Resume builder |
| `/notifications/` | GET | Auth | Notifications |

---

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

Built by [saujankhnl](https://github.com/saujankhnl)
