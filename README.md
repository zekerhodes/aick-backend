# AIC Kapsowar Hospital - Asset Management API

FastAPI backend powering the hospital's asset management portal.

## What's New in v0.2
- CSV bulk import endpoint: `POST /api/tools/import-assets`
- Generic CRUD for all master data (categories, locations, vendors, etc.)
- Asset edit endpoint (`PUT /api/assets/{id}`)

## Tech Stack
- FastAPI + Uvicorn
- MongoDB (motor async driver)
- JWT authentication (pyjwt + bcrypt)

## Default Seeded Admin
- Email: admin@kapsowar.org
- Password: demo1234
- CHANGE THIS IN PRODUCTION

## Deployment (Railway)
Dockerfile-based. Required environment variables: MONGO_URL, DB_NAME, JWT_SECRET, CORS_ORIGINS, FEATURE_PHARMACY, FEATURE_INVENTORY.
