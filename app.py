"""
Data Legend — FastAPI Backend
Serves React frontend + API endpoints for healthcare facility intelligence.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.routes import facilities, trust, search, persistence, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    from server.data_loader import load_facilities
    load_facilities()  # Pre-load on startup
    yield


app = FastAPI(
    title="Data Legend",
    description="Healthcare Facility Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(facilities.router, prefix="/api")
app.include_router(trust.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(persistence.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

# Serve React build
DIST_DIR = Path(__file__).parent / "client" / "dist"

if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        file_path = DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(DIST_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "Data Legend API",
            "docs": "/docs",
            "note": "React build not found. Run 'npm run build' in client/ directory.",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DATABRICKS_APP_PORT", os.getenv("PORT", "8080")))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
