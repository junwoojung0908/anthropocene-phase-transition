#!/usr/bin/env python3
"""Canonical, reproducible data build for the Anthropocene phase-transition page.

Emits data.json in the structure the page's JS expects:
  p1.world   = { "<indicator>": [values...], "_years": [...] }
  p1.country = { "<country>":   [values...], "_years": [...] }
  p1.mixed   = { "<label>":     [values...], "_years": [...], "_kinds": {label: "pos"|"signed"} }
  p2         = { "years": [...], "co2": [...] }

Sources (auto-downloaded if missing):
  OWID / Global Carbon Project  owid-co2-data.csv
  NASA GISTEMP global surface temperature anomaly (J-D annual)
  NOAA Mauna Loa annual mean atmospheric CO2 concentration
"""
import csv, json, math, os, re, urllib.request, hashlib

TMP = "/tmp"
OWID = os.path.join(TMP, "owid-co2-data.csv")
GIST = os.path.join(TMP, "gistemp.csv")
MLO  = os.path.join(TMP, "mlo.csv")
SG   = os.path.join(TMP, "sg_index.txt")
URLS = {
    OWID: "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
    GIST: "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
    MLO:  "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.csv",
    SG:   "https://www.pik-potsdam.de/~caesar/AMOC_slowdown/sg_index_hadisst.txt",
}
for p in (OWID, GIST, MLO, SG):
    if not os.path.exists(p) or os.path.getsize(p) < 500:
        urllib.request.urlretrieve(URLS[p], p)

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

rows = list(csv.DictReader(open(OWID, newline="")))
by_country = {}
for row in rows:
    by_country.setdefault(row["country"], {})[int(float(row["year"]))] = row
world = by_country["World"]

def wseries(ind, y0, y1):
    s = []
    for y in range(y0, y1 + 1):
        r = world.get(y)
        v = num(r[ind]) if r else None
        if v is None or v <= 0:
            return None
        s.append(v)
    return s

# ---------- Probe I: world (auto-select clean indicators) ----------
WR = (1900, 2022)
CAND = ["population", "co2", "coal_co2", "oil_co2", "gas_co2", "cement_co2",
        "land_use_change_co2", "methane", "nitrous_oxide"]
world_block = {"_years": list(range(WR[0], WR[1] + 1))}
w_used = []
for ind in CAND:
    s = wseries(ind, *WR)
    if s is not None:
        world_block[ind] = s
        w_used.append(ind)

# ---------- Probe I: countries (clean co2; cap top emitters for readability) ----------
CR = (1910, 2022)
CAP = 40
def is_country(c):
    iso = next(iter(by_country[c].values()))["iso_code"]
    return iso and len(iso) == 3 and not iso.startswith("OWID")
cyrs = list(range(CR[0], CR[1] + 1))
cand = []
for c in by_country:
    if c == "World" or not is_country(c):
        continue
    s, ok = [], True
    for y in cyrs:
        r = by_country[c].get(y)
        v = num(r["co2"]) if r else None
        if v is None or v <= 0:
            ok = False; break
        s.append(v)
    if ok:
        cand.append((c, s, s[-1]))
cand.sort(key=lambda t: -t[2])
cand = cand[:CAP]
cand.sort(key=lambda t: t[0])
country_block = {"_years": cyrs}
for c, s, _ in cand:
    country_block[c] = s

# ---------- Probe II: world annual co2 ----------
PR = (1850, 2022)
p2_years, p2_co2 = [], []
for y in range(PR[0], PR[1] + 1):
    r = world.get(y); v = num(r["co2"]) if r else None
    p2_years.append(y); p2_co2.append(v if (v and v > 0) else None)

# ---------- Mixed: human forcing + independent Earth-system response ----------
gist = {}
gl = open(GIST).read().splitlines()
hi = next(i for i, l in enumerate(gl) if l.startswith("Year"))
jd = gl[hi].split(",").index("J-D")
for l in gl[hi + 1:]:
    p = l.split(",")
    if not p[0].strip().isdigit():
        continue
    v = p[jd].strip()
    if v in ("", "***"):
        continue
    gist[int(p[0])] = float(v) / 100.0
mlo = {}
for l in open(MLO):
    if l.startswith("#") or l.lower().startswith("year"):
        continue
    p = l.split(",")
    if len(p) < 2 or not p[0].strip()[:4].isdigit():
        continue
    mlo[int(float(p[0]))] = float(p[1])

MR = (1965, 2022)
myrs = list(range(MR[0], MR[1] + 1))
defs = [
    ("population",        "pos",    lambda y: num(world[y]["population"]) if world.get(y) else None),
    ("co2 emissions",     "pos",    lambda y: num(world[y]["co2"]) if world.get(y) else None),
    ("primary energy",    "pos",    lambda y: num(world[y]["primary_energy_consumption"]) if world.get(y) else None),
    ("CO2 concentration", "pos",    lambda y: mlo.get(y)),
    ("temperature",       "signed", lambda y: gist.get(y)),
]
mixed_block = {"_years": myrs, "_kinds": {}}
for label, kind, get in defs:
    s = [get(y) for y in myrs]
    if any(v is None for v in s):
        continue
    mixed_block[label] = s
    mixed_block["_kinds"][label] = kind

# ---------- AMOC fingerprint (Caesar et al. 2018, HadISST subpolar-gyre index) ----------
# Single-column file: one annual SST value per line; header gives the year span.
# This is the warming-compensated index (SG anomaly minus 2x global mean) that
# Ditlevsen & Ditlevsen (2023) analysed for early-warning signals.
sg_lines = open(SG).read().splitlines()
amoc_start = None
amoc_idx = []
for l in sg_lines:
    s = l.strip()
    if not s or s.startswith("#") or s.startswith("%"):
        m = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", s)
        if m:
            amoc_start = int(m.group(1))
        continue
    try:
        v = float(s.split()[0])
    except ValueError:
        continue
    if v == v:  # not NaN
        amoc_idx.append(v)
amoc_years = list(range(amoc_start, amoc_start + len(amoc_idx)))

data = {
    "meta": {"source": "OWID/Global Carbon Project; NASA GISTEMP; NOAA Mauna Loa; "
                       "Caesar et al. 2018 (HadISST AMOC subpolar-gyre fingerprint)",
             "world_range": WR, "country_range": CR, "mix_range": MR, "p2_range": PR,
             "country_cap": CAP, "amoc_range": [amoc_years[0], amoc_years[-1]]},
    "p1": {"world": world_block, "country": country_block, "mixed": mixed_block},
    "p2": {"years": p2_years, "co2": p2_co2,
           "amoc": {"years": amoc_years, "idx": amoc_idx}},
}
json.dump(data, open(os.path.join(TMP, "data.json"), "w"), separators=(",", ":"))

# ---------- headline reproduction (sanity) ----------
def log_growth(a):
    o = []
    for i in range(1, len(a)):
        p = a[i-1] if a[i-1] and a[i-1] > 0 else 1e-9
        c = a[i] if a[i] and a[i] > 0 else 1e-9
        o.append(math.log(c/p))
    return o
def diff(a): return [a[i]-a[i-1] for i in range(1, len(a))]
def win_corr(vs, s0, win):
    n = len(vs); z = []
    for v in vs:
        s = v[s0:s0+win]; m = sum(s)/len(s)
        sd = (sum((x-m)**2 for x in s)/len(s))**0.5 or 1e-9
        z.append([(x-m)/sd for x in s])
    return [[sum(z[i][k]*z[j][k] for k in range(win))/win for j in range(n)] for i in range(n)]
def lam(C):
    n=len(C); v=[1/n**0.5]*n
    for _ in range(200):
        w=[sum(C[i][j]*v[j] for j in range(n)) for i in range(n)]
        nm=sum(x*x for x in w)**0.5
        if nm<1e-12: break
        v=[x/nm for x in w]
    return sum(v[i]*sum(C[i][j]*v[j] for j in range(n)) for i in range(n))/sum(x*x for x in v)
def head(block, win):
    names=[k for k in block if k[0]!='_']; kinds=block.get("_kinds",{})
    series=[block[k] for k in names]; n=len(series); out=[]
    for mode in ("levels","growth"):
        if mode=="levels": vs=[s[:] for s in series]
        else: vs=[diff(series[i]) if kinds.get(names[i])=="signed" else log_growth(series[i]) for i in range(n)]
        np=len(vs[0])-win+1
        out.append("%s %.2f->%.2f"%(mode, lam(win_corr(vs,0,win))/n, lam(win_corr(vs,np-1,win))/n))
    return out
S=[]
S.append("world  n=%d %d-%d : %s"%(len(w_used),WR[0],WR[1],",".join(w_used)))
S.append("   "+" | ".join(head(world_block,25)))
nc=len([k for k in country_block if k[0]!='_'])
S.append("country n=%d %d-%d (cap %d)"%(nc,CR[0],CR[1],CAP))
S.append("   "+" | ".join(head(country_block,21)))
nm=len([k for k in mixed_block if k[0]!='_'])
S.append("mixed  n=%d %d-%d : %s"%(nm,MR[0],MR[1],",".join(k for k in mixed_block if k[0]!='_')))
S.append("   "+" | ".join(head(mixed_block,21)))
S.append("owid lines=%d md5=%s"%(open(OWID,'rb').read().count(b'\n'), hashlib.md5(open(OWID,'rb').read()).hexdigest()[:10]))
open(os.path.join(TMP,"summary.txt"),"w").write("\n".join(S)+"\n")
print("BUILD OK n_world=%d n_country=%d n_mixed=%d"%(len(w_used),nc,nm))
