# Setup Guide — Port Pulse

## Prerequisites
| Tool | Version | Check |
|---|---|---|
| Python | 3.10 or 3.11 | `python --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |
| Browser | Chrome / Firefox / Edge | — |

No Docker, database, or cloud account needed for mock mode.

---

## Step 1 — Clone the Repository
```bash
git clone https://github.com/RudraX-19/bob-ai-hackathon-code-blooded.git
cd bob-ai-hackathon-code-blooded
```

## Step 2 — Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

## Step 3 — Install Dependencies
```bash
cd src
pip install -r requirements.txt
```

## Step 4 — Configure Environment
```bash
cp .env.example .env
```

**Mock mode (works immediately):**
```env
MOCK_MODE=true
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**Live watsonx.ai mode:**
```env
MOCK_MODE=false
WATSONX_API_KEY=<real key from cloud.ibm.com/iam/apikeys>
WATSONX_PROJECT_ID=<project ID from watsonx.ai>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> Never commit `.env` — it is already in `.gitignore`

## Step 5 — Run the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

## Step 6 — Open the Dashboard
Go to: **http://localhost:8000**

You should see:
- 5 summary cards at the top
- 3 terminal congestion cards (Terminal A, B, C)
- Two charts (congestion scores, vessel distribution)
- Vessel schedule table (10 vessels)
- Berth assignment table

## Step 7 — Generate the AI Plan
Click **"Generate 72-Hour Plan"** button.

---

## Verify It's Working

| URL | Expected |
|---|---|
| `http://localhost:8000` | Dashboard loads with data |
| `http://localhost:8000/api/health` | `{"status":"healthy"}` |
| `http://localhost:8000/api/vessels` | JSON array of 10 vessels |
| `http://localhost:8000/api/congestion` | JSON array of 3 terminals scored |
| `http://localhost:8000/api/assignments` | Berth assignment for each vessel |
| `http://localhost:8000/docs` | Swagger API docs |

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: fastapi` | Deps not installed | `pip install -r requirements.txt` in `src/` |
| `Address already in use` | Port 8000 taken | Use `--port 8001` |
| "Error: backend offline" in dashboard | Server not running | Start uvicorn |
| `FileNotFoundError: vessels.json` | Wrong directory | Run uvicorn from `src/backend/` |
| watsonx call fails | Invalid key | Set `MOCK_MODE=true` in `.env` |
