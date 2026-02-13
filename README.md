🏢 EnterpriseHub - Multi-Tenant HR Management System
<div align="center">
Show Image
Show Image
Show Image
Show Image
Show Image
A powerful, secure, and scalable enterprise HR management platform with complete data isolation
Features • Architecture • Installation • Usage • Documentation
</div>

📋 Table of Contents

Overview
Key Features
System Architecture
Technology Stack
Prerequisites
Installation
Configuration
Usage Guide
Project Structure
API Documentation
Testing
Deployment
Contributing
License
Support


🌟 Overview
EnterpriseHub is a comprehensive, production-ready HR management system built with Django that leverages schema-based multi-tenancy for complete organizational data isolation. Each organization operates in its own secure database schema, ensuring maximum privacy and security.
🎯 Perfect For:

🏢 SaaS HR Platform Providers
🏭 Enterprise Organizations
🏗️ Multi-tenant Application Developers
📊 HR Management Companies
🌐 B2B Service Providers


✨ Features
🔐 Multi-Tenant Architecture

Schema-Based Isolation - Each organization gets its own PostgreSQL schema
Subdomain Routing - Automatic tenant detection via subdomain (e.g., company.yourdomain.com)
Data Privacy - Complete data isolation between organizations
Scalable Design - Easily handle thousands of tenants

👥 User Management

Three-Tier Role System:

🏆 Tenant Owner - Organization administrator with full control
🛡️ HR Managers - Department or organization-wide HR access
👤 Employees - Standard employee access with self-service features



✅ Secure Approval Workflows

HR Application Approval - Tenant owners approve HR manager applications
Employee Application Approval - HR managers approve employee applications
Email Notifications - Automated approval/rejection notifications
Audit Trail - Complete tracking of all approval decisions

🏢 Department Management

Create and manage organizational departments
Assign employees to specific departments
Department-specific or organization-wide HR access
Admin HR role with full access across all departments

📅 Attendance Management

Daily attendance tracking with Present/Absent/Leave status
Monthly attendance reports with statistics
Attendance correction requests with approval workflow
Department-filtered attendance views for HRs

📧 Email Integration

SMTP configuration for automated emails
Welcome emails on account approval
Application status notifications
Rejection reason notifications

📊 Analytics & Dashboards

Tenant Dashboard - Organization-wide statistics and insights
HR Dashboard - Department metrics and pending approvals
Employee Dashboard - Personal attendance and leave balance
Real-time data visualization

🎨 Modern UI/UX

Beautiful, responsive design with Tailwind CSS
Consistent indigo/blue color scheme
Mobile-friendly interface
Intuitive navigation and workflows


🏗️ Architecture
Multi-Tenancy Strategy
┌─────────────────────────────────────────────────────────────┐
│                     Main Domain                              │
│              (yourdomain.com)                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Public Schema                              │  │
│  │  • Tenant Records                                     │  │
│  │  • User Authentication                                │  │
│  │  • Application Metadata                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Subdomain: company1.yourdomain.com              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Tenant Schema: tenant_abc123                  │  │
│  │  • Users (Employees & HRs)                            │  │
│  │  • Departments                                        │  │
│  │  • Attendance Records                                 │  │
│  │  • Leave Applications                                 │  │
│  │  • Approval Requests                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Subdomain: company2.yourdomain.com              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Tenant Schema: tenant_xyz789                  │  │
│  │  • Completely isolated data                           │  │
│  │  • No cross-tenant access                             │  │
│  │  • Independent operations                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
User Flow Diagram
┌───────────────┐
│  Tenant Owner │
│   Signs Up    │
└───────┬───────┘
        │
        ├─► Creates Organization
        │   └─► Subdomain Generated
        │   └─► Schema Created
        │   └─► Default Departments Created
        │
        ├─► Reviews HR Applications
        │   ├─► Approves → Email Sent → HR Account Created
        │   └─► Rejects → Email Sent → Application Deleted
        │
        └─► Manages Departments
            └─► Views All Employees

┌───────────────┐
│  HR Manager   │
│   Applies     │
└───────┬───────┘
        │
        ├─► Application Created (Not User)
        │   └─► Email to Tenant Owner
        │
        ├─► (After Approval)
        │   └─► Account Created
        │   └─► Can Login
        │
        ├─► Reviews Employee Applications
        │   ├─► Approves → Email Sent → Employee Account Created
        │   └─► Rejects → Email Sent → Application Deleted
        │
        ├─► Marks Attendance
        └─► Reviews Attendance Corrections

┌───────────────┐
│   Employee    │
│   Applies     │
└───────┬───────┘
        │
        ├─► Application Created (Not User)
        │   └─► Email to HR Managers
        │
        ├─► (After Approval)
        │   └─► Account Created
        │   └─► Can Login
        │
        ├─► Views Personal Attendance
        ├─► Requests Attendance Corrections
        └─► Checks Leave Balance

🛠️ Technology Stack
Backend

Framework: Django 5.0+
Database: PostgreSQL 15+ (with schema support)
Authentication: Django Allauth
Task Queue: Celery (for async operations)
Cache: Redis

Frontend

CSS Framework: Tailwind CSS 3.0+
JavaScript: Vanilla JS (no framework overhead)
Icons: Heroicons (via Tailwind)

Email

SMTP: Gmail/Custom SMTP
Templates: Django Email Templates

Development Tools

Environment: Python 3.11+
Package Manager: pip
Version Control: Git


📦 Prerequisites
Before installation, ensure you have:
bash✓ Python 3.11 or higher
✓ PostgreSQL 15 or higher
✓ Redis (for caching and Celery)
✓ Git
✓ Virtual Environment tool (venv/virtualenv)

🚀 Installation
Step 1: Clone the Repository
bashgit clone https://github.com/yourusername/enterprisehub.git
cd enterprisehub
Step 2: Create Virtual Environment
bash# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
Step 3: Install Dependencies
bashpip install -r requirements.txt
Step 4: Configure Environment Variables
Create a .env file in the project root:
env# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost

# Database Configuration
DB_NAME=enterprisehub_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
ADMIN_USER_NAME=EnterpriseHub Admin
ADMIN_USER_EMAIL=admin@enterprisehub.com

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
Step 5: Setup Database
bash# Create PostgreSQL database
psql -U postgres

CREATE DATABASE enterprisehub_db;
\q

# Run migrations
python manage.py makemigrations
python manage.py migrate
Step 6: Create Superuser
bashpython manage.py createsuperuser
Step 7: Run Development Server
bash# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
celery -A your_project worker -l info

# Start Django server
python manage.py runserver
Visit: http://localhost:8000

⚙️ Configuration
Email Setup (Gmail)

Enable 2-Step Verification in your Google Account
Generate App Password:

Go to Google Account → Security → 2-Step Verification → App Passwords
Select "Mail" and "Other" device
Copy the 16-character password


Add to .env:

envEMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # 16-char app password
```

### Subdomain Configuration

#### Local Development

Add to your `hosts` file:

**Windows**: `C:\Windows\System32\drivers\etc\hosts`
**macOS/Linux**: `/etc/hosts`
```
127.0.0.1   localhost
127.0.0.1   company1.localhost
127.0.0.1   company2.localhost
127.0.0.1   testorg.localhost
```

#### Production

Configure your DNS:
```
A     @              → Your Server IP
A     *              → Your Server IP  (wildcard for subdomains)
CNAME www            → yourdomain.com
```

---

## 📖 Usage Guide

### For Tenant Owners

#### 1. Create Your Organization

1. Visit the main domain: `http://localhost:8000`
2. Click **"Start Free Trial"**
3. Fill in organization details
4. Choose a unique subdomain (e.g., `mycompany`)
5. Complete signup

✅ Your organization is created with:
- Unique subdomain: `mycompany.localhost:8000`
- Dedicated database schema
- Default departments (Engineering, Sales, etc.)

#### 2. Access Tenant Dashboard

Visit: `http://mycompany.localhost:8000/users/tenant/home/`

**Dashboard Features**:
- View total employees, HRs, and departments
- See pending HR approval requests
- Monitor recent signups
- Access department details

#### 3. Review HR Applications

1. Navigate to **"HR Approvals"** section
2. Review pending applications
3. Click **"Review Application"** to see full details:
   - Username and email
   - Admin or Department HR type
   - Requested departments
4. **Approve** → Email sent, HR account created
5. **Reject** → Email sent, application deleted

#### 4. Manage Departments

1. Click on any department card
2. View assigned HRs and employees
3. See department statistics

---

### For HR Managers

#### 1. Apply for HR Access

1. Visit your organization's subdomain: `http://yourcompany.localhost:8000`
2. Click **"Sign Up"**
3. Select role: **"HR"**
4. Choose:
   - **Admin HR**: Full access to all departments
   - **Department HR**: Select specific departments
5. Submit application

⏳ Wait for tenant owner approval email

#### 2. Access HR Dashboard

After approval, visit: `http://yourcompany.localhost:8000/users/hr/home/`

**Dashboard Features**:
- View total employees in your departments
- See pending employee approvals
- Monitor today's attendance
- Access recent requests

#### 3. Review Employee Applications

1. Navigate to **"Employee Approvals"**
2. Review pending applications (filtered by your departments)
3. Click **"Review Application"**
4. See applicant details:
   - Personal information
   - Requested department
   - Leave balance
5. **Approve** → Email sent, employee account created
6. **Reject** → Email sent with reason

#### 4. Mark Attendance

1. Go to **"Mark Attendance"**
2. Select employee from dropdown (your departments only)
3. Choose date
4. Select status: Present / Absent / Leave
5. Submit

#### 5. Review Attendance Corrections

1. Navigate to **"Review Requests"**
2. See pending correction requests
3. Review employee's reason
4. Approve or reject with feedback

---

### For Employees

#### 1. Apply for Employment

1. Visit your company's subdomain: `http://yourcompany.localhost:8000`
2. Click **"Sign Up"**
3. Select role: **"Employee"**
4. Choose your department
5. Submit application

⏳ Wait for HR approval email

#### 2. Access Employee Dashboard

After approval, visit: `http://yourcompany.localhost:8000/users/employee/home/`

**Dashboard Features**:
- View leave balance
- Check attendance percentage
- See current month's attendance
- View attendance history

#### 3. Request Attendance Correction

1. Click **"Request Correction"**
2. Select date for correction
3. Choose correct status
4. Provide detailed reason
5. Submit request

⏳ Wait for HR review

#### 4. View Attendance History

- See all attendance records for current month
- Color-coded status indicators:
  - 🟢 Green: Present
  - 🔴 Red: Absent
  - 🟡 Yellow: Leave

---

## 📁 Project Structure
```
enterprisehub/
│
├── 📁 src/                          # Main Django project
│   ├── 📁 accounts/                 # User management & authentication
│   │   ├── 📁 views/
│   │   │   ├── views.py            # Login, Signup, Logout
│   │   │   ├── home_views.py       # Employee & HR dashboards
│   │   │   ├── tenant_views.py     # Tenant owner dashboard & approvals
│   │   │   ├── emp_views_utils.py  # Employee utilities
│   │   │   └── hr_views_utils.py   # HR utilities & approvals
│   │   ├── models.py               # Account, EmployeeProfile, HRProfile
│   │   ├── middleware.py           # Tenant detection middleware
│   │   └── urls.py                 # Account-related routes
│   │
│   ├── 📁 approvals/                # Approval workflow management
│   │   ├── models.py               # HRApproval, EmployeeApproval
│   │   ├── signals.py              # Auto-delete rejected applications
│   │   └── apps.py                 # App configuration
│   │
│   ├── 📁 tenants/                  # Multi-tenancy management
│   │   ├── models.py               # Tenants model
│   │   ├── utils.py                # Schema generation utilities
│   │   ├── tasks.py                # Celery tasks for migrations
│   │   └── validators.py           # Subdomain validation
│   │
│   ├── 📁 attendance/               # Attendance tracking
│   │   ├── models.py               # Attendance, AttendanceRequest
│   │   └── admin.py                # Admin interface
│   │
│   ├── 📁 helpers/                  # Utility modules
│   │   └── 📁 db/
│   │       ├── schemas.py          # Schema switching utilities
│   │       └── validators.py       # Custom validators
│   │
│   ├── 📁 templates/                # HTML templates
│   │   ├── 📁 accounts/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   ├── signup_success.html
│   │   │   ├── tenant_home.html
│   │   │   ├── hr_home.html
│   │   │   ├── employee_home.html
│   │   │   ├── hr_approval_list.html
│   │   │   ├── hr_approval_detail.html
│   │   │   ├── hr_employee_approval_list.html
│   │   │   ├── hr_employee_approval_detail.html
│   │   │   ├── department_detail.html
│   │   │   └── request_attendance.html
│   │   └── 📁 tenants/
│   │       └── landing_page.html
│   │
│   ├── 📁 static/                   # Static files (CSS, JS, images)
│   ├── 📁 media/                    # User-uploaded files
│   │
│   ├── manage.py                   # Django management script
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # Main URL configuration
│   └── wsgi.py                     # WSGI application
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 .gitignore                    # Git ignore rules
└── 📄 README.md                     # This file

🧪 Testing
Run All Tests
bashpython manage.py test
Run Specific App Tests
bashpython manage.py test accounts
python manage.py test approvals
python manage.py test attendance
Coverage Report
bashpip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report

🌐 Deployment
Production Checklist

 Set DEBUG=False in settings
 Configure ALLOWED_HOSTS with your domain
 Use strong SECRET_KEY
 Setup PostgreSQL in production
 Configure Redis for caching
 Setup Celery with supervisor/systemd
 Configure SMTP for production emails
 Setup SSL/TLS certificates
 Configure static files with WhiteNoise or CDN
 Setup monitoring (Sentry, New Relic)
 Configure backup strategy
 Setup logging

Deploy to VPS (Ubuntu)
bash# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx redis-server

# Setup PostgreSQL
sudo -u postgres psql
CREATE DATABASE enterprisehub_prod;
CREATE USER enterprisehub_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE enterprisehub_prod TO enterprisehub_user;
\q

# Clone and setup project
git clone https://github.com/yourusername/enterprisehub.git
cd enterprisehub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings

# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Setup Gunicorn
pip install gunicorn
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000

# Setup Nginx (create /etc/nginx/sites-available/enterprisehub)
server {
    listen 80;
    server_name yourdomain.com *.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/enterprisehub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d *.yourdomain.com

🤝 Contributing
We welcome contributions! Please follow these steps:
1. Fork the Repository
bashgit clone https://github.com/yourusername/enterprisehub.git
2. Create a Feature Branch
bashgit checkout -b feature/amazing-feature
3. Make Your Changes

Follow PEP 8 style guide
Write meaningful commit messages
Add tests for new features
Update documentation

4. Commit Your Changes
bashgit commit -m "Add: Amazing new feature"
5. Push to Branch
bashgit push origin feature/amazing-feature
6. Open a Pull Request

Describe your changes clearly
Reference any related issues
Wait for code review

Code Style Guidelines
python# Use meaningful variable names
employee_count = Employee.objects.count()  # Good
ec = Employee.objects.count()  # Bad

# Add docstrings
def create_tenant_schema(tenant_id):
    """
    Create a new database schema for the given tenant.
    
    Args:
        tenant_id (UUID): The unique identifier for the tenant
        
    Returns:
        str: The generated schema name
    """
    pass

# Use type hints
def get_attendance_percentage(employee: Employee) -> float:
    pass
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2025 EnterpriseHub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

💬 Support
Documentation

📚 Full Documentation
🎥 Video Tutorials
📖 API Reference

Community

💬 Discord Server
🐦 Twitter
📧 Email Support

Issues & Bugs
Found a bug? Have a feature request?

Check existing issues
If not found, create a new issue

Issue Template:
markdown**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Browser: [e.g. Chrome 120]
- Python version: [e.g. 3.11]
- Django version: [e.g. 5.0]

🙏 Acknowledgments

Django Team - For the amazing web framework
PostgreSQL Team - For powerful schema support
Tailwind CSS - For beautiful, utility-first CSS
Contributors - Thank you to all who have contributed!
Community - For feedback and support


📊 Project Statistics
<div align="center">
Show Image
Show Image
Show Image
Show Image
Lines of Code: ~15,000+ | Files: 50+ | Contributors: Growing
</div>

🗺️ Roadmap
Version 1.1 (Q2 2025)

 Leave Management System
 Employee Performance Reviews
 Document Management
 Mobile Apps (iOS & Android)

Version 1.2 (Q3 2025)

 Payroll Integration
 Advanced Analytics Dashboard
 Multi-language Support
 Dark Mode

Version 2.0 (Q4 2025)

 AI-Powered HR Assistant
 Video Interview Integration
 Learning Management System
 Advanced Reporting


💡 Tips & Best Practices
Security
python# Always validate user input
from django.core.validators import validate_email

# Use Django's built-in protections
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Never commit .env files
# Add to .gitignore
.env
*.pyc
__pycache__/
Performance
python# Use select_related and prefetch_related
employees = Employee.objects.select_related('account', 'department')

# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['subdomain']),
        models.Index(fields=['email']),
    ]

# Use caching
from django.core.cache import cache
employees = cache.get('employees_list')
if not employees:
    employees = Employee.objects.all()
    cache.set('employees_list', employees, 3600)

📞 Contact
Project Maintainer: Your Name

📧 Email: your.email@example.com
🐦 Twitter: @yourhandle
💼 LinkedIn: Your Profile
🌐 Website: yourwebsite.com


<div align="center">
⭐ If you find this project helpful, please give it a star! ⭐
Made with ❤️ by developers, for developers
Back to Top
</div>

Alhamdulillah! JazakAllahu Khairan (May Allah reward you with goodness) for using EnterpriseHub! 🚀
