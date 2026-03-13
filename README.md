# Bitcoin Sentiment x Hyperliquid Performance Intelligence

Research-grade analysis pipeline and interactive dashboard for studying how Bitcoin Fear & Greed regimes influence trader performance on Hyperliquid.

## Live Dashboard

- Production URL: https://fina-khaki.vercel.app

## Highlights

- Regime-level PnL and win-rate breakdown (Extreme Fear to Extreme Greed)
- Account-level divergence analysis (fear-dominant vs greed-dominant traders)
- Daily sentiment versus net PnL diagnostics
- Frontend command-deck dashboard with interactive charts
- Auto-generated report tables, figures, JSON payload, and browser data script

## Project Structure

- `analysis/run_analysis.py`: End-to-end analysis pipeline
- `data/raw/historical_data`: Raw trader executions
- `data/raw/fear_greed_data`: Raw sentiment dataset
- `reports/analysis_report.md`: Narrative summary report
- `reports/tables/`: CSV outputs
- `reports/figures/`: Generated PNG figures
- `reports/dashboard_data.json`: Dashboard payload (JSON)
- `frontend/dashboard-v2.html`: Main dashboard entry page
- `frontend/app.js`: Frontend rendering and chart logic
- `frontend/styles.css`: Dashboard theme and layout
- `frontend/assets/dashboard-data.js`: Browser-consumable payload (`window.__DASHBOARD_DATA__`)

## Requirements

- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Analysis

From project root:

```bash
python analysis/run_analysis.py
```

Generated artifacts:

- `reports/tables/sentiment_summary.csv`
- `reports/tables/daily_summary.csv`
- `reports/tables/account_regime_summary.csv`
- `reports/analysis_report.md`
- `reports/dashboard_data.json`
- `frontend/assets/dashboard-data.js`
- `reports/figures/net_pnl_per_trade_by_sentiment.png`
- `reports/figures/net_pnl_distribution_by_sentiment.png`
- `reports/figures/daily_sentiment_vs_net_pnl.png`

## Run Frontend Locally

```bash
python -m http.server 8000
```

Open:

- http://127.0.0.1:8000/frontend/dashboard-v2.html

Note: `frontend/index.html` redirects to the latest dashboard page.

## Deploy to Vercel

This repository is configured as a static deployment.

```bash
npx vercel --prod --yes
```

After deployment, Vercel provides:

- Inspect URL (build/deploy metadata)
- Production URL (immutable deployment)
- Alias URL (project domain)

Current alias:

- https://fina-khaki.vercel.app

## Analytical Scope

- Sentiment regime effect on fee-adjusted net PnL per trade
- Regime-level participation and trade sizing patterns
- Fear-versus-greed aggregate performance split
- High-activity account behavior by regime
- Daily sentiment-to-PnL relationship strength

## Caveats

- Leverage is not available in the source trade file, so leverage-adjusted analysis is out of scope.
- Closed PnL at trade level can include broader position context.
- Sentiment join is daily; intraday sentiment shifts are not captured.

## Stack

- Python: pandas, numpy, matplotlib
- Frontend: HTML, CSS, vanilla JavaScript, Chart.js
- Hosting: Vercel
