#!/usr/bin/env python3
"""Extract real Our World in Data / Global Carbon Project series into data.json
for the Anthropocene phase-transition interactive.

Source CSV: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
"""
import csv, json, math, sys

CSV = sys.argv[1] if len(sys.argv) > 1 else "/tmp/owid-co2-data.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/data.json"

# Probe I — world indicators with clean, gap-free, strictly-positive annual
# coverage over the whole window (so log-growth is well defined). In the current
# OWID file the World entity's methane / nitrous_oxide series only begin in 1970
# and land_use_change_co2 in 1950, so they are excluded to keep a long baseline.
WORLD_IND = ["population", "co2", "coal_co2", "oil_co2", "gas_co2", "cement_co2"]
WORLD_RANGE = (1900, 2022)          # common contiguous range
COUNTRY_RANGE = (1910, 2022)        # common contiguous range for the country set
P2_RANGE = (1850, 2022)             # world annual CO2 for the honesty plot

# ---- load ----
rows = []
with open(CSV, newline="") as f:
    r = csv.DictReader(f)
    cols = r.fieldnames
    for row in r:
        rows.append(row)

def num(v):
    if v is None or v == "":
        return None
    try:
        x = float(v)
        return x
    except ValueError:
        return None

# index: country -> year -> row
by_country = {}
for row in rows:
    by_country.setdefault(row["country"], {})[int(float(row["year"]))] = row

# ---------- Probe I: world ----------
world = by_country["World"]
y0, y1 = WORLD_RANGE
world_years = list(range(y0, y1 + 1))
world_series = []
for ind in WORLD_IND:
    s = []
    for y in world_years:
        row = world.get(y)
        v = num(row[ind]) if row else None
        if v is None or v <= 0:
            v = None
        s.append(v)
    world_series.append(s)

# verify no gaps
for ind, s in zip(WORLD_IND, world_series):
    missing = [world_years[i] for i, v in enumerate(s) if v is None]
    if missing:
        print(f"  WARN world {ind}: missing {missing[:5]}{'...' if len(missing)>5 else ''}", file=sys.stderr)

# ---------- Probe I: countries ----------
# real sovereign countries only: 3-letter ISO, not OWID_ aggregates
def is_country(c):
    rows_c = by_country[c]
    iso = next(iter(rows_c.values()))["iso_code"]
    return iso and len(iso) == 3 and not iso.startswith("OWID")

cy0, cy1 = COUNTRY_RANGE
country_years = list(range(cy0, cy1 + 1))
candidates = []
for c in by_country:
    if c == "World" or not is_country(c):
        continue
    rows_c = by_country[c]
    s = []
    ok = True
    for y in country_years:
        row = rows_c.get(y)
        v = num(row["co2"]) if row else None
        if v is None or v <= 0:
            ok = False
            break
        s.append(v)
    if ok:
        candidates.append((c, s))

candidates.sort(key=lambda t: t[0])
country_names = [c for c, _ in candidates]
country_series = [s for _, s in candidates]
print(f"  country set: {len(country_names)} countries fully cover {cy0}-{cy1}", file=sys.stderr)

# ---------- Probe II: world annual CO2 ----------
p0, p1y = P2_RANGE
p2_years = list(range(p0, p1y + 1))
p2_co2 = []
for y in p2_years:
    row = world.get(y)
    v = num(row["co2"]) if row else None
    if v is not None and v <= 0:
        v = None
    p2_co2.append(v)

data = {
    "meta": {
        "source": "Our World in Data / Global Carbon Project (owid-co2-data.csv)",
        "world_range": WORLD_RANGE,
        "country_range": COUNTRY_RANGE,
        "p2_range": P2_RANGE,
        "world_indicators": WORLD_IND,
        "n_countries": len(country_names),
        "country_names": country_names,
    },
    "p1": {
        "world": {"years": world_years, "labels": WORLD_IND, "series": world_series},
        "country": {"years": country_years, "labels": country_names, "series": country_series},
    },
    "p2": {"years": p2_years, "co2": p2_co2},
}

with open(OUT, "w") as f:
    json.dump(data, f, separators=(",", ":"))
print(f"  wrote {OUT}", file=sys.stderr)

# ---------- sanity: reproduce the headline numbers ----------
def log_growth(a):
    o = []
    for i in range(1, len(a)):
        p = a[i-1] if a[i-1] and a[i-1] > 0 else 1e-9
        c = a[i] if a[i] and a[i] > 0 else 1e-9
        o.append(math.log(c/p))
    return o

def win_corr(vars_, start, win):
    n = len(vars_)
    z = []
    for v in vars_:
        s = v[start:start+win]
        m = sum(s)/len(s)
        sd = (sum((x-m)**2 for x in s)/len(s))**0.5 or 1e-9
        z.append([(x-m)/sd for x in s])
    C = [[sum(z[i][k]*z[j][k] for k in range(win))/win for j in range(n)] for i in range(n)]
    return C

def lambda_max(C):
    n = len(C)
    v = [1/n**0.5]*n
    for _ in range(200):
        w = [sum(C[i][j]*v[j] for j in range(n)) for i in range(n)]
        nm = sum(x*x for x in w)**0.5
        if nm < 1e-12: break
        v = [x/nm for x in w]
    num = sum(v[i]*sum(C[i][j]*v[j] for j in range(n)) for i in range(n))
    den = sum(x*x for x in v)
    return num/den

def headline(block, win, label):
    yrs = block["years"]; series = block["series"]; n = len(series)
    for mode in ("levels", "growth"):
        vs = [s[:] if mode == "levels" else log_growth(s) for s in series]
        npos = len(vs[0]) - win + 1
        first = lambda_max(win_corr(vs, 0, win))/n
        last = lambda_max(win_corr(vs, npos-1, win))/n
        print(f"  {label} {mode:7s}: PC1 {first:.2f} -> {last:.2f}", file=sys.stderr)

def headline_str(block, win, label):
    yrs = block["years"]; series = block["series"]; n = len(series)
    parts = [f"{label}(n={n},{yrs[0]}-{yrs[-1]})"]
    for mode in ("levels", "growth"):
        vs = [s[:] if mode == "levels" else log_growth(s) for s in series]
        npos = len(vs[0]) - win + 1
        first = lambda_max(win_corr(vs, 0, win))/n
        last = lambda_max(win_corr(vs, npos-1, win))/n
        parts.append(f"{mode}:{first:.2f}to{last:.2f}")
    return " ".join(parts)

with open(OUT.replace(".json", "_headline.txt"), "w") as f:
    f.write(headline_str(data["p1"]["world"], 25, "world") + "\n")
    f.write(headline_str(data["p1"]["country"], 21, "country") + "\n")
