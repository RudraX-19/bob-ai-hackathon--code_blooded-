"""
AIS connector — hybrid mode:
1. Seeds vessel_store instantly from live_seed.json (28 real Indian vessels)
2. Simulates live movement every 3 seconds (speed + heading → new lat/lon)
3. Layers real AISStream.io updates on top whenever they arrive
4. Filters vessels by active port bounding box
"""
import asyncio
import json
import math
import os
import time
import logging
from pathlib import Path
from typing import Optional
import websockets

logger = logging.getLogger("ais_connector")

AIS_API_KEY = os.getenv("AIS_API_KEY", "cc6f20924693147d5bd1a2b4e3c6a183d05340a9")
AIS_URL     = "wss://stream.aisstream.io/v0/stream"
DATA_DIR    = Path(__file__).parent.parent / "data"

# In-memory vessel store
vessel_store: dict[str, dict] = {}

# Callbacks for WebSocket broadcast
_callbacks: list = []

# Active port state
_active_port: str  = "JNPT"
_active_bbox: list = [[18.70, 72.70], [19.20, 73.20]]

_running = False
_sim_task: Optional[asyncio.Task] = None
_ais_task: Optional[asyncio.Task] = None


def register_callback(cb):
    _callbacks.append(cb)


def set_active_port(port_key: str, bbox: list):
    global _active_port, _active_bbox
    _active_port = port_key
    _active_bbox = bbox
    # Keep only vessels belonging to this port from seed
    to_remove = [m for m, v in vessel_store.items() if v.get("port", "") != port_key]
    for m in to_remove:
        vessel_store.pop(m, None)
    _load_seed_for_port(port_key)
    logger.info(f"Switched to port: {port_key} — {len(vessel_store)} vessels loaded")


def _load_seed_for_port(port_key: str):
    """Load seeded vessels for the given port instantly."""
    seed_file = DATA_DIR / "live_seed.json"
    if not seed_file.exists():
        return
    try:
        seeds = json.loads(seed_file.read_text(encoding="utf-8"))
        now = time.time()
        for v in seeds:
            if v.get("port", "").upper() == port_key.upper():
                v["last_seen"] = now
                vessel_store[v["mmsi"]] = dict(v)
    except Exception as e:
        logger.warning(f"Seed load error: {e}")


def get_vessels() -> list[dict]:
    now = time.time()
    return [v for v in vessel_store.values() if now - v.get("last_seen", 0) < 900]


def _move_vessel(v: dict) -> dict:
    """Advance vessel position based on speed and heading."""
    speed   = v.get("speed", 0)       # knots
    heading = v.get("heading", 0)     # degrees
    if speed < 0.3:
        return v                       # anchored — don't move

    # 3-second tick: distance in km
    dist_km = (speed * 1.852) * (3 / 3600)

    lat = v["lat"]
    lon = v["lon"]
    head_rad = math.radians(heading)

    # Approximate movement
    dlat = (dist_km / 111.0) * math.cos(head_rad)
    dlon = (dist_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(head_rad)

    new_lat = lat + dlat
    new_lon = lon + dlon

    # Bounce back toward port if vessel drifts too far from bbox centre
    bbox = _active_bbox
    lat_mid = (bbox[0][0] + bbox[1][0]) / 2
    lon_mid = (bbox[0][1] + bbox[1][1]) / 2
    lat_range = abs(bbox[1][0] - bbox[0][0]) * 0.6
    lon_range = abs(bbox[1][1] - bbox[0][1]) * 0.6

    if abs(new_lat - lat_mid) > lat_range:
        new_lat = lat_mid + (lat_mid - new_lat) * 0.1
        v["heading"] = (heading + 180) % 360
    if abs(new_lon - lon_mid) > lon_range:
        new_lon = lon_mid + (lon_mid - new_lon) * 0.1
        v["heading"] = (heading + 180) % 360

    v["lat"] = round(new_lat, 6)
    v["lon"] = round(new_lon, 6)
    v["last_seen"] = time.time()
    return v


async def _simulation_loop():
    """Tick every 3 seconds — move vessels and broadcast updates."""
    while _running:
        await asyncio.sleep(3)
        for mmsi, v in list(vessel_store.items()):
            if v.get("speed", 0) >= 0.3:
                vessel_store[mmsi] = _move_vessel(v)
                for cb in _callbacks:
                    try:
                        await cb(dict(vessel_store[mmsi]))
                    except Exception:
                        pass


async def _ais_stream_loop():
    """Connect to AISStream and layer real updates on top."""
    while _running:
        try:
            async with websockets.connect(AIS_URL, ping_interval=30, ping_timeout=20) as ws:
                payload = {
                    "APIKey":       AIS_API_KEY,
                    "BoundingBoxes": [_active_bbox],
                    "FilterMessageTypes": ["PositionReport"]
                }
                await ws.send(json.dumps(payload))
                logger.info(f"AISStream connected for {_active_port}")
                async for raw_msg in ws:
                    if not _running:
                        break
                    try:
                        data   = json.loads(raw_msg)
                        mtype  = data.get("MessageType", "")
                        meta   = data.get("MetaData", {})
                        mmsi   = str(meta.get("MMSI", ""))
                        if mtype == "PositionReport" and mmsi:
                            pos = data.get("Message", {}).get("PositionReport", {})
                            lat = pos.get("Latitude", 0)
                            lon = pos.get("Longitude", 0)
                            if lat == 0 and lon == 0:
                                continue
                            existing = vessel_store.get(mmsi, {})
                            updated  = {
                                **existing,
                                "mmsi":      mmsi,
                                "name":      str(meta.get("ShipName", existing.get("name", f"Vessel-{mmsi[-4:]}"))).strip(),
                                "lat":       lat,
                                "lon":       lon,
                                "speed":     pos.get("Sog", 0),
                                "heading":   pos.get("TrueHeading", pos.get("Cog", 0)),
                                "last_seen": time.time(),
                                "port":      _active_port,
                                "source":    "live",
                            }
                            vessel_store[mmsi] = updated
                            for cb in _callbacks:
                                try:
                                    await cb(dict(updated))
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"AISStream error: {e} — retrying in 10s")
            await asyncio.sleep(10)


async def start_ais_stream():
    global _running, _sim_task, _ais_task
    _running = True
    _load_seed_for_port(_active_port)
    if _sim_task is None or _sim_task.done():
        _sim_task = asyncio.create_task(_simulation_loop())
    if _ais_task is None or _ais_task.done():
        _ais_task = asyncio.create_task(_ais_stream_loop())


async def stop_ais_stream():
    global _running
    _running = False
    for t in [_sim_task, _ais_task]:
        if t:
            t.cancel()
