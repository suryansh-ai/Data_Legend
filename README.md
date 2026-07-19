# Data Legend

**Healthcare Facility Intelligence for India** — a polished React + FastAPI platform that turns facility claims into trust signals, coverage gap maps, and actionable recommendations.

## What it does

Data Legend helps analysts and health planners:

- Search and shortlist hospitals by capability, region, and trust signal
- Surface facilities with strong evidence vs weak claims
- Visualize medical desert zones and coverage gaps
- Explore detailed facility profiles with trust breakdowns and maps
- Use triage-driven specialty recommendations and clinic booking insights
- Persist analyst notes, overrides, and shortlist state securely

## User experience

The app is built as a modern single-page experience with:

- **Trust Desk**: searchable facility scoring and evidence review
- **Medical Desert**: regional coverage analysis with map overlays
- **Facility Detail**: deep dive into facility trust, services, and location
- **Data Readiness**: dataset completeness, quality, and trust distribution
- **Triage**: symptom-driven specialty guidance and hospital recommendations
- **Booking**: appointment flow for facility services
- **NGO Dashboard**: NGO-focused action and capacity monitoring

## Tech stack

- Frontend: **React 19**, **TypeScript**, **Vite**, **Tailwind CSS**, **Recharts**, **Leaflet**, **Framer Motion**
- Backend: **FastAPI**, **pandas**, **pyarrow**, **MLflow 3**, **uvicorn**
- Data: **Parquet-first local data**, **Databricks SQL Warehouse fallback**, **Lakebase / SQLite persistence**
- Deploy: **Databricks Apps** with a single backend process and static SPA assets

## Quick start

```bash
npm install
pip install -r requirements.txt
npm run build
npm start
```

Open `http://localhost:8080` after startup.

## Local development notes

- `npm run dev` starts the frontend dev server for UI iteration
- `npm run build` generates the SPA in `client/dist`
- `uvicorn app:app --host 0.0.0.0 --port 8080` launches the backend directly
- Backend startup loads the facility dataset from local Parquet by default

## Active project structure

```text
.
├── app.py
├── app.yaml
├── client/
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── lib/
│       └── pages/
├── data/
│   ├── data_legend_local.db
│   ├── district_health.parquet
│   ├── facilities_master.parquet
│   ├── facilities_scored.parquet
│   └── facilities.parquet
├── server/
│   ├── ai_service.py
│   ├── booking_engine.py
│   ├── data_loader.py
│   ├── lakebase.py
│   ├── routes/
│   ├── sql_connector.py
│   ├── triage_engine.py
│   ├── trust_engine.py
│   └── outcome_tracker.py
├── requirements.txt
├── package.json
└── README.md
```

## Main APIs

| Method | Path                                     | Purpose                             |
| ------ | ---------------------------------------- | ----------------------------------- |
| GET    | `/api/facilities`                      | Search, filter, and page facilities |
| GET    | `/api/facilities/{id}`                 | Facility detail by ID               |
| GET    | `/api/facilities/map`                  | Map-ready facility geo data         |
| GET    | `/api/facilities/autocomplete`         | Facility name autocomplete          |
| POST   | `/api/trust/score/{id}`                | Compute facility trust score        |
| POST   | `/api/trust/batch`                     | Batch trust scoring                 |
| GET    | `/api/search?q=`                       | Full-text facility search           |
| GET    | `/api/stats`                           | Dataset summary metrics             |
| GET    | `/api/stats/states`                    | State-level coverage stats          |
| GET    | `/api/stats/trust-distribution`        | Trust signal breakdown              |
| GET    | `/api/stats/column-completeness`       | Column completeness counts          |
| GET    | `/api/stats/district-health`           | NFHS-5 district health metrics      |
| GET    | `/api/persistence/notes/{facility_id}` | Get analyst notes                   |
| POST   | `/api/persistence/notes`               | Save a note                         |
| GET    | `/api/persistence/shortlist`           | Get shortlist                       |
| POST   | `/api/persistence/shortlist`           | Add to shortlist                    |

## Data flow

- Local dev loads facility data from the first available Parquet file in `data/`
- Databricks uses SQL Warehouse first, then falls back to local Parquet
- Persistence uses Lakebase when available, otherwise SQLite fallback via `data/data_legend_local.db`
- The UI fetches data through a clean API layer defined in `client/src/lib/api.ts`

## Notes

This repository is designed for rapid Databricks deployment and local experimentation. Feel free to extend the AI routes, add new facility insights, or adapt the dataset to broader health systems.
