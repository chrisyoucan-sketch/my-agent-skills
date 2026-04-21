#!/usr/bin/env python3
"""Plot A-share candlestick charts with moving averages, volume, and MACD."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from public_data import fetch_stock_hist as fetch_public_stock_hist
from public_data import normalize_symbol

matplotlib.use("Agg")


MA_WINDOWS = (5, 10, 20, 30, 60, 120, 250)


def default_start_date() -> str:
    return (date.today() - timedelta(days=420)).strftime("%Y%m%d")


def rename_stock_hist_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(
        columns={"date": "Date", "open": "Open", "close": "Close", "high": "High", "low": "Low", "volume": "Volume"}
    ).copy()
    renamed["Date"] = pd.to_datetime(renamed["Date"])
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        renamed[col] = pd.to_numeric(renamed[col], errors="coerce")
    renamed = renamed.set_index("Date").sort_index()
    return renamed[["Open", "High", "Low", "Close", "Volume"]]


def fetch_stock_hist(symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
    raw = fetch_public_stock_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date)
    if raw.empty:
        raise ValueError(f"no data returned for {symbol} {period}")
    return rename_stock_hist_columns(raw)


def add_bollinger(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["BOLL_MID"] = out["Close"].rolling(20).mean()
    rolling_std = out["Close"].rolling(20).std(ddof=0)
    out["BOLL_UPPER"] = out["BOLL_MID"] + 2 * rolling_std
    out["BOLL_LOWER"] = out["BOLL_MID"] - 2 * rolling_std
    return out


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ema12 = out["Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Close"].ewm(span=26, adjust=False).mean()
    out["MACD_DIF"] = ema12 - ema26
    out["MACD_DEA"] = out["MACD_DIF"].ewm(span=9, adjust=False).mean()
    out["MACD_HIST"] = (out["MACD_DIF"] - out["MACD_DEA"]) * 2
    return out


def build_level_lines(df: pd.DataFrame) -> dict[str, float]:
    prior_20 = df.iloc[-21:-1]
    prior_60 = df.iloc[-61:-1]
    if prior_20.empty:
        return {}
    support = float(prior_20["Low"].min())
    breakout = float(prior_20["High"].max())
    resistance = float(prior_60["High"].max()) if not prior_60.empty else breakout
    return {
        "support": support,
        "breakout": breakout,
        "resistance": resistance,
    }


def build_addplots(df: pd.DataFrame, show_boll: bool) -> list:
    addplots = []
    if show_boll:
        addplots.extend(
            [
                mpf.make_addplot(df["BOLL_UPPER"], color="#6a4c93", width=0.9),
                mpf.make_addplot(df["BOLL_MID"], color="#1982c4", width=0.9),
                mpf.make_addplot(df["BOLL_LOWER"], color="#6a4c93", width=0.9),
            ]
        )
    hist_colors = ["#d1495b" if value >= 0 else "#2a9d8f" for value in df["MACD_HIST"]]
    addplots.extend(
        [
            mpf.make_addplot(
                df["MACD_HIST"],
                type="bar",
                panel=2,
                color=hist_colors,
                alpha=0.8,
                width=0.7,
                ylabel="MACD",
            ),
            mpf.make_addplot(df["MACD_DIF"], panel=2, color="#1982c4", width=1.0),
            mpf.make_addplot(df["MACD_DEA"], panel=2, color="#6a4c93", width=1.0),
        ]
    )
    return addplots


def annotate_levels(ax, df: pd.DataFrame, levels: dict[str, float]) -> None:
    if not levels:
        return
    label_map = {
        "support": "Support",
        "breakout": "Breakout",
        "resistance": "Resistance",
    }
    color_map = {
        "support": "#2a9d8f",
        "breakout": "#f4a261",
        "resistance": "#e76f51",
    }
    x_pos = len(df) - 1
    for key in ("support", "breakout", "resistance"):
        if key not in levels:
            continue
        y = levels[key]
        ax.annotate(
            f"{label_map[key]} {y:.2f}",
            xy=(x_pos, y),
            xytext=(10, 0),
            textcoords="offset points",
            color=color_map[key],
            fontsize=8,
            va="center",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.2", fc="#fffaf0", ec=color_map[key], lw=0.8),
        )


def plot_chart(
    symbol: str,
    period: str,
    start_date: str,
    end_date: str,
    output_path: Path,
    show_boll: bool,
    show_levels: bool,
    title: str | None,
) -> Path:
    df = fetch_stock_hist(symbol, period, start_date, end_date)
    df = add_bollinger(df)
    df = add_macd(df)
    addplots = build_addplots(df, show_boll)
    levels = build_level_lines(df) if show_levels and len(df) >= 25 else {}
    hlines = [levels[key] for key in ("support", "breakout", "resistance") if key in levels]
    hline_colors = [color for key, color in (("support", "#2a9d8f"), ("breakout", "#f4a261"), ("resistance", "#e76f51")) if key in levels]

    market_colors = mpf.make_marketcolors(
        up="#d1495b",
        down="#2a9d8f",
        edge="inherit",
        wick="inherit",
        volume="inherit",
    )
    style = mpf.make_mpf_style(
        marketcolors=market_colors,
        gridstyle=":",
        facecolor="#fbf7ef",
        figcolor="#fbf7ef",
    )
    kwargs = {
        "type": "candle",
        "style": style,
        "mav": MA_WINDOWS,
        "volume": True,
        "addplot": addplots if addplots else None,
        "panel_ratios": (6, 2, 2),
        "figratio": (16, 9),
        "figscale": 1.2,
        "title": title or f"{symbol} {period.upper()} Chart",
        "tight_layout": True,
        "returnfig": True,
    }
    if hlines:
        kwargs["hlines"] = dict(hlines=hlines, colors=hline_colors, linestyle="-.", linewidths=0.9)

    fig, axes = mpf.plot(df, **kwargs)
    annotate_levels(axes[0], df, levels)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="6-digit A-share code, optionally with suffix")
    parser.add_argument("--period", default="daily", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--start-date", default=default_start_date(), help="YYYYMMDD")
    parser.add_argument("--end-date", default=date.today().strftime("%Y%m%d"), help="YYYYMMDD")
    parser.add_argument("--output", help="Output PNG path")
    parser.add_argument("--show-boll", action="store_true", help="Overlay Bollinger Bands")
    parser.add_argument("--hide-levels", action="store_true", help="Do not draw support/resistance/breakout levels")
    parser.add_argument("--title", help="Custom chart title")
    args = parser.parse_args()

    symbol, _ = normalize_symbol(args.symbol)
    output_path = Path(args.output) if args.output else Path.cwd() / f"{symbol}_{args.period}_chart.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_path = plot_chart(
        symbol=symbol,
        period=args.period,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=output_path,
        show_boll=args.show_boll,
        show_levels=not args.hide_levels,
        title=args.title,
    )
    print(final_path)


if __name__ == "__main__":
    main()
