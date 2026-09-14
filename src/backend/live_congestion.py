"""
Live congestion scoring based on real AIS vessel data.
Scores each terminal of the active port using vessel density,
speed (anchored vs moving), and count near port area.
"""
import math


def _distance_km(lat1, lon1, lat2, lon2) -> float:
    """Haversine distance in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def score_live_terminals(vessels: list[dict], port: dict) -> list[dict]:
    """
    Score each terminal of the given port based on live vessel data.
    """
    port_lat = port["lat"]
    port_lon = port["lon"]
    terminals = port["terminals"]

    # Classify vessels by proximity to port center
    near_vessels  = [v for v in vessels if _distance_km(port_lat, port_lon, v.get("lat", 0), v.get("lon", 0)) <= 15]
    anchored      = [v for v in near_vessels if v.get("speed", 0) <= 0.5]
    slow_moving   = [v for v in near_vessels if 0.5 < v.get("speed", 0) <= 3]
    approaching   = [v for v in near_vessels if v.get("speed", 0) > 3]

    total_near = len(near_vessels)
    anchored_count = len(anchored)

    results = []
    num_terminals = len(terminals)

    for i, terminal in enumerate(terminals):
        # Distribute vessels across terminals proportionally
        t_vessels = near_vessels[i::num_terminals]  # round-robin split
        t_anchored = [v for v in t_vessels if v.get("speed", 0) <= 0.5]
        t_approaching = [v for v in t_vessels if v.get("speed", 0) > 0.5]

        factors = []

        # Density score (0-40): based on vessels near terminal
        density_score = min(len(t_vessels) * 6, 40)
        if len(t_vessels) >= 6:
            factors.append(f"{len(t_vessels)} vessels detected near terminal")
        elif len(t_vessels) >= 3:
            factors.append(f"{len(t_vessels)} vessels in terminal zone")

        # Anchored score (0-30): anchored = waiting = congestion signal
        anchor_score = min(len(t_anchored) * 8, 30)
        if len(t_anchored) >= 3:
            factors.append(f"{len(t_anchored)} vessels anchored/waiting")
        elif len(t_anchored) >= 1:
            factors.append(f"{len(t_anchored)} vessel(s) at anchor")

        # Approach score (0-20): vessels currently moving toward port
        approach_score = min(len(t_approaching) * 5, 20)
        if len(t_approaching) >= 2:
            factors.append(f"{len(t_approaching)} vessels currently approaching")

        # Port-wide pressure bonus (0-10)
        pressure_score = min(anchored_count * 2, 10)
        if anchored_count >= 4:
            factors.append(f"Port-wide anchor queue: {anchored_count} vessels")

        total = min(round(density_score + anchor_score + approach_score + pressure_score, 1), 100)

        # Level
        if total >= 76:   level = "CRITICAL"
        elif total >= 56: level = "HIGH"
        elif total >= 31: level = "MEDIUM"
        else:             level = "LOW"

        # Recommended action
        actions = {
            "CRITICAL": f"Halt new vessel entry to {terminal} — divert to alternate terminal immediately",
            "HIGH":     f"Restrict arrivals to {terminal} — deploy additional crane operators",
            "MEDIUM":   f"Monitor {terminal} — alert berth planners for increased vessel activity",
            "LOW":      f"{terminal} operating normally",
        }

        # Estimate wait
        queue = max(0, len(t_anchored) - 1)
        wait_hours = round(queue * 18.0, 1)

        results.append({
            "terminal":             terminal,
            "congestion_score":     total,
            "congestion_level":     level,
            "vessels_incoming":     len(t_vessels),
            "vessels_anchored":     len(t_anchored),
            "vessels_approaching":  len(t_approaching),
            "berths_available":     max(0, 2 - len(t_anchored)),
            "berths_total":         2,
            "utilization_pct":      min(100, round(len(t_anchored) / 2 * 100, 1)),
            "queue_size":           queue,
            "estimated_wait_hours": wait_hours,
            "risk_factors":         factors if factors else ["No significant congestion detected"],
            "recommended_action":   actions[level],
        })

    results.sort(key=lambda x: x["congestion_score"], reverse=True)
    return results
