# Data Legend

### Building the Trust Layer for Indian Healthcare

> A Databricks App that turns 1,889 messy Indian healthcare facility records into decisions a non-technical NGO planner can trust, defend, and save.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-red)
![Databricks](https://img.shields.io/badge/Databricks-Free%20Edition-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## The Problem

In India, a postal code often determines a lifespan. Families travel hours to reach a hospital — only to discover the ICU was a claim, not a capability. NGOs and public-health planners don't lack data. They lack **evidence they can act on**.

## The Solution

Data Legend is a live Databricks App that:

- **Extracts structure** from 1,889 messy facility records across 5 evidence fields
- **Scores trust** — every output traces back to facility text
- **Communicates uncertainty** — "we don't know" is honest, not a failure
- **Persists decisions** — notes, overrides, shortlists survive sessions via Lakebase
- **Traces everything** — MLflow 3 tracks every scoring run and user action

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA LEGEND                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Trust    │  │ Facility │  │ Medical  │  │ Data     │   │
│  │ Desk     │  │ Detail   │  │ Desert   │  │ Readiness│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│  ┌────┴──────────────┴──────────────┴──────────────┴────┐   │
│  │              Streamlit UI Layer                       │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │                                  │
│  ┌───────────────────────┴──────────────────────────────┐   │
│  │              Trust Engine + MLflow Tracing            │   │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────────┐  │   │
│  │  │ Cross-  │  │ Negation │  │ Sparsity-Aware     │  │   │
│  │  │ Ref     │  │ Detect   │  │ Scoring            │  │   │
│  │  └─────────┘  └──────────┘  └────────────────────┘  │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │                                  │
│  ┌───────────────────────┴──────────────────────────────┐   │
│  │              Data + Persistence Layer                 │   │
│  │  facilities_scored.parquet │ Lakebase (Postgres)     │   │
│  │  india_post_pin_directory  │ MLflow Experiment       │   │
│  │  nfhs5_district_health     │                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Databricks Free Edition account

### Local Development
```bash
git clone https://github.com/your-repo/data-legend
cd data-legend
pip install -r requirements.txt
python -m streamlit run app/main.py
```

### Deploy to Databricks
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure
databricks configure

# Setup database schema
bash scripts/setup.sh

# Deploy
bash scripts/deploy.sh
```

---

## Pages

### 1. Trust Desk
Select a capability (ICU, maternity, emergency...) and region → see ranked facilities with trust signals.

### 2. Facility Detail
Full evidence breakdown with field-by-field citations. Actions: override trust score, add notes, shortlist, flag for review.

### 3. Medical Desert Map
State-level facility distribution showing underserved regions. Bar chart + treemap + underserved ranking.

### 4. Data Readiness
Trust distribution donut, field completeness bars, score histogram, suspicious claims, high-leverage records.

---

## Trust Scoring Engine

### How It Works

1. **Parse** — Extract claims from 5 evidence fields (description, capability, procedure, equipment, specialties)
2. **Cross-Reference** — Check if claims appear in multiple fields
3. **Detect Negation** — Flag "not available", "proposed", "under construction"
4. **Weight Sources** — Description (1.0) > capability (0.8) > procedure (0.8) > equipment (0.7) > specialties (0.6)
5. **Handle Sparsity** — Empty fields = "we don't know", never "bad"

### Signal Categories

| Signal | Meaning | Action |
|--------|---------|--------|
| **CORROBORATED** | 2+ fields agree | Trust this capability |
| **CLAIMED_ONLY** | Single field claim | Verify before trusting |
| **WEAK** | Contradicted or aspirational | Treat with caution |
| **UNKNOWN** | Too sparse to judge | Don't assume; investigate |

### Example

```python
# Aravind Eye Hospital
description: "Leading eye care hospital in Hyderabad..."
capability: ["Eye care", "Cataract surgery", "Glaucoma treatment"]
equipment: ["Phaco machine", "OCT scanner"]
procedure: ["Cataract surgery", "LASIK"]

# Trust signals:
# ✅ Eye care: CORROBORATED (description + capability + equipment)
# ✅ Cataract surgery: CORROBORATED (capability + procedure)
# ⚠️ Glaucoma treatment: CLAIMED_ONLY (capability only)
# ❓ ICU: UNKNOWN (not mentioned anywhere)
```

---

## Databricks Integrations

| Integration | Status | Purpose |
|-------------|--------|---------|
| **Streamlit App** | ✅ | UI layer deployed via Databricks Apps |
| **MLflow 3** | ✅ | Traces every trust scoring run + user actions |
| **Lakebase** | ✅ | Persists notes, overrides, shortlists, review flags |
| **SQL Warehouse** | ✅ | Schema creation via SQL statements |
| **Data Files** | ✅ | Parquet-based instant loading |

---

## Dataset

| Field | Coverage | Type | Trust Weight |
|-------|----------|------|--------------|
| description | 100% | Free text | High (1.0) |
| capability | 100% | JSON array | Medium (0.8) |
| procedure | 100% | JSON array | Medium (0.8) |
| equipment | 100% | JSON array | Medium (0.7) |
| specialties | 100% | JSON array | Supporting (0.6) |
| numberDoctors | 36.4% | Numeric | Low |
| capacity | 25.2% | Numeric | Low |

---

## Tech Stack

- **UI**: Streamlit 1.39+
- **Charts**: Plotly 5.18+
- **Data**: Pandas 2.0+
- **Persistence**: Lakebase (Postgres) via psycopg2
- **Tracing**: MLflow 3
- **Deployment**: Databricks Apps + CLI

---

## Project Structure

```
data-legend/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── app.yaml                     # Databricks App config
├── .streamlit/config.toml       # Theme configuration
├── data/
│   ├── facilities_scored.parquet   # Pre-scored facility data
│   ├── facilities.parquet          # Raw facility parquet
│   ├── facilities.csv              # Original CSV (1,889 rows)
│   ├── india_post_pin_directory.csv
│   └── nfhs5_district_health.xlsx
├── pipeline/
│   ├── trust_engine.py          # Core scoring + MLflow tracing
│   ├── geo_normalizer.py        # PIN → district mapping
│   └── desert_classifier.py     # District classification
├── app/
│   ├── main.py                  # Home page
│   ├── components/
│   │   ├── __init__.py
│   │   └── css.py               # Design system v4
│   ├── pages/
│   │   ├── 1_trust_desk.py      # Trust Desk
│   │   ├── 2_facility_detail.py # Facility Detail + actions
│   │   ├── 3_medical_desert.py  # Medical Desert map
│   │   └── 4_data_readiness.py  # Data Readiness dashboard
│   └── utils/
│       ├── data_loader.py       # Parquet-based loader
│       └── lakebase.py          # Postgres persistence layer
└── scripts/
    ├── create_tables.sql        # Lakebase schema
    ├── setup.sh                 # One-time setup
    └── deploy.sh                # Deployment script
```

---

## Demo Script (1 minute)

1. **Open** → Home page loads with clean KPI cards and narrative
2. **Trust Desk** → Select "ICU" + "Maharashtra" → ranked facilities
3. **Detail** → Click facility → field-by-field evidence citations
4. **Actions** → Override score, add note, shortlist, flag for review
5. **Medical Desert** → See state-level distribution + underserved ranking
6. **Data Readiness** → Trust donut, completeness bars, suspicious claims

---

## Team

Built for Databricks × Hack-Nation Challenge 04

---

## Acknowledgments

- Virtue Foundation for the dataset
- Databricks for the platform
- MIT Club of Northern California & Germany

---

## License

MIT License
