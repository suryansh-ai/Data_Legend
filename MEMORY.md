# Data Legend - Project Memory & Context

## Project Overview
- **Name**: Data Legend — Healthcare Facility Intelligence App
- **Purpose**: Databricks hackathon challenge (Databricks Apps & Agents for Good 2026)
- **Goal**: Trust Layer for ~1,889 messy Indian healthcare facility records
- **Stack**: React 19 + TypeScript + FastAPI (Python)
- **Deploy**: Databricks Apps (single uvicorn process serving React build + API)

## Databricks Workspace
- **Workspace URL**: `https://dbc-bc97011a-f032.cloud.databricks.com`
- **Org ID**: `7474647855860628`
- **App name**: `data-legend-v2`
- **App URL**: `https://data-legend-v2-7474647855860628.aws.databricksapps.com`
- **App ID**: `cea04a49-6121-499f-9d3d-ccc09a3314ce`
- **Service principal**: `app-33ksvr data-legend-v2` (ID: `76926135758045`)
- **Token**: (stored locally in env, not committed — Apps REST API only, lacks workspace scope)
- **App compute**: MEDIUM (Up to 2 vCPUs, 6 GB memory)
- **Creator**: `fortestsubject2026@gmail.com`

## GitHub
- **Repo**: `https://github.com/suryansh-ai/Data_Legend.git` (public)
- **Git config**: `suryansh-ai` / `pandeygs305@gmail.com`

## Dataset
- **Primary**: `data/facilities_scored.parquet` (9.1MB, 1,889 rows, 51 columns)
- **Fallback**: `data/facilities.parquet` (9.1MB)
- **Other**: `data/nfhs5_district_health.xlsx` (0.5MB)
- **Key columns**: `unique_id`, `name`, `description`, `capability`, `procedure`, `equipment`, `specialties` (JSON arrays), `numberDoctors`, `capacity`, `address_stateOrRegion`, `address_city`, `latitude`, `longitude`, `_trust_score`, `_trust_signal`, `_total_claims`, `_corroborated`

## Hackathon Details
- **Event**: Databricks Apps & Agents for Good 2026 (DAIS, June 15-16 2026)
- **Participants**: 368 teams, 122 submitted
- **Prize pool**: $17,500
- **Status**: Winners already announced — this is practice/learning build
- **Tracks**: Trust Desk, Medical Desert, Trust for Patients, Ambition (4 tracks)
- **Evaluation**: Evidence & Trust (35%), Product Judgment (30%), Technical Execution (25%), Ambition (10%)
- **Required**: Databricks Apps, SQL Warehouse, Lakebase (Postgres), MLflow 3 tracing
- **Databricks Free Edition**: Limited serverless, 1 SQL warehouse (2X-Small), 3 apps max, auto-stop after 24h

## Competitor Analysis (5 repos + winners)

### 1. CarePilot (HumfDev/CarePilot) — MOST COMPLETE
- React 19 + TypeScript + Vite + Tailwind + shadcn/ui + AppKit (Express)
- Features: NL search (Databricks Genie), Leaflet map (5-marker trust), driving ETA (OSRM), planner (notes/overrides/shortlists), LLM summaries (Llama 4 Maverick), facility detail modal, data quality audit
- Strengths: Resizable split-panel UI, real OSRM routing, Genie integration, 56 TS files
- Weaknesses: Desktop only, no MLflow, no choropleth, static 34-city table, no auth/dark mode
- **Key to beat**: Their map, NL search, and driving ETA

### 2. AarogyaNet (Terobyte/multi-agent-healthcare-intelligence-system)
- React 18 + FastAPI + Llama 3.3 70B + Vector Search (RAG) + Framer Motion
- Features: AI chat with tool-calling agents, Trust Scorer (rule-based), Vector Search, Evidence Analyzer, Medical Desert Detector, 502KB Q&A dataset
- Strengths: Multi-agent architecture, animated dark UI, 4-agent pipeline
- Weaknesses: Railway/Vercel hosting, monolithic 35KB main.py, no real-time data
- **Key to beat**: Their agent architecture and Q&A dataset

### 3. dbx-for-good (dalfindata/dbx-for-good)
- Streamlit + Plotly + Llama 4 Maverick + Genie + Lakebase
- Features: 5 tabs (Desert, Trust, Facility, Readiness, AI), choropleth, AI assistant
- Strengths: Best Plotly map, strongest data engineering, Lakebase persistence
- Weaknesses: Stock Streamlit UI, no polish, monolithic, no mobile
- **Key to beat**: Their data preparation quality and 5-tab completeness

### 4. MedIndia (DeerEdge/databricks-apps-agents)
- Next.js 15 + React 19 + MapLibre GL + Recharts + Cloudflare Workers + Lakebase
- Features: Genie queries, AI chat (Maya, 8 tools), 650KB Parquet, choropleth, scenario planner, Lakebase
- Strengths: Strongest Databricks integration (6 services), best typography, dual hosting
- Weaknesses: No Python backend, Genie-only SQL, LLM hallucination risk, no mobile
- **Key to beat**: Their Next.js architecture and Genie/agent integration

### 5. Raha-Care (Sharmishay/Raha-Care)
- TypeScript AppKit + shadcn/ui + Databricks AppKit 0.46.1 + Lakebase
- Features: Patient portal, AI chat, AI trust score, facility search
- Strengths: AppKit 0.46.1 (latest), production persistence layer
- Weaknesses: 2 commits, minimal README, no AI/ML, no maps, no visualizations
- **Key to beat**: Their AppKit integration pattern

### Winners (Devpost)
- 1st: "Data Readiness Desk" — claim-level trust scoring (THE winning insight)
- 2nd: "Asclepius" — all 4 tracks, distance-based desert model, citation guard, medallion architecture
- 3rd: "CareSignal" — decision-support framing, polished UI

## Key Insights from Research
- **Claim-level trust scoring** is the winning innovation (analyze at CLAIM level, not row level)
- **All 4 tracks in one app** differentiates (only Asclepius did this)
- **Mobile responsive** — NO competitor does this
- **Dark mode** — only AarogyaNet has it
- **Streaming AI reasoning** — nobody does well
- **Print/export** — only MedIndia has print stylesheet
- **Lakebase persistence** for user data (notes, overrides, shortlists) is expected

## Databricks Auto-Set Environment Variables (for Streamlit, but relevant)
- `STREAMLIT_SERVER_PORT` = `DATABRICKS_APP_PORT`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`
- For React+FastAPI: `uvicorn app:app --host 0.0.0.0 --port $DATABRICKS_APP_PORT`

## Previous 502 Root Cause
- `app.yaml` hardcoded `--server.port 8080` and `--server.address 0.0.0.0`
- Databricks auto-sets these for Streamlit apps → conflict → 502
- Fix: `command: ["streamlit", "run", "app/main.py"]` (no port/address args)
- **Lesson**: For FastAPI, use `command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$DATABRICKS_APP_PORT"]`

## Architecture Decision
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui + Framer Motion
- **Backend**: FastAPI (Python 3.11+) serving React build + API endpoints
- **Data**: pandas + pyarrow for parquet loading
- **Maps**: Leaflet (react-leaflet) with clustering
- **Charts**: Recharts
- **State**: React hooks + context (no Redux needed)
- **Routing**: React Router v6
- **Persistence**: Lakebase (Postgres) with SQLite fallback
- **Trust Engine**: Claim-level scoring with MLflow tracing
- **Deployment**: Single uvicorn process on Databricks Apps

## Project Structure (34 files)
```
Data_Legend/
├── app.py                          # FastAPI entry point
├── app.yaml                        # Databricks Apps config
├── requirements.txt                # Python dependencies
├── package.json                    # npm scripts (build React)
├── vite.config.ts                  # Vite config
├── tailwind.config.js              # Tailwind config
├── tsconfig.json                   # TypeScript config
├── postcss.config.js               # PostCSS
├── client/
│   ├── index.html                  # Entry HTML
│   └── src/
│       ├── main.tsx                # React entry
│       ├── App.tsx                 # Router + Layout
│       ├── index.css               # Tailwind base + CSS vars
│       ├── lib/
│       │   ├── api.ts              # API client
│       │   └── types.ts            # TypeScript interfaces
│       ├── components/
│       │   ├── Layout.tsx          # Sidebar + header + theme
│       │   ├── TrustBadge.tsx      # Trust score chip
│       │   ├── FacilityCard.tsx    # Facility card
│       │   ├── MapView.tsx         # Leaflet map + clustering
│       │   ├── TrustChart.tsx      # Recharts radar/bar
│       │   ├── SearchBar.tsx       # NL search input
│       │   ├── DataTable.tsx       # Sortable table
│       │   ├── EmptyState.tsx      # Empty state
│       │   ├── LoadingSpinner.tsx  # Loading skeleton
│       │   ├── ExportButton.tsx    # Export PDF/CSV
│       │   └── ThemeToggle.tsx     # Dark/light toggle
│       └── pages/
│           ├── Home.tsx            # Overview + stats
│           ├── TrustDesk.tsx       # Trust scoring + search
│           ├── FacilityDetail.tsx  # Deep dive
│           ├── MedicalDesert.tsx   # Coverage gaps
│           └── DataReadiness.tsx   # Data quality audit
├── server/
│   ├── __init__.py
│   ├── trust_engine.py             # Claim-level trust scoring
│   ├── data_loader.py              # Parquet loader
│   ├── lakebase.py                 # Lakebase connection pool
│   └── routes/
│       ├── __init__.py
│       ├── facilities.py           # /api/facilities
│       ├── trust.py                # /api/trust/score
│       ├── search.py               # /api/search
│       ├── persistence.py          # /api/notes, /api/shortlist
│       └── stats.py                # /api/stats, /api/gaps
└── data/
    ├── facilities_scored.parquet
    └── facilities.parquet
```

## Implementation Phases

### Phase 1: Scaffold (~10 min)
- Delete old Streamlit files (app/, .streamlit/)
- Create app.py, requirements.txt, app.yaml, package.json
- Initialize Vite+React+TypeScript in client/
- Install: tailwindcss, shadcn/ui, recharts, leaflet, react-leaflet, react-router-dom, framer-motion

### Phase 2: Backend (~30 min)
- server/data_loader.py — Parquet loader with fallback
- server/trust_engine.py — Claim-level scoring + MLflow tracing
- server/lakebase.py — Connection pool with SQLite fallback
- server/routes/facilities.py — List, detail, map data
- server/routes/trust.py — Score single, batch, breakdown
- server/routes/search.py — NL search
- server/routes/persistence.py — Notes, shortlist, overrides
- server/routes/stats.py — Summary stats, coverage gaps
- app.py — Mount routes, serve React, CORS

### Phase 3: Frontend (~40 min)
- Layout: Sidebar nav, header, theme toggle, responsive
- Home: Stats cards, recent activity, quick links
- TrustDesk: Search + filter + table + map split view + batch scoring + export
- FacilityDetail: Hero + trust radar + AI summary + evidence + notes + map
- MedicalDesert: Choropleth map + gap table + scatter + stats
- DataReadiness: Completeness bars + distribution + signal breakdown + issues

### Phase 4: Integration (~15 min)
- API client with retry + error handling
- React Router with active states
- Loading skeletons + empty states
- Dark mode (CSS variables)
- Framer Motion transitions

### Phase 5: Deploy (~10 min)
- npm run build → client/dist/
- Git commit + push
- Deploy via Databricks Apps API
- Verify

## Target Features (Surpass ALL Competitors)
1. All 4 tracks in one app
2. Claim-level trust scoring (winning insight)
3. Mobile responsive (nobody has this)
4. React + FastAPI (best performance)
5. Leaflet with clustering for 10K markers
6. Streaming AI reasoning
7. shadcn/ui + Tailwind + Framer Motion
8. Dark mode (system preference toggle)
9. Exportable PDF/CSV reports
10. Lakebase persistence for user data
11. MLflow tracing
12. Data readiness audit
