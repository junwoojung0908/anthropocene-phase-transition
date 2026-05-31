# PROJECT HANDOFF — Anthropocene Phase-Transition Visualization

> For continuation in Claude Code / a GitHub repo. Read this first, then open
> `anthropocene_phase_transition.html`. The chat thread this came from will not
> carry over; this document + the HTML file are the full context.

**Author:** Junwoo Jung (정준우), KAIST Physics
**Course:** Anthropocene Humanities (Prof. Buhm Soon Park), 2026 Spring — **Final Project (30%)**
**Format:** Option 2 (creative/research work) — a web-based interactive. **Must clear the format with Prof. Park before finalizing.**
**Due:** Week 15 (6/9), with a 5-min show-and-tell at the Anthropocene Festival.

---

## 1. The core idea (what this is)

A **computational essay as an interactive web page**: it treats the Anthropocene
as a *phase transition in the Earth system* and then **honestly tests whether that
transition is actually visible in real data** — rather than asserting the metaphor.

The intellectual spine comes directly from the author's own course essays:

- **Week 9 ("Beyond Entanglement"):** the Anthropocene is a phase transition in
  *correlation structure*, invisible to *local order parameters*; near a transition
  correlation length diverges so *no finite/local measurement resolves the phase*;
  local metrics fail **structurally, not contingently**.
- **Week 5 ("Knowing What Cannot Be Seen"):** every representation is a
  *fact-metaphor* — it makes some features visible and hides others; even rigorous
  math is a translation with limits.
- **Recurring thesis across all essays (W7, W10, W12, W13, W14):** a single
  number/metric promises to settle a question it can't, by flattening what is
  incommensurable and hiding who/what it omits. ("The map is not the territory.")

**The conclusion the piece earns (not asserts):** the physics is right — the
Anthropocene really does have the shape of a transition in correlation structure —
but *which representation you choose decides what you can see*, no aggregate/local
measurement fully resolves it, and **physics does not yield ethics** (is–ought).
This is the honest, unresolved ending that fits the author's voice (process over
completion; Camus).

---

## 2. Structure of the page (current build = `anthropocene_phase_transition.html`)

Single self-contained HTML, scroll-based, editorial monochrome aesthetic
(paper/oxblood; Fraunces + Newsreader + Space Mono). Real data embedded as JSON in
a `<script id="data">` tag. All computation runs client-side in vanilla JS + canvas.

### Probe I — Correlation structure ("the transition the scale invents")
- Datasets: **9 world indicators** (default) and **51 countries (CO₂)**.
- Toggle **Levels ↔ Growth**; slider moves a correlation window through history.
- Renders: correlation-matrix **heatmap** (canvas) + **PC1-share-of-variance over
  time** line (canvas) + readout (PC1 share, mean correlation, window years).
- **The payoff:** Levels → matrix blazes red, PC1 ≈ 0.82→0.90 ("one synchronized
  system — a transition!"). Growth → it collapses, PC1 ≈ 0.47 flat. The clean
  transition was an **artifact of correlating monotone-rising levels**. What
  survives is episodic shared shocks (wars, oil crises, 2008, COVID), not a 1950
  phase change.
- Verified numbers (real data): world levels 0.82→0.90; world growth 0.47→0.47;
  country levels 0.60→0.67; country growth 0.46→0.38. **World is the strongest
  demonstration; country is weaker (see TODO).**

### Probe II — Critical slowing down ("the transition the data can barely see")
- A **saddle-node (tilted double-well) normal form** with additive noise, simulated
  live (Euler–Maruyama). Fold at μ_c = 2/(3√3) ≈ 0.385.
- The **forcing axis is read as cumulative CO₂** (real OWID series).
- Drag forcing or "Auto-ramp": as μ → fold, **variance & lag-1 autocorrelation**
  gauges climb *before* the tip; after tipping, pulling forcing back does **not**
  reverse it (**hysteresis = irreversibility**).
- **CSD is exact for this model** — so this is physics, not analogy. BUT the plotted
  state is a **model response, not a measured Earth variable** (stated in the page).
- **Honesty sub-panel:** the *same detector* run on **real world CO₂ growth** shows
  **no clean climb** (trend ≈ 0). The warning lives in subsystem fingerprints
  (AMOC, an ice sheet, a forest), not the aggregate.
- Real result cited: Ditlevsen & Ditlevsen 2023 (AMOC early warning).

### Close
Both probes hit the same wall → the unifying conclusion in §1.

---

## 3. Data (REAL — already used)

Source: **Our World in Data / Global Carbon Project**, file
`owid-co2-data.csv` (raw: `raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv`).

World-level coverage actually verified:

| indicator | range | n |
|---|---|---|
| population | 1750–2024 | 230 |
| co2 | 1750–2024 | 275 |
| coal_co2 | 1750–2024 | 275 |
| oil_co2 | 1855–2024 | 170 |
| gas_co2 | 1882–2024 | 143 |
| cement_co2 | 1880–2024 | 145 |
| land_use_change_co2 | 1850–2024 | 175 |
| methane | 1850–2024 | 175 |
| nitrous_oxide | 1850–2024 | 175 |
| cumulative_co2 | 1850–2024 | (forcing axis, Probe II) |
| gdp | 1820–2022 | **21 (sparse — Maddison decadal, not used in the matrix)** |
| primary_energy_consumption | 1965–2024 | **60 (too short — not used)** |

- Probe I "world" set = the 9 indicators with long annual coverage (population, co2,
  coal/oil/gas/cement co2, land_use_change_co2, methane, n2o), common range
  **1900–2022**.
- Probe I "country" set = 51 countries with CO₂ coverage ≥110 yrs, common range
  **1910–2022**.
- Probe II forcing = `cumulative_co2`, World, 1850–2022.

The embedded JSON in the HTML was generated from this CSV. To refresh/expand:
re-download the CSV, extract World rows + chosen country rows, write JSON, replace
the `<script id="data">` contents.

---

## 4. Methodology notes (KEEP THESE HONEST — they are the point)

1. **Levels correlate trivially.** Any monotone-rising series correlate near 1. So a
   "transition" read off levels is an artifact. Use **log-growth rates** for the
   honest signal. (Probe I makes this contrast the entire lesson.)
2. **PC1 share = λ_max / n** (trace of a correlation matrix = n). Computed via power
   iteration in JS — fine for n=9 and n=51.
3. **Finite system.** 9 (or 51) series is not a thermodynamic system; do **not**
   claim literal critical exponents or a clean critical point. Frame as the
   *empirical signature* the framework predicts, on real but finite/messy data.
4. **Correlation ≠ causation.** Isolating one subsystem's causal weight needs
   conditional mutual information I(B;A|Z) over the full network (Week 9). The
   correlation views can't deliver this — stated in the footer.
5. **Probe II state is a model, forcing is real.** Never present the simulated state
   as measured Earth data. CSD itself is an exact property of the model.
6. The visualization is itself a **fact-metaphor** (Week 5) — say so.

---

## 5. Remaining work (priority order)

1. **Strengthen Probe I's cross-system claim.** The 9-indicator set is all
   GHG/economic (human subsystem). To really show the *human↔Earth* coupling, add
   **independent Earth-system indicators** from the canonical **Steffen et al. (2015)
   "Great Acceleration" 24-indicator dataset** (surface temperature, atmospheric CO₂
   *concentration*, ocean acidification, marine fish capture, tropical forest loss,
   terrestrial biosphere degradation). Source: IGBP / Steffen 2015 supplementary.
   This is the single biggest upgrade and ties directly to the course (Steffen is a
   contributor to *Altered Earth*, the Week 14 book).
2. **Decide the country set's role.** Its levels-PC1 (~0.6) is less dramatic than
   world (~0.9). Either (a) keep world as the headline and country as a secondary
   "spatial" view, or (b) drop country and lean on world + Steffen indicators.
3. **Optional real positive for Probe II.** If a *measured* early-warning is wanted,
   wire in the actual AMOC fingerprint SST series (Ditlevsen 2023 data/code, likely
   on Zenodo/GitHub) and run the live detector on it — turning the honesty panel
   from "no signal in aggregate" into "signal in the right fingerprint."
4. **Language & slides.** Page is currently English. Decide Korean vs English.
   Trim captions into 1–2 slide-ready lines for the 5-min show-and-tell
   (the killer demo = Probe I Levels→Growth toggle + Probe II auto-ramp tip).
5. **Short accompanying statement (~1 page).** Basically already written across the
   author's essays — distill W9 + W5 + the recurring "scale that lies" thesis.
6. **Confirm format with Prof. Park** (Option 2 requires it).

---

## 6. Suggested repo structure (for Claude Code / GitHub Pages)

```
anthropocene-phase-transition/
├── index.html              # the page (rename from anthropocene_phase_transition.html)
├── data/
│   ├── build_data.py        # downloads OWID CSV, extracts series, writes data.json
│   └── data.json            # generated; or keep inlined in index.html
├── js/
│   ├── probe1_correlation.js
│   ├── probe2_csd.js
│   └── core.js              # logGrowth, winCorr, lambdaMax, meanOff
├── css/style.css
├── README.md
└── PROJECT_HANDOFF.md       # this file
```

Deploy: push to GitHub, enable Pages on `main` → same flow as the author's
"one-question-one-day" site. Keep it a single static page (no backend needed).

### Reusable numeric core (already written & tested in the HTML)
```js
function logGrowth(a){let o=[];for(let i=1;i<a.length;i++){let p=a[i-1]<=0?1e-9:a[i-1],c=a[i]<=0?1e-9:a[i];o.push(Math.log(c/p));}return o;}
function winCorr(vars,start,win){const n=vars.length;const z=vars.map(v=>{const s=v.slice(start,start+win);const m=s.reduce((a,b)=>a+b,0)/s.length;const sd=Math.sqrt(s.reduce((a,b)=>a+(b-m)*(b-m),0)/s.length)||1e-9;return s.map(x=>(x-m)/sd);});const C=[];for(let i=0;i<n;i++){C[i]=new Array(n);for(let j=0;j<n;j++){let s=0;for(let k=0;k<win;k++)s+=z[i][k]*z[j][k];C[i][j]=s/win;}}return C;}
function lambdaMax(C){const n=C.length;let v=new Array(n).fill(1/Math.sqrt(n));for(let it=0;it<70;it++){const w=new Array(n).fill(0);for(let i=0;i<n;i++){let s=0;for(let j=0;j<n;j++)s+=C[i][j]*v[j];w[i]=s;}let nm=Math.sqrt(w.reduce((a,b)=>a+b*b,0));if(nm<1e-12)break;for(let i=0;i<n;i++)v[i]=w[i]/nm;}let num=0,den=0;for(let i=0;i<n;i++){let r=0;for(let j=0;j<n;j++)r+=C[i][j]*v[j];num+=v[i]*r;den+=v[i]*v[i];}return num/den;}
```
Saddle-node CSD step: `dx = (-x³ + x + μ)·dt + σ·√dt·N(0,1)`, fold at μ_c=2/(3√3).

---

## 7. One-paragraph pitch (for the README / talk intro)

> If the Anthropocene is a phase transition in the Earth system, can we see it in the
> data? This interactive runs two honest probes on real records (1850–2022). The
> first shows that a "synchronized planet" read off rising curves is an artifact of
> the scale — detrend honestly and the clean transition dissolves. The second shows
> a real transition's fingerprint (critical slowing down) is exact in theory but
> washes out of the aggregate data we have on hand. Both end at the same wall: the
> physics is right, but no finite, local, or aggregate measurement resolves the
> phase — and none of it tells us what we owe. The map was never the territory.
