# Restaurant Management System (Django)

A complete Django project for managing a restaurant: menu, tables, orders, and
reservations, with a staff login and Django admin for back-office work.

## Features

- **Menu** — categories + items, browsable publicly, editable by staff (with image upload)
- **Tables** — track table number, capacity, and status (available/occupied/reserved)
- **Orders** — create an order for a table, add/remove menu items, track status
  (pending → preparing → served → paid), auto-computed totals
- **Reservations** — book a table for a customer at a date/time
- **Staff accounts** — `StaffProfile` extends Django's built-in `User` with a role
  (manager/waiter/chef/cashier); login required for all management pages
- **Dashboard** — quick stats: occupied tables, active orders, today's reservations,
  today's revenue
- **Django Admin** — full CRUD for every model at `/admin/`

## Project structure

```
restaurant_management/
├── manage.py
├── requirements.txt
├── restaurant_management/       # project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── restaurant/                  # the app — all business logic
│   ├── models.py                # Category, MenuItem, Table, Customer,
│   │                             # StaffProfile, Reservation, Order, OrderItem
│   ├── admin.py                 # admin.site registrations
│   ├── forms.py                 # ModelForms for every model
│   ├── views.py                 # dashboard, menu, tables, orders, reservations
│   ├── urls.py                  # app URL routes
│   └── management/commands/seed_data.py   # `python manage.py seed_data`
├── templates/                   # Bootstrap-styled HTML templates
│   ├── base.html
│   ├── registration/login.html
│   └── restaurant/*.html
└── static/css/style.css
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run migrations** (creates the SQLite database `db.sqlite3`)

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Load sample data** (optional but recommended — creates a superuser,
   sample menu items, tables, and a customer)

   ```bash
   python manage.py seed_data
   ```

   This creates login `admin / admin123`. **Change this password before any
   real deployment.** Alternatively, skip this and run
   `python manage.py createsuperuser` to make your own account.

4. **Run the development server**

   ```bash
   python manage.py runserver
   ```

5. Visit:
   - `http://127.0.0.1:8000/` — staff dashboard (login required)
   - `http://127.0.0.1:8000/menu/` — public menu page
   - `http://127.0.0.1:8000/admin/` — Django admin
   - `http://127.0.0.1:8000/accounts/login/` — staff login

## How the core logic works

- **Order totals** are never stored directly — `Order.total` is a `@property`
  that sums `OrderItem.subtotal` (`price * quantity`) on the fly, so it's
  always accurate even after items are added/removed.
- **Price locking**: `OrderItem.save()` copies the menu item's current price
  into `OrderItem.price` the first time it's saved, so later menu price
  changes don't retroactively change historical order totals.
- **Table status automation**: creating an order marks its table `occupied`;
  marking an order `paid` or `cancelled` frees the table back to `available`
  (see `order_create` and `order_update_status` in `views.py`).
- **Access control**: every staff-only view uses `@login_required`; the menu
  page itself is public (customers could browse it without an account).

## Extending this project

Ideas for next steps:
- Add `django-crispy-forms` for nicer form rendering
- Add a REST API layer with Django REST Framework for a mobile app
- Add role-based permissions (e.g. only managers can delete menu items)
- Add a kitchen-display view that auto-refreshes orders with status `preparing`
- Deploy with PostgreSQL instead of SQLite (`DATABASES` in `settings.py`)
- Move `SECRET_KEY` and `DEBUG` into environment variables before deploying
