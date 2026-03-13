from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"
TABLE_DIR = REPORT_DIR / "tables"
FIGURE_DIR = REPORT_DIR / "figures"
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_ASSET_DIR = FRONTEND_DIR / "assets"

SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
SENTIMENT_SCORE = {
    "Extreme Fear": 0,
    "Fear": 25,
    "Neutral": 50,
    "Greed": 75,
    "Extreme Greed": 100,
}


@dataclass(frozen=True)
class AnalysisOutputs:
    sentiment_summary: Path
    daily_summary: Path
    account_summary: Path
    report: Path
    dashboard_data: Path
    dashboard_script: Path


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    trader = pd.read_csv(RAW_DIR / "historical_data")
    sentiment = pd.read_csv(RAW_DIR / "fear_greed_data")
    return trader, sentiment


def prepare_datasets(trader: pd.DataFrame, sentiment: pd.DataFrame) -> pd.DataFrame:
    df = trader.rename(
        columns={
            "Account": "account",
            "Coin": "coin",
            "Execution Price": "execution_price",
            "Size Tokens": "size_tokens",
            "Size USD": "size_usd",
            "Side": "side",
            "Timestamp IST": "timestamp_ist",
            "Start Position": "start_position",
            "Direction": "direction",
            "Closed PnL": "closed_pnl",
            "Transaction Hash": "transaction_hash",
            "Order ID": "order_id",
            "Crossed": "crossed",
            "Fee": "fee",
            "Trade ID": "trade_id",
            "Timestamp": "timestamp",
        }
    ).copy()

    df["trade_time"] = pd.to_datetime(df["timestamp_ist"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["trade_date"] = df["trade_time"].dt.normalize()

    numeric_cols = ["execution_price", "size_tokens", "size_usd", "start_position", "closed_pnl", "fee"]
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    sentiment_df = sentiment.rename(
        columns={
            "timestamp": "sentiment_timestamp",
            "value": "sentiment_value",
            "classification": "classification",
            "date": "sentiment_date",
        }
    ).copy()
    sentiment_df["trade_date"] = pd.to_datetime(sentiment_df["sentiment_date"], errors="coerce")

    merged = df.merge(
        sentiment_df[["trade_date", "sentiment_value", "classification"]],
        on="trade_date",
        how="left",
    )

    merged = merged.dropna(subset=["trade_time", "classification"]).copy()
    merged["net_pnl"] = merged["closed_pnl"] - merged["fee"]
    merged["is_win"] = merged["closed_pnl"] > 0
    merged["is_buy"] = merged["side"].astype(str).str.upper().eq("BUY")
    merged["pnl_per_usd"] = np.where(merged["size_usd"].ne(0), merged["net_pnl"] / merged["size_usd"], np.nan)
    merged["sentiment_value_from_class"] = merged["classification"].map(SENTIMENT_SCORE)
    merged["sentiment_bucket"] = pd.Categorical(merged["classification"], categories=SENTIMENT_ORDER, ordered=True)
    return merged


def build_sentiment_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("sentiment_bucket", observed=True)
        .agg(
            trades=("account", "size"),
            unique_accounts=("account", "nunique"),
            total_size_usd=("size_usd", "sum"),
            gross_pnl=("closed_pnl", "sum"),
            total_fees=("fee", "sum"),
            net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            median_net_pnl=("net_pnl", "median"),
            win_rate=("is_win", "mean"),
            buy_share=("is_buy", "mean"),
            avg_size_usd=("size_usd", "mean"),
            median_pnl_per_usd=("pnl_per_usd", "median"),
            mean_pnl_per_usd=("pnl_per_usd", "mean"),
        )
        .reset_index()
        .rename(columns={"sentiment_bucket": "classification"})
    )
    summary["net_pnl_per_trade"] = summary["net_pnl"] / summary["trades"]
    summary["fee_to_gross_pnl"] = np.where(summary["gross_pnl"].ne(0), summary["total_fees"] / summary["gross_pnl"], np.nan)
    return summary


def build_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        df.groupby(["trade_date", "classification"], observed=True)
        .agg(
            trades=("account", "size"),
            active_accounts=("account", "nunique"),
            daily_size_usd=("size_usd", "sum"),
            daily_net_pnl=("net_pnl", "sum"),
            daily_win_rate=("is_win", "mean"),
            sentiment_value=("sentiment_value", "first"),
        )
        .reset_index()
        .sort_values("trade_date")
    )
    daily["daily_net_pnl_per_trade"] = daily["daily_net_pnl"] / daily["trades"]
    return daily


def build_account_summary(df: pd.DataFrame) -> pd.DataFrame:
    account_regime = (
        df.groupby(["account", "classification"], observed=True)
        .agg(
            trades=("account", "size"),
            net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            win_rate=("is_win", "mean"),
            total_size_usd=("size_usd", "sum"),
        )
        .reset_index()
    )

    pivot = account_regime.pivot(index="account", columns="classification", values="net_pnl").fillna(0.0)
    for column in SENTIMENT_ORDER:
        if column not in pivot.columns:
            pivot[column] = 0.0
    pivot = pivot[SENTIMENT_ORDER]
    pivot["fear_net_pnl"] = pivot["Extreme Fear"] + pivot["Fear"]
    pivot["greed_net_pnl"] = pivot["Greed"] + pivot["Extreme Greed"]
    pivot["fear_minus_greed"] = pivot["fear_net_pnl"] - pivot["greed_net_pnl"]
    pivot = pivot.reset_index()

    total_trades = df.groupby("account").size().rename("all_trades")
    total_net = df.groupby("account")["net_pnl"].sum().rename("all_net_pnl")
    total_win = df.groupby("account")["is_win"].mean().rename("all_win_rate")
    return pivot.merge(total_trades, on="account").merge(total_net, on="account").merge(total_win, on="account")


def create_figures(df: pd.DataFrame, sentiment_summary: pd.DataFrame, daily_summary: pd.DataFrame) -> None:
    plt.style.use("ggplot")

    fig, ax = plt.subplots(figsize=(9, 5))
    ordered_summary = sentiment_summary.set_index("classification").reindex(SENTIMENT_ORDER).reset_index()
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(ordered_summary)))
    ax.bar(ordered_summary["classification"], ordered_summary["net_pnl_per_trade"], color=colors)
    ax.set_title("Fee-adjusted net PnL per trade by sentiment")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Net PnL per trade")
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "net_pnl_per_trade_by_sentiment.png", dpi=180)
    plt.close(fig)

    clipped = df.copy()
    lower = clipped["net_pnl"].quantile(0.01)
    upper = clipped["net_pnl"].quantile(0.99)
    clipped["net_pnl_clipped"] = clipped["net_pnl"].clip(lower=lower, upper=upper)
    fig, ax = plt.subplots(figsize=(9, 5))
    boxplot_data = [
        clipped.loc[clipped["classification"] == sentiment, "net_pnl_clipped"].dropna().to_numpy()
        for sentiment in SENTIMENT_ORDER
    ]
    boxplot = ax.boxplot(boxplot_data, tick_labels=SENTIMENT_ORDER, patch_artist=True)
    for patch, color in zip(boxplot["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_title("Trade net PnL distribution by sentiment (1st-99th pct clipped)")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Clipped net PnL")
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "net_pnl_distribution_by_sentiment.png", dpi=180)
    plt.close(fig)

    daily_rollup = (
        daily_summary.groupby("trade_date", observed=True)
        .agg(
            daily_net_pnl=("daily_net_pnl", "sum"),
            trades=("trades", "sum"),
            sentiment_value=("sentiment_value", "mean"),
        )
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    scatter = ax.scatter(
        daily_rollup["sentiment_value"],
        daily_rollup["daily_net_pnl"],
        c=daily_rollup["trades"],
        cmap="viridis",
        alpha=0.8,
    )
    ax.set_title("Daily sentiment value versus fee-adjusted net PnL")
    ax.set_xlabel("Fear & Greed index value")
    ax.set_ylabel("Daily net PnL")
    cbar = fig.colorbar(scatter)
    cbar.set_label("Daily trade count")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "daily_sentiment_vs_net_pnl.png", dpi=180)
    plt.close(fig)


def format_currency(value: float) -> str:
    return f"{value:,.2f}"


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def render_table(df: pd.DataFrame, columns: list[str] | None = None, float_format: str = "{:.4f}") -> str:
    table = df if columns is None else df[columns]
    return "```\n" + table.to_string(index=False, float_format=lambda value: float_format.format(value)) + "\n```"


def build_dashboard_payload(
    df: pd.DataFrame,
    sentiment_summary: pd.DataFrame,
    daily_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
) -> dict:
    total_trades = int(len(df))
    total_accounts = int(df["account"].nunique())
    total_net = float(df["net_pnl"].sum())
    total_win_rate = float(df["is_win"].mean())
    trade_start = df["trade_time"].min().strftime("%Y-%m-%d")
    trade_end = df["trade_time"].max().strftime("%Y-%m-%d")

    best_regime = sentiment_summary.sort_values("net_pnl_per_trade", ascending=False).iloc[0]
    worst_regime = sentiment_summary.sort_values("net_pnl_per_trade", ascending=True).iloc[0]

    fear_net = float(
        sentiment_summary[sentiment_summary["classification"].isin(["Extreme Fear", "Fear"])]["net_pnl"].sum()
    )
    greed_net = float(
        sentiment_summary[sentiment_summary["classification"].isin(["Greed", "Extreme Greed"])]["net_pnl"].sum()
    )

    daily_rollup = (
        daily_summary.groupby("trade_date", observed=True)
        .agg(
            daily_net_pnl=("daily_net_pnl", "sum"),
            trades=("trades", "sum"),
            sentiment_value=("sentiment_value", "mean"),
        )
        .reset_index()
        .sort_values("trade_date")
    )
    daily_rollup["trade_date"] = pd.to_datetime(daily_rollup["trade_date"]).dt.strftime("%Y-%m-%d")
    sentiment_corr = float(daily_rollup["sentiment_value"].corr(daily_rollup["daily_net_pnl"]))

    top_fear = account_summary.sort_values("fear_minus_greed", ascending=False).head(5).copy()
    top_greed = account_summary.sort_values("fear_minus_greed", ascending=True).head(5).copy()

    high_activity = df["account"].value_counts().head(10).index
    account_behavior = (
        df[df["account"].isin(high_activity)]
        .groupby(["account", "classification"], observed=True)
        .agg(net_pnl=("net_pnl", "sum"), trades=("account", "size"), win_rate=("is_win", "mean"))
        .reset_index()
        .sort_values(["account", "classification"])
    )

    findings = [
        f"Strongest regime: {best_regime['classification']} with {best_regime['net_pnl_per_trade']:.2f} net PnL per trade.",
        f"Weakest regime: {worst_regime['classification']} with {worst_regime['net_pnl_per_trade']:.2f} net PnL per trade.",
        f"Fear regimes delivered {fear_net:,.2f} net PnL versus {greed_net:,.2f} in greed regimes.",
        f"Daily sentiment-to-PnL correlation was {sentiment_corr:.3f}, indicating a weak linear relationship.",
        "Median trade-level net PnL stayed near zero across regimes, implying performance is driven by skew rather than steady small wins.",
    ]

    return {
        "overview": {
            "trades": total_trades,
            "accounts": total_accounts,
            "startDate": trade_start,
            "endDate": trade_end,
            "totalNetPnl": total_net,
            "overallWinRate": total_win_rate,
            "sentimentCorrelation": sentiment_corr,
            "fearNetPnl": fear_net,
            "greedNetPnl": greed_net,
            "strongestRegime": {
                "classification": str(best_regime["classification"]),
                "netPnlPerTrade": float(best_regime["net_pnl_per_trade"]),
                "winRate": float(best_regime["win_rate"]),
            },
            "weakestRegime": {
                "classification": str(worst_regime["classification"]),
                "netPnlPerTrade": float(worst_regime["net_pnl_per_trade"]),
                "winRate": float(worst_regime["win_rate"]),
            },
        },
        "findings": findings,
        "regimeSummary": json.loads(sentiment_summary.to_json(orient="records")),
        "dailySeries": json.loads(daily_rollup.to_json(orient="records")),
        "topFearAccounts": json.loads(top_fear.to_json(orient="records")),
        "topGreedAccounts": json.loads(top_greed.to_json(orient="records")),
        "highActivityBehavior": json.loads(account_behavior.to_json(orient="records")),
        "figures": {
            "netPnlPerTrade": "reports/figures/net_pnl_per_trade_by_sentiment.png",
            "distribution": "reports/figures/net_pnl_distribution_by_sentiment.png",
            "dailyScatter": "reports/figures/daily_sentiment_vs_net_pnl.png",
        },
        "caveats": [
            "The provided trader dataset does not include leverage, so leverage-adjusted analysis was not possible.",
            "Closed PnL is realized at trade events and can reflect broader position context, not a clean isolated return for each fill.",
            "Sentiment is joined at daily granularity, so intraday sentiment shifts are not represented.",
        ],
    }


def build_report(df: pd.DataFrame, sentiment_summary: pd.DataFrame, daily_summary: pd.DataFrame, account_summary: pd.DataFrame) -> str:
    total_trades = len(df)
    trade_start = df["trade_time"].min().strftime("%Y-%m-%d")
    trade_end = df["trade_time"].max().strftime("%Y-%m-%d")
    total_accounts = df["account"].nunique()
    total_net = df["net_pnl"].sum()
    total_win_rate = df["is_win"].mean()

    best_regime = sentiment_summary.sort_values("net_pnl_per_trade", ascending=False).iloc[0]
    worst_regime = sentiment_summary.sort_values("net_pnl_per_trade", ascending=True).iloc[0]

    fear_net = sentiment_summary[sentiment_summary["classification"].isin(["Extreme Fear", "Fear"])]["net_pnl"].sum()
    greed_net = sentiment_summary[sentiment_summary["classification"].isin(["Greed", "Extreme Greed"])]["net_pnl"].sum()

    daily_rollup = (
        daily_summary.groupby("trade_date", observed=True)
        .agg(daily_net_pnl=("daily_net_pnl", "sum"), sentiment_value=("sentiment_value", "mean"))
        .reset_index()
    )
    sentiment_corr = daily_rollup["sentiment_value"].corr(daily_rollup["daily_net_pnl"])

    top_fear = account_summary.sort_values("fear_minus_greed", ascending=False).head(5)
    top_greed = account_summary.sort_values("fear_minus_greed", ascending=True).head(5)

    high_activity = df["account"].value_counts().head(10).index
    high_activity_df = df[df["account"].isin(high_activity)]
    account_behavior = (
        high_activity_df.groupby(["account", "classification"], observed=True)
        .agg(net_pnl=("net_pnl", "sum"), trades=("account", "size"), win_rate=("is_win", "mean"))
        .reset_index()
    )

    lines = [
        "# Trader Performance vs Bitcoin Market Sentiment",
        "",
        "## Dataset coverage",
        "This section frames the scale of the study, the overlap window between both datasets, and the baseline profitability profile before splitting results by sentiment regime.",
        f"- Trades analyzed: {total_trades:,}",
        f"- Distinct accounts: {total_accounts:,}",
        f"- Time window: {trade_start} to {trade_end}",
        f"- Total fee-adjusted net PnL: {format_currency(total_net)}",
        f"- Overall trade win rate: {format_pct(total_win_rate)}",
        "",
        "## Key findings",
        "This section compresses the highest-signal conclusions so a reader can understand the regime effects without scanning the full detail tables.",
        f"- The strongest regime was {best_regime['classification']}, with net PnL per trade of {format_currency(best_regime['net_pnl_per_trade'])} and win rate of {format_pct(best_regime['win_rate'])}.",
        f"- The weakest regime was {worst_regime['classification']}, with net PnL per trade of {format_currency(worst_regime['net_pnl_per_trade'])} and win rate of {format_pct(worst_regime['win_rate'])}.",
        f"- Fear regimes produced aggregate fee-adjusted net PnL of {format_currency(fear_net)} versus {format_currency(greed_net)} in greed regimes.",
        f"- The correlation between daily sentiment value and daily net PnL was {sentiment_corr:.3f}, which suggests the linear relationship is weak and regime effects matter more than raw index level alone.",
        "- Median trade-level net PnL remains near zero across all regimes, which implies a heavily skewed payoff profile where a small number of large wins drive most profits.",
        "",
        "## Regime summary",
        "This section compares each sentiment bucket on trade count, account participation, fee-adjusted profitability, trade sizing, and win behavior. It is the core evidence for regime-aware strategy decisions.",
        render_table(sentiment_summary),
        "",
        "## Account patterns",
        "This section highlights that the aggregate signal is not evenly distributed. Some traders are structurally stronger in fear, while others monetize greed much better, which matters for trader selection and strategy routing.",
        "Top accounts that outperform more in fear than greed:",
        render_table(
            top_fear,
            columns=["account", "fear_net_pnl", "greed_net_pnl", "fear_minus_greed", "all_net_pnl", "all_trades"],
            float_format="{:.2f}",
        ),
        "",
        "Top accounts that outperform more in greed than fear:",
        render_table(
            top_greed,
            columns=["account", "fear_net_pnl", "greed_net_pnl", "fear_minus_greed", "all_net_pnl", "all_trades"],
            float_format="{:.2f}",
        ),
        "",
        "High-activity account regime behavior sample:",
        render_table(account_behavior.sort_values(["account", "classification"])),
        "",
        "## Trading implications",
        "This section translates the descriptive analysis into practical portfolio and execution decisions that can be tested or operationalized.",
        "- Favor regime-aware sizing. Average outcomes can change materially by sentiment bucket even when median trade PnL does not.",
        "- Treat greed regimes as higher-selectivity environments. If your strategy depends on momentum continuation, use stricter confirmation and tighter risk limits when the index is elevated.",
        "- Maintain optionality in fear regimes. The data indicates that dislocated conditions can produce better realized PnL per trade, likely because volatility creates larger mean-reversion or short-squeeze opportunities.",
        "- Measure performance at the account-strategy level, not just in aggregate. Several accounts exhibit strong fear-versus-greed asymmetry, which is a concrete signal for strategy routing or trader profiling.",
        "",
        "## Caveats",
        "This section records the analytical limits of the provided data so downstream users do not over-interpret the conclusions.",
        "- The trader dataset does not include a leverage column in the provided file, so leverage-adjusted conclusions were not possible.",
        "- Closed PnL is realized at trade events and may reflect prior position context, so trade-level return metrics should be treated as directional rather than exact strategy returns.",
        "- Sentiment is joined at daily granularity. Intraday shifts are not captured.",
    ]
    return "\n".join(lines)


def save_outputs(
    sentiment_summary: pd.DataFrame,
    daily_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
    report_text: str,
    dashboard_payload: dict,
) -> AnalysisOutputs:
    sentiment_path = TABLE_DIR / "sentiment_summary.csv"
    daily_path = TABLE_DIR / "daily_summary.csv"
    account_path = TABLE_DIR / "account_regime_summary.csv"
    report_path = REPORT_DIR / "analysis_report.md"
    dashboard_path = REPORT_DIR / "dashboard_data.json"
    dashboard_script_path = FRONTEND_ASSET_DIR / "dashboard-data.js"

    sentiment_summary.to_csv(sentiment_path, index=False)
    daily_summary.to_csv(daily_path, index=False)
    account_summary.to_csv(account_path, index=False)
    report_path.write_text(report_text, encoding="utf-8")
    dashboard_path.write_text(json.dumps(dashboard_payload, indent=2), encoding="utf-8")
    dashboard_script_path.write_text(
        "window.__DASHBOARD_DATA__ = " + json.dumps(dashboard_payload, indent=2) + ";\n",
        encoding="utf-8",
    )

    return AnalysisOutputs(
        sentiment_summary=sentiment_path,
        daily_summary=daily_path,
        account_summary=account_path,
        report=report_path,
        dashboard_data=dashboard_path,
        dashboard_script=dashboard_script_path,
    )


def main() -> None:
    ensure_dirs([REPORT_DIR, TABLE_DIR, FIGURE_DIR, FRONTEND_DIR, FRONTEND_ASSET_DIR])
    trader, sentiment = load_inputs()
    prepared = prepare_datasets(trader, sentiment)
    sentiment_summary = build_sentiment_summary(prepared)
    daily_summary = build_daily_summary(prepared)
    account_summary = build_account_summary(prepared)
    create_figures(prepared, sentiment_summary, daily_summary)
    report_text = build_report(prepared, sentiment_summary, daily_summary, account_summary)
    dashboard_payload = build_dashboard_payload(prepared, sentiment_summary, daily_summary, account_summary)
    outputs = save_outputs(sentiment_summary, daily_summary, account_summary, report_text, dashboard_payload)

    print(f"Saved sentiment summary to {outputs.sentiment_summary}")
    print(f"Saved daily summary to {outputs.daily_summary}")
    print(f"Saved account summary to {outputs.account_summary}")
    print(f"Saved markdown report to {outputs.report}")
    print(f"Saved dashboard data to {outputs.dashboard_data}")
    print(f"Saved dashboard script to {outputs.dashboard_script}")


if __name__ == "__main__":
    main()