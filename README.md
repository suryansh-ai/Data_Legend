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
- **Deploy**: Databricks Apps (single uvicorn process)

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

## Deployment

```bash
# Commit and push
git add -A && git commit -m "Update" && git push

# Deploy to Databricks Apps
curl -X POST https://<workspace>/api/2.0/apps/data-legend-v2/deployments \
  -H "Authorization: Bearer <token>" \
  -d '{"mode": "SNAPSHOT"}'
```

## License

Built for Databricks Apps & Agents for Good 2026.
