# Hospital Appointment Booking System

[![Live Demo](https://img.shields.io/badge/Live-Demo-0f766e?style=for-the-badge)](https://hospital-appointment-booking-system-h0cy.onrender.com/)
![stack](https://img.shields.io/badge/stack-Django%206.1%20%7C%20Python-0f766e)
![db](https://img.shields.io/badge/database-MySQL%20%2F%20SQLite-2563eb)
![tests](https://img.shields.io/badge/tests-18%20passing-16a34a)
![license](https://img.shields.io/badge/license-MIT-6b7688)

**Live Application:** 👉 **[hospital-appointment-booking-system-h0cy.onrender.com](https://hospital-appointment-booking-system-h0cy.onrender.com/)**
**Source Code:** 👉 **[github.com/Vijay2425k/Hospital-Appointment-Booking-System](https://github.com/Vijay2425k/Hospital-Appointment-Booking-System)**

A full-stack Django application for booking, managing, and tracking hospital
appointments. Patients browse doctors and book available slots; doctors
manage their own appointment schedule.

The system is built around a real backend engineering problem, not just
CRUD: **preventing two patients from booking the same doctor, date, and time
slot — including under concurrent requests.**

---

## 🚀 Live Demo

👉 **https://hospital-appointment-booking-system-h0cy.onrender.com/**

### Main workflows

- 👤 Patient registration and authentication
- 🩺 Browse doctors, filter by specialization
- 📅 Book an appointment
- 🔒 Server-side double-booking prevention
- 📋 Patient appointment dashboard
- 👨‍⚕️ Doctor appointment management
- ❌ Appointment cancellation
- ✅ Appointment completion
- 🛠️ Django admin management

> The live application is deployed on Render and uses MySQL for production
> data persistence.

---

## 📸 Screenshots

All screenshots below are from an actual running instance of the
application, covering the complete patient-to-doctor booking workflow.

### Find a Doctor
Patients can browse available doctors and filter by specialization.

![Doctor list](docs/screenshots/doctor-list.png)

### Booking Form
Patients select a doctor, date, and time slot to book an appointment.

![Book appointment](docs/screenshots/book-appointment.png)

### Patient Dashboard
Patients view and manage their booked appointments.

![Patient dashboard](docs/screenshots/patient-dashboard.png)

### Doctor Dashboard
Doctors see appointments booked by patients and manage their schedule.

![Doctor dashboard](docs/screenshots/doctor-dashboard.png)

---

## 💡 Why This Project Exists

Hospital appointment booking looks like a straightforward CRUD app, but the
backend problem that actually matters is **preventing double bookings**.

> Two patients simultaneously try to book the same doctor for
> **10:00 AM on the same date.**

Client-side validation alone can't reliably prevent this — both requests can
pass validation before either booking is actually saved. This project
protects the booking operation at two levels:

1. **Application-level validation**
   `Appointment.clean()` checks for an existing booking on the same
   doctor/date/slot and raises a clean `ValidationError`.

2. **Database-level protection**
   A `UniqueConstraint` acts as the final safety net, preventing duplicate
   bookings even when two requests race each other. The resulting
   `IntegrityError` is caught by the view and turned into a friendly form
   error instead of a server crash.

This makes the booking logic meaningfully more reliable than a simple CRUD
implementation.

---

## ✨ Features

### Authentication & Roles
- Custom Django `User` model with a `role` field (Patient / Doctor / Admin)
- Role-based dashboards and permissions
- Registration and login

### Patient Features
- Browse and filter doctors by specialization
- Book appointments
- View personal appointment history
- Cancel appointments
- Protected from booking a slot that's already taken

### Doctor Features
- Doctor-specific dashboard
- View booked appointments and patient details
- Mark appointments completed
- Cancel appointments

### Admin Features
- Full Django admin interface for doctors, appointments, and users

### Booking Reliability
- Application-level slot validation
- Database-level `UniqueConstraint`
- Race-condition protection
- Graceful handling of database integrity errors (no raw 500 pages)

### Production Features
- Environment-based configuration (`.env` / `DATABASE_URL`)
- MySQL in production, SQLite for local dev — same codebase, no branching
- WhiteNoise for static file serving
- Gunicorn production server
- Deployed live on Render
- GitHub Actions CI running the full test suite on every push

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 |
| Web Framework | Django 6.1 |
| Database — Development | SQLite |
| Database — Production | MySQL |
| DB Configuration | `dj-database-url` |
| MySQL Driver | PyMySQL (pure Python, no system libs required) |
| Authentication | Django's built-in auth, extended with a custom `User` model |
| Static Files | WhiteNoise |
| Production Server | Gunicorn |
| Deployment | Render |
| CI | GitHub Actions |
| Testing | Django's built-in test framework |

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │       Browser        │
                    │  Patient / Doctor    │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │        Django        |
                    │   Views / Forms      │
                    │   Authentication     │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Booking Business    │
                    │       Logic          │
                    │                      │
                    │  clean() validation  │
                    │  Permission checks   │
                    └──────────┬───────────
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Database       │
                    │                      │
                    │  UniqueConstraint    │
                    │  Double-booking      │
                    └──────────────────────┘
```

---

## 📁 Project Structure

```text
hospital-appointment-booking-system/
│
├── manage.py
├── requirements.txt
├── .env.example
│
├── config/
│   ├── __init__.py          # PyMySQL driver registration
│   ├── settings.py          # Env-driven DB config (SQLite → MySQL)
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py            # Custom User model (role field)
│   ├── forms.py
│   ├── views.py
│   └── tests.py             # 6 tests: registration, login, auth
│
├── appointments/
│   ├── models.py            # Doctor, Appointment (+ double-booking guard)
│   ├── forms.py             # Booking form with slot-clash validation
│   ├── views.py             # doctor_list, book, dashboard, cancel
│   ├── tests.py             # 12 tests: booking, cancellation, permissions
│   └── management/commands/
│       └── seed_demo_data.py
│
├── templates/
│   ├── base.html
│   └── ...
│
├── static/
│   └── css/style.css
│
├── docs/
│   └── screenshots/
│       ├── doctor-list.png
│       ├── book-appointment.png
│       ├── patient-dashboard.png
│       └── doctor-dashboard.png
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 🧠 Key Design Decisions

### 1. Double-booking prevention, at two layers

**Application-level:** `Appointment.clean()` checks whether the selected
doctor already has a pending/confirmed appointment for the same date and
time slot, and raises a `ValidationError` with a clear message.

**Database-level:** A `UniqueConstraint` is the real backstop. Application
validation alone isn't enough under concurrent requests:

```text
Patient A ────────┐
                   ├──> Both check slot ──> Database
Patient B ────────┘
```

Without a DB constraint, both requests could pass validation before either
save completes. With the constraint in place:

```text
Patient A ────────> Booking created ✅

Patient B ────────> IntegrityError
                     │
                     ▼
              User-friendly booking error
```

This gives a database-backed guarantee against duplicate appointments, not
just a best-effort check.

### 2. One `User` model, role-based

Rather than separate patient/doctor auth systems, the app uses one custom
`User` model with a `role` field:

```text
User
 ├── PATIENT
 ├── DOCTOR
 └── ADMIN
```

`Doctor` is a thin profile extension (specialization, fee, bio) connected
via `OneToOneField`. One login flow, no duplicated user logic.

### 3. Environment-driven database configuration

```text
Local Development          Production
       │                        │
       ▼                        ▼
    SQLite                DATABASE_URL set
 (DATABASE_URL unset)             │
                                  ▼
                                MySQL
```

Same codebase runs locally and in production with zero code branching —
only an environment variable changes.

### 4. PyMySQL over mysqlclient

The project uses **PyMySQL**, a pure-Python MySQL driver, registered in
`config/__init__.py` via `pymysql.install_as_MySQLdb()`. This means
`pip install -r requirements.txt` works on a fresh machine or CI runner
without needing system-level MySQL client libraries — one less thing to
debug during setup.

---

## 🧪 Testing

**18 automated tests**, all passing, covering:

- User registration and authentication
- Role-based access control
- Doctor listing and filtering
- Appointment creation
- **Double-booking prevention specifically**
- Appointment cancellation and cancellation permissions (a patient can't
  cancel someone else's appointment)
- Doctor-side appointment management

Run the suite:

```bash
python manage.py test
```

Expected result:

```text
Ran 18 tests
OK
```

---

## ⚙️ Local Setup

### Requirements
- Python 3.10+
- pip
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Vijay2425k/Hospital-Appointment-Booking-System.git
cd Hospital-Appointment-Booking-System
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Windows PowerShell:
```powershell
Copy-Item .env.example .env
```
Leave `DATABASE_URL` blank to use SQLite automatically for local dev.

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Seed demo data
```bash
python manage.py seed_demo_data
```
Creates 4 demo doctors across different specializations for local testing.

### 7. Create an admin account (optional)
```bash
python manage.py createsuperuser
```

### 8. Start the development server
```bash
python manage.py runserver
```
Open **http://localhost:8000/**

---

## 🔐 Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=mysql://username:password@host:3306/database
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Allowed production hostnames |
| `DATABASE_URL` | MySQL connection URL — omit to fall back to SQLite |

**Never commit real production credentials to GitHub.**

---

## 🚀 Production Deployment (Render)

**Live URL:** [hospital-appointment-booking-system-h0cy.onrender.com](https://hospital-appointment-booking-system-h0cy.onrender.com/)

**Build Command**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command**
```bash
gunicorn config.wsgi
```

**Required environment variables**
```text
SECRET_KEY=<long-random-secret>
DEBUG=False
ALLOWED_HOSTS=hospital-appointment-booking-system-h0cy.onrender.com
DATABASE_URL=mysql://username:password@host:3306/database
```

After deployment, run once via Render's shell:
```bash
python manage.py migrate
python manage.py seed_demo_data
```

---

## 🔄 Production Request Flow

```text
User → Render → Gunicorn → Django
                              │
                              ├── Authentication
                              ├── Views
                              ├── Forms
                              └── Booking Logic
                                    │
                                    ▼
                                  MySQL
```

---

## 🔒 Security Considerations

- Secrets loaded from environment variables, never hardcoded
- `DEBUG=False` in production
- Django's built-in authentication and authorization on all protected views
- CSRF protection via Django middleware
- Appointment ownership verified before cancellation (a patient cannot
  cancel another patient's booking)
- Database constraints protect appointment uniqueness at the data layer

For a real production healthcare system, additional requirements — data
encryption at rest, audit logging, stronger access controls, and regulatory
compliance (e.g. HIPAA-equivalent standards) — would be necessary beyond
the scope of this portfolio project.

---

## 🗺️ Roadmap

- [ ] Email confirmation when a doctor confirms/cancels an appointment
- [ ] Doctor-defined availability windows instead of a fixed slot list
- [ ] Patient appointment history export as PDF
- [ ] REST API layer with Django REST Framework
- [ ] API documentation
- [ ] Appointment reminders
- [ ] Pagination for doctor and appointment listings
- [ ] Production monitoring and centralized logging
- [ ] Dockerized deployment

---

## 🤝 Contributing

Contributions and suggestions are welcome.

```bash
git clone https://github.com/Vijay2425k/Hospital-Appointment-Booking-System.git
git checkout -b feature/your-feature
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```
Then open a Pull Request.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 👤 Author

**Kongari Vijay Kumar**
QA Automation Engineer / SDET

- GitHub: [github.com/Vijay2425k](https://github.com/Vijay2425k)
- LinkedIn: [linkedin.com/in/kongari-vijay-kumar-270111298](https://linkedin.com/in/kongari-vijay-kumar-270111298)
- Live Demo: [hospital-appointment-booking-system-h0cy.onrender.com](https://hospital-appointment-booking-system-h0cy.onrender.com/)
- Source Code: [github.com/Vijay2425k/Hospital-Appointment-Booking-System](https://github.com/Vijay2425k/Hospital-Appointment-Booking-System)
