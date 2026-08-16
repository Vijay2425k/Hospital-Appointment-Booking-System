# Hospital Appointment Booking System

**A full-stack Django app for booking, managing, and tracking hospital appointments — patients browse doctors and book slots, doctors manage their schedule, with server-side double-booking prevention.**

![stack](https://img.shields.io/badge/stack-Django%20%7C%20Python-0f766e)
![db](https://img.shields.io/badge/database-MySQL%20%2F%20SQLite-2563eb)
![tests](https://img.shields.io/badge/tests-18%20passing-16a34a)
![license](https://img.shields.io/badge/license-MIT-6b7688)

---

## Screenshots

All four of these are real screenshots from an actual running instance of this app — registered a patient, booked a real appointment, and captured both sides of the flow.

**Find a Doctor — homepage with specialization filter**

![Doctor list](docs/screenshots/doctor-list.png)

**Booking form**

![Book appointment](docs/screenshots/book-appointment.png)

**Patient dashboard — after booking**

![Patient dashboard](docs/screenshots/patient-dashboard.png)

**Doctor dashboard — the same booking, seen from the doctor's side**

![Doctor dashboard](docs/screenshots/doctor-dashboard.png)

## Why this exists

Appointment booking is a classic CRUD app on the surface, but the part that
actually matters — preventing two patients from booking the same doctor at
the same time — is easy to get wrong with just client-side validation. This
project enforces it at two levels: a Django model `clean()` check for a
clean user-facing error message, and a database-level `UniqueConstraint` as
a hard backstop, so a race condition between two simultaneous requests still
can't create a double-booking.

## Features

- **Role-based accounts** — patients and doctors share one `User` model
  with a `role` field; each gets a different dashboard and permissions.
- **Double-booking prevention** — enforced at both the application and
  database level (see Design decisions below).
- **Doctor search/filter** by specialization.
- **Patient flow** — browse doctors → book a slot → view/cancel from a
  personal dashboard.
- **Doctor flow** — see who's booked, mark appointments completed, cancel.
- **Django admin** wired up for both `Doctor` and `Appointment` models for
  hospital-staff-style management.
- **MySQL-ready** — SQLite by default for zero-setup local dev, switches to
  MySQL automatically in production via `DATABASE_URL`.

## Tech stack

- **Backend:** Python, Django 5+
- **Database:** SQLite (dev/test) → MySQL (production), via `dj-database-url` + `PyMySQL` (pure-Python driver, no system MySQL libraries needed to install)
- **Static files:** WhiteNoise (serves compressed static assets without a separate static file host)
- **Deployment:** Gunicorn-ready for Render/Railway
- **CI:** GitHub Actions running the full test suite on every push

## Project structure

```
hospital-appointment-booking-system/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                    # Project settings, URLs, WSGI
│   └── settings.py            # Env-driven DB config (SQLite → MySQL)
├── accounts/                  # Custom User model, registration, login
│   ├── models.py              # User with role (PATIENT/DOCTOR/ADMIN)
│   ├── forms.py
│   ├── views.py
│   └── tests.py               # 6 tests: registration, login, auth
├── appointments/               # Core booking logic
│   ├── models.py              # Doctor, Appointment (+ double-booking guard)
│   ├── forms.py                # Booking form with slot-clash validation
│   ├── views.py                # doctor_list, book, dashboard, cancel
│   ├── management/commands/
│   │   └── seed_demo_data.py  # Creates demo doctors for local testing
│   └── tests.py               # 12 tests: booking, cancellation, permissions
├── templates/                  # Server-rendered HTML (base + per-view)
├── static/css/style.css        # Custom healthcare-themed styling
└── .github/workflows/ci.yml
```

## Design decisions

- **Double-booking prevention, twice over** — `Appointment.clean()` checks
  for an existing PENDING/CONFIRMED booking on the same doctor/date/slot and
  raises a clean `ValidationError`. A `UniqueConstraint` at the database
  level backs this up, so even a race condition between two simultaneous
  requests can't slip through — the second request gets an `IntegrityError`
  that the view catches and turns into a normal form error, not a 500.
- **One `User` model, role-based, not two separate tables** — patients and
  doctors are both `User` rows with a `role` field; `Doctor` is a thin
  profile extension (specialization, fee, bio) via `OneToOneField`. Simpler
  auth, one login flow, no duplicated user logic.
- **Environment-driven database** — `DATABASE_URL` unset → SQLite (zero
  setup for `manage.py test` and local dev). Set → MySQL in production.
  Same codebase, no environment-specific branches in the code itself.
- **PyMySQL over mysqlclient** — pure-Python MySQL driver means `pip
  install -r requirements.txt` doesn't need system-level MySQL client
  libraries to succeed, which is one less thing to debug on a fresh machine
  or CI runner.

## Setup (local)

Requires Python 3.10+.

```bash
git clone https://github.com/Vijay2425k/hospital-appointment-booking-system.git
cd hospital-appointment-booking-system

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py seed_demo_data   # creates 4 demo doctors
python manage.py createsuperuser  # optional, for /admin/

python manage.py runserver
```

Visit `http://localhost:8000`.

## Running tests

```bash
python manage.py test
```

18 tests covering registration, login/auth, appointment booking, the
double-booking guard specifically, cancellation permissions (a patient can't
cancel someone else's appointment), and doctor-list filtering.

## Deploying live with MySQL (Render)

1. Push this repo to GitHub.
2. Create a MySQL database (Render, PlanetScale, or any MySQL host) and copy
   its connection URL.
3. On [render.com](https://render.com), create a **New Web Service** →
   connect your repo.
4. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Start command: `gunicorn config.wsgi`
6. Environment variables:
   - `SECRET_KEY` — any long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — your Render domain
   - `DATABASE_URL` — `mysql://user:password@host:3306/dbname`
7. Deploy, then run migrations once via Render's shell:
   `python manage.py migrate && python manage.py seed_demo_data`

## Roadmap

- [ ] Email confirmation when a doctor confirms/cancels an appointment
- [ ] Doctor-defined availability windows instead of a fixed slot list
- [ ] Patient appointment history export (PDF)
- [ ] REST API layer (Django REST Framework) for a future mobile client

## License

MIT — free to use, modify, and build on.
