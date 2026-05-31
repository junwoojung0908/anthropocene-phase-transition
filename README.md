# A Phase Transition You Cannot Quite Measure

An interactive computational essay for **Anthropocene Humanities** (Prof. Buhm Soon Park, KAIST, 2026 Spring). It treats the Anthropocene as a *phase transition in the Earth system* and then **honestly tests whether that transition is actually visible in real data** — instead of asserting the metaphor.

**Live:** https://junwoojung0908.github.io/anthropocene-phase-transition/

## What it does

Two probes, both run client-side (vanilla JS + canvas) on **real records**:

- **Probe I — Correlation structure.** Toggle *Levels ↔ Growth* on the cross-correlation of global series. Levels make the planet look like one synchronized system; detrend to growth rates and that "transition" collapses. The clean transition was an artifact of correlating monotone-rising curves. Three datasets:
  - **world** — 9 OWID/GCP indicators (population, CO₂ and its sources, land-use, CH₄, N₂O), 1900–2022.
  - **countries** — the 40 largest emitters with gap-free CO₂ records, 1910–2022.
  - **Earth + human** — human drivers (population, emissions, energy) paired with **independent Earth-system measurements** (atmospheric CO₂ concentration, global surface temperature), 1965–2022, following Steffen et al. (2015). Shows the coupling that is obvious in levels becomes invisible in honest growth rates — the temperature response decouples into internal variability.
- **Probe II — Critical slowing down.** A saddle-node tipping model (exact physics) with forcing read as cumulative CO₂: variance and lag-1 autocorrelation climb *before* the tip, and the tip does not reverse (hysteresis). A companion panel runs the *same* detector on real aggregate world-CO₂ growth and finds no clean signal — because the warning lives in subsystem fingerprints (AMOC, ice sheets, forests), not the aggregate.

Both probes hit the same wall: the physics is right, but no finite/local/aggregate measurement fully resolves the phase — and none of it tells us what we owe.

## Verified numbers (from the embedded data)

| dataset | levels PC1 (first→last) | growth PC1 (first→last) |
|---|---|---|
| world, 9 indicators, 1900–2022 | 0.82 → 0.90 | 0.47 → 0.47 |
| 40 countries (CO₂), 1910–2022 | 0.48 → 0.65 | 0.22 → 0.38 |
| Earth + human, 5 indicators, 1965–2022 | 0.90 → 0.92 | 0.49 → 0.46 |

PC1 share = λ_max(correlation matrix) / n, via power iteration; growth = log-growth for
strictly-positive series, first difference for the signed temperature anomaly.

## Data sources

- **Our World in Data / Global Carbon Project** — `owid-co2-data.csv` (emissions, population, energy).
- **NASA GISTEMP** — global land-ocean surface temperature anomaly (J-D annual).
- **NOAA Mauna Loa** — annual mean atmospheric CO₂ concentration.

All series are embedded in `index.html`; the build is fully reproducible (see below).

## Repo layout

```
.
├── index.html              # self-contained interactive (real data embedded)
├── data/
│   ├── build_data.py        # downloads sources → extracts series → writes data.json
│   └── data.json            # generated; also embedded inside index.html
├── README.md
└── PROJECT_HANDOFF.md       # full design notes & remaining work
```

## Rebuild / refresh the data

```bash
python3 data/build_data.py        # auto-downloads OWID, GISTEMP, Mauna Loa into /tmp
# regenerates /tmp/data.json and prints a headline-number sanity check;
# re-embed it into the <script id="data"> block of index.html
```

## References

- W. Steffen et al., "The trajectory of the Anthropocene: The Great Acceleration," *The Anthropocene Review* (2015).
- P. Ditlevsen & S. Ditlevsen, "Warning of a forthcoming collapse of the Atlantic meridional overturning circulation," *Nature Communications* (2023).
- Data: Our World in Data, Global Carbon Project, NASA GISTEMP, NOAA GML.
