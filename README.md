# BlueHub

An interactive directory of ADNU organizations and events, built by **BlueByte**
(Micco Dominic D. Alcantara, Felix Sta. Rosa III, Xildjian Asetre).

Stack: **Vue 3 (Vite)** frontend · **Flask** backend · **Oracle Database**.

```
bluehub/
├── backend/     Flask API + Oracle SQL
└── frontend/    Vue 3 app
```

## Prerequisites

- Python 3.10+ for the backend
- Node.js 18+ for the frontend
- Oracle Database access:
  - local Oracle Database XE, or
  - Oracle Autonomous Database on Oracle Cloud

## 1. Database setup (Oracle)

1. Create (or reuse) a schema/user for the app, for example `bluehub_app`.
2. Grant the schema the required privileges:
   - `CONNECT`
   - `RESOURCE`
   - `CREATE SEQUENCE`
3. Connect as that schema user using SQL*Plus, SQLcl, or SQL Developer.
4. Run the SQL scripts from the repository root:

```sql
@backend/sql/schema.sql
@backend/sql/seed.sql   -- optional sample data
```

The seed script creates three sample accounts, all with password `password123`:

- `admin@adnu.edu.ph` — admin
- `officer@adnu.edu.ph` — officer of `ADNU Computer Science Society`
- `student@adnu.edu.ph` — student

## 2. Backend setup (Flask)

From the repository root:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- macOS / Linux:
  ```bash
  source venv/bin/activate
  ```
- Windows PowerShell:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- Windows Command Prompt:
  ```cmd
  venv\Scripts\activate.bat
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file and update it with your Oracle credentials:

```bash
copy .env.example .env
```

Edit `.env` and set:

- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_HOST`
- `ORACLE_PORT`
- `ORACLE_SERVICE_NAME`
- `JWT_SECRET_KEY`

Start the backend server:

```bash
python run.py
```

The API will be available at `http://localhost:5000`.
Check health at `http://localhost:5000/api/health`.

> The backend uses the `oracledb` driver in thin mode by default, so a separate
> Oracle Instant Client install is not required for a standard XE or ADB setup.

## 3. Frontend setup (Vue)

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api/*` requests to
`http://localhost:5000` by default (see `frontend/vite.config.js`).

## 4. Project structure notes

- **Auth**: JWT-based. `POST /register` and `POST /login` return an `access_token`.
  The token is stored client-side and sent as `Authorization: Bearer <token>`.
- **Roles**: `student`, `officer`, `admin`.
  - `student` is the default role for new signups.
  - `officer` accounts can manage events and the organization profile linked to
    their `organization_id`.
  - `admin` can manage broader application state and user roles.
- **Routes**: see `backend/app/routes/` for implementation of auth, events,
  organizations, dashboard, and related endpoints.

## 5. Implemented features (MVP)

- [x] Register / login / logout (JWT)
- [x] Event CRUD scoped to the officer's organization
- [x] Organization profile view and edit
- [x] Event directory search with category, organization, and date filters
- [x] Organization directory search with category filtering
- [x] Officer dashboard for managing their organization's events
