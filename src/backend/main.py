"""
Port Pulse — Real-Time FastAPI backend
Supports:
  - Live AIS vessel tracking via AISStream.io
  - WebSocket broadcast to frontend
  - Indian port selection
  - Congestion scoring on live data
  - watsonx.ai operations plan generation
"""
import os
import sys
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Set

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent))

from indian_ports import INDIAN_PORTS
from ais_connector import (
    start_ais_stream, stop_ais_stream, set_active_port,
    get_vessels, register_callback, vessel_store
)
from live_congestion import score_live_terminals
from watsonx_client import generate_ops_plan

app = FastAPI(
    title="Port Pulse — Real-Time Indian Port Monitor",
    description="L1 Hackathon Solution — IBM Bob AI Innovation Hackathon 2026",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Connected WebSocket clients
ws_clients: Set[WebSocket] = set()

# Current active port
_current_port_key = "JNPT"


async def broadcast_vessel(vessel: dict):
    """Broadcast a vessel update to all connected WebSocket clients."""
    msg = json.dumps({"type": "vessel_update", "data": vessel})
    dead = set()
    for ws in ws_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.add(ws)
    ws_clients.difference_update(dead)


# Register our broadcast callback with the AIS connector
register_callback(broadcast_vessel)


@app.on_event("startup")
async def startup():
    port = INDIAN_PORTS.get(_current_port_key, INDIAN_PORTS["JNPT"])
    set_active_port(_current_port_key, port["bbox"])
    await start_ais_stream()


@app.on_event("shutdown")
async def shutdown():
    await stop_ais_stream()


# ── REST endpoints ────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    index = Path(__file__).parent.parent / "frontend" / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Port Pulse API v2 running. Visit /docs"}


@app.get("/api/ports", summary="List all supported Indian ports")
async def list_ports():
    return [
        {
            "key":      k,
            "name":     v["name"],
            "city":     v["city"],
            "lat":      v["lat"],
            "lon":      v["lon"],
            "annual_teu": v["annual_teu"],
            "terminals": v["terminals"],
        }
        for k, v in INDIAN_PORTS.items()
    ]


@app.post("/api/ports/{port_key}", summary="Switch active port")
async def switch_port(port_key: str):
    global _current_port_key
    port_key = port_key.upper()
    if port_key not in INDIAN_PORTS:
        return {"error": f"Unknown port: {port_key}"}
    port = INDIAN_PORTS[port_key]
    _current_port_key = port_key
    set_active_port(port_key, port["bbox"])
    # Restart stream with new bbox
    await stop_ais_stream()
    await asyncio.sleep(1)
    await start_ais_stream()
    # Notify all clients
    msg = json.dumps({"type": "port_switched", "data": {"port_key": port_key, "port": port}})
    for ws in ws_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            pass
    return {"status": "switched", "port": port}


@app.get("/api/vessels", summary="Get all live vessels for active port")
async def get_live_vessels():
    return get_vessels()


@app.get("/api/vessels/count", summary="Get vessel count")
async def vessel_count():
    vessels = get_vessels()
    moving   = [v for v in vessels if v.get("speed", 0) > 0.5]
    anchored = [v for v in vessels if v.get("speed", 0) <= 0.5]
    return {
        "total":    len(vessels),
        "moving":   len(moving),
        "anchored": len(anchored),
        "port":     _current_port_key,
    }


@app.get("/api/congestion", summary="Live congestion scoring for active port")
async def live_congestion():
    vessels = get_vessels()
    port    = INDIAN_PORTS.get(_current_port_key, INDIAN_PORTS["JNPT"])
    return score_live_terminals(vessels, port)


@app.get("/api/plan", summary="Generate AI 72-hour operations plan")
async def get_plan():
    vessels  = get_vessels()
    port     = INDIAN_PORTS.get(_current_port_key, INDIAN_PORTS["JNPT"])
    hotspots = score_live_terminals(vessels, port)
    # Build simple assignment list for plan generator
    assignments = [
        {
            "vessel_id":   v["mmsi"],
            "vessel_name": v.get("name", "Unknown"),
            "vessel_teu":  0,
            "assigned_berth": "LIVE",
            "notes": f"Speed: {v.get('speed',0)} kn"
        }
        for v in vessels
    ]
    plan_text = generate_ops_plan(hotspots, assignments)
    return {
        "generated_at":       datetime.now().isoformat(),
        "port":               port["name"],
        "total_vessels":      len(vessels),
        "plan_text":          plan_text,
        "congestion_hotspots": hotspots,
    }


@app.get("/api/health", summary="Health check")
async def health():
    mock = os.getenv("MOCK_MODE", "true").lower() == "true"
    return {
        "status":         "healthy",
        "service":        "Port Pulse v2 (Real-Time)",
        "watsonx_mode":   "mock" if mock else "live",
        "active_port":    _current_port_key,
        "live_vessels":   len(get_vessels()),
        "ws_clients":     len(ws_clients),
        "timestamp":      datetime.now().isoformat(),
    }


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    try:
        # Send current vessel snapshot immediately on connect
        vessels = get_vessels()
        await websocket.send_text(json.dumps({
            "type": "snapshot",
            "data": vessels,
            "port": _current_port_key,
        }))
        # Keep alive — listen for ping/port-switch messages from client
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                data = json.loads(msg)
                if data.get("type") == "switch_port":
                    pk = data.get("port_key", "JNPT").upper()
                    if pk in INDIAN_PORTS:
                        await switch_port(pk)
            except asyncio.TimeoutError:
                # Send heartbeat with latest vessel count
                await websocket.send_text(json.dumps({
                    "type":    "heartbeat",
                    "vessels": len(get_vessels()),
                    "port":    _current_port_key,
                    "ts":      int(time.time()),
                }))
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(websocket)
