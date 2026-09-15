# 🚀 Port Pulse — AI-Powered Container Congestion Predictor & Port Operations Optimiser

> ⚠️ **Replace everything in `[ ]` brackets with your actual content before submission.**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Code Blooded |
| **Track** | AI |
| **Team Lead** | Shubham Vora — shubhamvora269@gmail.com |
| **Members** | Rudra Vaghasiya, Vraj Viradiya, Jay Zalavadiya |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

Port operators manage berth allocation, crane scheduling, and vessel routing using manual spreadsheets. Congestion hotspots are identified only after vessels are already queuing — costing global supply chains billions. The 2021 LA/Long Beach backlog saw 100+ ships waiting for weeks, costing $10B+. Operators need a real-time, AI-driven system that predicts congestion before it happens and generates actionable 72-hour operations plans.

---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

Port Pulse is an AI-powered web dashboard that ingests vessel schedules and berth capacity data to predict congestion hotspots per terminal using a multi-factor scoring engine (0–100). It auto-assigns vessels to optimal berths, recommends alternate routing strategies, and uses IBM watsonx.ai (Granite model) to generate a natural-language 72-hour port operations and crew pre-positioning plan. Built with IBM Bob as the core development partner.

---

## ✨ Key Features

- **Multi-factor Congestion Scoring:** Berth utilization (40 pts) + queue pressure (30 pts) + incident history (15 pts) + priority vessel load (15 pts) — per terminal, 0–100 score
- **Automated Berth Assignment:** Best-fit algorithm with vessel length, TEU capacity, water depth, and hazmat constraints; alternate terminal fallback when primary is full
- **IBM watsonx.ai 72-Hour Operations Plan:** Granite model generates structured Phase 1/2/3 plan with crew pre-positioning and equipment checklists
- **Live Dashboard:** Terminal congestion cards, vessel schedule table, berth assignment table, and real-time charts
- **Hazmat Detection:** Flags dangerous cargo vessels requiring dedicated crane protocol and isolation berths
- **REST API:** FastAPI backend fully documented at `/docs` with Swagger UI

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.11, HTML5, CSS3, JavaScript |
| **Frameworks** | FastAPI, Uvicorn, Chart.js |
| **IBM Technologies** | watsonx.ai (Granite 13B Instruct), IBM Bob IDE |
| **Databases** | JSON + CSV (vessel schedules, berth capacity, incidents) |
| **Other** | GitHub Actions, python-dotenv, Pydantic |

---

## 📁 Repository Structure

```
├── src/                  # All source code
│   ├── backend/          # FastAPI app, congestion engine, watsonx client
│   ├── frontend/         # Single-page HTML dashboard
│   └── data/             # Vessel, berth, and incident data files
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/RudraX-19/bob-ai-hackathon--code_blooded-.git
cd bob-ai-hackathon--code_blooded-

# 2. Install dependencies
cd src
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set MOCK_MODE=true to run without a real watsonx.ai key

# 4. Run the project
cd backend
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- Vessel and berth data is synthetic (representative of real port schedules, not live AIS feed)
- Weather impact on port operations is not yet modelled
- Berth assignment uses a greedy best-fit algorithm (production would use constraint optimization)

---

## 🏅 What We're Most Proud Of

The **multi-factor congestion prediction engine** combined with **automatic berth assignment** — no open-source tool today fuses vessel queue pressure, berth utilization, historical incident patterns, and hazmat priority into a single congestion score that directly drives an AI-generated operations plan a shift supervisor can act on immediately.

---
