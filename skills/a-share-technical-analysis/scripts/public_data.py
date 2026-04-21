#!/usr/bin/env python3
"""Shared public-data helpers for the A-share technical analysis skill."""

from __future__ import annotations

import time
from typing import Any

import akshare as ak
import pandas as pd


HIST_RETRY_DELAYS = (1.0, 2.0, 4.0)
SUPPORTED_PERIODS = {"daily", "weekly", "monthly"}


def normalize_symbol(raw: str) -> tuple[str, str]:
    symbol = raw.strip().upper()
    digits = symbol.split(".")[0]
    if len(digits) != 6 or not digits.isdigit():
        raise ValueError("symbol must be a 6-digit A-share code, optionally with suffix")
    if digits.startswith("688"):
        return digits, "star"
    if digits.startswith("300"):
        return digits, "chinext"
    return digits, "main"


def to_exchange_ticker(symbol: str) -> str:
    suffix = "SH" if symbol.startswith(("6", "9")) else "SZ"
    return f"{symbol}.{suffix}"


def to_prefixed_symbol(symbol: str) -> str:
    prefix = "sh" if symbol.startswith(("6", "9")) else "sz"
    return f"{prefix}{symbol}"


def rename_eastmoney_hist_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(
        columns={
            "日期": "date",
            "股票代码": "symbol",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "振幅": "amplitude_pct",
            "涨跌幅": "pct_change",
            "涨跌额": "change",
            "换手率": "turnover_rate",
        }
    ).copy()
    renamed["date"] = pd.to_datetime(renamed["date"])
    numeric_columns = [c for c in renamed.columns if c not in {"date", "symbol"}]
    for col in numeric_columns:
        renamed[col] = pd.to_numeric(renamed[col], errors="coerce")
    return renamed.sort_values("date").reset_index(drop=True)


def rename_sina_daily_columns(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    renamed = df.rename(
        columns={
            "date": "date",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low",
            "volume": "volume",
            "amount": "amount",
            "turnover": "turnover_rate",
        }
    ).copy()
    renamed["date"] = pd.to_datetime(renamed["date"])
    renamed["symbol"] = symbol
    for col in ["open", "close", "high", "low", "volume", "amount", "turnover_rate"]:
        renamed[col] = pd.to_numeric(renamed[col], errors="coerce")
    # Sina returns turnover as a fraction; the rest of the skill expects percent.
    renamed["turnover_rate"] = renamed["turnover_rate"] * 100
    return renamed.sort_values("date").reset_index(drop=True)


def resample_hist(df: pd.DataFrame, symbol: str, period: str) -> pd.DataFrame:
    if period == "daily":
        return df.copy()
    rule = {"weekly": "W-FRI", "monthly": "ME"}[period]
    resampled = (
        df.set_index("date")
        .sort_index()
        .resample(rule)
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "amount": "sum",
                "turnover_rate": "sum",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )
    resampled["symbol"] = symbol
    return resampled[
        ["date", "symbol", "open", "close", "high", "low", "volume", "amount", "turnover_rate"]
    ].reset_index(drop=True)


def _fetch_stock_hist_eastmoney(symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
    last_error: Exception | None = None
    for index, delay in enumerate((*HIST_RETRY_DELAYS, None), start=1):
        try:
            raw = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
                timeout=10,
            )
            if raw.empty:
                raise ValueError(f"eastmoney returned no data for {symbol} {period}")
            return rename_eastmoney_hist_columns(raw)
        except Exception as exc:  # AKShare surfaces different network exceptions per endpoint.
            last_error = exc
            if delay is None:
                break
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def _fetch_stock_hist_sina_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    raw = ak.stock_zh_a_daily(
        symbol=to_prefixed_symbol(symbol),
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",
    )
    if raw.empty:
        raise ValueError(f"sina returned no daily data for {symbol}")
    return rename_sina_daily_columns(raw.reset_index(drop=True), symbol)


def fetch_stock_hist(symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
    if period not in SUPPORTED_PERIODS:
        raise ValueError(f"unsupported period: {period}")
    try:
        return _fetch_stock_hist_eastmoney(symbol, period, start_date, end_date)
    except Exception:
        daily_df = _fetch_stock_hist_sina_daily(symbol, start_date, end_date)
        return resample_hist(daily_df, symbol, period)


def fetch_index_daily(index_symbol: str, start_dt: pd.Timestamp, end_dt: pd.Timestamp) -> pd.DataFrame:
    raw = ak.stock_zh_index_daily(symbol=index_symbol).copy()
    raw["date"] = pd.to_datetime(raw["date"])
    for col in ["open", "high", "low", "close", "volume"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    filtered = raw[(raw["date"] >= start_dt) & (raw["date"] <= end_dt)].copy()
    return filtered.sort_values("date").reset_index(drop=True)


def fetch_stock_profile(symbol: str) -> dict[str, Any]:
    info_df = ak.stock_individual_info_em(symbol=symbol, timeout=10)
    info: dict[str, Any] = {}
    for _, row in info_df.iterrows():
        info[str(row["item"])] = row["value"]
    return info
