# OFCNetTracker Django Web Application

A clean, production-ready Django application designed for tracking OFC networks. This project is pre-configured and optimized for hosting on [Render](https://render.com) using standard blueprints.

---

## 📁 Clean Repository Structure

All obsolete configuration folders (Vercel, Netlify, Firebase), diagnostic scripts, logs, and site-package caches have been cleaned up. The repository is organized as a textbook-perfect, lightweight Django structure:

```
OFCNetTracker/
├── nwo_portal/           # Django project root settings and WSGI module
├── inventory/            # Primary inventory management Django application
├── network/              # Network configuration Django application
├── db.sqlite3            # Populated local SQLite database (for local dev)
├── render.yaml           # Render Blueprint configuration for automatic infrastructure
├── build.sh              # Unified build script used by Render for deployment
├── requirements.txt      # Python dependencies for development and production
├── manage.py             # Django admin CLI entry point
├── Dockerfile            # Multi-environment container setup (optional fallback)
├── .gitignore            # Clean git ignore rule set
└── README.md             # Developer documentation
```

---

## 🚀 Deployment to Render (Recommended)

Render offers a fully-automated, zero-config deployment path using the included Blueprint spec (`render.yaml`).

### Option 1: Render Blueprint (Automatic & Instant)

1. Commit your changes and push the repository to GitHub or GitLab.
2. Sign in to the [Render Dashboard](https://dashboard.render.com).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub/GitLab repository.
5. Render will automatically detect the `render.yaml` configuration and provision:
   - 🐘 **A PostgreSQL database** (`ofcnet_db`) to store production data securely.
   - ⚡ **A Python Web Service** (`ofc-net-tracker`) with:
     - **Build Command**: `./build.sh` (automatic package install and static assets processing)
     - **Pre-deploy Command**: `python manage.py migrate --noinput` (automatic database migrations during release phase)
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT nwo_portal.wsgi:application` (production web server)
6. Click **Approve** and let Render automatically build and deploy!

### Option 2: Manual Web Service Setup

If you prefer deploying a standalone Web Service manually without a blueprint:

1. Click **New +** -> **Web Service** in Render.
2. Select your repository.
3. Configure the following parameters:
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT nwo_portal.wsgi:application`
4. In the **Environment Variables** tab, add your settings:
   - `DATABASE_URL`: Connection string to your production database
   - `DEBUG`: `False` (for production security)
   - `ALLOWED_HOSTS`: `*` or your custom domain name
   - `SECRET_KEY`: *[Insert a unique random key]*

---

## 💻 Local Development Setup

To run and edit the project locally on your machine, follow these steps:

### 1. Create a Clean Virtual Environment
Open your terminal at the root of the project and execute:
```bash
# Create a fresh virtual environment
python -m venv venv

# Activate on Windows (Command Prompt)
venv\Scripts\activate

# Or on Git Bash / macOS / Linux
source venv/bin/activate
```

### 2. Install Project Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Local System & Database
Run Django checks to verify there are no system problems:
```bash
python manage.py check
```

Run database migrations (or verify the local SQLite database state):
```bash
python manage.py migrate
```

### 4. Seed Data (Optional)
If you need to seed or sync database entries, use the provided helper scripts:
```bash
python populate_exchanges.py
python populate_data.py
python setup_roles.py
```

### 5. Launch the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000`** in your browser to access the local application.

---

## 🛡️ Production & Performance Features Enabled

- **Database Fallback**: Automatically connects to the PostgreSQL cloud database in production via `DATABASE_URL`, and smoothly falls back to local `db.sqlite3` in development.
- **Static Assets Delivery**: Configured with `WhiteNoise` for compressed, highly cached, and lightning-fast delivery of CSS, JavaScript, and asset files.
- **Security Protocols**: Configured to run behind Gunicorn, automatically reads keys from secure Render Environment Variables, and disables Django debug logs in production.
