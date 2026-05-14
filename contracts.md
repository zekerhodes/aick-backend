# AIC Kapsowar Hospital Asset Management — API Contracts

## Authentication (JWT)
- `POST /api/auth/signup` → { name, email, password } → { user, token }
- `POST /api/auth/login` → { email, password } → { user, token }
- `GET  /api/auth/me` → (Bearer token) → { user }

## Assets
- `GET    /api/assets?search=&category_id=&location_id=&status=&page=&per_page=` → paginated list
- `POST   /api/assets` → create
- `GET    /api/assets/{id}` → detail
- `PUT    /api/assets/{id}` → update
- `DELETE /api/assets/{id}` → delete
- `POST   /api/assets/{id}/check-out` → { person, return_date, notes }
- `POST   /api/assets/{id}/check-in` → { condition, notes }
- `POST   /api/assets/{id}/move` → { location_id, notes }
- `POST   /api/assets/{id}/maintenance` → { type, technician, cost, date, notes }
- `POST   /api/assets/{id}/dispose` → { reason, notes }
- `POST   /api/assets/{id}/reserve` → { person, start_date, end_date, notes }
- `POST   /api/assets/{id}/lease` → { person, return_date, cost, notes }
- `POST   /api/assets/{id}/lease-return` → { condition, notes }

## Generic CRUD endpoints (same shape)
- `/api/categories`     — Asset categories
- `/api/locations`      — Locations
- `/api/departments`    — Departments
- `/api/vendors`        — Vendors/suppliers
- `/api/funding-sources`— Funding sources/donors
- `/api/persons`        — Persons/employees
- `/api/sites`          — Sites
- `/api/security-groups`— Security groups
- `/api/maintenance-records`
- `/api/warranties`
- `/api/transactions`   — Audit log (read-only mostly)

## Reports
- `GET /api/reports/dashboard-stats` → KPI summary
- `GET /api/reports/{kind}` → kind-specific aggregations

## Tools
- `POST /api/tools/import-assets` → CSV upload (multipart)
- `GET  /api/tools/export-assets?format=csv|json` → download
- `POST /api/tools/audit/start` → start audit session
- `POST /api/tools/audit/scan` → record scanned tag

## Seed
On first startup, seed Kapsowar-specific data from `mock.js` equivalents.

## Frontend Integration
- Remove imports from `mock/mock.js`, replace with axios calls using `REACT_APP_BACKEND_URL`.
- Add an `api.js` helper with axios instance + auth interceptor.
- AuthContext.jsx → real `/api/auth/*` calls.
- All list/detail pages → real fetch with loading/error states.

## Data Model Prefixes (for future Pharmacy/Inventory extension)
- `assets_*` collections (this build)
- `pharmacy_*` (reserved, not yet active)
- `inventory_*` (reserved, not yet active)

Feature flags in backend `.env`:
- `FEATURE_PHARMACY=false`
- `FEATURE_INVENTORY=false`
