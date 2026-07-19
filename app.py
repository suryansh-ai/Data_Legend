"""
Data Legend — FastAPI Backend
Serves React frontend + API endpoints for healthcare facility intelligence.
Three-layer data architecture: Parquet + SQL Warehouse + Lakebase.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from server.routes import facilities, trust, search, persistence, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize all data sources."""
    from server.data_loader import load_facilities
    from server.sql_connector import init_warehouse
    from server.lakebase import db

    load_facilities()
    wh_ok = init_warehouse()
    print(f"[startup] SQL Warehouse: {'connected' if wh_ok else 'unavailable (using parquet)'}")
    print(f"[startup] Persistence: {db.get_backend()}")
    print(f"[startup] Facilities loaded: {len(load_facilities())} records")

    yield

    try:
        from server.sql_connector import _connection
        if _connection:
            _connection.close()
    except Exception:
        pass
    try:
        if db.connection:
            db.connection.close()
    except Exception:
        pass


app = FastAPI(
    title="Data Legend",
    description="Healthcare Facility Intelligence Platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routes ---
app.include_router(facilities.router, prefix="/api")
app.include_router(trust.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(persistence.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health")
def health_check():
    from server.data_loader import get_data_source_info
    return get_data_source_info()


# --- Serve React SPA ---
DIST_DIR = Path(__file__).parent / "client" / "dist"

if DIST_DIR.exists():
    # Mount static assets at /assets/*
    ASSETS_DIR = DIST_DIR / "assets"
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="static-assets")

    # Serve favicon and other root files
    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(str(DIST_DIR / "favicon.svg"))

    # SPA catch-all: only for non-API, non-asset requests
    class SPAFilterMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            path = request.url.path

            # Let API routes through normally
            if path.startswith("/api/"):
                return await call_next(request)

            # Let static assets through
            if path.startswith("/assets/"):
                return await call_next(request)

            # For everything else, try to serve the file, fallback to index.html
            file_path = DIST_DIR / path.lstrip("/")
            if file_path.is_file():
                return FileResponse(str(file_path))

            # SPA fallback: serve index.html for client-side routing
            return FileResponse(str(DIST_DIR / "index.html"))

    app.add_middleware(SPAFilterMiddleware)

else:
    @app.get("/")
    async def root():
        return {
            "message": "Data Legend API",
            "docs": "/docs",
            "note": "React build not found. Run 'npm run build' in client/.",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DATABRICKS_APP_PORT", os.getenv("PORT", "8080")))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
