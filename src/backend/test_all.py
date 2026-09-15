import urllib.request, json, sys

BASE = "http://localhost:8000"
results = {}

endpoints = [
    "/api/health",
    "/api/ports",
    "/api/vessels",
    "/api/vessels/count",
    "/api/congestion",
    "/api/plan",
]

for ep in endpoints:
    try:
        r = urllib.request.urlopen(BASE + ep, timeout=30)
        data = json.loads(r.read().decode())
        results[ep] = "OK"
        if ep == "/api/health":
            print(f"  {ep}: OK — mode={data.get('watsonx_mode')}, vessels={data.get('live_vessels')}, port={data.get('active_port')}")
        elif ep == "/api/ports":
            print(f"  {ep}: OK — {len(data)} ports")
        elif ep == "/api/vessels":
            print(f"  {ep}: OK — {len(data)} vessels")
        elif ep == "/api/vessels/count":
            print(f"  {ep}: OK — total={data.get('total')}, moving={data.get('moving')}, anchored={data.get('anchored')}")
        elif ep == "/api/congestion":
            print(f"  {ep}: OK — {len(data)} terminals scored")
            for t in data:
                print(f"    - {t['terminal']}: {t['congestion_level']} ({t['congestion_score']}/100)")
        elif ep == "/api/plan":
            print(f"  {ep}: OK — port={data.get('port')}, vessels={data.get('total_vessels')}")
            plan = data.get("plan_text", "")
            print(f"    Plan length: {len(plan)} chars")
            print(f"    First 200 chars: {plan[:200]}")
    except Exception as e:
        results[ep] = f"FAIL: {e}"
        print(f"  {ep}: FAIL — {e}")

print()
passed = sum(1 for v in results.values() if v == "OK")
print(f"Result: {passed}/{len(endpoints)} endpoints passed")
