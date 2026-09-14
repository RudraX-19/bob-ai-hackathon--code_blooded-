"""Pydantic models for Port Pulse API."""
from pydantic import BaseModel
from typing import List, Optional


class VesselSchedule(BaseModel):
    vessel_id: str
    name: str
    type: str
    flag: str
    length_m: float
    teu_capacity: int
    teu_loaded: int
    eta: str
    destination_berth: str
    origin_port: str
    priority: str
    hazmat: bool
    reefer_units: int
    status: str


class Berth(BaseModel):
    berth_id: str
    terminal: str
    max_vessel_length_m: float
    max_teu: int
    cranes_available: int
    crane_moves_per_hour: int
    current_vessel: Optional[str]
    occupied_until: Optional[str]
    water_depth_m: float
    status: str


class CongestionResult(BaseModel):
    terminal: str
    congestion_score: float        # 0-100
    congestion_level: str          # LOW / MEDIUM / HIGH / CRITICAL
    vessels_incoming: int
    berths_available: int
    berths_total: int
    utilization_pct: float
    queue_size: int                # vessels that can't berth immediately
    estimated_wait_hours: float
    risk_factors: List[str]
    recommended_action: str


class BerthAssignment(BaseModel):
    vessel_id: str
    vessel_name: str
    vessel_teu: int
    assigned_berth: str
    terminal: str
    estimated_start: str
    estimated_completion: str
    cranes_assigned: int
    unload_hours: float
    wait_hours: float
    alternate_berth: Optional[str]
    notes: str


class OperationsPlan(BaseModel):
    generated_at: str
    planning_window_hours: int
    total_vessels: int
    congested_terminals: int
    plan_text: str
    congestion_hotspots: List[CongestionResult]
    berth_assignments: List[BerthAssignment]
