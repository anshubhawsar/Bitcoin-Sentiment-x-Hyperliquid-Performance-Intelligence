# Bitcoin Sentiment x Hyperliquid Performance Intelligence

A data pipeline and interactive dashboard that analyze how Bitcoin Fear & Greed sentiment regimes relate to trader performance on Hyperliquid.

The project combines:
- Regime-level performance analytics
- Account-level behavior profiling
- Daily sentiment vs PnL diagnostics
- A modern frontend dashboard for fast visual exploration

## What This Project Does

- Loads and standardizes raw trade and sentiment datasets
- Joins trade activity with daily sentiment regimes
- Computes fee-adjusted performance metrics
- Produces structured outputs for reporting and visualization
- Exports a dashboard-ready data payload used directly by the frontend

## Repository Structure

- `analysis/run_analysis.py`: Main analysis pipeline
- `data/raw/historical_data`: Raw trader execution data
- `data/raw/fear_greed_data`: Raw Bitcoin Fear & Greed data
- `reports/analysis_report.md`: Narrative report with section-wise findings
- `reports/tables/`: CSV output tables
- `reports/figures/`: Generated analysis charts
- `reports/dashboard_data.json`: Dashboard data payload (JSON)
- `frontend/dashboard-v2.html`: Main interactive dashboard page
- `frontend/app.js`: Frontend rendering logic and chart configuration
- `frontend/styles.css`: Dashboard design system and layout
- `frontend/assets/dashboard-data.js`: Browser-consumable data export

## Requirements

- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Analysis Pipeline

From the repository root:

```bash
python analysis/run_analysis.py
```

This generates:
- `reports/tables/sentiment_summary.csv`
- `reports/tables/daily_summary.csv`
- `reports/tables/account_regime_summary.csv`
- `reports/analysis_report.md`
- `reports/dashboard_data.json`
- `frontend/assets/dashboard-data.js`
- figure files under `reports/figures/`

## Launch the Dashboard Locally

Start a local static server from repo root:

```bash
python -m http.server 8000
```

Open:

- `http://127.0.0.1:8000/frontend/dashboard-v2.html`

`frontend/index.html` redirects to the latest dashboard page.

## Core Analytical Outputs

- Sentiment regime comparison (Extreme Fear -> Extreme Greed)
- Net PnL per trade and win-rate behavior by regime
- Fear-vs-greed aggregate performance split
- Top accounts by fear-minus-greed performance divergence
- Daily sentiment-to-PnL relationship diagnostics

## Notes and Caveats

- The source trader file does not include leverage; leverage-adjusted analysis is not included.
- Trade-level closed PnL may reflect broader position context.
- Sentiment is joined at daily granularity, so intraday sentiment shifts are not represented.

## Tech Stack

- Python: pandas, numpy, matplotlib
- Frontend: HTML, CSS, vanilla JavaScript, Chart.js

## Reproducibility

For reproducible outputs:
- Keep raw input files unchanged in `data/raw/`
- Re-run `analysis/run_analysis.py`
- Serve the `frontend/` directory through a local HTTP server
