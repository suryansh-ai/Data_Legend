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

# --- API Routes (registered FIRST, before catch-all) ---
app.include_router(facilities.router, prefix="/api")
app.include_router(trust.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(persistence.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health")
def health_check():
    from server.data_loader import get_data_source_info
    return get_data_source_info()


# --- Serve React build ---
DIST_DIR = Path(__file__).parent / "client" / "dist"

if DIST_DIR.exists():
    # Mount static assets (CSS, JS, images)
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="static-assets")

    # Catch-all: serve React for non-API, non-asset routes
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        # Skip API routes (shouldn't reach here, but safety check)
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Try to serve the file from dist
        file_path = DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Default: serve React index.html (SPA routing)
        return FileResponse(str(DIST_DIR / "index.html"))
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
