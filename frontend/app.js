(function () {
  const data = window.__DASHBOARD_DATA__;

  if (!data || !data.overview) {
    document.body.innerHTML = "<div style='padding:24px;color:#fff;font-family:sans-serif'>Dashboard data is missing. Run analysis pipeline first.</div>";
    return;
  }

  const overview = data.overview;
  const regimeSummary = data.regimeSummary || [];
  const dailySeries = data.dailySeries || [];
  const topFearAccounts = data.topFearAccounts || [];
  const topGreedAccounts = data.topGreedAccounts || [];
  const highActivityBehavior = data.highActivityBehavior || [];

  const regimeOrder = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"];
  const regimeColor = {
    "Extreme Fear": "#ff6f7d",
    Fear: "#f8bf5b",
    Neutral: "#8394ff",
    Greed: "#3ac5d8",
    "Extreme Greed": "#29e0b1"
  };

  function num(value) {
    return Number(value || 0);
  }

  function usd(value) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0
    }).format(num(value));
  }

  function usdShort(value) {
    const v = num(value);
    const abs = Math.abs(v);
    if (abs >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(2)}B`;
    if (abs >= 1_000_000) return `${(v / 1_000_000).toFixed(2)}M`;
    if (abs >= 1_000) return `${(v / 1_000).toFixed(2)}K`;
    return v.toFixed(2);
  }

  function pct(value) {
    return `${(num(value) * 100).toFixed(1)}%`;
  }

  function accountShort(account) {
    if (!account || account.length < 12) return account;
    return `${account.slice(0, 6)}...${account.slice(-4)}`;
  }

  function heatColor(value, min, max) {
    const n = num(value);
    const range = Math.max(max - min, 1);
    const ratio = (n - min) / range;
    const r = Math.round(255 - ratio * 180);
    const g = Math.round(90 + ratio * 150);
    const b = Math.round(120 + ratio * 120);
    return `rgb(${r}, ${g}, ${b})`;
  }

  function aggregateSeries(series, maxPoints) {
    if (series.length <= maxPoints) return series;

    const sorted = [...series].sort((a, b) => new Date(a.trade_date) - new Date(b.trade_date));
    const bucketSize = Math.ceil(sorted.length / maxPoints);
    const out = [];

    for (let i = 0; i < sorted.length; i += bucketSize) {
      const bucket = sorted.slice(i, i + bucketSize);
      const date = bucket[bucket.length - 1].trade_date;
      const pnl = bucket.reduce((sum, row) => sum + num(row.daily_net_pnl), 0);
      const sentiment = bucket.reduce((sum, row) => sum + num(row.sentiment_value), 0) / bucket.length;
      out.push({ trade_date: date, daily_net_pnl: pnl, sentiment_value: sentiment });
    }

    return out;
  }

  function setHero() {
    const strong = overview.strongestRegime || {};
    const weak = overview.weakestRegime || {};

    const signalEl = document.getElementById("hero-signal-text");
    const strongEl = document.getElementById("hero-strong-regime");
    const weakEl = document.getElementById("hero-weak-regime");
    const fearEl = document.getElementById("hero-fear");
    const greedEl = document.getElementById("hero-greed");

    if (signalEl) {
      signalEl.textContent = `${strong.classification || "N/A"} leads at ${usdShort(strong.netPnlPerTrade)} per trade, while correlation stays weak at ${num(overview.sentimentCorrelation).toFixed(3)}.`;
    }
    if (strongEl) strongEl.textContent = strong.classification || "-";
    if (weakEl) weakEl.textContent = weak.classification || "-";
    if (fearEl) fearEl.textContent = usd(overview.fearNetPnl);
    if (greedEl) greedEl.textContent = usd(overview.greedNetPnl);
  }

  function renderMetrics() {
    const grid = document.getElementById("metric-grid");
    if (!grid) return;

    const metrics = [
      { label: "Total Net PnL", value: usd(overview.totalNetPnl) },
      { label: "Trades", value: new Intl.NumberFormat("en-US").format(num(overview.trades)) },
      { label: "Accounts", value: new Intl.NumberFormat("en-US").format(num(overview.accounts)) },
      { label: "Overall Win Rate", value: pct(overview.overallWinRate) },
      { label: "Sentiment Correlation", value: num(overview.sentimentCorrelation).toFixed(3) },
      { label: "Coverage", value: `${overview.startDate} to ${overview.endDate}` }
    ];

    grid.innerHTML = metrics
      .map(
        (m) =>
          `<article class="metric"><small>${m.label}</small><strong>${m.value}</strong></article>`
      )
      .join("");
  }

  function renderFindings() {
    const el = document.getElementById("findings-grid");
    if (!el) return;

    const findings = data.findings || [];
    el.innerHTML = findings
      .slice(0, 6)
      .map((item) => `<div class="finding">${item}</div>`)
      .join("");
  }

  function renderRegimeChart() {
    const canvas = document.getElementById("regime-chart");
    if (!canvas) return;

    const ordered = regimeOrder
      .map((name) => regimeSummary.find((row) => row.classification === name))
      .filter(Boolean);

    const labels = ordered.map((r) => r.classification);
    const pnlPerTrade = ordered.map((r) => num(r.net_pnl_per_trade));
    const winRate = ordered.map((r) => num(r.win_rate) * 100);

    new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            type: "bar",
            label: "Net PnL / Trade",
            data: pnlPerTrade,
            backgroundColor: labels.map((l) => regimeColor[l] || "#9fb3ff"),
            borderRadius: 10,
            yAxisID: "y"
          },
          {
            type: "line",
            label: "Win Rate %",
            data: winRate,
            yAxisID: "y1",
            borderColor: "#ffffff",
            backgroundColor: "rgba(255,255,255,0.2)",
            borderWidth: 2,
            pointRadius: 4,
            tension: 0.35
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#d7e2ff" } },
          tooltip: { mode: "index", intersect: false }
        },
        scales: {
          x: { ticks: { color: "#b8c6f5" }, grid: { color: "rgba(255,255,255,0.08)" } },
          y: {
            position: "left",
            ticks: { color: "#b8c6f5" },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y1: {
            position: "right",
            ticks: { color: "#e9efff" },
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  }

  function renderTimelineChart() {
    const canvas = document.getElementById("timeline-chart");
    if (!canvas) return;

    const compact = aggregateSeries(dailySeries, 220);
    const labels = compact.map((row) => row.trade_date);
    const pnl = compact.map((row) => num(row.daily_net_pnl));
    const sentiment = compact.map((row) => num(row.sentiment_value));

    new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            type: "bar",
            label: "Net PnL",
            data: pnl,
            backgroundColor: pnl.map((v) => (v >= 0 ? "rgba(30, 200, 165, 0.58)" : "rgba(255, 111, 125, 0.58)")),
            borderWidth: 0,
            yAxisID: "y"
          },
          {
            type: "line",
            label: "Sentiment Index",
            data: sentiment,
            borderColor: "#33d9f4",
            backgroundColor: "rgba(51, 217, 244, 0.2)",
            borderWidth: 2,
            tension: 0.25,
            pointRadius: 0,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { color: "#d7e2ff" } },
          tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.dataset.yAxisID === "y1" ? ctx.parsed.y.toFixed(1) : usd(ctx.parsed.y)}` } }
        },
        scales: {
          x: {
            ticks: { color: "#a5b4e7", maxTicksLimit: 10 },
            grid: { color: "rgba(255,255,255,0.05)" }
          },
          y: {
            ticks: { color: "#b9c7f4", callback: (value) => usdShort(value) },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y1: {
            position: "right",
            min: 0,
            max: 100,
            ticks: { color: "#7fefff" },
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  }

  function renderSplitChart() {
    const canvas = document.getElementById("split-chart");
    if (!canvas) return;

    new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: ["Fear Regimes", "Greed Regimes"],
        datasets: [
          {
            data: [num(overview.fearNetPnl), num(overview.greedNetPnl)],
            backgroundColor: ["#f8bf5b", "#29e0b1"],
            borderColor: ["#f8bf5b", "#29e0b1"],
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#d7e2ff" } },
          tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${usd(ctx.parsed)}` } }
        }
      }
    });
  }

  function renderAccountChart() {
    const canvas = document.getElementById("account-chart");
    if (!canvas) return;

    const joined = [...topFearAccounts, ...topGreedAccounts];
    const unique = new Map();
    joined.forEach((row) => {
      if (!unique.has(row.account)) unique.set(row.account, row);
    });

    const leaders = [...unique.values()]
      .sort((a, b) => Math.abs(num(b.fear_minus_greed)) - Math.abs(num(a.fear_minus_greed)))
      .slice(0, 10)
      .reverse();

    new Chart(canvas, {
      type: "bar",
      data: {
        labels: leaders.map((r) => accountShort(r.account)),
        datasets: [
          {
            label: "Fear - Greed Net PnL",
            data: leaders.map((r) => num(r.fear_minus_greed)),
            backgroundColor: leaders.map((r) => (num(r.fear_minus_greed) >= 0 ? "rgba(51, 217, 244, 0.72)" : "rgba(255, 111, 125, 0.72)")),
            borderRadius: 9
          }
        ]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#d7e2ff" } },
          tooltip: { callbacks: { label: (ctx) => usd(ctx.parsed.x) } }
        },
        scales: {
          x: {
            ticks: { color: "#b8c6f5", callback: (value) => usdShort(value) },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y: {
            ticks: { color: "#b8c6f5" },
            grid: { color: "rgba(255,255,255,0.04)" }
          }
        }
      }
    });
  }

  function renderBubbleChart() {
    const canvas = document.getElementById("bubble-chart");
    if (!canvas) return;

    const xMap = {
      "Extreme Fear": 10,
      Fear: 30,
      Neutral: 50,
      Greed: 70,
      "Extreme Greed": 90
    };

    const points = highActivityBehavior.slice(0, 200).map((row) => ({
      x: xMap[row.classification] || 50,
      y: num(row.net_pnl),
      r: Math.max(4, Math.min(18, Math.sqrt(Math.max(num(row.trades), 1)) / 2.2)),
      classification: row.classification,
      account: row.account,
      trades: num(row.trades)
    }));

    new Chart(canvas, {
      type: "bubble",
      data: {
        datasets: [
          {
            label: "Activity Points",
            data: points,
            backgroundColor: points.map((p) => `${regimeColor[p.classification] || "#9bb1ff"}aa`),
            borderColor: points.map((p) => regimeColor[p.classification] || "#9bb1ff"),
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#d7e2ff" } },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const p = ctx.raw;
                return `${accountShort(p.account)} | ${p.classification} | trades ${p.trades} | net ${usd(p.y)}`;
              }
            }
          }
        },
        scales: {
          x: {
            min: 0,
            max: 100,
            ticks: {
              color: "#b8c6f5",
              callback: (value) => {
                if (value === 10) return "Extreme Fear";
                if (value === 30) return "Fear";
                if (value === 50) return "Neutral";
                if (value === 70) return "Greed";
                if (value === 90) return "Extreme Greed";
                return "";
              }
            },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y: {
            ticks: { color: "#b8c6f5", callback: (value) => usdShort(value) },
            grid: { color: "rgba(255,255,255,0.08)" }
          }
        }
      }
    });
  }

  function renderHeatmap() {
    const root = document.getElementById("heatmap");
    if (!root) return;

    const joined = [...topFearAccounts, ...topGreedAccounts];
    const unique = new Map();
    joined.forEach((row) => {
      if (!unique.has(row.account)) unique.set(row.account, row);
    });

    const rows = [...unique.values()].slice(0, 8);
    const values = [];

    rows.forEach((row) => {
      regimeOrder.forEach((regime) => {
        values.push(num(row[regime]));
      });
    });

    const min = Math.min(...values);
    const max = Math.max(...values);

    const header = document.createElement("div");
    header.className = "heat-row";
    header.innerHTML = `<div class="heat-label"></div>${regimeOrder.map((r) => `<div class="heat-cell" style="background:rgba(132,149,255,0.18)">${r}</div>`).join("")}`;
    root.appendChild(header);

    rows.forEach((row) => {
      const rowEl = document.createElement("div");
      rowEl.className = "heat-row";

      const cells = regimeOrder
        .map((regime) => {
          const v = num(row[regime]);
          const bg = heatColor(v, min, max);
          return `<div class="heat-cell" style="background:${bg}">${usdShort(v)}</div>`;
        })
        .join("");

      rowEl.innerHTML = `<div class="heat-label">${accountShort(row.account)}</div>${cells}`;
      root.appendChild(rowEl);
    });
  }

  function renderCaveats() {
    const root = document.getElementById("caveats");
    if (!root) return;

    const caveats = data.caveats || [];
    root.innerHTML = caveats.map((c) => `<div class="caveat">${c}</div>`).join("");
  }

  function initChartsTheme() {
    Chart.defaults.color = "#cdd8ff";
    Chart.defaults.font.family = "Sora, sans-serif";
    Chart.defaults.animation.duration = 1000;
  }

  setHero();
  renderMetrics();
  renderFindings();
  initChartsTheme();
  renderRegimeChart();
  renderTimelineChart();
  renderSplitChart();
  renderAccountChart();
  renderBubbleChart();
  renderHeatmap();
  renderCaveats();
})();
