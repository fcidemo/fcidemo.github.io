#!/usr/bin/env python3
"""Generate sample-database.json so the UI can be opened before any hardware exists.

The slip layout here is the INVENTED illustration from MASTER_NOTES.md section 5,
not a real capture. Replace it the moment you have 20 genuine slips.
"""
import base64, json, random, zlib
from datetime import datetime, timedelta, timezone

random.seed(7)

COMMODITIES = [
    ("WHEAT", "01", 11.5, 1.3),
    ("PADDY", "02", 16.0, 2.0),
    ("MUSTARD", "07", 7.5, 1.1),
    ("GRAM", "11", 10.0, 1.0),
]

SLIP = ("    MOISTURE METER\r\n"
        "COMMODITY : {commodity}\r\n"
        "CODE      : {code}\r\n"
        "MOISTURE  : {moist:.1f} %\r\n"
        "TEMP      : {temp:.1f} C\r\n"
        "DATE      : {date}\r\n"
        "TIME      : {time}\r\n\r\n\r\n")

N = 160
now = datetime.now(timezone.utc)
records = []

for i in range(N):
    name, code, mu, sd = random.choices(COMMODITIES, weights=[6, 4, 2, 1])[0]
    ts = now - timedelta(minutes=(N - i) * 47 + random.randint(0, 20))
    moist = max(3.5, min(40.0, random.gauss(mu, sd)))
    temp = random.gauss(29.0, 2.4)
    local = ts + timedelta(hours=5, minutes=30)          # IST, as the meter clock would read
    raw = SLIP.format(commodity=name, code=code, moist=moist, temp=temp,
                      date=local.strftime("%d/%m/%y"),
                      time=local.strftime("%H:%M")).encode("ascii")
    records.append({
        "seq": i + 1,
        "device": "depot-01",
        "device_ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "uptime_ms": (i + 1) * 47 * 60000,
        "meter_date": local.strftime("%d/%m/%y"),
        "meter_time": local.strftime("%H:%M"),
        "commodity": name,
        "code": code,
        "moisture_pct": round(moist, 2),
        "temperature_c": round(temp, 2),
        "humidity_pct": None,
        "bytes": len(raw),
        "fields": 6,
        "parser": 1,
        "crc32": format(zlib.crc32(raw) & 0xFFFFFFFF, "08x"),
        "raw_b64": base64.b64encode(raw).decode("ascii"),
    })

db = {
    "device": "depot-01",
    "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "schema": 1,
    "parser": 1,
    "total_readings": N,
    "dropped_from_window": 0,
    "window": 1000,
    "records": records,
}

with open("sample-database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, separators=(",", ":"))

print(f"wrote sample-database.json: {N} records, "
      f"{len(json.dumps(db, separators=(',', ':')))} bytes")
