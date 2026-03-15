# Django Online Ticket Booking

Online ticket booking web app built with Django as part of Epic Learn Python Master Course (Batch 01 - 2026).

## Features

- User registration, login, logout, and dashboard
- Event listing and event detail pages
- Venue page
- Booking domain models for bookings and tickets
- Django admin management
- Tailwind CSS integration for UI styling

## Tech Stack

- Python 3.12+
- Django 6.0.2
- PostgreSQL (via `psycopg`)
- Tailwind (`django-tailwind` app integration)

## Project Apps

- `bookings` - home, event/venue pages, booking-related models
- `accounts` - auth flows and dashboard
- `theme` - Tailwind theme app
- `config` - project settings and URL routing

## Setup

### 1. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):

```bat
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

## Run the Project

Start Django server:

```bash
python manage.py runserver
```

Optional: run Tailwind watcher in a second terminal:

```bash
python manage.py tailwind start
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin/`

## Main Routes

- `/` - home page
- `/venue` - venue page
- `/events/` - event list
- `/events/<uuid:event_id>/` - event details
- `/accounts/login/` - login
- `/accounts/register/` - register
- `/accounts/logout/` - logout
- `/accounts/dashboard/` - user dashboard

## Tests

```bash
python manage.py test
```

## Notes

- Database engine is configured for PostgreSQL in project settings.
- Static files are served from the `static/` directory during development.
