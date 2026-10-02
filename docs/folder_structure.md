# Folder Structure

```
online-shopping-cart-system/
├── README.md
├── .gitignore
├── .env.example
│
├── backend/                       # Python (Flask) backend
│   ├── run.py                     # App entry point
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py            # App factory, blueprint registration
│   │   ├── config.py
│   │   ├── extensions.py          # db, login_manager instances
│   │   ├── static/
│   │   ├── templates/
│   │   ├── utils/
│   │   └── modules/
│   │       ├── user/               # User Module: sign up, login, profile
│   │       │   ├── models.py
│   │       │   ├── routes.py
│   │       │   └── services.py
│   │       ├── product/            # Product Module: view/search/details
│   │       │   ├── models.py
│   │       │   ├── routes.py
│   │       │   └── services.py
│   │       ├── cart/                # Cart Module: add/remove/update qty
│   │       │   ├── models.py
│   │       │   ├── routes.py
│   │       │   └── services.py
│   │       ├── order/               # Order Module: place order, status
│   │       │   ├── models.py
│   │       │   ├── routes.py
│   │       │   └── services.py
│   │       └── admin/               # Admin Module: manage products/orders/reports
│   │           ├── models.py
│   │           ├── routes.py
│   │           └── services.py
│   ├── tests/                      # One test file per module
│   └── migrations/                 # DB migration scripts (Flask-Migrate/Alembic)
│
├── frontend/                       # HTML / CSS / JS frontend
│   ├── css/
│   │   ├── style.css
│   │   └── admin.css
│   ├── js/
│   │   ├── main.js
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── product.js
│   │   ├── cart.js
│   │   ├── order.js
│   │   └── admin.js
│   ├── images/
│   └── pages/
│       ├── index.html              # Product catalog / home
│       ├── login.html
│       ├── register.html
│       ├── cart.html
│       ├── checkout.html
│       ├── order-history.html
│       └── admin/
│           └── dashboard.html      # Admin panel
│
├── database/
│   ├── schema.sql                  # Table definitions
│   └── seed.sql                    # Sample data
│
└── docs/
    └── folder_structure.md         # This file
```

## Module → Feature Mapping

| Module | Key Features |
|---|---|
| User Module | Sign up, Login, Profile Management |
| Product Module | View Products, Search Products, Product Details |
| Cart Module | Add to Cart, Remove from Cart, Update Quantity |
| Order Module | Place Order, View Order Status |
| Admin Module | Add/Edit/Delete Products, Manage Orders, View Sales Reports |

## Notes
- Backend is scaffolded for **Flask**; swapping to **FastAPI** or **PHP** would replace the `app/` package but keep the same module boundaries.
- Swap MySQL ↔ PostgreSQL by adjusting `DATABASE_URL` in `.env` and minor type tweaks in `schema.sql` (e.g. `ENUM`, `AUTO_INCREMENT` vs `SERIAL`).
