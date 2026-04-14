# ⛏ DevPro — Underground Development Productivity Suite

> **Operator-led continuous improvement · Lean mining methodology · Real-time panel intelligence**

DevPro is a Streamlit web application designed for underground coal development teams. It translates proven Process Improvement Event (PIE) methodology and time-and-motion benchmarks into an always-on, interactive toolkit that every supervisor, engineer and manager can use to drive measurable improvements in development metres.

---

## What It Does

| Module | Purpose |
|---|---|
| **Executive Overview** | Live KPI summary, proven results table, four-step PIE cycle guide, financial impact calculator |
| **Diagnostic Scanner** | Downtime Pareto, ranked opportunity table with estimated m/shift gains and annual revenue impact |
| **Golden Meter Builder** | Interactive 15-minute cutting sequence builder — 6-bolt, 8-bolt and mega-bolt variants |
| **Pillar Cycle Simulator** | Model the effect of manning, fans, belt downtime and bolting pattern on cycle time |
| **Live Takt Planner** | Editable weekly shift plan with cumulative metres vs target vs PIE benchmark |
| **Performance Dashboard** | Rolling actuals, crew benchmarking, crew performance gap revenue calculator, pillar history |
| **Downtime Loss Analyser** | Quantify metres and revenue lost per downtime category; re-ramp compound loss calculation |
| **Idea Bank & Action Tracker** | Crew-owned improvement ideas, PIE linkage, status tracking, gain-by-category chart |
| **Future PIE Generator** | Impact vs ease priority matrix, Wave backlog, revenue forecast, senior team diagnostic guide |

---

## Key Benchmarks Built Into the App

All benchmarks are derived from real-world PIE programme outcomes in underground coal development:

| Metric | Baseline | Post-PIE Achieved | Target |
|---|---|---|---|
| Pillar cycle — green roof | 24 shifts | 17 shifts | 14 shifts |
| Pillar cycle — high clay | 32 shifts | 22 shifts | 18 shifts |
| Cut rate — 8-bolt green | 2.0–2.5 m/hr | 2.8–4.0 m/hr | 4.0 m/hr |
| Cut rate — 6-bolt green | — | 3.5–4.5 m/hr | 4.5 m/hr |
| Cut rate — mega-bolt | — | 2.4 m/hr | 2.7–3.0 m/hr |
| Weekly metres — green | ~140 m | 220–235 m | 235 m |
| Belt downtime | 20–30% | Reducing | < 5% |
| Operators on CM | 3–4 | 5–7 | 7 |

---

## Deploy to Streamlit Cloud

### Step 1 — Fork or clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/devpro.git
cd devpro
```

### Step 2 — Push to GitHub

Ensure the repository contains:

```
devpro/
├── app.py
├── requirements.txt
└── README.md
```

### Step 3 — Connect to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your GitHub account
2. Click **New app**
3. Select your repository, branch (`main`) and set the **Main file path** to `app.py`
4. Click **Deploy**

Streamlit Cloud will install dependencies from `requirements.txt` automatically. The app is typically live within 2–3 minutes.

### Step 4 — Share

Copy the generated URL (format: `https://YOUR_USERNAME-devpro-app-XXXX.streamlit.app`) and share it with your team. No installation required on any device — runs in any modern browser.

---

## Run Locally

### Prerequisites

- Python 3.10 or higher
- pip

### Install and launch

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/devpro.git
cd devpro

# (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## Project Structure

```
devpro/
├── app.py              # Main Streamlit application — all modules in one file
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Configuration

All global settings are available in the **sidebar at runtime** — no code changes required:

| Setting | Default | Description |
|---|---|---|
| HCC Price (AUD/t) | 220 | Hard coking coal reference price — drives all financial calculations |
| LW Float (days) | 95 | Current development days ahead of the longwall — triggers status alerts |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.35.0 | Web application framework |
| `plotly` | ≥ 5.22.0 | Interactive charts and visualisations |
| `pandas` | ≥ 2.2.0 | Data manipulation and tabular display |
| `numpy` | ≥ 1.26.0 | Numerical calculations |

---

## Session Data

All data entered during a session (Golden Meter observations, shift log actuals, Takt plan updates, Idea Bank entries, pillar history) is held in **Streamlit session state**. It persists for the duration of the browser session and resets on page refresh. For persistent storage across sessions, the data editor components can be extended to read from and write to a CSV, database, or cloud storage backend.

---

## Licence

This application is provided for demonstration and operational use. All benchmark data and methodology is derived from real-world underground coal development PIE programmes. No mine-specific, operator-specific or company-specific data is embedded in the application.

---

## Contributing

Pull requests are welcome. For major changes please open an issue first to discuss the proposed modification.

```
git checkout -b feature/your-feature-name
git commit -m "Add: description of change"
git push origin feature/your-feature-name
```

---

*DevPro v2.0 · Lean Mining Methodology · Built for underground coal development teams*
