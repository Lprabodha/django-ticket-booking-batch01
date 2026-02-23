# 🎟️ Django Online Ticket Booking Application

### Epic Learn - Python Master Course  
### Batch 01 - 2026  

## 📌 Project Overview

This project is a Django-based Online Ticket Booking Application developed as part of the **Epic Learn Python Master Course (Batch 01 - 2026)**.

## ✨ Features

- **User Authentication**: Secure user registration and login
- **Event Management**: Browse and search available events
- **Ticket Booking**: Book tickets for events with real-time availability
- **Payment Integration**: Secure payment processing
- **Order History**: View booking history and tickets
- **Admin Dashboard**: Manage events, users, and bookings

## 🛠️ Tech Stack

- **Backend**: Django 6.x+
- **Database**: PostgreSQL
- **Python**: 3.12+
- **Additional Libraries**: Listed in `requirements.txt`

## 📋 Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 🚀 Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 📁 Project Structure

```
online-ticket-booking/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
├── config/                   # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
└── bookings/                 # Main application
    ├── models.py            # Database models
    ├── views.py             # Application views
    ├── admin.py             # Admin interface
    ├── urls.py              # App URL patterns
    ├── forms.py             # Django forms
    └── templates/           # HTML templates
```

## 🔒 Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Use the superuser credentials created during setup.

## 📝 API Endpoints

- `GET /` - Home page
- `GET /bookings/` - View all events
- `POST /bookings/book/` - Book a ticket
- `GET /bookings/history/` - View booking history

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📚 Learning Outcomes

Through this project, you'll learn:

- Django project structure and configuration
- Database models and migrations
- Views and URL routing
- Template rendering
- Authentication and authorization
- Form handling
- Admin interface customization
- Best practices for Django development
---

**Happy Coding! 🚀**
