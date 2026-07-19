# 🏥 Data Legend — Healthcare Facility Intelligence Platform for India

> **Trust-first healthcare discovery. Analyze — Verify — Refer — Track.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

Data Legend is an open-source platform that **scores, verifies, and analyzes** healthcare facility capability claims across **9,947 Indian hospitals and clinics** using claim-level trust analysis. Built for the [Databricks Apps & Agents for Good 2026](https://www.databricks.com/) hackathon.

## ✨ Features

### 🔍 Facility Trust Desk
Search, filter, and score facility claims with evidence breakdown. View trust radar charts, capability corroboration analysis, and override trust scores with audit notes.

### 🤖 AI Referral & Triage Copilot
Enter patient symptoms in plain language (including **Hindi/Hinglish** support) to get:
- Urgency classification (Emergent → Routine)
- Diagnostic specialty matching with confidence scores
- Red flag detection for critical conditions
- First-aid advisory guidelines
- AI-powered hospital recommendations ranked by composite scoring

### 🏨 Smart Booking Engine
Search available time slots, book appointments with confirmation codes, manage status (pending → confirmed → completed), and track patient outcomes.

### 🧭 NGO Planning Panel
Analyze regional resource gaps, essential capability coverage (emergency, maternity, ICU, surgery, etc.), district health indicators (NFHS-5), and get intervention plans with priority recommendations.

### 📊 Medical Desert Analysis
Interactive choropleth map showing state-level trust coverage, low-trust regions needing attention, and district-level health indicator overlays.

### 🩺 Facility Detail Deep Dive
Trust radar visualization, evidence table with snippet-level breakdown, analyst notes, shortlisting, override management, and trust impact from outcomes.

### 📋 Data Readiness Dashboard
Full data quality audit: column completeness, trust signal distribution, facility coverage by state, and data source status.

### 📈 Outcome Tracking & Learning Loop
Record patient outcomes, calculate trust impact based on satisfaction and improvement rates, and derive insights across specialties and facilities.

### 🎤 Voice Input Support
Speech-to-text for symptom input with multi-language support (English, Hindi, Bengali, Tamil, Telugu, Marathi, Urdu, Gujarati, Kannada, Malayalam, Punjabi).

### 🧠 AI Integration
Databricks Foundation Model API integration (Llama 3.3 70B, Mixtral) for:
- Enhanced triage assessment
- Hospital recommendation explanations
- Facility quality analysis
- Regional health insights generation

## 📊 Data Architecture

Data Legend uses a **three-layer data architecture** with intelligent fallback:

| Layer | Technology | Use Case |
|-------|-----------|----------|
| **Primary** | Databricks SQL Warehouse | Full 10K dataset on Databricks Apps |
| **Secondary** | Parquet files (local) | Fast local development & staging |
| **Tertiary** | Lakebase (Postgres) / SQLite | Analyst notes, overrides, shortlists |

**11,977 capability claims analyzed** across 16 categories using 5 evidence fields:

| Capability | Evidence Sources |
|------------|-----------------|
| ICU, NICU, Emergency | Description, Capability, Equipment |
| Maternity, Surgery, Trauma | Description, Procedure, Specialties |
| Cardiology, Oncology, Dialysis | Description, Capability, Procedure |
| Radiology, Laboratory, Pharmacy | Description, Equipment, Specialties |
| Ophthalmology, Orthopedics, Pediatrics, Dental | Description, Specialties |

### Trust Signal Levels

| Signal | Meaning | Color |
|--------|---------|-------|
| **CORROBORATED** | Multiple fields confirm the claim (≥2 sources) | 🟢 Green |
| **CLAIMED_ONLY** | Single field mentions it; needs verification | 🟡 Amber |
| **WEAK** | Negated ("not available") or aspirational ("planned") language | 🔴 Red |
| **UNKNOWN** | No evidence found in any field | ⚪ Gray |

### Data Sources

- **Facilities Dataset**: 9,947 hospitals and clinics across 34 Indian states/UTs
- **NFHS-5 District Health**: 707 districts with institutional birth rates, ANC visits, health insurance, electricity coverage, and more
- **Real-time SQL Warehouse**: Auto-discovers Unity Catalog tables in Databricks

## 🛠️ Tech Stack

### Frontend
- **React 19** with TypeScript & Vite
- **Tailwind CSS** with dark mode support
- **Recharts** for interactive data visualization
- **Leaflet / React-Leaflet** for interactive maps
- **Framer Motion** for animations & transitions
- **Lucide React** for icons
- **React Router v7** for client-side routing

### Backend
- **FastAPI** (Python) with async support
- **Pandas & PyArrow** for data processing
- **MLflow 3** for experiment tracking & logging
- **Databricks SDK** for Lakebase OAuth & SQL Warehouse
- **psycopg2** for Postgres connectivity

### ML/AI
- **Rule-based Triage Engine**: Symptom→specialty mapping with Hindi/Hinglish support
- **Recommendation Engine**: Composite scoring (trust × capability match × urgency × proximity × capacity × district health)
- **Databricks Foundation Model API**: Llama 3.3 70B & Mixtral 8x7B for LLM-enhanced assessments

### Deployment
- **Render** — FastAPI backend
- **Vercel** — React frontend (from `client/`)
- **Databricks Apps** — Unified deployment (retained)

## 🚀 Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/data-legend.git
cd data-legend

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Build the React frontend
npm run build

# Run the FastAPI backend (serves the built frontend)
npm start
# or
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

App runs at **http://localhost:8080**.

### Frontend Dev Mode (with HMR)

```bash
cd client
npm run dev
```
Frontend hot-reloads at **http://localhost:5173** while FastAPI runs at **:8080**.

## 📁 Project Structure

```
├── app.py                      # FastAPI entry point + SPA middleware
├── app.yaml                    # Databricks Apps deployment config
├── package.json                # npm scripts & dependencies
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── postcss.config.js           # PostCSS config
├── tailwind.config.js          # Tailwind CSS theme
├── tsconfig.json               # TypeScript config
├── vite.config.ts              # Vite build config
├──
├── client/                     # React frontend
│   ├── index.html
│   ├── vercel.json             # Vercel deployment config
│   ├── src/
│   │   ├── App.tsx             # Router + layout
│   │   ├── main.tsx            # Entry point
│   │   ├── index.css           # Tailwind base + custom styles
│   │   ├── components/
│   │   │   ├── Layout.tsx      # App shell (navbar + mobile drawer)
│   │   │   ├── ThemeToggle.tsx # Light/dark/system theme
│   │   │   ├── MapView.tsx     # Leaflet interactive map
│   │   │   ├── EmergencyBox.tsx # Floating emergency contacts
│   │   │   ├── VoiceInput.tsx  # Speech-to-text component
│   │   │   ├── TrustBadge.tsx  # Trust signal badge
│   │   │   ├── TrustChart.tsx  # Radar chart for capabilities
│   │   │   ├── SearchBar.tsx   # Autocomplete search
│   │   │   ├── DataTable.tsx   # Tabular data view
│   │   │   ├── ExportButton.tsx # CSV export
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx        # Overview dashboard
│   │   │   ├── TrustDesk.tsx   # Facility search & scoring
│   │   │   ├── FacilityDetail.tsx # Deep dive with radar + evidence
│   │   │   ├── Triage.tsx      # AI triage copilot
│   │   │   ├── Booking.tsx     # Appointment booking
│   │   │   ├── NGODashboard.tsx # NGO resource planning
│   │   │   ├── MedicalDesert.tsx # Coverage gap map
│   │   │   └── DataReadiness.tsx # Data quality audit
│   │   ├── hooks/
│   │   │   └── useVoiceInput.ts # Web Speech API hook
│   │   └── lib/
│   │       ├── api.ts          # API client
│   │       ├── types.ts        # TypeScript interfaces
│   │       └── utils.ts        # Helpers (cn, format, trust colors)
│   └── dist/                   # Built frontend (served by FastAPI)
├──
├── server/                     # Python backend
│   ├── data_loader.py          # Multi-source data loading with fallback
│   ├── trust_engine.py         # Claim-level trust scoring (16 capabilities)
│   ├── triage_engine.py        # Symptom→specialty mapping + Hindi support
│   ├── recommendation_engine.py # Composite facility scoring
│   ├── booking_engine.py       # Appointment scheduling & management
│   ├── outcome_tracker.py      # Patient outcome recording & analytics
│   ├── ai_service.py           # Databricks Foundation Model API wrapper
│   ├── lakebase.py             # Persistence (Postgres/SQLite) with fallback
│   ├── sql_connector.py        # Databricks SQL Warehouse connector
│   └── routes/
│       ├── facilities.py       # List, detail, map, autocomplete
│       ├── trust.py            # Score & batch score
│       ├── search.py           # Vectorized relevance search
│       ├── stats.py            # Dataset, state, trust distribution stats
│       ├── persistence.py      # Notes, overrides, shortlists CRUD
│       ├── triage.py           # Symptom assessment + hospital recommend
│       ├── booking.py          # Appointment CRUD + slot availability
│       ├── outcomes.py         # Outcome recording + trust impact
│       ├── ngo.py              # NGO dashboard, gap analysis, interventions
│       └── ai.py              # AI chat, triage, explain, analyze
├──
├── data/                       # Parquet datasets
│   ├── facilities_master.parquet     # 9,947 clean facilities
│   ├── facilities_scored.parquet     # Scored facilities
│   ├── facilities.parquet            # Raw facilities
│   ├── district_health.parquet       # 707 NFHS-5 districts
│   └── nfhs5_district_health.xlsx    # Source NFHS-5 data
├──
└── scripts/                    # Data pipeline scripts
    ├── build_master_dataset.py
    ├── normalize_cities_v2.py
    ├── normalize_names.py
    ├── convert_csv_to_scored_parquet.py
    ├── analyze_names.py
    ├── analyze_cities.py
    ├── check_all_data.py
    ├── test_api.py
    ├── test_api_full.py
    ├── test_frontend.py
    └── test_pipeline.py
```

## 🌐 API Endpoints

### Facilities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/facilities` | List facilities (paginated, filterable by state/trust/capability) |
| GET | `/api/facilities/{id}` | Facility detail with all fields |
| GET | `/api/facilities/map` | Map data (with coordinates, trust scores) |
| GET | `/api/facilities/autocomplete?q=` | Autocomplete facility names |

### Trust Scoring
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/trust/score/{id}` | Score a single facility |
| POST | `/api/trust/batch` | Batch score up to 50 facilities |

### Search
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search?q=` | Vectorized relevance search across names, descriptions, cities, capabilities |

### Statistics
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Dataset-level summary statistics |
| GET | `/api/stats/states` | State-level coverage & trust averages |
| GET | `/api/stats/trust-distribution` | Trust signal distribution counts |
| GET | `/api/stats/column-completeness` | Field completeness counts |
| GET | `/api/stats/district-health` | NFHS-5 district health indicators (707 districts) |

### Persistence (Notes & Shortlists)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/persistence/notes/{id}` | Get notes for a facility |
| POST | `/api/persistence/notes` | Add a note |
| GET | `/api/persistence/overrides/{id}` | Get trust score override |
| POST | `/api/persistence/overrides` | Set trust score override |
| GET | `/api/persistence/shortlist` | Get shortlisted facility IDs |
| POST | `/api/persistence/shortlist` | Add facility to shortlist |
| DELETE | `/api/persistence/shortlist` | Remove facility from shortlist |

### Triage & Recommendation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/triage/assess` | Assess symptoms → specialties, urgency, red flags |
| POST | `/api/triage/recommend` | Recommend hospitals by specialty & location |
| GET | `/api/triage/specialties` | List supported medical specialties |
| GET | `/api/triage/urgency-levels` | List urgency levels & criteria |

### Booking
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/booking/appointments` | Create appointment |
| GET | `/api/booking/appointments/{id}` | Get appointment details |
| GET | `/api/booking/appointments/facility/{id}` | Facility appointments |
| GET | `/api/booking/appointments/patient/{phone}` | Patient appointments |
| PUT | `/api/booking/appointments/{id}/status` | Update appointment status |
| POST | `/api/booking/appointments/{id}/cancel` | Cancel appointment |
| POST | `/api/booking/appointments/{id}/confirm` | Confirm appointment |
| GET | `/api/booking/slots` | Get available time slots |
| GET | `/api/booking/stats` | Booking statistics |

### Outcomes
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/outcomes/record` | Record patient outcome |
| GET | `/api/outcomes/facility/{id}` | Facility outcomes |
| GET | `/api/outcomes/facility/{id}/summary` | Facility outcome summary |
| GET | `/api/outcomes/facility/{id}/trust-impact` | Trust score impact from outcomes |
| GET | `/api/outcomes/patient/{id}` | Patient outcomes |
| GET | `/api/outcomes/insights` | Cross-facility learning insights |
| GET | `/api/outcomes/stats` | Overall outcome statistics |

### NGO Dashboard
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ngo/dashboard` | NGO dashboard overview & key metrics |
| POST | `/api/ngo/gap-analysis` | Regional gap analysis |
| GET | `/api/ngo/resource-gaps` | Resource gap analysis by capability |
| GET | `/api/ngo/intervention-plan` | Prioritized intervention recommendations |

### AI (Databricks LLM)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ai/chat` | Chat completion (Llama 3.3 70B / Mixtral) |
| POST | `/api/ai/triage` | AI-powered triage (falls back to rule-based) |
| POST | `/api/ai/explain` | Explain hospital recommendation |
| POST | `/api/ai/analyze-facility` | AI facility quality analysis |
| POST | `/api/ai/health-insights` | Regional health insights generation |
| GET | `/api/ai/models` | List available AI models |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with data source info |
| GET | `/docs` | Interactive Swagger API documentation |

## 🏗️ Deployment Architecture

The project supports a **split deployment** for production:

```
User Browser
    │
    ▼
┌─────────────┐     ┌──────────────────┐
│   Vercel    │────▶│    Render API    │
│  (Frontend) │     │  (FastAPI)       │
│  client/    │     │  app:app         │
└─────────────┘     └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Data Sources    │
                    │  ┌─────────────┐ │
                    │  │ Parquet     │ │
                    │  ├─────────────┤ │
                    │  │ SQL WH      │ │
                    │  ├─────────────┤ │
                    │  │ Lakebase    │ │
                    │  └─────────────┘ │
                    └──────────────────┘
```

### Deploy to Render (API)

1. Create a new **Render Web Service** from this repository.
2. Set root directory to repository root.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add env vars:
   - `PYTHONPATH=.`
   - `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`
   - (Optional) `LAKEBASE_ENDPOINT` for Postgres persistence
   - (Optional) `DATABRICKS_WAREHOUSE_ID` for SQL Warehouse

### Deploy to Vercel (Frontend)

1. Import repository into Vercel.
2. Set root directory to `client`.
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add env var: `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`

### Databricks Apps (Alternative)

The existing `app.yaml` retains full Databricks Apps support:
- Auto-injects `PGHOST`, `PGUSER`, `PGDATABASE` from Lakebase
- Auto-injects `DATABRICKS_WAREHOUSE_ID` from SQL Warehouse
- Generates OAuth tokens via `databricks.sdk`

## 🧠 Trust Engine Details

The trust engine analyzes **16 capability categories** across **5 evidence fields**:

### Capabilities Analyzed

ICU, NICU, Maternity, Emergency, Oncology, Trauma, Dialysis, Surgery,
Pharmacy, Laboratory, Radiology, Cardiology, Ophthalmology,
Orthopedics, Pediatrics, Dental

### Scoring Logic

```python
CORROBORATED  = evidence in ≥2 fields  → score 0.7–1.0 (green)
CLAIMED_ONLY  = evidence in 1 field     → score 0.5      (amber)
WEAK          = negated/aspirational     → score 0.1–0.3  (red)
UNKNOWN       = no evidence found        → score 0.0      (gray)
```

Evidence fields are weighted:
- **Description**: 1.0× (richest source)
- **Capability**: 0.8×
- **Procedure**: 0.8×
- **Equipment**: 0.7×
- **Specialties**: 0.6×

### Hindi/Hinglish Triage Support

The triage engine maps 80+ Hindi medical phrases to English equivalents:
- `"seene me dard"` → chest pain
- `"saans phulna"` → shortness of breath
- `"kamar dard"` → back pain
- `"bukhar"` → fever
- `"behos"` → unconscious

## 📈 Recommendation Scoring

Hospitals are ranked by **composite scoring** with weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Trust Score | 35% | Claim-level verification confidence |
| Capability Match | 25% | How well the facility matches required specialties |
| Urgency Bonus | 15% | Emergency/ICU availability for urgent cases |
| Proximity | 10% | Distance from patient (closer = better) |
| Capacity | 10% | Bed count & doctor availability |
| District Health | 5% | NFHS-5 health indicators bonus |

## 🤝 Contributing

We welcome contributions! Areas we'd love help with:

- **Additional data sources**: Integrate more Indian healthcare datasets
- **Language expansion**: More Indian language support for triage
- **Mobile app**: React Native or Flutter client
- **Real-time availability**: API integration with actual hospital bed management systems
- **Telemedicine**: Video consultation scheduling and integration

## 📄 License

Built for the **Databricks Apps & Agents for Good 2026** hackathon.

---

<div align="center">
  <sub>Built with ❤️ for better healthcare access in India</sub>
</div>
