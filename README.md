# 🚀 Port Pulse — AI-Powered Maritime Congestion Predictor & Port Operations Optimiser

![Port Pulse Live Dashboard](demo/main.png)

*Real-time global vessel tracking across 6 Indian port terminals, powered by IBM watsonx.ai Llama 3.3 and live AIS satellite data.*

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Code Blooded |
| **Hackathon** | IBM Battle of Brains (BoB) AI Hackathon |
| **Track** | AI |
| **Team Lead** | Shubham Vora — shubhamvora269@gmail.com |
| **Members** | Rudra Vaghasiya, Vraj Viradiya, Jay Zalavadiya |

---

## 🎯 Problem Statement

Port operators across India's busiest maritime hubs — JNPT, Mundra, Cochin, Chennai — manage berth allocation, crane scheduling, and vessel routing using manual processes and reactive decision-making. Congestion hotspots are identified only **after** vessels are already queuing at anchor, costing global supply chains billions annually. The 2021 LA/Long Beach backlog saw 100+ ships waiting for weeks at a cost of **$10 Billion+**. India's ports face identical risk as container traffic grows 8% year-on-year.

Operators urgently need a real-time, AI-driven system that **predicts congestion before it happens** and generates actionable operations plans — not dashboards that just describe what already went wrong.

---

## 💡 Solution

**Port Pulse** is an AI-powered maritime operations platform that ingests **100% live global AIS satellite vessel data** via AISStream.io and applies a multi-factor congestion scoring engine (0–100) per terminal in real time. When congestion is detected, the system automatically recommends alternate routing strategies (e.g., diverting JNPT-bound vessels to Mundra) and triggers **IBM watsonx.ai (Llama 3.3 70B)** to generate a structured, actionable **72-hour Port Operations Plan** — covering berth assignments, crane pre-positioning, and crew logistics — that a shift supervisor can act on immediately.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🛰️ **Live AIS Satellite Tracking** | 100+ global vessels tracked in real time via AISStream.io WebSocket feed across the entire Indian coastline |
| 📊 **Multi-Factor Congestion Engine** | Berth utilization (40 pts) + queue pressure (30 pts) + incident history (15 pts) + priority vessel load (15 pts) → 0–100 score per terminal |
| 🤖 **IBM watsonx.ai 72-Hour Plan** | Llama 3.3 70B generates a structured Phase 1/2/3 operations plan with crew pre-positioning, crane assignments, and routing diversions |
| 🗺️ **Interactive Maritime Map** | Live vessel positions plotted on Leaflet.js map with real-time movement simulation |
| 🔀 **Alternate Routing Recommendations** | AI-powered automatic rerouting suggestions when a terminal exceeds its congestion threshold |
| 📈 **Fleet Analytics** | Live donut charts (Fleet Distribution) and bar charts (Vessel Types: Bulk Carrier, Container Ship, Oil Tanker) |
| 🔍 **Fleet Search & Monitoring** | Search any vessel by MMSI or name with live Speed Over Ground (SOG) data |
| ⚡ **Visual Executive Summary** | Color-coded ROUTINE / WARNING / CRITICAL status badge with congestion hotspots and idle fleet ratio |

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.10+, HTML5, CSS3, JavaScript (ES6+) |
| **Backend Framework** | FastAPI + Uvicorn (ASGI) |
| **Frontend** | Vanilla JS, Leaflet.js (maps), Chart.js (analytics) |
| **IBM AI** | watsonx.ai — `meta-llama/llama-3-3-70b-instruct` |
| **Live Data** | AISStream.io WebSocket (global AIS satellite feed) |
| **Config** | python-dotenv, Pydantic v2 |
| **Deployment** | Render.com (Always-On WebSocket server) |

---

## 📁 Repository Structure

```
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app — all API endpoints & WebSocket manager
│   │   ├── ais_connector.py     # Live AISStream WebSocket + proximity port assignment
│   │   ├── live_congestion.py   # Multi-factor congestion scoring engine (0-100)
│   │   ├── watsonx_client.py    # IBM watsonx.ai Llama 3.3 client + 72-hr plan builder
│   │   └── indian_ports.py      # Port terminal definitions with bounding boxes
│   ├── frontend/
│   │   └── index.html           # Single-page enterprise dashboard (all-in-one)
│   ├── data/
│   │   └── live_seed.json       # 41 seed vessels for immediate demo data
│   ├── .env.example             # Environment variable template
│   └── requirements.txt         # Python dependencies
├── demo/
│   ├── main.png                 # Hero screenshot — full live dashboard
│   ├── screenshots/             # Additional screenshots gallery
│   └── demo-video-link.txt      # Demo video link
├── docs/
│   ├── architecture.md
│   ├── problem-statement.md
│   ├── solution-overview.md
│   └── setup-guide.md
├── presentation/                # Slide deck (PPT/PDF)
└── submission.yaml              # Structured submission metadata
```

---

## ⚡ How to Run Locally

**Prerequisites:** Python 3.10+, Git

```bash
# 1. Clone the repository
git clone https://github.com/RudraX-19/bob-ai-hackathon--code_blooded-.git
cd bob-ai-hackathon--code_blooded-

# 2. Install dependencies
cd src
python -m pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Open .env and set:
#   MOCK_MODE=true        → Run with mock AI (no watsonx key needed)
#   MOCK_MODE=false       → Enable live IBM watsonx.ai calls (requires API key)
#   AISSTREAM_KEY=...     → Your AISStream.io API key for live vessel data

# 4. Start the server
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Open [http://localhost:8000](http://localhost:8000) in your browser.**

> 💡 **Tip:** Set `MOCK_MODE=true` to run the full dashboard with simulated AI responses — no IBM credentials required.

---

## 🌐 Live Deployment

The application is deployed on Render.com with an Always-On WebSocket server:

**👉 [bob-ai-hackathon-code-blooded.onrender.com](https://bob-ai-hackathon-code-blooded.onrender.com)**

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 **Demo Video** | [Watch on Google Drive](https://drive.google.com/drive/folders/120lRzG5KcjU2TbEX6w-PXbu8eN8tPa31?usp=drive_link) |
| 📊 **Presentation (PPT)** | [Port_Pulse_Hackathon_Pitch.pptx](demo/Port_Pulse_Hackathon_Pitch.pptx) |
| 🌐 **Live Demo** | [bob-ai-hackathon-code-blooded.onrender.com](https://bob-ai-hackathon-code-blooded.onrender.com) |
| 🖼️ **Screenshots Gallery** | [See demo/screenshots/](demo/screenshots/) |

---

## 🧠 IBM watsonx.ai Integration

The AI engine is driven by **`meta-llama/llama-3-3-70b-instruct`** on IBM watsonx.ai.

**What the AI receives:**
- Live congestion scores (0–100) per terminal
- Number of vessels queued at anchor per port
- Current alternate routing recommendations
- Berth and crane availability status

**What the AI generates:**
- Phase 1 (0–24h): Immediate vessel rerouting directives
- Phase 2 (24–48h): Crane pre-positioning and crew logistics
- Phase 3 (48–72h): Traffic normalization and incident prevention checklist

---

## ⚠️ Known Limitations

- The Leaflet map tile layer requires a free API key (Carto tiles used as fallback — entirely functional)
- Live AIS data volume varies by time of day based on satellite pass coverage
- The watsonx.ai Llama model requires ~8–12 seconds to generate the 72-hour plan (spinner is shown)

---

## 🏅 What We're Most Proud Of

The **live AIS satellite integration** combined with **IBM watsonx.ai's operational intelligence** — instead of just displaying data, Port Pulse tells operators exactly what to do next: *"Divert VESSEL X from JNPT to Mundra Terminal 2, pre-position 3 cranes at Berth 7, alert crew on shift change."* This is the difference between a dashboard and a decision-support system.

---
