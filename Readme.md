# Letter of Credit

## Overview

The **Letter of Credit** project is a Django-based application designed to manage letters of credit (LCs). This project includes user registration, login functionality, and various LC management features such as adding, viewing, editing, deleting, and approving letters of credit. It also provides LC prediction functionality based on static data.

## Features

- **User Authentication**: Registration and login functionality.
- **LC Management**: Add, view, edit, delete, and approve letters of credit.
- **LC Prediction**: Predict future LCs based on static data.
- **Dashboard**: A simple dashboard page for navigation.

## Requirements

- Python 3.8 or higher
- Django 5.0.6
- MySQL

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/Letter_Of_Credit.git
   cd Letter_Of_Credit
# Running the code in our Local

1.Install the requiremts.txt
    pip install -r requirements.txt


Note: In your local system You have to install the My Sql Database.
      Change the details in settings.py. Which is present in my Project file(Letter of Credit)
      
myproject/
│
├── myproject/                   # Project package
│   ├── __init__.py              # Makes this directory a Python package
│   ├── asgi.py                  # ASGI configuration
│   ├── settings.py              # Settings for this Django project
│   ├── urls.py                  # URL declarations for this Django project
│   └── wsgi.py                  # WSGI configuration
│
├── myapp/                       # Application package (can be multiple apps)
│   ├── __init__.py              # Makes this directory a Python package
│   ├── admin.py                 # Admin interface settings for the app
│   ├── apps.py                  # App-specific settings
│   ├── forms.py                 # Forms for the app
│   ├── models.py                # Models for the app
│   ├── tests.py                 # Test cases for the app
│   ├── urls.py                  # URL declarations for the app
│   ├── views.py                 # Views for the app
│   └── migrations/              # Database migrations for the app
│       └── __init__.py          # Makes this directory a Python package
│
├── manage.py                    # Command-line utility for administrative tasks
│
├── static/                      # Directory for static files (CSS, JavaScript, images)
│
├── templates/                   # Directory for template files
│
└── requirements.txt             # List of project dependencies

2.Migrations
    python manage.py migrate
3. Run the server
    python manage.py runserver