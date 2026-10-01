import urllib.request
import json

BASE_URL = "http://localhost:8000"

centres = [
    {"name": "City Diagnostics", "location": "Mumbai"},
    {"name": "Apollo Diagnostics", "location": "Bangalore"},
    {"name": "HealthCare Plus", "location": "Delhi"},
]

tests = [
    {"name": "Complete Blood Count", "description": "Full blood panel", "price": "750.00"},
    {"name": "Lipid Profile", "description": "Cholesterol and triglycerides", "price": "1200.00"},
    {"name": "Thyroid Panel", "description": "T3, T4, TSH", "price": "900.00"},
    {"name": "Vitamin D", "description": "Vitamin D3 levels", "price": "1500.00"}
]

print("Seeding database...")

def post_json(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

for c_data in centres:
    status, centre = post_json(f"{BASE_URL}/centres", c_data)
    if status == 201:
        print(f"OK Created Centre: {centre['name']}")
        
        # Add all tests to each centre
        for t_data in tests:
            payload = {
                "centre_id": centre["id"],
                "name": t_data["name"],
                "description": t_data["description"],
                "price": t_data["price"]
            }
            t_status, tr_data = post_json(f"{BASE_URL}/tests", payload)
            if t_status == 201:
                print(f"  -> Added Test: {t_data['name']}")
            else:
                print(f"  FAIL Failed to add test: {tr_data}")
    else:
        print(f"FAIL Failed to create centre. Status: {status} Response: {centre}")

print("\nDone seeding!")

