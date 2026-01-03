# Exeat Management System

A Django-based web application for managing student exeats (leave requests).

## Features

- User authentication
- Student and admin roles
- Exeat request creation and approval
- Admin panel for management

## Installation

1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Run server: `python manage.py runserver`

## Usage

- Students can log in and request exeats
- Admins can approve/reject exeats via the admin panel or web interface