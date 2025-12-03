# BusFlow (Python)

**Seamless Bus Booking & Fleet Management Platform**

BusFlow is a Python Flask web application for online bus ticket booking and transportation management. It provides dedicated portals for passengers, drivers, and administrators.

---

## Features

### User Portal
- Search buses by route (source → destination)
- Book seats with visual seat selection
- View booking history
- Cancel tickets

### Driver Portal
- View assigned buses and routes
- Check bus capacity and status

### Admin Portal
- Full fleet management (add, edit buses)
- Create/update routes
- Assign drivers to buses
- Create driver accounts

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Flask 3.0 |
| Database | Supabase (PostgreSQL + Auth) |
| Templates | Jinja2 |
| Styling | Tailwind CSS (CDN) |
| Documentation | Sphinx |

---

## Architecture

BusFlow follows the **MVC (Model-View-Controller)** architecture:

```
busflow_python/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration constants
│   ├── models/               # Data models (M)
│   │   ├── user.py
│   │   ├── bus.py
│   │   └── booking.py
│   ├── views/                # Flask blueprints (V)
│   │   ├── landing.py
│   │   ├── auth.py
│   │   ├── user_portal.py
│   │   ├── driver_portal.py
│   │   └── admin_portal.py
│   ├── controllers/          # Business logic (C)
│   │   ├── auth_controller.py
│   │   ├── bus_controller.py
│   │   ├── booking_controller.py
│   │   └── user_controller.py
│   ├── services/             # External integrations
│   │   └── supabase_service.py
│   └── templates/            # Jinja2 templates
├── docs/                     # Sphinx documentation
├── requirements.txt
├── run.py
└── README.md
```

---

## Naming Conventions

This project follows these Python naming conventions:

| Element | Convention | Example |
|---------|------------|---------|
| Variables | snake_case | `total_cost`, `user_id` |
| Boolean Variables | camelCase (with is/has) | `isActive`, `hasDriver` |
| Constants | UPPERCASE_UNDERSCORES | `SECRET_KEY`, `BUS_STATUS_ACTIVE` |
| Methods | snake_case | `get_all_buses()`, `create_booking()` |
| Classes | PascalCase | `BusController`, `User` |
| Modules | lowercase_underscores | `supabase_service.py` |
| Exceptions | PascalCase + Error suffix | `AuthenticationError` |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Navigate to the project directory:
```bash
cd busflow_python
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python run.py
```

5. Open http://localhost:5000 in your browser

---

## Database Setup

The application uses the existing Supabase database. The schema is defined in `supabase-schema.sql` in the parent directory.

### Test Accounts

Use these credentials to test the application:

- **Admin**: Create via Supabase dashboard with ADMIN role
- **Driver**: Created by admin through the Admin Portal
- **User**: Self-register through the User Portal

---

## Documentation

Generate API documentation using Sphinx:

```bash
cd docs
make html     # Linux/Mac
make.bat html # Windows
```

Documentation will be generated in `docs/_build/html/`.

---

## API Endpoints

### Authentication
- `GET /auth/login/<portal_type>` - Login page
- `POST /auth/login/<portal_type>` - Process login
- `GET /auth/register` - Registration page
- `POST /auth/register` - Process registration
- `GET /auth/logout` - Logout

### User Portal
- `GET /user/dashboard` - User dashboard
- `POST /user/search` - Search buses
- `GET /user/seats/<bus_id>` - Get seat availability
- `POST /user/book` - Create booking
- `GET /user/bookings` - Get user bookings
- `POST /user/cancel/<booking_id>` - Cancel booking

### Driver Portal
- `GET /driver/dashboard` - Driver dashboard
- `GET /driver/buses` - Get assigned buses

### Admin Portal
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/buses` - Get all buses
- `POST /admin/bus/create` - Create bus
- `POST /admin/bus/<bus_id>/update` - Update bus
- `POST /admin/bus/<bus_id>/assign` - Assign driver
- `GET /admin/drivers` - Get all drivers
- `POST /admin/driver/create` - Create driver

---

## License

Built for CSE327 - Software Engineering course.

