# Data Legend

Healthcare Facility Intelligence Platform for India — React + FastAPI on Databricks Apps.

## Overview

Scores and verifies healthcare facility capability claims across ~1,889 Indian facilities using claim-level trust analysis. Built for the Databricks Apps & Agents for Good 2026 hackathon.

## Tracks

| Track | Description |
|-------|-------------|
| **Trust Desk** | Search, filter, and score facility claims with evidence breakdown |
| **Medical Desert** | Identify underserved regions and coverage gaps |
| **Facility Detail** | Deep dive with trust radar, evidence table, notes, shortlist |
| **Data Readiness** | Audit data quality, completeness, and trust distribution |

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Recharts, Leaflet, Framer Motion
- **Backend**: FastAPI, pandas, pyarrow, MLflow 3
- **Data**: Parquet files, Lakebase (Postgres) with in-memory fallback
- **Deploy**: Render API + Vercel frontend, with Databricks Apps support retained

## Local Development

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Build frontend
npm run build

# Run backend
npm start
# or
uvicorn app:app --host 0.0.0.0 --port 8080
```

App runs at `http://localhost:8080`.

## Deployment Architecture

The project is now structured for a split deployment:

- **Render** hosts the FastAPI backend at a public API URL.
- **Vercel** hosts the React frontend from `client/`.
- The frontend reads `VITE_API_BASE_URL` and calls `${VITE_API_BASE_URL}/api`.
- The backend reads `CORS_ORIGINS` so Vercel can call the Render API.

This keeps local development simple while making production deployment explicit.

## Project Structure

```
├── app.py                  # FastAPI entry point
├── app.yaml                # Databricks Apps config
├── package.json            # npm scripts + dependencies
├── client/
│   ├── src/
│   │   ├── App.tsx         # Router + layout
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # 5 page components
│   │   └── lib/            # API client, types, utils
│   └── dist/               # Built frontend (served by FastAPI)
├── server/
│   ├── trust_engine.py     # Claim-level trust scoring
│   ├── data_loader.py      # Parquet data loading
│   ├── lakebase.py         # Persistence (Lakebase/Postgres)
│   └── routes/             # API endpoints
└── data/
    └── facilities_scored.parquet
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/facilities` | List facilities (paginated, filterable) |
| GET | `/api/facilities/{id}` | Facility detail |
| GET | `/api/facilities/map` | Map data with coordinates |
| POST | `/api/trust/score/{id}` | Score a facility |
| POST | `/api/trust/batch` | Batch score multiple facilities |
| GET | `/api/search?q=` | Natural language search |
| GET | `/api/stats` | Dataset statistics |
| GET | `/api/stats/states` | State-level coverage |
| GET | `/api/stats/trust-distribution` | Trust signal distribution |
| GET | `/api/stats/column-completeness` | Field completeness |
| GET/POST | `/api/persistence/notes` | Analyst notes |
| GET/POST | `/api/persistence/shortlist` | Facility shortlist |

## Trust Engine

Claim-level scoring analyzes each capability (ICU, maternity, surgery, etc.) against 5 evidence fields:

- **CORROBORATED** — Multiple fields confirm the claim (green)
- **CLAIMED_ONLY** — Single field mentions it (amber)
- **WEAK** — Negated or aspirational language (red)
- **UNKNOWN** — No evidence found (gray)

## Deployment Walkthrough

### 1. Deploy the API to Render

1. Create a new Render Web Service from this repository.
1. Set the root directory to the repository root.
1. Use the included `render.yaml` or configure manually with:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
1. Add any required environment variables:
  - `PYTHONPATH=.`
  - `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`
  - `LAKEBASE_ENDPOINT` if you use Lakebase/Postgres
  - `DATABRICKS_WAREHOUSE_ID` if your SQL Warehouse is enabled
1. Deploy and copy the public API URL from Render.

### 2. Deploy the frontend to Vercel

1. Import the same repository into Vercel.
1. Set the project root to `client`.
1. Use the included `client/vercel.json` or configure manually with:
  - Build command: `npm run build`
  - Output directory: `dist`
1. Add the environment variable:
  - `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`
1. Deploy the site.

### 3. Validate the split setup

1. Open the Vercel frontend.
1. Confirm the first dashboard/API requests succeed.
1. If requests fail, verify `CORS_ORIGINS` on Render and `VITE_API_BASE_URL` on Vercel.

### 4. Optional: keep Databricks Apps support

The existing `app.yaml` still works for Databricks Apps if you want to keep that path alongside Render/Vercel.

## License

Built for Databricks Apps & Agents for Good 2026.
