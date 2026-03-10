# Database Setup & Documentation

## Overview

Remotely uses **SQLite** for development and can be configured to use **PostgreSQL** for production.

---

## Development Setup (SQLite)

No additional setup required. Django creates `db.sqlite3` automatically.

```bash
# Run migrations to create all tables
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py loaddata fixtures/sample_data.json
```

---

## Production Setup (PostgreSQL)

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
```

### 2. Create Database & User

```sql
CREATE DATABASE remotely_db;
CREATE USER remotely_user WITH PASSWORD 'your_secure_password';
ALTER ROLE remotely_user SET client_encoding TO 'utf8';
ALTER ROLE remotely_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE remotely_user SET timezone TO 'Asia/Kathmandu';
GRANT ALL PRIVILEGES ON DATABASE remotely_db TO remotely_user;
```

### 3. Install Python Driver

```bash
pip install psycopg2-binary
```

### 4. Configure Settings

Update `DATABASES` in `settings.py` or set the environment variable:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'remotely_db',
        'USER': 'remotely_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Database Schema

### Apps & Models

| App | Model | Description |
|-----|-------|-------------|
| **accounts** | `CustomUser` | Auth model with `user_type` (user/company) |
| **accounts** | `UserProfile` | Job seeker profile (skills, resume, etc.) |
| **accounts** | `CompanyProfile` | Company profile (approval workflow, verification) |
| **accounts** | `PasswordResetOTP` | Hashed OTP for password reset |
| **accounts** | `UserExperience` | Work experience entries |
| **accounts** | `UserEducation` | Education entries |
| **accounts** | `UserProject` | Portfolio projects |
| **internships** | `Job` | Job postings with screening config |
| **internships** | `JobApplication` | Job applications with match scoring |
| **internships** | `Internship` | Internship postings |
| **internships** | `Application` | Internship applications |
| **internships** | `Interview` | Scheduled interviews |
| **internships** | `StatusChange` | Application status audit trail |
| **internships** | `ApplicationRemark` | Structured remarks (rejection/acceptance tags) |
| **internships** | `AutoScreeningResult` | Detailed screening breakdown per application |
| **internships** | `CandidateFeedback` | Feedback visible to candidates |
| **internships** | `JobBookmark` | Saved/bookmarked jobs |
| **internships** | `JobView` | Job view analytics |
| **internships** | `JobCategory` | Categories for filtering |
| **internships** | `SavedSearch` | Saved search configurations |
| **internships** | `SearchLog` | Search analytics |
| **internships** | `RejectionTag` | Predefined rejection reasons |
| **internships** | `AcceptanceTag` | Predefined acceptance reasons |
| **chat** | `ChatRoom` | Chat room per job application |
| **chat** | `Message` | Chat messages with attachments |
| **notifications** | `Notification` | In-app notifications |
| **resume** | `GeneratedResume` | PDF resumes generated from profile |
| **assessments** | `SkillAssessment` | Skill test definitions |
| **assessments** | `Question` | MCQ questions |
| **assessments** | `AssessmentAttempt` | User attempts with timing |
| **assessments** | `AttemptAnswer` | Individual answers |
| **assessments** | `VerifiedBadge` | Earned skill badges |

### Key Relationships

```
CustomUser (1) ──── (1) UserProfile
CustomUser (1) ──── (1) CompanyProfile
CustomUser (1) ──── (N) Job
CustomUser (1) ──── (N) Internship
Job        (1) ──── (N) JobApplication
Internship (1) ──── (N) Application
JobApplication (1) ── (1) ChatRoom
ChatRoom   (1) ──── (N) Message
JobApplication (1) ── (N) Interview
JobApplication (1) ── (1) AutoScreeningResult
SkillAssessment (1) ─ (N) Question
SkillAssessment (1) ─ (N) AssessmentAttempt
AssessmentAttempt (1)─(N) AttemptAnswer
```

### Constraints

- `UniqueConstraint('internship', 'applicant')` — one application per internship per user
- `UniqueConstraint('job', 'applicant')` — one application per job per user
- `UniqueConstraint('user', 'job')` — one bookmark per job per user
- `unique_together('user', 'assessment')` — one badge per assessment per user

---

## Common Commands

```bash
# Check for model changes
python manage.py makemigrations --dry-run

# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reset a specific app's migrations (development only!)
python manage.py migrate app_name zero

# Open database shell
python manage.py dbshell

# Export data
python manage.py dumpdata --indent 2 > backup.json

# Import data
python manage.py loaddata backup.json
```
