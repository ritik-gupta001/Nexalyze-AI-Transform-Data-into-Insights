from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import os

from app.core.config import get_settings, create_directories
from app.core.logger import log
from app.api import routes_health, routes_tasks
from app.db.base import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    log.info("Starting PRA - Personal Research Agent...")
    create_directories()
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    log.info("Database initialized")
    
    yield
    
    # Shutdown
    log.info("Shutting down...")


# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Multi-Agent AI System for Research & Automation",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Mount reports and charts directories for downloads
from pathlib import Path

# Use absolute paths for Docker/production compatibility
reports_dir = Path("./app/reports").resolve()
charts_dir = Path("./app/charts").resolve()

# Ensure directories exist
reports_dir.mkdir(parents=True, exist_ok=True)
charts_dir.mkdir(parents=True, exist_ok=True)

app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")
app.mount("/charts", StaticFiles(directory=str(charts_dir)), name="charts")


# Root endpoint - Serve Web UI
@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """Serve the web interface"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


# Download endpoints with proper headers
@app.get("/download/report/{filename}", tags=["Downloads"])
async def download_report(filename: str):
    """Download report file with proper headers"""
    file_path = reports_dir / filename
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    return {"error": "File not found"}


@app.get("/download/chart/{filename}", tags=["Downloads"])
async def download_chart(filename: str):
    """Download chart file with proper headers"""
    file_path = charts_dir / filename
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    return {"error": "File not found"}


# Include routers
app.include_router(routes_health.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_tasks.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False  # Disabled reload to avoid multiprocessing issues
    )
