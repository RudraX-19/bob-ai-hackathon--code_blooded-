# Solution Overview — Port Pulse

## Core Mechanism
Port Pulse is a **congestion-aware, AI-explained berth planning system** for container port operators.

Instead of showing raw berth occupancy tables, it:
1. **Fuses** vessel schedules, berth capacity, and historical delay records into a 0–100 congestion score per terminal
2. **Assigns** every incoming vessel to the best available berth automatically — respecting vessel length, TEU capacity, water depth, and hazmat constraints
3. **Explains** every congestion score in plain language
4. **Acts** by generating a structured 72-hour operations plan via IBM watsonx.ai

## What Makes It Different

### vs. Manual Spreadsheet Scheduling
Spreadsheets show current state. Port Pulse shows **future state** — it calculates which terminal will overflow 12–24 hours from now based on incoming vessel ETAs vs. available berths.

### vs. Single-Metric Dashboards
Most port management systems show one metric (berth occupancy %). Port Pulse fuses four factors into a compound risk score, catching situations like: "berths are 60% occupied but 5 HIGH-priority vessels arrive in the next 4 hours" — invisible to a single-metric system.

### vs. Manual Berth Assignment
Planners manually match vessel dimensions to berth capacity. Port Pulse's assignment engine enforces vessel length, TEU capacity, water depth, and hazmat constraints automatically, with an alternate terminal fallback when the primary terminal is full.

## Scoring Model

```
Congestion Score (0-100) = Berth Utilization    (0-40 pts)
                         + Queue Pressure        (0-30 pts)
                         + Historical Incidents  (0-15 pts)
                         + Priority Vessel Load  (0-15 pts)
```

| Component | Weight | Key Signals |
|---|---|---|
| Berth Utilization | 40 pts | % of berths occupied, maintenance downtime |
| Queue Pressure | 30 pts | Incoming vessels vs available berths |
| Historical Incidents | 15 pts | Count of prior delay incidents per terminal |
| Priority Vessel Load | 15 pts | HIGH-priority arrivals, hazmat vessels |

## Berth Assignment Engine
The greedy best-fit algorithm:
1. Sorts vessels by priority (HIGH first) then TEU size (largest first)
2. For each vessel, finds available berths in the target terminal that fit length + TEU + depth constraints
3. If no berth in target terminal → searches alternate terminals
4. If no berth anywhere → marks vessel as QUEUED with estimated wait time
5. Marks assigned berths as occupied to prevent double-booking

## IBM Bob & watsonx.ai Integration
IBM Bob was the **primary development partner** used throughout the entire build:
- Generated the congestion scoring engine from natural language spec
- Wrote the FastAPI backend and berth assignment algorithm
- Created all Pydantic models and API endpoint structure
- Reviewed and refactored all code for quality

IBM watsonx.ai (Granite 13B Instruct) generates at runtime:
- A structured 72-hour operations plan with Phase 1/2/3 sections
- Crew pre-positioning recommendations
- Alternate routing instructions for queued vessels
- Equipment pre-loading checklist for crane teams

## User Experience Flow
1. Supervisor opens dashboard → sees terminal congestion cards with live scores
2. Reviews berth assignment table → sees which vessels need redirecting
3. Clicks "Generate 72-Hour Plan" → AI plan ready in seconds with actionable steps
4. Shares plan with crane operators and vessel agents — no technical translation needed
