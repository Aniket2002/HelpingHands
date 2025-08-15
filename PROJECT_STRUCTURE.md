# MindBridge Project Structure

This document explains the purpose of each file and directory in the MindBridge mental health platform.

## Root Directory Files

### Configuration Files
- `.env` - Environment variables (secrets, database URLs, etc.)
- `.env.example` - Template for environment variables
- `.gitignore` - Git ignore rules for files not to track
- `requirements.txt` - Python package dependencies
- `package.json` - Node.js dependencies for frontend tools
- `tailwind.config.js` - Tailwind CSS configuration
- `setup.py` - Python package setup configuration

### Deployment Files
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Multi-container Docker setup
- `manage.py` - Django management script

### Database
- `db.sqlite3` - SQLite database file (development)

### Documentation
- `README.md` - Project documentation and setup instructions

## Directories

### Core Django Project
- `mindbridge/` - Django project settings and configuration
  - `settings.py` - Django settings
  - `urls.py` - Main URL configuration
  - `wsgi.py` - WSGI configuration for deployment

### Django Applications
- `apps/` - All Django applications
  - `authentication/` - User authentication and profiles
  - `wellness/` - Mental health tracking and goals
  - `chat/` - Support chat and crisis intervention
  - `appointments/` - Therapist matching and booking
  - `community/` - Support groups and community features

### Frontend
- `templates/` - Django HTML templates
  - `base.html` - Base template for all pages
  - `home.html` - Landing page
  - `dashboard.html` - User dashboard
  - `auth/` - Authentication templates (login, register, profile)
  - `wellness/` - Wellness module templates
  - `chat/` - Chat and support templates
  - `appointments/` - Appointment booking templates
  - `community/` - Community and support group templates

### Static Files & Media
- `static/` - Static files (CSS, JS, images) - served by Django
- `media/` - User uploaded files (profile pictures, etc.)

### Development Environment
- `.git/` - Git repository data
- `.venv/` - Python virtual environment

## File Organization Principles

1. **Modular Architecture**: Each feature is contained in its own Django app
2. **Separation of Concerns**: Templates, static files, and Python code are organized separately
3. **Security**: Sensitive configuration is in environment variables
4. **Scalability**: Apps can be developed and deployed independently
5. **Standards Compliance**: Follows Django best practices and project structure

## Getting Started

1. Set up virtual environment: `python -m venv .venv`
2. Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables: Copy `.env.example` to `.env` and fill in values
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Start development server: `python manage.py runserver`

For detailed setup instructions, see README.md.
