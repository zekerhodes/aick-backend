# AIC Kapsowar Hospital - Asset Management API

FastAPI backend powering the hospital's asset management portal.

## Tech Stack
- FastAPI + Uvicorn
- MongoDB (motor async driver)
- JWT authentication (pyjwt + bcrypt)

## Local Setup
1. Copy env template: `cp .env.example .env` and fill in real values
2. Install deps: `pip install -r requirements.txt`
3. Run dev server: `uvicorn server:app --reload --port 8001`

## Default Seeded Admin
- Email: `admin@kapsowar.org`
- Password: `demo1234`
- **CHANGE PASSWORD IN PRODUCTION**

## Key Endpoints
- `POST /api/auth/login` - returns JWT token
- `GET  /api/assets` - paginated asset list (filters: search, category_id, location_id, status)
- `POST /api/assets/{id}/{action}` - check-out, check-in, lease, dispose, maintenance, move, reserve
- `GET  /api/reports/dashboard-stats` - KPIs for dashboard
- See `contracts.md` for full API contract

## Deployment (Railway)
Deploys via Dockerfile. Required environment variables:
- `MONGO_URL` (MongoDB Atlas connection string)
- `DB_NAME` (e.g., `aic_kapsowar`)
- `JWT_SECRET` (strong random string)
- `CORS_ORIGINS` (comma-separated origins)
- `FEATURE_PHARMACY` / `FEATURE_INVENTORY` (false/true)

## Companion Frontend Repo
https://github.com/YOUR-USERNAME/aick-frontend
