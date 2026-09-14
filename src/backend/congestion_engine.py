"""
Congestion scoring and berth assignment engine for Port Pulse.

Congestion Score (0-100) per terminal:
  - Berth utilization  (40 pts max)
  - Incoming vessel queue vs capacity (30 pts max)
  - Historical incident rate (15 pts max)
  - High-priority / hazmat vessel pressure (15 pts max)

Levels:
  0-30   LOW
  31-55  MEDIUM
  56-75  HIGH
  76-100 CRITICAL
"""
from datetime import datetime, timedelta
from data_loader import (
    get_berths_for_terminal, get_vessels_for_terminal,
    get_terminal_incident_count
)

TERMINALS = ["Terminal A", "Terminal B", "Terminal C"]

# Average crane moves to unload a full container ship per TEU
MOVES_PER_TEU = 2.1   # each TEU needs ~2.1 crane moves on avg


def _congestion_level(score: float) -> str:
    if score >= 76: return "CRITICAL"
    if score >= 56: return "HIGH"
    if score >= 31: return "MEDIUM"
    return "LOW"


def _recommended_action(level: str, terminal: str) -> str:
    actions = {
        "CRITICAL": f"Immediate diversion of incoming vessels from {terminal} — activate overflow protocol",
        "HIGH":     f"Restrict new arrivals to {terminal} — pre-position crane crews and yard tractors",
        "MEDIUM":   f"Monitor {terminal} closely — alert crane operators for extended shifts",
        "LOW":      f"{terminal} operating normally — continue standard scheduling",
    }
    return actions[level]


def _estimate_wait(incoming: int, available_berths: int, avg_turnaround_hours: float = 18.0) -> float:
    """Estimate queue wait time in hours."""
    if available_berths >= incoming:
        return 0.0
    queued = incoming - available_berths
    return round(queued * avg_turnaround_hours, 1)


def score_terminals(vessels: list[dict], berths: list[dict], incidents: list[dict]) -> list[dict]:
    results = []

    for terminal in TERMINALS:
        t_berths   = get_berths_for_terminal(terminal, berths)
        t_vessels  = get_vessels_for_terminal(terminal, vessels)
        inc_count  = get_terminal_incident_count(terminal, incidents)

        total_berths    = len(t_berths)
        occupied_berths = len([b for b in t_berths if b["status"] == "OCCUPIED"])
        maintenance     = len([b for b in t_berths if b["status"] == "MAINTENANCE"])
        avail_berths    = len([b for b in t_berths if b["status"] == "AVAILABLE"])
        incoming        = len(t_vessels)

        # effective available = available - maintenance
        effective_avail = max(avail_berths, 0)
        util_pct = (occupied_berths / total_berths * 100) if total_berths else 0

        # ── score components ────────────────────────────────────────────────
        factors = []

        # 1. Berth utilization (0-40)
        util_score = 0.0
        if util_pct >= 90:
            util_score = 40; factors.append(f"Berth utilization critical at {util_pct:.0f}%")
        elif util_pct >= 70:
            util_score = 25; factors.append(f"High berth utilization at {util_pct:.0f}%")
        elif util_pct >= 50:
            util_score = 12
        if maintenance > 0:
            util_score += 5; factors.append(f"{maintenance} berth(s) under maintenance")

        # 2. Incoming queue pressure (0-30)
        queue_score = 0.0
        queue_size  = max(0, incoming - effective_avail)
        if queue_size >= 4:
            queue_score = 30; factors.append(f"Severe queue: {queue_size} vessels cannot berth immediately")
        elif queue_size >= 2:
            queue_score = 18; factors.append(f"Moderate queue: {queue_size} vessels waiting")
        elif queue_size == 1:
            queue_score = 8;  factors.append(f"1 vessel queuing for berth")
        elif incoming > 0 and effective_avail > 0:
            queue_score = min(incoming * 3, 10)

        # 3. Historical incident rate (0-15)
        hist_score = 0.0
        if inc_count >= 6:
            hist_score = 15; factors.append(f"{inc_count} historical delay incidents — chronic congestion pattern")
        elif inc_count >= 3:
            hist_score = 8;  factors.append(f"{inc_count} historical delay incidents on record")

        # 4. High-priority / hazmat pressure (0-15)
        prio_score = 0.0
        high_prio  = len([v for v in t_vessels if v["priority"] == "HIGH"])
        hazmat     = len([v for v in t_vessels if v["hazmat"]])
        if high_prio >= 3:
            prio_score += 10; factors.append(f"{high_prio} HIGH-priority vessels arriving simultaneously")
        elif high_prio >= 1:
            prio_score += 5
        if hazmat:
            prio_score += 5; factors.append(f"{hazmat} hazmat vessel(s) requiring dedicated crane protocol")
        prio_score = min(prio_score, 15)

        total = min(round(util_score + queue_score + hist_score + prio_score, 1), 100)
        level = _congestion_level(total)
        wait  = _estimate_wait(incoming, effective_avail)

        results.append({
            "terminal":          terminal,
            "congestion_score":  total,
            "congestion_level":  level,
            "vessels_incoming":  incoming,
            "berths_available":  effective_avail,
            "berths_total":      total_berths,
            "utilization_pct":   round(util_pct, 1),
            "queue_size":        queue_size,
            "estimated_wait_hours": wait,
            "risk_factors":      factors if factors else ["No significant congestion factors"],
            "recommended_action": _recommended_action(level, terminal),
        })

    results.sort(key=lambda x: x["congestion_score"], reverse=True)
    return results


def assign_berths(vessels: list[dict], berths: list[dict]) -> list[dict]:
    """Greedy best-fit berth assignment for all incoming vessels."""
    assignments = []
    berth_state = {b["berth_id"]: dict(b) for b in berths}  # mutable copy

    # Sort: HIGH priority first, then by TEU descending
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    sorted_vessels = sorted(
        vessels,
        key=lambda v: (priority_order.get(v["priority"], 1), -v["teu_loaded"])
    )

    for v in sorted_vessels:
        terminal = v["destination_berth"]
        # Find available berths in the target terminal that fit the vessel
        candidates = [
            b for b in berth_state.values()
            if b["terminal"] == terminal
            and b["status"] == "AVAILABLE"
            and b["max_vessel_length_m"] >= v["length_m"]
            and b["max_teu"] >= v["teu_loaded"]
        ]

        # Alternate: look in other terminals if no candidate found
        alt_candidates = []
        if not candidates:
            alt_candidates = [
                b for b in berth_state.values()
                if b["terminal"] != terminal
                and b["status"] == "AVAILABLE"
                and b["max_vessel_length_m"] >= v["length_m"]
                and b["max_teu"] >= v["teu_loaded"]
            ]

        chosen     = candidates[0] if candidates else (alt_candidates[0] if alt_candidates else None)
        alternate  = alt_candidates[0] if (candidates and alt_candidates) else None

        eta_dt = datetime.fromisoformat(v["eta"])

        if chosen:
            cranes        = chosen["cranes_available"]
            moves_needed  = v["teu_loaded"] * MOVES_PER_TEU
            unload_hours  = round(moves_needed / (cranes * chosen["crane_moves_per_hour"]), 1)
            wait_hours    = 0.0
            start_dt      = eta_dt
            end_dt        = start_dt + timedelta(hours=unload_hours)

            # Mark berth occupied
            berth_state[chosen["berth_id"]]["status"] = "OCCUPIED"

            notes = "Direct berth assignment"
            if chosen["terminal"] != terminal:
                notes = f"Redirected from {terminal} — no available berths"
        else:
            # No berth available — estimate wait based on soonest free berth
            occupied_in_terminal = [
                b for b in berth_state.values()
                if b["terminal"] == terminal and b["status"] == "OCCUPIED"
            ]
            wait_hours    = 18.0
            cranes        = 3
            unload_hours  = round((v["teu_loaded"] * MOVES_PER_TEU) / (cranes * 25), 1)
            start_dt      = eta_dt + timedelta(hours=wait_hours)
            end_dt        = start_dt + timedelta(hours=unload_hours)
            chosen_id     = "QUEUED"
            notes         = f"No berth available — vessel will anchor and wait ~{wait_hours}h"

        assignments.append({
            "vessel_id":            v["vessel_id"],
            "vessel_name":          v["name"],
            "vessel_teu":           v["teu_loaded"],
            "assigned_berth":       chosen["berth_id"] if chosen else "QUEUED",
            "terminal":             chosen["terminal"] if chosen else terminal,
            "estimated_start":      start_dt.strftime("%Y-%m-%d %H:%M"),
            "estimated_completion": end_dt.strftime("%Y-%m-%d %H:%M"),
            "cranes_assigned":      chosen["cranes_available"] if chosen else 0,
            "unload_hours":         unload_hours,
            "wait_hours":           wait_hours,
            "alternate_berth":      alternate["berth_id"] if alternate else None,
            "notes":                notes,
        })

    return assignments
