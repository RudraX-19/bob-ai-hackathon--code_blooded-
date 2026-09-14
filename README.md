# Port Pulse 🚢
### AI-Powered Container Congestion Predictor & Port Operations Optimiser
**IBM Bob AI Innovation Hackathon 2026 — Problem Statement L1**

---

## Team — Code Blooded
| Role | Name | Email |
|---|---|---|
| Team Lead | Rudra Vaghasiya | rudravaghasiya.ce@gmail.com |
| Member 2  | MEMBER_NAME | EMAIL |
| Member 3  | MEMBER_NAME | EMAIL |
| Member 4  | MEMBER_NAME | EMAIL |

**Track:** AI &nbsp;|&nbsp; **Problem:** L1 — Logistics: Container Congestion Predictor & Port Operations Optimiser

---

## Problem Statement
The 2021 LA/Long Beach port backlog had **100+ ships waiting offshore for weeks**, costing global supply chains **$10B+**. Port operators today allocate berths, cranes, and yard space using **manual spreadsheets**. Congestion hotspots are identified only **after vessels are already queuing** — alternate routing decisions come too late to help.

---

## Solution
**Port Pulse** is an AI-powered web dashboard that:
1. **Predicts** congestion hotspots using vessel schedules and berth capacity data
2. **Assigns** vessels to optimal berths automatically with alternate routing fallback
3. **Generates** a natural-language 72-hour port operations plan via **IBM watsonx.ai**

---

## Key Features
- 🚢 **Multi-factor congestion scoring** — berth utilization (40 pts) + queue pressure (30 pts) + incident history (15 pts) + priority vessels (15 pts)
- 🏗️ **Auto berth assignment** — best-fit algorithm with hazmat and TEU constraints, alternate terminal fallback
- 🤖 **AI Operations Plan** — IBM watsonx.ai Granite generates structured 72-hour plan with crew pre-positioning
- 📊 **Live dashboard** — terminal congestion cards, vessel schedule table, berth assignment table, charts
- ⚠️ **Hazmat detection** — flags dangerous cargo vessels requiring dedicated crane protocol
- 🔌 **REST API** — FastAPI backend, fully documented at `/docs`

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI | IBM watsonx.ai (Granite 13B Instruct) |
| Frontend | HTML5, CSS3, Chart.js |
| Data | JSON + CSV (vessel schedules, berth capacity, incidents) |
| Dev Partner | IBM Bob IDE |

---

## How to Run
```bash
cd src
pip install -r requirements.txt
cp .env.example .env
cd backend
uvicorn main:app --reload --port 8000
```
Open **http://localhost:8000**

Full instructions: [`docs/setup-guide.md`](docs/setup-guide.md)

---

## Demo
- 📹 Video: [demo/demo-video-link.txt](demo/demo-video-link.txt)
- 🌐 Live Demo: [demo/live-demo-url.txt](demo/live-demo-url.txt)
- 📸 Screenshots: [demo/screenshots/](demo/screenshots/)

---

## Known Limitations
- Vessel and berth data is synthetic (representative of real port schedules)
- Weather impact on port operations not yet modelled
- Berth assignment uses greedy algorithm (production would use constraint optimization)

---

## What We're Most Proud Of
The **multi-factor congestion prediction engine** combined with **automatic berth assignment** — no open-source tool today fuses vessel queue pressure, berth utilization, historical incident patterns, and hazmat priority into a single congestion score that directly drives an AI-generated operations plan a shift supervisor can act on immediately.
