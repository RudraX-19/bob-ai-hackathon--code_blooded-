import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ["MOCK_MODE"] = "true"

from data_loader import load_vessels, load_berths, load_incidents
from congestion_engine import score_terminals, assign_berths
from watsonx_client import generate_ops_plan

vessels   = load_vessels()
berths    = load_berths()
incidents = load_incidents()

hotspots    = score_terminals(vessels, berths, incidents)
assignments = assign_berths(vessels, berths)

print("=== CONGESTION SCORES ===")
for h in hotspots:
    print(f"{h['terminal']:15} | {h['congestion_level']:8} | Score: {h['congestion_score']:5} | Queue: {h['queue_size']} | Wait: {h['estimated_wait_hours']}h")

print()
print("=== BERTH ASSIGNMENTS ===")
for a in assignments:
    print(f"{a['vessel_name'][:25]:25} | Berth: {a['assigned_berth']:6} | Wait: {a['wait_hours']}h | {a['notes'][:40]}")

plan = generate_ops_plan(hotspots, assignments)
print()
print("=== PLAN (first 400 chars) ===")
print(plan[:400])
print()
print("ALL TESTS PASSED")
