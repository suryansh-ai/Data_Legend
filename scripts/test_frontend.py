import requests
r = requests.get("http://localhost:8080/", timeout=5)
print("Status:", r.status_code)
ct = r.headers.get("content-type", "")
print("Content-Type:", ct)
if "html" in ct:
    print("Has root div:", 'id="root"' in r.text)
    print("Has script tag:", "<script" in r.text)
    print("First 500 chars:", r.text[:500])
else:
    print("Body:", r.text[:300])
