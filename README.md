# A Phase Transition You Cannot Quite Measure

An interactive computational essay for **Anthropocene Humanities** (Prof. Buhm Soon Park, KAIST, 2026 Spring). It treats the Anthropocene as a *phase transition in the Earth system* and then **honestly tests whether that transition is actually visible in real data** — instead of asserting the metaphor.

**Live page:** see the GitHub Pages URL in this repo's *About* / *Settings → Pages*.

## What it does

Two probes, both run client-side (vanilla JS + canvas) on **real records** from
[Our World in Data / Global Carbon Project](https://github.com/owid/co2-data):

- **Probe I — Correlation structure.** Toggle *Levels ↔ Growth* on the cross-correlation of global series. Levels make the planet look like one synchronized system (PC1 share ≈ 0.91→0.93); detrend to growth rates and that "transition" collapses (≈ 0.45→0.49). The clean transition was an artifact of correlating monotone-rising curves.
- **Probe II — Critical slowing down.** A saddle-node tipping model (exact physics) with forcing read as cumulative CO₂: variance and lag-1 autocorrelation climb *before* the tip, and the tip does not reverse (hysteresis). A companion panel runs the *same* detector on real aggregate world-CO₂ growth and finds no clean signal — because the warning lives in subsystem fingerprints (AMOC, ice sheets, forests), not the aggregate.

Both probes hit the same wall: the physics is right, but no finite/local/aggregate measurement fully resolves the phase — and none of it tells us what we owe.

## Real data shipped in the page

Source: `owid-co2-data.csv` (OWID / Global Carbon Project). Verified numbers from the embedded data:

| set | levels PC1 (first→last) | growth PC1 (first→last) |
|---|---|---|
| World, 6 indicators, 1900–2022 | 0.91 → 0.93 | 0.45 → 0.49 |
| 25 countries (CO₂), 1910–2022 | 0.59 → 0.71 | 0.39 → 0.40 |

World indicators: population, co2, coal_co2, oil_co2, gas_co2, cement_co2 — the
series with clean, gap-free, strictly-positive annual coverage over the window.
(In the current OWID file the World methane / N₂O series start only in 1970 and
land-use-change CO₂ in 1950, so they are excluded to keep a long baseline.)

## Repo layout

```
.
├── index.html              # the self-contained interactive (real data embedded)
├── data/
│   ├── build_data.py        # downloads OWID CSV → extracts series → writes data.json
│   └── data.json            # generated; also embedded inside index.html
├── README.md
└── PROJECT_HANDOFF.md       # full design notes & remaining work
```

## Rebuild / refresh the data

```bash
curl -sL -o /tmp/owid-co2-data.csv \
  https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
python3 data/build_data.py /tmp/owid-co2-data.csv data/data.json
# then re-embed data/data.json into the <script id="data"> block of index.html
```

## Sources

- W. Steffen et al., "The trajectory of the Anthropocene: The Great Acceleration," *The Anthropocene Review* (2015).
- P. Ditlevsen & S. Ditlevsen, "Warning of a forthcoming collapse of the Atlantic meridional overturning circulation," *Nature Communications* (2023).
- Data: Our World in Data, Global Carbon Project.
