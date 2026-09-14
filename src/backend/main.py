"""
Port Pulse — FastAPI backend
Run: uvicorn main:app --reload --port 8000
"""
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent))
from data_loader import load_vessels, load_berths, load_incidents
from congestion_engine import score_terminals, assign_berths
from watsonx_client import generate_ops_plan
from models import OperationsPlan

app = FastAPI(
    title="Port Pulse — Container Congestion Predictor API",
    description="L1 Hackathon Solution — IBM Bob AI Innovation Hackathon 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    index = Path(__file__).parent.parent / "frontend" / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Port Pulse API running. Visit /docs"}


@app.get("/api/vessels", summary="Get all incoming vessel schedules")
async def get_vessels():
    return load_vessels()


@app.get("/api/berths", summary="Get all berth status and capacity")
async def get_berths():
    return load_berths()


@app.get("/api/congestion", summary="Predict congestion hotspots per terminal")
async def get_congestion():
    """Scores each terminal 0-100 for congestion risk. Returns terminals ranked highest first."""
    vessels   = load_vessels()
    berths    = load_berths()
    incidents = load_incidents()
    return score_terminals(vessels, berths, incidents)


@app.get("/api/assignments", summary="Get optimised berth assignments for all vessels")
async def get_assignments():
    """Returns best-fit berth assignment for every incoming vessel."""
    vessels = load_vessels()
    berths  = load_berths()
    return assign_berths(vessels, berths)


@app.get("/api/plan", summary="Generate 72-hour port operations plan")
async def get_ops_plan():
    """Calls IBM watsonx.ai (or mock) to generate a 72-hour port operations plan."""
    vessels   = load_vessels()
    berths    = load_berths()
    incidents = load_incidents()
    hotspots    = score_terminals(vessels, berths, incidents)
    assignments = assign_berths(vessels, berths)
    plan_text   = generate_ops_plan(hotspots, assignments)
    critical = [h for h in hotspots if h["congestion_level"] in ("CRITICAL", "HIGH")]
    return OperationsPlan(
        generated_at=datetime.now().isoformat(),
        planning_window_hours=72,
        total_vessels=len(vessels),
        congested_terminals=len(critical),
        plan_text=plan_text,
        congestion_hotspots=hotspots,
        berth_assignments=assignments,
    )


@app.get("/api/health", summary="Health check")
async def health():
    mock = os.getenv("MOCK_MODE", "true").lower() == "true"
    return {
        "status": "healthy",
        "service": "Port Pulse",
        "watsonx_mode": "mock" if mock else "live",
        "timestamp": datetime.now().isoformat(),
    }
