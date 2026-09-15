import urllib.request, json

d = json.loads(urllib.request.urlopen("http://localhost:8000/api/stats").read().decode())
print("Stats endpoint:")
print(f"  Total: {d['total_vessels']}, Moving: {d['moving']}, Anchored: {d['anchored']}")
print(f"  Types: {d['vessel_types']}")
print(f"  Per-port: {d['per_port']}")
