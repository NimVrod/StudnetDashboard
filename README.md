# StudentDashboard

## Getting Started

This guide will help you set up and run the StudentDashboard Django project on your local machine.

### Prerequisites

- Python 3.x
- Django 5.1.2
- Virtual environment tool (e.g., `venv`)

### Installation
   ```bash
   git clone <repository-url>
   cd StudentDashboard
   Create and activate a virtual environment:  
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   pip install -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```
