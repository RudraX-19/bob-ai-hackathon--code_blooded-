"""Data loader for Port Pulse."""
import json
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_vessels() -> list[dict]:
    with open(DATA_DIR / "vessels.json", encoding="utf-8") as f:
        return json.load(f)


def load_berths() -> list[dict]:
    with open(DATA_DIR / "berths.json", encoding="utf-8") as f:
        return json.load(f)


def load_incidents() -> list[dict]:
    rows = []
    with open(DATA_DIR / "incidents.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def get_berths_for_terminal(terminal: str, berths: list[dict]) -> list[dict]:
    return [b for b in berths if b["terminal"] == terminal]


def get_vessels_for_terminal(terminal: str, vessels: list[dict]) -> list[dict]:
    return [v for v in vessels if v["destination_berth"] == terminal]


def get_terminal_incident_count(terminal: str, incidents: list[dict]) -> int:
    return len([i for i in incidents if i["terminal"] == terminal])
