# src/

## Layout
```
src/
├── backend/
│   ├── main.py               ← FastAPI app — run this
│   ├── congestion_engine.py  ← Multi-factor scoring + berth assignment
│   ├── watsonx_client.py     ← IBM watsonx.ai Granite + mock fallback
│   ├── data_loader.py        ← JSON/CSV readers
│   └── models.py             ← Pydantic models
├── data/
│   ├── vessels.json          ← 10 incoming vessel schedules
│   ├── berths.json           ← 7 berths across 3 terminals
│   └── incidents.csv         ← 12 historical delay records
├── frontend/
│   └── index.html            ← Single-page port operations dashboard
├── .env.example
└── requirements.txt
```

## Quick start
```bash
pip install -r requirements.txt
cp .env.example .env
cd backend
uvicorn main:app --reload --port 8000
```
