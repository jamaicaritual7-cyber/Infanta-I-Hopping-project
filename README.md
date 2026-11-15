# Infanta, I Hopping

Boat Rental and Reservation Management System for Infanta, Quezon.

## Technology

- Python Flask and Flask Blueprints
- SQLAlchemy with MySQL through XAMPP/phpMyAdmin
- Bootstrap, HTML, CSS, and JavaScript
- Flask-Login and Flask-WTF/CSRF protection

## Run the project

From the project folder, activate the virtual environment and install the requirements:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

For Flask's development server, use the virtual-environment interpreter explicitly:

```powershell
.\\.venv\\Scripts\\python.exe -m flask --app app run --debug
```

Open `http://127.0.0.1:5000` in a browser.

## Database setup

Run the main [database/schema.sql](database/schema.sql) in phpMyAdmin first. Then import the seed files when their tables are ready:

- [database/seed_destinations.sql](database/seed_destinations.sql)
- [database/seed_packages.sql](database/seed_packages.sql)
- [database/seed_boats.sql](database/seed_boats.sql)
- [database/add_bookings.sql](database/add_bookings.sql)

The database files are SQL files for phpMyAdmin. They are not Python commands and should not be pasted into the PowerShell terminal.

## Main pages

- `/` — public homepage
- `/destinations/` — destinations grouped by area
- `/boats/` — available boats
- `/about` — project information
- `/contact` — contact information placeholder
- `/safety` — safety guidance
- `/booking/book` — authenticated customer booking form
- `/customer/dashboard` — authenticated customer dashboard
- `/admin/dashboard` — administrator dashboard
- `/admin/bookings` — administrator booking management
- `/admin/reports` — booking reports

## OOP requirements

The four OOP pillars are documented in [docs/oop_pillars.md](docs/oop_pillars.md). The implementation uses models, service classes, inheritance, abstraction, encapsulation, and polymorphic booking-status objects.

## Important development notes

OTP email delivery requires valid Gmail SMTP settings in the local `.env` file. Keep `.env` private and never commit it. The system is being developed and tested module by module; placeholder and unverified business information is labeled accordingly.

## Demonstration checklist

1. Open the homepage and browse destinations and boats.
2. Register a customer account and complete the existing email OTP verification.
3. Log in, submit a future booking, and open its booking summary.
4. Open My bookings to review status and cancel a pending request if needed.
5. Log in as an administrator, filter bookings by status, and review a booking detail page.
6. Confirm, complete, or cancel the reservation, then return to the customer account to verify the status explanation.
7. Use `/admin/boats` to mark a boat available, under maintenance, or unavailable.

The isolated workflow suite can be run without sending OTP email or changing MySQL data:

```powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v
```
