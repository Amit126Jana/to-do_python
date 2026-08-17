# Todo App (FastAPI + React), Auth included

A full-stack todo app:
- **Backend**: FastAPI, SQLite via SQLAlchemy, JWT auth (passlib + python-jose)
- **Frontend**: React (Vite) + React Router, talks to backend via fetch

```
todo-app/
  backend/     # FastAPI app
  frontend/    # React app
```

## 1. Run locally

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs at http://localhost:8000/docs

### Frontend
```bash
cd frontend
cp .env.example .env          # VITE_API_URL=http://localhost:8000
npm install
npm run dev
```
App at http://localhost:5173

Register a user, log in, and start adding todos.

## 2. Deploy to Vercel

You deploy **backend and frontend as two separate Vercel projects** (this is the simplest, most reliable setup for a FastAPI + React combo).

### Deploy backend
1. Push this repo to GitHub.
2. In Vercel: "Add New Project" → import repo → set **Root Directory** to `backend`.
3. Vercel auto-detects `vercel.json` and `@vercel/python`. No build command needed.
4. Add environment variables in Vercel project settings:
   - `SECRET_KEY` — a long random string (e.g. `openssl rand -hex 32`)
   - `CORS_ORIGINS` — your frontend's URL once deployed, e.g. `https://your-frontend.vercel.app` (comma-separate multiple origins)
5. Deploy. Note the resulting URL, e.g. `https://your-backend.vercel.app`.

> **Database note:** SQLite on Vercel is stored in `/tmp`, which is **ephemeral** — it resets on every cold start/deploy, so data won't persist reliably in production. This is fine for a demo/portfolio project. For real persistence, swap in a hosted Postgres (e.g. [Neon](https://neon.tech) or [Supabase](https://supabase.com), both have free tiers) — just change `SQLALCHEMY_DATABASE_URL` in `database.py` to the Postgres URL and add `psycopg2-binary` to `requirements.txt`. The rest of the code (models, routes) needs no changes since it uses SQLAlchemy.

### Deploy frontend
1. In Vercel: "Add New Project" → import the same repo again → set **Root Directory** to `frontend`.
2. Framework preset: Vite. Build command `npm run build`, output dir `dist` (auto-detected).
3. Add environment variable:
   - `VITE_API_URL` — your backend URL from above, e.g. `https://your-backend.vercel.app`
4. Deploy.

Once both are live, update the backend's `CORS_ORIGINS` env var to match the frontend's actual Vercel URL and redeploy the backend.

## API summary

| Method | Path            | Auth | Description         |
|--------|-----------------|------|----------------------|
| POST   | /auth/register  | No   | Create account       |
| POST   | /auth/login     | No   | Get JWT (form data: `username`=email, `password`) |
| GET    | /auth/me        | Yes  | Current user         |
| GET    | /todos          | Yes  | List your todos      |
| POST   | /todos          | Yes  | Create todo          |
| PATCH  | /todos/{id}     | Yes  | Update title/completed |
| DELETE | /todos/{id}     | Yes  | Delete todo           |

Auth uses `Authorization: Bearer <token>` header, token from `/auth/login`.
