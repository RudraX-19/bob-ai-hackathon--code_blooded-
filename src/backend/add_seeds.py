import json
import random
import string
from pathlib import Path

SEED_FILE = Path(r"d:\ibm\port-pulse\src\data\live_seed.json")

def generate_random_ships():
    try:
        data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    except:
        data = []
        
    ports = {
        "JNPT": [18.95, 72.95],
        "MUNDRA": [22.839, 69.705],
        "CHENNAI": [13.09, 80.299],
        "VIZAG": [17.6868, 83.2985],
        "COCHIN": [9.9658, 76.2673],
        "KOLKATA": [22.5726, 88.3639]
    }
    
    types = ["Container Ship", "Bulk Carrier", "Oil Tanker", "General Cargo"]
    
    # Let's add 60 more ships (10 for each port)
    for port, (plat, plon) in ports.items():
        for i in range(10):
            # random offset between -0.4 and 0.4 degrees
            lat = plat + random.uniform(-0.4, 0.4)
            lon = plon + random.uniform(-0.4, 0.4)
            
            # roughly half moving, half anchored
            speed = random.uniform(5.0, 18.0) if random.random() > 0.5 else random.uniform(0.0, 0.2)
            heading = random.randint(0, 359)
            
            mmsi = str(random.randint(400000000, 499999999))
            name = "MSC " + ''.join(random.choices(string.ascii_uppercase, k=4))
            t = random.choice(types)
            
            data.append({
                "mmsi": mmsi,
                "name": name,
                "type": t,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "speed": round(speed, 1),
                "heading": heading,
                "port": port
            })
            
    SEED_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Added ships. Total count is now: {len(data)}")

if __name__ == "__main__":
    generate_random_ships()
