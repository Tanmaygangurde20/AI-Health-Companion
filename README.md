# Hospital Management System

A comprehensive web-based hospital management system built with Flask, featuring role-based access for doctors, patients, and receptionists.

![Medical Dashboard](https://img.shields.io/badge/Medical-Dashboard-blue)
![Flask](https://img.shields.io/badge/Flask-2.0.1-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)

## 🏥 Overview

This Hospital Management System is designed to streamline healthcare operations by providing dedicated interfaces for different stakeholders in a medical facility. The system features role-based access control, allowing doctors, patients, and receptionists to access relevant information and perform their specific tasks.

## ✨ Features

- **Multi-role Authentication**: Secure login system for doctors, patients, and receptionists
- **Patient Management**: Track patient records, appointments, and medical history
- **Doctor Dashboard**: Manage appointments, view patient records, and prescribe medications
- **Receptionist Interface**: Handle patient registration and appointment scheduling
- **Health Reports**: Generate and view detailed health reports
- **Follow-up Management**: Schedule and track patient follow-ups
- **Medicine Expiry Alerts**: Monitor medication inventory and expiry dates
- **Health Chatbot**: AI-powered assistant for basic health queries
- **Analytics Dashboard**: Visualize healthcare data and trends

## 🚀 Project Structure

```
hospital-management-system/
├── app/                      # Main application package
│   ├── __init__.py           # Application initialization
│   ├── config.py             # Configuration settings
│   ├── models.py             # Database models
│   ├── routes/               # Route handlers
│   │   ├── main.py           # Main routes (login, etc.)
│   │   ├── doctor.py         # Doctor-specific routes
│   │   ├── patient.py        # Patient-specific routes
│   │   ├── receptionist.py   # Receptionist-specific routes
│   │   └── analytics.py      # Analytics and reporting routes
│   ├── static/               # Static files
│   │   └── style.css         # Custom CSS styles
│   ├── templates/            # HTML templates
│   │   ├── base.html         # Base template
│   │   ├── login.html        # Login page
│   │   ├── doctor_dashboard.html  # Doctor dashboard
│   │   ├── patient_dashboard.html # Patient dashboard
│   │   ├── receptionist_dashboard.html # Receptionist dashboard
│   │   └── ...               # Other templates
│   └── utils/                # Utility functions
│       └── email.py          # Email functionality
├── migrations/               # Database migrations
├── instance/                 # Instance-specific files
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── update_db.py              # Database update script
├── create_receptionist.py    # Script to create receptionist accounts
└── migrations.py             # Migration utilities
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap
- **Icons**: Font Awesome
- **Authentication**: Flask-Login

## 🚦 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   python run.py
   ```

7. Access the application at `http://localhost:5000`

## 👥 User Roles

### Doctor
- View and manage patient records
- Schedule appointments
- Prescribe medications
- Generate health reports
- View analytics

### Patient
- View personal health records
- Schedule appointments
- View prescriptions
- Access health chatbot
- Track follow-ups

### Receptionist
- Register new patients
- Schedule appointments
- Manage patient information
- Handle administrative tasks

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Flask framework and its extensions
- Bootstrap for the UI components
- Font Awesome for icons
- All contributors to this project 