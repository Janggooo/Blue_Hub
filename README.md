# BlueHub

An interactive directory of ADNU organizations and events, built by **BlueByte**
(Micco Dominic D. Alcantara, Felix Sta. Rosa III, Xildjian Asetre).

Stack: **Vue 3 (Vite)** frontend · **Flask** backend · **Oracle Database**.

```
bluehub/
├── backend/     Flask API + Oracle SQL
└── frontend/    Vue 3 app
```

## 1. Database setup (Oracle)

You need access to an Oracle database — either a local **Oracle Database XE**
install, or a free **Oracle Autonomous Database** instance on Oracle Cloud.

1. Create (or use) a schema/user for the app, e.g. `bluehub_app`, and grant it
   `CONNECT`, `RESOURCE`, and `CREATE SEQUENCE` (or the ADB equivalent).
2. Connect as that user with SQL*Plus, SQLcl, or SQL Developer and run:
   ```sql
   @backend/sql/schema.sql
   @backend/sql/seed.sql   -- optional sample data
   ```
   The seed script creates three accounts, all with password `password123`:
   - `admin@adnu.edu.ph` — admin
   - `officer@adnu.edu.ph` — officer of "ADNU Computer Science Society"
   - `student@adnu.edu.ph` — student

## 2. Backend setup (Flask)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your Oracle credentials (ORACLE_USER, ORACLE_PASSWORD,
# ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME) and a real JWT_SECRET_KEY

python run.py
```

The API runs at `http://localhost:5000`. Check `http://localhost:5000/api/health`.

> Uses the `oracledb` driver in "thin" mode by default — no separate Oracle
> Instant Client install needed for a typical local XE / Autonomous DB setup.

## 3. Frontend setup (Vue)

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and proxies `/api/*` requests to the
Flask server on port 5000 (see `vite.config.js`).

## 4. Project structure notes

- **Auth**: JWT-based. `POST /register` and `POST /login` return an
  `access_token`, stored client-side and sent as `Authorization: Bearer <token>`.
  New signups always get the `student` role — an admin promotes accounts to
  `officer` (and links them to an organization) directly in the database or
  a future admin panel.
- **Roles**: `student`, `officer`, `admin`. Officers can only manage events
  and the organization profile tied to their `organization_id`.
- **CRUD**: see `backend/app/routes/` for events, organizations, auth, and
  the dashboard endpoint.

## 5. What's implemented (MVP)

- [x] Register / login / logout (JWT)
- [x] Event CRUD, scoped to the officer's organization
- [x] Organization profile view + edit
- [x] Event directory: search + category/organization/date filters
- [x] Organization directory: search + category filter
- [x] User dashboard: officers see and manage their org's events

## 6. Next steps to build on this

- Admin screens to create organizations and promote users to `officer`
- Image upload (currently just an image URL field)
- Pagination for large event/org lists
- Categories management UI (currently seeded directly in the DB)
