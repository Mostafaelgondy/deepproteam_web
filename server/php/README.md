# PHP Backend (lightweight) for Marketplace

Files added under `server/php`:

- `config.php` - configuration constants (DB path, JWT secret)
- `db.php` - SQLite connection helper
- `helpers.php` - response helpers, JWT helpers, auth helpers
- `auth.php` - `/api/auth/login` and `/api/auth/me`
- `admin.php` - `/api/admin/*` endpoints (users, stats, approve/suspend)
- `index.php` - router entrypoint for `/api/*`
- `migrate.php` - creates SQLite schema and seeds test users

Quick start (from project root):

1. Run migration to create the database and seed users:

```bash
php server/php/migrate.php
```

2. Serve the `server/php` folder with PHP's built-in server for local testing:

```bash
php -S localhost:8001 -t server/php
```

3. API examples:

- Login:

  POST http://localhost:8001/api/auth/login
  Body JSON: { "username": "admin", "password": "admin123" }

- Me:

  GET http://localhost:8001/api/auth/me
  Header: Authorization: Bearer <access_token>

- Admin users list:

  GET http://localhost:8001/api/admin/users
  Header: Authorization: Bearer <admin_token>

Notes:
- Replace `JWT_SECRET` in `config.php` with a strong secret for production.
- This is a compact, self-contained backend to support existing frontend pages. Expand as needed.
