"""Test all local API endpoints with correct paths."""
import requests, json

base = "http://localhost:8080/api"

# 1. Facilities
r = requests.get(f"{base}/facilities", params={"limit": 3}, timeout=10)
data = r.json()
print(f"1. GET /api/facilities: {r.status_code}, total={data.get('total')}")
for f in data.get("facilities", [])[:3]:
    print(f"   {f.get('name')} | trust={f.get('_trust_score')} | {f.get('_trust_signal')}")
print()

# 2. Stats
r = requests.get(f"{base}/stats", timeout=10)
print(f"2. GET /api/stats: {r.status_code}")
if r.status_code == 200:
    for k, v in r.json().items():
        print(f"   {k}: {v}")
print()

# 3. Map
r = requests.get(f"{base}/facilities/map", params={"limit": 5}, timeout=10)
print(f"3. GET /api/facilities/map: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   points={len(data.get('facilities', []))}")
print()

# 4. Trust distribution
r = requests.get(f"{base}/stats/trust-distribution", timeout=10)
print(f"4. GET /api/stats/trust-distribution: {r.status_code}")
if r.status_code == 200:
    print(f"   {r.json()}")
print()

# 5. Search
r = requests.get(f"{base}/search", params={"q": "cancer"}, timeout=10)
print(f"5. GET /api/search?q=cancer: {r.status_code}")
if r.status_code == 200:
    print(f"   results={len(r.json().get('results', []))}")
print()

# 6. Facility detail
r = requests.get(f"{base}/facilities", params={"limit": 1}, timeout=10)
if r.status_code == 200:
    fid = r.json()["facilities"][0]["unique_id"]
    r2 = requests.get(f"{base}/facilities/{fid}", timeout=10)
    print(f"6. GET /api/facilities/{{id}}: {r2.status_code}")
    if r2.status_code == 200:
        fac = r2.json()
        print(f"   name={fac.get('name')}, trust={fac.get('_trust_score')}")
