# StockSmart — Web-Based Inventory Management System

A smart, simple inventory management system built with Django for tracking products, managing stock levels, and generating reports.

---

## Project Info

- **Course:** Software Quality Engineering (SQE) & Software Construction and Development (SCD)
- **University:** KIET — Karachi Institute of Economics and Technology
- **Stack:** Django, SQLite, Bootstrap 5, Chart.js

---

## Features

- Role-based authentication (Admin & Staff) with approval system
- Product and category management
- Supplier management
- Stock In / Stock Out transactions with full history
- Low stock alerts
- Reports and analytics with graphs
- Product detail page with transaction history

---

## Design Patterns Used

- **Simple Factory** — UserFactory and TransactionFactory
- **Observer / Signals** — Low stock alert trigger via Django signals
- **MVC (MTV)** — Django's built-in Model-Template-View architecture
- **SOLID Principles** — Single responsibility per app, role-based access

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip
- Git

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/QASIM-ARAIN/StockSmart.git
cd StockSmart
```

---

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / Mac:**
```bash
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Run Migrations

```bash
python manage.py migrate
```

---

### Step 5 — Create Superuser

```bash
python manage.py createsuperuser
```

Enter your preferred username, email, and password when prompted.

---

### Step 6 — Set Admin Role

```bash
python manage.py shell
```

Then run these lines one by one:

```python
from apps.accounts.models import User
u = User.objects.get(username='your_username_here')
u.role = 'admin'
u.status = 'active'
u.save()
exit()
```

Replace `your_username_here` with the username you created in Step 5.

---

### Step 7 — Run the Server

```bash
python manage.py runserver
```

Open your browser and go to:

```
http://127.0.0.1:8000
```

---

## Project Structure

```
stocksmart/
├── apps/
│   ├── accounts/        # Auth, user management, roles
│   ├── products/        # Products, categories, suppliers
│   ├── transactions/    # Stock in/out transactions
│   └── reports/         # Reports and analytics
├── config/              # Django settings and URLs
├── templates/           # HTML templates
├── static/              # CSS and static files
├── manage.py
└── requirements.txt
```

---

## User Roles

| Role  | Permissions |
|-------|-------------|
| Admin | Full access — manage products, suppliers, users, view reports |
| Staff | Record stock in/out, view products and transaction history |

---

## Running Tests

```bash
python manage.py test
```

With coverage:

```bash
coverage run manage.py test
coverage report
coverage html
```

---

## Team

| Member | Module |
|--------|--------|
| Member 1 | Authentication & User Management |
| Member 2 | Products & Categories |
| Member 3 | Stock Transactions |
| Member 4 | Reports & Alerts |

---

## License

This project is for academic purposes only.
