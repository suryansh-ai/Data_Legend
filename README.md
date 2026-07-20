<div align="center">
  <br />
  <br />
  <img src="https://img.shields.io/badge/status-production%20ready-0f766e?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/databricks-apps-FF3621?style=flat-square&logo=databricks" alt="Databricks Apps" />
  <img src="https://img.shields.io/badge/react-19-61DAFB?style=flat-square&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/fastapi-0.115-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/typescript-5.7-3178C6?style=flat-square&logo=typescript" alt="TypeScript" />
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" alt="License" />
  
  <br />
  <br />

  <h1 align="center" style="font-size: 3.5rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.5rem;">
    🏥 Data Legend
  </h1>

  <p align="center" style="font-size: 1.25rem; font-weight: 500; color: #64748b; max-width: 600px; margin: 0 auto;">
    <strong>Healthcare Facility Intelligence Platform</strong><br />
    Trust scoring · Coverage gap analysis · Smart referrals · NGO planning
  </p>
  
  <br />
  
  <p align="center">
    <a href="#-overview">Overview</a> •
    <a href="#-key-features">Features</a> •
    <a href="#-tech-stack">Tech Stack</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-deployment">Deployment</a> •
    <a href="#-api-reference">API</a>
  </p>
  
  <br />
</div>

---

## 🌐 Live Deployment

Experience Data Legend live on both deployment platforms:

| Platform | Live URL |
|----------|----------|
| 🚀 Databricks Apps | https://data-legend-v3-7474647855860628.aws.databricksapps.com/ |
| ▲ Vercel | https://hacknation-databrick-nu.vercel.app/ |

---

## 📋 Overview

**Data Legend** transforms messy Indian healthcare facility records into a structured, trust-rated intelligence system. Built for the **Databricks Apps & Agents for Good 2026** hackathon, it analyzes **9,947+ clinics** across **34+ states/UTs** to verify capability claims, detect coverage deserts, and power smart referral workflows.

> **Core Mission:** Build the trust layer for Indian healthcare — corroborate what facilities *actually* have vs. what they merely *claim*.

### Who It's For

| Role | Value |
|------|-------|
| 🏛️ **Health Planners** | Identify coverage gaps, allocate resources to desert regions |
| 🩺 **Referral Coordinators** | Verify facility capabilities before referring patients |
| 🤝 **NGOs** | Map infrastructure deficits, plan intervention zones |
| 📊 **Analysts** | Audit data readiness, export verified facility shortlists |
| 🏥 **Hospital Administrators** | Showcase corroborated capabilities to referral networks |

---

## 🚀 Key Features

### 1. 🛡️ **Facility Trust Desk**
Search & filter across **9,947+ facilities** with claim-level trust scoring:
- **CORROBORATED** ✅ — Double-verified across multiple data fields
- **CLAIMED_ONLY** ⚠️ — Stated in one source only
- **WEAK** ✖️ — Negated or aspirational ("planned", "coming soon")
- Batch score facilities, annotate with audit notes, build shareable shortlists
- Export shortlists as CSV for offline coordination

### 2. 🗺️ **Medical Desert Detection**
Identify healthcare coverage voids across Indian states:
- Interactive **Leaflet map** with marker clustering for 10K+ facilities
- Filter by **ICU availability**, **bed capacity**, or trust level
- State-wise trust rankings with low-coverage alerts
- Choropleth-ready analytics for priority intervention zones

### 3. 🤖 **AI Triage & Referral**
Natural language symptom assessment with Hindi/Hinglish support:
- "सीने में दर्द" → cardiology referral
- "बुखार और खांसी" → general medicine
- Urgency classification (Emergent → Routine)
- Automatic hospital matching by specialty + distance + trust

### 4. 📅 **Smart Booking Engine**
End-to-end appointment management:
- Specialty-based slot availability
- Confirmation codes & status tracking
- Integration with trust scores for confident referrals
- Outcome recording for follow-up analysis

### 5. 📊 **Data Readiness Audit**
Transparent data quality metrics:
- Column-level completeness with visual progress bars
- Trust signal distribution breakdown
- Critical field warnings for missing data
- Automated data source health monitoring

### 6. 🏢 **NGO Planning Dashboard**
Resource gap analysis for non-profits:
- Doctor-to-bed ratios by region
- Facility density heat mapping
- Infrastructure deficit identification
- Capacity vs. population need analysis

---

## 🧰 Tech Stack

### Frontend

| Technology | Purpose |
|---|---|
| [React 19](https://react.dev/) | UI framework with concurrent features |
| [TypeScript 5.7](https://www.typescriptlang.org/) | Type-safe development |
| [Vite 6](https://vitejs.dev/) | Lightning-fast HMR & builds |
| [Tailwind CSS 3.4](https://tailwindcss.com/) | Utility-first styling |
| [Recharts 2.15](https://recharts.org/) | Declarative charting |
| [Leaflet](https://leafletjs.com/) + [react-leaflet](https://react-leaflet.js.org/) | Interactive maps with clustering |
| [Framer Motion 11](https://www.framer.com/motion/) | Animation & transitions |
| [Lucide React](https://lucide.dev/) | Consistent iconography |
| [clsx](https://github.com/lukeed/clsx) + [tailwind-merge](https://github.com/dcastil/tailwind-merge) | Class management |

### Backend

| Technology | Purpose |
|---|---|
| [FastAPI 0.115+](https://fastapi.tiangolo.com/) | Async Python web framework |
| [pandas 2.0+](https://pandas.pydata.org/) | Data manipulation |
| [pyarrow](https://arrow.apache.org/) / [fastparquet](https://fastparquet.readthedocs.io/) | Parquet file I/O |
| [MLflow 3.0+](https://mlflow.org/) | Trust scoring tracing |
| [psycopg2](https://www.psycopg.org/) | Postgres (Lakebase) connector |
| [databricks-sql-connector](https://docs.databricks.com/dev-tools/python-sql-connector.html) | SQL Warehouse queries |
| [databricks-sdk](https://docs.databricks.com/dev-tools/sdk-python.html) | OAuth token generation |

### Infrastructure

| Service | Role |
|---|---|
| [Databricks Apps](https://www.databricks.com/product/apps) | Hosting & deployment |
| [Databricks SQL Warehouse](https://www.databricks.com/product/sql-warehouse) | Primary data source (10K records) |
| [Databricks Lakebase](https://www.databricks.com/product/lakebase) (Postgres) | User data persistence |
| **SQLite** | Local development fallback |
| **Parquet files** | Portable data distribution |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Data Legend App                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              FastAPI Backend                  │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │   │
│  │  │ Trust   │ │ Triage   │ │ Booking      │  │   │
│  │  │ Engine  │ │ Engine   │ │ Engine       │  │   │
│  │  └─────────┘ └──────────┘ └──────────────┘  │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │   │
│  │  │ Data    │ │ Recomm.  │ │ Outcome      │  │   │
│  │  │ Loader  │ │ Engine   │ │ Tracker      │  │   │
│  │  └─────────┘ └──────────┘ └──────────────┘  │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │         API Routes                    │   │   │
│  │  │  /facilities  /trust  /search  /triage│   │   │
│  │  │  /booking  /ngo  /outcomes  /ai /stats│   │   │
│  │  └──────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │       Persistence Layer              │   │   │
│  │  │  Lakebase (Postgres) ←→ SQLite        │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                      │                              │
│                      ▼                              │
│  ┌──────────────────────────────────────────────┐   │
│  │              React SPA (Vite)                 │   │
│  │  ┌──────┐ ┌──────────┐ ┌────────────────┐   │   │
│  │  │Home  │ │Trust Desk│ │Medical Desert  │   │   │
│  │  └──────┘ └──────────┘ └────────────────┘   │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────────┐   │   │
│  │  │Triage  │ │Booking │ │NGO Dashboard  │   │   │
│  │  └────────┘ └────────┘ └──────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌──────────┐
   │ Parquet │   │  SQL     │   │ Lakebase │
   │ Files   │   │ Warehouse│   │(Postgres)│
   └─────────┘   └──────────┘   └──────────┘
```

### Data Flow

1. **Startup** → Backend loads facility dataset (SQL Warehouse on Databricks, Parquet locally)
2. **Trust Scoring** → Claim-level verification across 5 data fields (description, capability, procedure, equipment, specialties)
3. **Persistence** → User notes, overrides, and shortlists stored in Lakebase (Postgres) with SQLite fallback
4. **Serving** → FastAPI serves React SPA + RESTful JSON APIs from a single process
5. **Caching** → API responses cached client-side (30s TTL) for smooth navigation

---

## 🚦 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm 9+**

### Installation

```bash
# Clone the repository
git clone https://github.com/suryansh-ai/Data_Legend.git
cd Data_Legend

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies & build SPA
npm install
npm run build

# Start the application
npm start
```

Open **http://localhost:8080** in your browser.

### Development Mode

```bash
# Terminal 1: Backend
uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# Terminal 2: Frontend (Vite dev server)
npm run dev
```

The Vite dev server runs on `http://localhost:5173` with HMR, proxying API calls to port `8080`.

---

## 🧪 Project Structure

```
Data_Legend/
├── app.py                          # FastAPI entry point
├── app.yaml                        # Databricks Apps deployment config
├── requirements.txt                # Python dependencies
├── package.json                    # npm scripts
├── vite.config.ts                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS config
├── tsconfig.json                   # TypeScript config
├── Dockerfile                      # Multi-stage Docker build
│
├── client/                         # React Frontend (SPA)
│   ├── index.html
│   └── src/
│       ├── main.tsx                # React entry point
│       ├── App.tsx                 # Router + lazy loading
│       ├── index.css               # Tailwind + CSS variables
│       ├── lib/
│       │   ├── api.ts              # API client with caching
│       │   ├── types.ts            # TypeScript interfaces
│       │   ├── utils.ts            # Utilities (formatting, etc.)
│       │   └── useDebounce.ts      # Debounce hook
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
│       │   ├── ThemeToggle.tsx     # Dark/light toggle
│       │   └── EmergencyBox.tsx    # Emergency alert
│       └── pages/
│           ├── Home.tsx            # Overview + stats
│           ├── TrustDesk.tsx       # Trust scoring + search
│           ├── FacilityDetail.tsx  # Deep dive into facility
│           ├── MedicalDesert.tsx   # Coverage gaps map
│           ├── DataReadiness.tsx   # Data quality audit
│           ├── Triage.tsx          # Symptom assessment
│           ├── Booking.tsx         # Appointment booking
│           └── NGODashboard.tsx    # NGO planning panel
│
├── server/                         # Python Backend
│   ├── __init__.py
│   ├── data_loader.py              # Multi-source data loading
│   ├── trust_engine.py             # Claim-level trust scoring
│   ├── triage_engine.py            # Symptom classification
│   ├── booking_engine.py           # Appointment management
│   ├── recommendation_engine.py    # Composite hospital scoring
│   ├── outcome_tracker.py          # Patient outcome tracking
│   ├── ai_service.py               # AI-powered insights
│   ├── sql_connector.py            # SQL Warehouse connector
│   ├── lakebase.py                 # Lakebase/SQLite persistence
│   └── routes/
│       ├── facilities.py           # /api/facilities
│       ├── trust.py                # /api/trust
│       ├── search.py               # /api/search
│       ├── stats.py                # /api/stats
│       ├── persistence.py          # /api/persistence
│       ├── triage.py               # /api/triage
│       ├── booking.py              # /api/booking
│       ├── ngo.py                  # /api/ngo
│       ├── outcomes.py             # /api/outcomes
│       ├── ai.py                   # /api/ai
│       └── __init__.py
│
└── data/                           # Parquet datasets
    ├── facilities_master.parquet   # 9,947 facilities
    ├── facilities_scored.parquet   # Scored facilities
    ├── facilities.parquet          # Raw facilities
    └── district_health.parquet     # NFHS-5 district metrics
```

---

## 📚 API Reference

### Core Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | System health & data source info |
| `GET` | `/api/facilities` | Search, filter, paginate facilities |
| `GET` | `/api/facilities/{id}` | Facility detail by unique ID |
| `GET` | `/api/facilities/map` | Map-ready geo data |
| `GET` | `/api/facilities/autocomplete` | Name autocomplete suggestions |
| `GET` | `/api/search?q=` | Full-text facility search |

### Trust Scoring

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/trust/score/{id}` | Compute trust score for a facility |
| `POST` | `/api/trust/batch` | Batch score multiple facilities |

### Analytics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/stats` | Dataset summary metrics |
| `GET` | `/api/stats/states` | State-level coverage stats |
| `GET` | `/api/stats/trust-distribution` | Trust signal breakdown |
| `GET` | `/api/stats/column-completeness` | Column fill rates |
| `GET` | `/api/stats/district-health` | NFHS-5 district metrics |

### Persistence (User Data)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/persistence/notes/{id}` | Get analyst notes |
| `POST` | `/api/persistence/notes` | Save a note |
| `GET` | `/api/persistence/shortlist` | Get facility shortlist |
| `POST` | `/api/persistence/shortlist` | Add to shortlist |
| `DELETE` | `/api/persistence/shortlist` | Remove from shortlist |

### Clinical Workflows

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/triage/assess` | Symptom triage assessment |
| `POST` | `/api/triage/recommend` | Hospital recommendations |
| `POST` | `/api/booking/create` | Create appointment |
| `GET` | `/api/booking/slots` | Available time slots |
| `GET` | `/api/ngo/stats` | NGO resource metrics |

---

## ☁️ Deployment

### Databricks Apps

```bash
# Deploy to Databricks
databricks apps deploy data-legend

# Or validate first
databricks apps validate data-legend
```

The `app.yaml` configuration handles:
- **Build**: Installs Python deps, runs `npm install && npm build`
- **Run**: Starts uvicorn on the Databricks-assigned port
- **Resources**: 4 CPU, 16GB memory
- **Environment**: Auto-injects SQL Warehouse, Lakebase credentials

### Docker

```bash
docker build -t data-legend .
docker run -p 8080:8080 data-legend
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <br />
  <p style="font-size: 0.875rem; color: #64748b;">
    Built with ❤️ for the 
    <a href="https://www.databricks.com/" style="color: #0f766e; font-weight: 600;">Databricks</a> 
    Apps & Agents for Good 2026 Hackathon
  </p>
  <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">
    © 2026 Data Legend. All rights reserved.
  </p>
  <br />
</div>
