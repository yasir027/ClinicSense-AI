# ClinicSense AI

ClinicSense AI is an internal hospital/clinic data intelligence MVP. The current published state covers the **foundation phase** only: authentication, role-based access control, a protected route, an audit log table, and login-event audit writing.

## Current status

What is complete right now:

- Login is working.
- JWT-based authentication is working.
- RBAC is working.
- A protected test route is working.
- The `audit_log` table has been created.
- Successful login events are written into the audit log.

What is **not** built yet:

- Semantic metadata layer
- Heterogeneous connectors
- AI query planning
- Execution layer
- Dashboards and exports
- Voice layer
- Full demo workflow

## Project tree

Below is the intended tree for the current published stage of the project. The descriptions explain what each file or folder is responsible for.

```text
clinicsense-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint; registers routes and health check
│   │   ├── core/
│   │   │   ├── config.py            # App settings and configuration values
│   │   │   ├── security.py          # Password hashing, password verification, JWT token creation
│   │   │   ├── deps.py              # Shared auth dependency to resolve the current user
│   │   │   └── rbac.py              # Shared RBAC permission checks such as require_module()
│   │   ├── db/
│   │   │   ├── session.py           # SQLAlchemy engine/session setup and Base import
│   │   │   ├── models.py            # Core relational models such as users, roles, categories, modules
│   │   │   └── audit_model.py       # Audit log ORM model
│   │   ├── audit/
│   │   │   └── writer.py            # Shared helper for writing audit_log entries
│   │   └── routers/
│   │       ├── schemas.py           # Pydantic request/response models for routes
│   │       ├── auth.py              # Login route and login audit write
│   │       └── protected.py         # Protected Billing test route
│   └── requirements.txt             # Python dependency snapshot for backend setup
├── frontend/                        # Frontend app folder for later phases
├── infra/
│   └── docker-compose.yml           # Local infrastructure services such as PostgreSQL and MongoDB
├── docs/
│   └── foundation_phase_steps.md    # Detailed documentation of the completed foundation phase
└── README.md                        # GitHub setup guide for the current state of the project
```

## What MUA should understand first

The current backend is not the full ClinicSense system yet. Authentication, RBAC and audit Table has been covered till covering the first two steps from the MVP guide.

## Prerequisites

Install these on your machine before trying to run the project locally

- Git
- Python 3.11 or higher
- Node.js 20 or higher
- Docker Desktop
- Docker Compose
- A code editor such as VS Code

## Clone and open the project

```bash
git clone <https://github.com/yasir027/ClinicSense-AI>
cd clinicsense-ai
```

If MUA is unsure which branch, environment values, or current local file state should be used, **ask Yasir first** before changing the setup flow. That is the safest handoff instruction for the current stage.

## Create a Python virtual environment

From the repository root, create your own local environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install Python dependencies

`requirements.txt` already exists
```bash
pip install -r backend/requirements.txt
```

## Docker setup

The project currently uses Docker for local infrastructure, especially PostgreSQL and MongoDB, Creds on what databases and it's respective fields are already written in ```infra/docker-compose.yml``` You Just need to run it and then update the env. Steps are given below...

### Expected Docker Compose values

For now, keep PostgreSQL credentials universal across the team using the same values already used in the current build state:

```.env.example``` at the root level
```
GROQ_API_KEY="ASK YASIR (THIS IS NOT THE KEY)"
POSTGRES_DB=clinicsense
POSTGRES_USER=clinicsense
POSTGRES_PASSWORD=devpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
MONGO_URL=mongodb://localhost:27017
SECRET_KEY=yasir1805
```

### Start Docker services

From the repository root:

```bash
docker compose -f infra/docker-compose.yml up -d
```

### Check whether containers are running

```bash
docker ps
```

You should see at least:

- `clinicsense-postgres`
- `clinicsense-mongo`

### Stop Docker services

```bash
docker compose -f infra/docker-compose.yml down
```

### Important note about database persistence

If the PostgreSQL container uses a named Docker volume, the database state will survive container restarts. That means the current admin user, roles, module permissions, and audit rows can remain available for the next teammate as long as the volume is not deleted.

## Enter PostgreSQL inside Docker

Use this command to open the running PostgreSQL instance:

```bash
docker exec -it clinicsense-postgres psql -U clinicsense -d clinicsense
```

This is the standard command teammates should use while the project still relies on a local Docker-backed control-plane database.

## Database setup queries

Run the following only if the database is new or must be rebuilt from scratch.

### 1. Enable UUID generation

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### 2. Create the core tables

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE
);

CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id),
    name TEXT
);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id),
    module_id UUID REFERENCES modules(id),
    PRIMARY KEY (role_id, module_id)
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id UUID REFERENCES roles(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type TEXT NOT NULL,
    category TEXT,
    module TEXT,
    detail JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### 3. Seed the current role/category/module structure

```sql
INSERT INTO roles (name)
VALUES ('admin')
ON CONFLICT (name) DO NOTHING;

INSERT INTO categories (name)
VALUES ('Billing')
ON CONFLICT (name) DO NOTHING;

INSERT INTO modules (category_id, name)
SELECT c.id, 'Billing'
FROM categories c
WHERE c.name = 'Billing'
AND NOT EXISTS (
    SELECT 1 FROM modules m WHERE m.name = 'Billing'
);
```

### 4. Create the admin user

First generate the password hash locally after the backend files are present and the Python environment is activated.

```bash
python -c "import bcrypt; print(bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode())"
```

Copy the generated hash and insert the admin user using the same universal email used in the current project state:

```sql
INSERT INTO users (email, password_hash, role_id)
SELECT 'admin@clinicsense.ai', 'PASTE_HASH_HERE', r.id
FROM roles r
WHERE r.name = 'admin'
AND NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@clinicsense.ai'
);
```

### 5. Grant the Billing module to the admin role

```sql
INSERT INTO role_permissions (role_id, module_id)
SELECT r.id, m.id
FROM roles r
JOIN modules m ON m.name = 'Billing'
WHERE r.name = 'admin'
AND NOT EXISTS (
    SELECT 1
    FROM role_permissions rp
    WHERE rp.role_id = r.id AND rp.module_id = m.id
);
```

## How to run the backend

With the Python virtual environment active, run the FastAPI app from the repository root.

### Windows PowerShell

```powershell
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload --app-dir backend
```

### Cross-platform fallback

```bash
python -m uvicorn app.main:app --reload --app-dir backend
```

## How to test what is currently working

### Open the API docs

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

### Test login

Use `POST /auth/login` with:

```json
{
  "email": "admin@clinicsense.ai",
  "password": "admin123"
}
```

A successful result returns:

- `access_token`
- `token_type`

### Test the protected route

1. Copy the access token.
2. Click **Authorize** in Swagger.
3. Paste `Bearer YOUR_ACCESS_TOKEN`.
4. Call `GET /protected/billing`.

Expected result:

```json
{
  "message": "You are authorized for the Billing module",
  "user_email": "admin@clinicsense.ai"
}
```

### Verify audit logging

In PostgreSQL, run:

```sql
SELECT event_type, user_id, detail, created_at
FROM audit_log
ORDER BY created_at DESC;
```

A successful login should produce a `login` event row.

## How a teammate can continue from the same database state

If Docker volumes are preserved, a teammate usually does **not** need to recreate the schema or reseed the admin data. They only need to:

1. Clone the repository.
2. Start Docker with the same compose file.
3. Activate a Python virtual environment.
4. Install dependencies.
5. Run the backend.
6. Test login and the protected route.

If the database has been wiped or Docker volumes were removed, the teammate must rerun the database setup and seed queries from this README.

## Handoff note for teammates

If you are the next developer picking this up:

- Do not delete Docker volumes unless you intentionally want a clean rebuild.
- Use the same PostgreSQL credentials documented above for now.
- Verify the current foundation state before building the next phase.
- If there is confusion about branch, local file state, or current implementation differences, ask Yasir before changing the setup.

## What has been completed so far

The foundation phase now satisfies the required checkpoint that login works, RBAC is enforced, protected routes are testable, and the audit trail exists early in the project lifecycle. That is the exact stopping point the build order expects before the team begins the semantic metadata layer.

## Next planned phase

The next phase is the **Semantic Metadata Layer**, which should introduce:

- dataset registry
- business glossary
- vector-enabled metadata support

This is the next dependency the build guide defines before AI query planning can be introduced.
