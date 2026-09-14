import asyncio, websockets, json, time

async def collect():
    url = "wss://stream.aisstream.io/v0/stream"
    # Try multiple Indian port bounding boxes simultaneously
    payload = {
        "APIKey": "cc6f20924693147d5bd1a2b4e3c6a183d05340a9",
        "BoundingBoxes": [
            [[18.5,  72.5],  [19.5,  73.5]],   # JNPT/Mumbai
            [[22.5,  69.3],  [23.2,  70.2]],   # Mundra
            [[12.8,  80.1],  [13.4,  80.6]],   # Chennai
            [[17.4,  83.0],  [17.9,  83.6]],   # Vizag
            [[9.7,   76.0],  [10.2,  76.6]],   # Cochin
            [[21.5,  88.0],  [22.3,  88.5]],   # Haldia
            [[20.0,  86.5],  [20.5,  87.0]],   # Paradip
        ],
        "FilterMessageTypes": ["PositionReport"]
    }
    ships = {}
    start = time.time()
    print("Scanning all major Indian ports (30s)...")
    async with websockets.connect(url, ping_interval=20) as ws:
        await ws.send(json.dumps(payload))
        while time.time() - start < 30:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=8)
                data = json.loads(msg)
                mtype = data.get("MessageType", "")
                meta  = data.get("MetaData", {})
                mmsi  = str(meta.get("MMSI", ""))
                if mtype == "PositionReport" and mmsi:
                    pos = data.get("Message", {}).get("PositionReport", {})
                    lat = pos.get("Latitude", 0)
                    lon = pos.get("Longitude", 0)
                    if lat == 0 and lon == 0:
                        continue
                    ships[mmsi] = {
                        "mmsi":      mmsi,
                        "name":      str(meta.get("ShipName", "Unknown")).strip(),
                        "lat":       lat,
                        "lon":       lon,
                        "speed":     pos.get("Sog", 0),
                        "heading":   pos.get("TrueHeading", pos.get("Cog", 0)),
                        "last_seen": time.time(),
                        "type":      "vessel"
                    }
                    print(f"  [{len(ships)}] {ships[mmsi]['name']:20} lat:{lat:.3f} lon:{lon:.3f} spd:{pos.get('Sog',0)}kn")
            except Exception as e:
                if "timeout" not in str(e).lower():
                    print(f"  err: {e}")
    print(f"\nTotal: {len(ships)} ships captured")
    with open("../data/live_seed.json", "w") as f:
        json.dump(list(ships.values()), f, indent=2)
    print("Saved to data/live_seed.json")

asyncio.run(collect())
