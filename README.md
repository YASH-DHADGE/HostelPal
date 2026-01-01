# HostelPal - Complete Hostel Management System

> **Your Complete Solution for Modern Hostel Management** - A comprehensive web-based platform for streamlining hostel operations, student services, and administrative tasks.

## 🌟 Overview

HostelPal is a Django-based hostel management system designed to digitize and simplify hostel operations. The platform serves both students and wardens, providing:

- **Attendance Tracking** - Digital check-in/check-out system
- **Leave Management** - Application, approval, and tracking system
- **Complaint Ticketing** - Structured issue resolution
- **Group Chat** - Real-time communication between students and wardens
- **Fee Payment** - Online payment processing
- **Meal Management** - Food preference tracking to reduce wastage
- **Notice Board** - Important announcements and updates
- **Feedback System** - Continuous improvement through student input

## 📁 Project Structure

```
HostelPal/
├── Home/                      # Main Django app
│   ├── management/            # Custom management commands
│   ├── migrations/            # Database migrations
│   ├── templatetags/          # Custom template filters
│   ├── admin.py               # Admin interface configuration
│   ├── apps.py                # App configuration
│   ├── forms.py               # Django forms
│   ├── models.py              # Database models
│   ├── urls.py                # URL routing
│   └── views.py               # View functions
├── HostelPal/                 # Django project settings
│   ├── settings.py            # Project configuration
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py & asgi.py      # Server gateways
├── static/                    # Static files (CSS, JS, images)
├── templates/                 # HTML templates
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Features

### For Students

#### 1. Dashboard & Profile
- Personal information management
- Room number and contact details
- Emergency contact information
- Parent/guardian details

#### 2. Attendance System
- View daily attendance records
- Check-in and check-out timestamps
- Attendance history and statistics
- Leave status integration

#### 3. Leave Applications
- Apply for leave with date range and reason
- Track application status (Pending/Approved/Rejected)
- View leave history
- Edit or delete pending applications
- Automatic attendance marking for approved leaves

#### 4. Complaint/Ticket System
- Submit complaints with categories
- Track complaint resolution status
- Receive replies from wardens
- View complaint history

#### 5. Group Chat
- Real-time messaging with wardens and peers
- Message history
- Timestamp tracking

#### 6. Meal Preferences
- Set daily meal preferences (breakfast, lunch, dinner)
- Update preferences for current/future dates
- Helps reduce food wastage by accurate meal planning

#### 7. Fee Payment
- View payment history
- Online fee submission
- Payment receipts

#### 8. Feedback System
- Submit feedback on various categories:
  - Mess/Food quality
  - Facilities
  - Cleanliness
  - Security
  - Staff behavior
- Rate services (1-5 stars)

#### 9. Notice Board
- View important announcements
- Priority notices highlighted
- Date-stamped updates

### For Wardens

#### 1. Admin Dashboard
- Overview of hostel statistics
- Quick access to all management features
- Pending actions summary

#### 2. Attendance Management
- Mark individual student attendance
- Bulk attendance marking
- Generate attendance reports
- View attendance trends
- Export attendance data

#### 3. Leave Application Management
- View all leave applications
- Filter by status (pending/approved/rejected)
- Approve or reject applications with comments
- View leave details and student information

#### 4. Complaint Resolution
- View all student complaints
- Filter by resolution status
- Reply to complaints
- Mark complaints as resolved
- Track resolution time

#### 5. Notice Management
- Create new notices
- Edit existing notices
- Delete outdated notices
- Mark notices as important

#### 6. Meal Management
- View daily meal preferences from all students
- Plan meals based on actual requirements
- Reduce food wastage
- Generate meal statistics

#### 7. Warden Chat
- Communicate with students
- Broadcast announcements
- Individual student messaging

## 🛠️ Technology Stack

- **Backend**: Django 4.x, Python 3.x
- **Database**: SQLite (development) / PostgreSQL/MySQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Django Auth System
- **Forms**: Django Forms with validation

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv/virtualenv)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/YASH-DHADGE/HostelPal.git
cd HostelPal
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser (Warden account)**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
- Student Portal: http://localhost:8000/
- Warden Admin: http://localhost:8000/warden/
- Warden Dashboard: http://localhost:8000/wardens/dashboard/

## 📚 Database Models

### Student
Extends Django User model with additional fields:
- Personal info (name, DOB, gender, email)
- Room number and phone
- Address
- Parent/guardian details
- Emergency contact information
- Registration date

### Complaint
- Student reference
- Complaint type and description
- Resolution status
- Reply from warden
- Timestamps (created, resolved, replied)

### Leave
- Student reference
- Application and approval dates
- Date range (from_date, to_date)
- Number of days
- Reason
- Status (pending/approved/rejected)
- Approver and approval comments

### Attendance
- Student reference
- Date
- Status (present/absent/on leave)
- Check-in and check-out times
- Marked by (warden reference)
- Comments

### MealPreference
- Student reference
- Date
- Meal selections (breakfast, lunch, dinner)
- Unique constraint per student per day

### ChatMessage
- Sender (User reference)
- Message content
- Timestamp
- Sender type (student/warden)

### Notice
- Title and content
- Date posted
- Important flag

### Feedback
- Student reference
- Category (Mess, Facilities, Cleanliness, Security, Staff)
- Rating (1-5 stars)
- Content
- Created timestamp

### Payment
- Student reference
- Amount
- Payment date

## 🔗 URL Endpoints

### Student URLs
- `/` - Home/Dashboard
- `/register/` - Student registration
- `/login/` - Student login
- `/logout/` - Logout
- `/account/` - Student profile
- `/attendance/` - View attendance
- `/leave/` - Leave dashboard
- `/leave/apply/` - Apply for leave
- `/leave-status/` - Check leave status
- `/ticket/` - Complaint/ticket system
- `/submit_complaint/` - Submit new complaint
- `/view_complaint/` - View complaint history
- `/chat/` - Group chat
- `/mess/` - Meal preferences
- `/update_today_meal/` - Update meal selection
- `/notice/` - View notices
- `/feedback/` - Submit feedback
- `/pay_fees/` - Fee payment
- `/password_change/` - Change password

### Warden URLs
- `/warden/` - Admin interface login
- `/wardens/dashboard/` - Warden dashboard
- `/wardens/complaints/` - View all complaints
- `/wardens/complaints/resolve/<id>/` - Resolve complaint
- `/wardens/complaints/reply/<id>/` - Reply to complaint
- `/wardens/leaves/` - View leave applications
- `/wardens/leaves/approve/<id>/` - Approve leave
- `/wardens/leaves/reject/<id>/` - Reject leave
- `/wardens/notices/` - Manage notices
- `/wardens/notices/create/` - Create notice
- `/wardens/notices/edit/<id>/` - Edit notice
- `/wardens/notices/delete/<id>/` - Delete notice
- `/wardens/attendance/` - Attendance management
- `/wardens/mark-attendance/` - Mark attendance
- `/wardens/bulk-mark-attendance/` - Bulk marking
- `/wardens/attendance-report/` - Generate reports
- `/wardens/chat/` - Warden chat interface
- `/wardens/meals/` - Meal management

## 🎯 Key Functions

### Student Views
| Function | Purpose | Auth Required |
|----------|---------|---------------|
| `index` | Dashboard/home page | Yes |
| `register` | New student registration | No |
| `account` | View/edit profile | Yes |
| `attendance` | View attendance records | Yes |
| `leave` | Leave dashboard | Yes |
| `apply_leave` | Submit leave application | Yes |
| `leave_status` | Check application status | Yes |
| `ticket` | View complaint system | Yes |
| `submit_complaint` | File new complaint | Yes |
| `student_chat` | Group chat interface | Yes |
| `mess` | Meal preferences page | Yes |
| `update_today_meal` | Update meal selection | Yes |
| `notice` | View notices | Yes |
| `feedback` | Submit feedback | Yes |
| `pay_fees` | Fee payment interface | Yes |

### Warden Views
| Function | Purpose | Warden Only |
|----------|---------|-------------|
| `warden_dashboard` | Main dashboard | Yes |
| `warden_complaints` | View all complaints | Yes |
| `resolve_complaint` | Mark complaint resolved | Yes |
| `reply_complaint` | Reply to complaint | Yes |
| `warden_leave_applications` | View leave requests | Yes |
| `approve_leave` | Approve leave | Yes |
| `reject_leave` | Reject leave | Yes |
| `manage_notices` | Notice management | Yes |
| `create_notice` | Create new notice | Yes |
| `edit_notice` | Update notice | Yes |
| `delete_notice` | Remove notice | Yes |
| `manage_attendance` | Attendance dashboard | Yes |
| `mark_attendance` | Mark single attendance | Yes |
| `bulk_mark_attendance` | Mark multiple | Yes |
| `attendance_report` | Generate reports | Yes |
| `warden_chat` | Chat with students | Yes |
| `warden_meal_management` | View meal stats | Yes |

## 🔐 Security Features

- **Authentication Required**: All student and warden features protected by login
- **Role-Based Access**: Separate interfaces for students and wardens
- **CSRF Protection**: Django CSRF tokens on all forms
- **Password Security**: Django's built-in password hashing
- **Session Management**: Secure session handling
- **User Authorization**: Permission checks using decorators

## 🧪 Testing

Run tests using Django's test framework:
```bash
python manage.py test Home
```

## 📱 Responsive Design

- Mobile-friendly interface
- Responsive layouts for all devices
- Touch-optimized for tablets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **YASH-DHADGE** - *Project Lead*
- **SOHAM3705** - *Contributor*

## 🙏 Acknowledgments

- Django framework for robust web development
- Python community for excellent libraries
- Contributors and testers

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/YASH-DHADGE/HostelPal/issues)
- Check existing documentation

---

**Made with ❤️ for efficient hostel management**
