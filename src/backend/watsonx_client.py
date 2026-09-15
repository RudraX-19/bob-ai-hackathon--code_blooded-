"""watsonx.ai client for Port Pulse — generates 72-hour ops plan."""
import os
from datetime import datetime

MOCK_MODE          = os.getenv("MOCK_MODE", "true").lower() == "true"
WATSONX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")


def _build_prompt(hotspots: list[dict], assignments: list[dict]) -> str:
    critical = [h for h in hotspots if h["congestion_level"] == "CRITICAL"]
    high     = [h for h in hotspots if h["congestion_level"] == "HIGH"]
    queued   = [a for a in assignments if a.get("assigned_berth") == "QUEUED"]

    summary = ""
    for h in hotspots:
        summary += (
            f"\n  {h['terminal']}: {h['congestion_level']} ({h['congestion_score']}/100) — "
            f"{h['vessels_incoming']} incoming, {h['berths_available']} berths free, "
            f"queue: {h['queue_size']} vessels, wait: {h['estimated_wait_hours']}h\n"
        )
        
    vessel_data = ""
    for a in assignments[:15]: # Show top 15 allocations
        vessel_data += f"- {a['vessel_name']} ({a.get('vessel_type', 'Ship')}): Route -> {a.get('routing_strategy', 'Standard')} | {a.get('assigned_berth')} with {a.get('assigned_cranes', 2)} cranes\n"

    return f"""You are a port operations planning expert.
Generate a structured 72-hour port operations plan based on this congestion analysis and proposed routing/resource allocations.

CONGESTION SUMMARY:
- Critical terminals: {len(critical)}
- High congestion terminals: {len(high)}
- Total incoming vessels: {len(assignments)}

TERMINAL STATUS:
{summary}
PROPOSED ROUTING & RESOURCE ALLOCATIONS (Sample):
{vessel_data}
Generate a clear 72-hour plan covering:
1. Immediate actions (0-24 hours) for critical terminals
2. Berth and crane optimization (24-48 hours) validating the proposed cranes/berths
3. Alternate routing recommendations validating the proposed route diversions
4. Crew and equipment pre-positioning
"""


def _mock_plan(hotspots: list[dict], assignments: list[dict]) -> str:
    critical = [h for h in hotspots if h["congestion_level"] == "CRITICAL"]
    high     = [h for h in hotspots if h["congestion_level"] == "HIGH"]
    queued   = [a for a in assignments if a["assigned_berth"] == "QUEUED"]
    total_vessels = len(assignments)
    sep  = "=" * 62
    sep2 = "-" * 44

    lines = [
        sep,
        "   PORT PULSE - 72-HOUR PORT OPERATIONS PLAN",
        f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        sep,
        "",
        "EXECUTIVE SUMMARY",
        "-" * 17,
        f"* Total incoming vessels: {total_vessels}",
        f"* Critical congestion terminals: {len(critical)}",
        f"* High congestion terminals: {len(high)}",
        f"* Vessels queued (no berth): {len(queued)}",
        f"* Estimated port-wide delay risk: {'SEVERE' if len(critical) > 0 else 'MODERATE'}",
        "",
        sep2,
        "PHASE 1 - IMMEDIATE ACTIONS (0-24 HOURS)",
        sep2,
    ]

    for h in [x for x in hotspots if x["congestion_level"] in ("CRITICAL", "HIGH")]:
        lines += [
            "",
            f">> {h['terminal']} - {h['congestion_level']} ({h['congestion_score']}/100)",
            f"   - {h['recommended_action']}",
            f"   - {h['vessels_incoming']} vessels incoming, {h['berths_available']} berths free",
            f"   - Estimated queue wait: {h['estimated_wait_hours']} hours",
        ]
        for f in h["risk_factors"]:
            lines.append(f"   - Risk: {f}")

    lines += [
        "",
        sep2,
        "PHASE 2 - BERTH & CRANE OPTIMIZATION (24-48 HOURS)",
        sep2,
        "",
        ">> Berth Assignment Summary",
    ]
    for a in assignments[:6]:
        berth_val = a.get("assigned_berth", "LIVE")
        status = "QUEUED - WAITING" if berth_val == "QUEUED" else f"Berth {berth_val}"
        start  = a.get("estimated_start", "Live tracking")
        unload = a.get("unload_hours", "—")
        teu    = a.get("vessel_teu", 0)
        lines.append(
            f"   - {a['vessel_name']} ({teu:,} TEU) -> {status} | "
            f"Start: {start} | Unload: {unload}h"
        )

    lines += [
        "",
        sep2,
        "PHASE 3 - ALTERNATE ROUTING (48-72 HOURS)",
        sep2,
        "",
    ]
    if queued:
        for a in queued:
            lines.append(f"   - Redirect {a['vessel_name']} to nearest uncongested terminal")
        lines.append("   - Coordinate with shipping agents for revised ETAs")
    else:
        lines.append("   - No diversions required — all vessels have berth assignments")

    lines += [
        "",
        "-" * 30,
        "CREW & EQUIPMENT PRE-POSITIONING",
        "-" * 30,
        "* Deploy extra crane operators to highest congestion terminal",
        "* Pre-position yard tractors for rapid container transfer",
        "* Activate overflow yard storage for peak TEU volume",
        "* Brief customs and documentation team for accelerated clearance",
        "",
        "-" * 38,
        "NOTE: Powered by IBM Bob + watsonx.ai",
        "-" * 38,
    ]

    return "\n".join(lines)


def generate_ops_plan(hotspots: list[dict], assignments: list[dict]) -> str:
    if MOCK_MODE or not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        return _mock_plan(hotspots, assignments)
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_API_KEY)
        model = ModelInference(
            model_id="meta-llama/llama-3-3-70b-instruct",
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params={"decoding_method": "greedy", "max_new_tokens": 1200, "temperature": 0.7}
        )
        response = model.generate_text(prompt=_build_prompt(hotspots, assignments))
        return response if response else _mock_plan(hotspots, assignments)
    except Exception as e:
        print(f"[watsonx] Error: {e} — falling back to mock plan")
        return _mock_plan(hotspots, assignments)
