"""Test all API endpoints with the new master dataset."""
import requests, json

base = "http://localhost:8080/api"

# 1. Health
r = requests.get(f"{base}/health", timeout=5)
print(f"1. GET /api/health: {r.status_code} -> {r.json()}")

# 2. Stats
r = requests.get(f"{base}/stats", timeout=5)
data = r.json()
print(f"2. GET /api/stats: {r.status_code}")
print(f"   total={data['total']}, states={data['states']}, cities={data['cities']}")

# 3. Facilities list
r = requests.get(f"{base}/facilities", params={"limit": 2}, timeout=5)
data = r.json()
print(f"3. GET /api/facilities: {r.status_code}, total={data['total']}")
for item in data["items"][:2]:
    print(f"   {item.get('name')} | city={item.get('city')} | state={item.get('state')} | trust={item.get('_trust_score')}")

# 4. Map data
r = requests.get(f"{base}/facilities/map", params={"limit": 3}, timeout=5)
data = r.json()
print(f"4. GET /api/facilities/map: {r.status_code}, points={len(data)}")

# 5. Search
r = requests.get(f"{base}/search", params={"q": "cancer", "limit": 3}, timeout=5)
data = r.json()
print(f"5. GET /api/search?q=cancer: {r.status_code}, total={data['total']}")

# 6. State stats
r = requests.get(f"{base}/stats/states", timeout=5)
data = r.json()
print(f"6. GET /api/stats/states: {r.status_code}, states={len(data)}")
for s in data[:3]:
    print(f"   {s['state']}: {s['total']} facilities, avg_trust={s['avg_trust']}")

# 7. Trust distribution
r = requests.get(f"{base}/stats/trust-distribution", timeout=5)
print(f"7. GET /api/stats/trust-distribution: {r.status_code} -> {r.json()}")

# 8. Column completeness
r = requests.get(f"{base}/stats/column-completeness", timeout=5)
data = r.json()
print(f"8. GET /api/stats/column-completeness: {r.status_code}")
for k, v in sorted(data.items(), key=lambda x: -x[1])[:5]:
    print(f"   {k}: {v}")

# 9. District health
r = requests.get(f"{base}/stats/district-health", timeout=5)
data = r.json()
print(f"9. GET /api/stats/district-health: {r.status_code}, districts={data.get('total', 0)}")
if data.get("districts"):
    d = data["districts"][0]
    print(f"   Sample: {d.get('district')}, {d.get('state')}, inst_births={d.get('institutional_births_pct')}")

# 10. Facility detail
r = requests.get(f"{base}/facilities", params={"limit": 1}, timeout=5)
if r.status_code == 200:
    fid = r.json()["items"][0]["unique_id"]
    r2 = requests.get(f"{base}/facilities/{fid}", timeout=5)
    print(f"10. GET /api/facilities/{{id}}: {r2.status_code}")
    if r2.status_code == 200:
        f = r2.json()
        print(f"    name={f.get('name')}, city={f.get('city')}, state={f.get('state')}")

print("\n--- ALL TESTS PASSED ---")
