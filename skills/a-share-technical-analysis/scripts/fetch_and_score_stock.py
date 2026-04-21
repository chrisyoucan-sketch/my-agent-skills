#!/usr/bin/env python3
"""Fetch public A-share data with AKShare, normalize it, and score the stock."""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from plot_stock_chart import plot_chart
from public_data import (
    fetch_index_daily,
    fetch_stock_hist,
    fetch_stock_profile,
    normalize_symbol,
    to_exchange_ticker,
)
from score_stock import build_output


MA_WINDOWS = [5, 10, 20, 30, 60, 120, 250]
BENCHMARK_MAP = {
    "main": ("sh000001", "sse"),
    "chinext": ("sz399006", "chinext"),
    "star": ("sh000688", "star50"),
}


def default_start_date() -> str:
    return (date.today() - timedelta(days=1100)).strftime("%Y%m%d")


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in MA_WINDOWS:
        out[f"ma{window}"] = out["close"].rolling(window).mean()
    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd_dif"] = ema12 - ema26
    out["macd_dea"] = out["macd_dif"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = (out["macd_dif"] - out["macd_dea"]) * 2
    out["boll_mid"] = out["close"].rolling(20).mean()
    rolling_std = out["close"].rolling(20).std(ddof=0)
    out["boll_upper"] = out["boll_mid"] + 2 * rolling_std
    out["boll_lower"] = out["boll_mid"] - 2 * rolling_std
    out["boll_bandwidth_pct"] = ((out["boll_upper"] - out["boll_lower"]) / out["boll_mid"]) * 100
    out["volume_ratio_5d"] = out["volume"] / out["volume"].rolling(5).mean()
    out["volume_ratio_20d"] = out["volume"] / out["volume"].rolling(20).mean()
    out["turnover_rate_20d_avg"] = out["turnover_rate"].rolling(20).mean()
    return out


def classify_trend(df: pd.DataFrame) -> str:
    latest = df.iloc[-1]
    ma20 = df["close"].rolling(20).mean()
    if pd.isna(ma20.iloc[-1]):
        return "range"
    ma20_slope = ma20.iloc[-1] - ma20.iloc[-5] if len(df) >= 25 else 0
    if latest["close"] > ma20.iloc[-1] and ma20_slope > 0:
        return "up"
    if latest["close"] < ma20.iloc[-1] and ma20_slope < 0:
        return "down"
    return "range"


def classify_stage(latest: pd.Series, daily_trend: str, weekly_trend: str, monthly_trend: str) -> str:
    if daily_trend == weekly_trend == monthly_trend == "up":
        return "uptrend"
    if weekly_trend == monthly_trend == "up" and latest["close"] >= latest["ma20"]:
        return "uptrend_pullback"
    if daily_trend == weekly_trend == monthly_trend == "down":
        return "downtrend"
    if daily_trend == "up" and weekly_trend == "down":
        return "rebound_in_downtrend"
    return "range"


def detect_macd_cross(df: pd.DataFrame) -> str:
    if len(df) < 2:
        return "none"
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if prev["macd_dif"] <= prev["macd_dea"] and curr["macd_dif"] > curr["macd_dea"]:
        return "golden"
    if prev["macd_dif"] >= prev["macd_dea"] and curr["macd_dif"] < curr["macd_dea"]:
        return "dead"
    return "none"


def detect_macd_divergence(df: pd.DataFrame) -> str:
    window = df.tail(25).copy()
    if len(window) < 10:
        return "none"
    recent = window.iloc[-1]
    earlier = window.iloc[:-1]
    if recent["close"] >= earlier["close"].max() and recent["macd_hist"] < earlier["macd_hist"].max():
        return "top"
    if recent["close"] <= earlier["close"].min() and recent["macd_hist"] > earlier["macd_hist"].min():
        return "bottom"
    return "none"


def detect_candlestick_signals(df: pd.DataFrame, stage: str) -> list[str]:
    signals: list[str] = []
    if len(df) < 3:
        return signals
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    body = abs(curr["close"] - curr["open"])
    total_range = max(curr["high"] - curr["low"], 1e-9)
    lower_shadow = min(curr["open"], curr["close"]) - curr["low"]
    upper_shadow = curr["high"] - max(curr["open"], curr["close"])

    if body / total_range <= 0.1:
        signals.append("doji")
    if lower_shadow >= body * 2 and upper_shadow <= body and curr["close"] >= curr["open"]:
        signals.append("hammer")
    if lower_shadow >= body * 2 and stage.startswith("up") and curr["close"] <= curr["open"]:
        signals.append("hanging_man")
    if curr["close"] > curr["open"] and prev["close"] < prev["open"] and curr["open"] <= prev["close"] and curr["close"] >= prev["open"]:
        signals.append("bullish_engulfing")
    if curr["close"] < curr["open"] and prev["close"] > prev["open"] and curr["open"] >= prev["close"] and curr["close"] <= prev["open"]:
        signals.append("bearish_engulfing")
    return signals


def detect_structure_signals(df: pd.DataFrame) -> list[str]:
    signals: list[str] = []
    if len(df) < 25:
        return signals
    prior_20 = df.iloc[-21:-1]
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    breakout_level = prior_20["high"].max()
    support_level = prior_20["low"].min()
    if latest["close"] > breakout_level and latest["volume_ratio_5d"] >= 1.2:
        signals.append("box_breakout")
    if prev["close"] > breakout_level and latest["close"] < breakout_level:
        signals.append("failed_breakout")
    if latest["close"] < support_level and latest["volume_ratio_5d"] >= 1.2:
        signals.append("box_breakdown")
    return signals


def latest_ma_slope(series: pd.Series, lag: int = 5) -> float:
    if len(series) <= lag or pd.isna(series.iloc[-1]) or pd.isna(series.iloc[-1 - lag]):
        return 0.0
    return float(series.iloc[-1] - series.iloc[-1 - lag])


def compute_market_context(stock_df: pd.DataFrame, index_df: pd.DataFrame, profile: dict[str, Any], board: str) -> dict[str, Any]:
    benchmark_symbol, benchmark_label = BENCHMARK_MAP[board]
    benchmark_trend = classify_trend(index_df)
    stock_return_20d = stock_df["close"].iloc[-1] / stock_df["close"].iloc[-21] - 1 if len(stock_df) >= 21 else 0.0
    index_return_20d = index_df["close"].iloc[-1] / index_df["close"].iloc[-21] - 1 if len(index_df) >= 21 else 0.0
    industry_name = str(profile.get("行业", "")).strip() or "unknown"
    return {
        "benchmark_index": benchmark_label,
        "benchmark_symbol": benchmark_symbol,
        "benchmark_trend": benchmark_trend,
        "industry_name": industry_name,
        "industry_trend": "range",
        "relative_strength_vs_index_20d": round(stock_return_20d - index_return_20d, 6),
        "relative_strength_vs_industry_20d": 0.0,
        "context_warnings": [] if industry_name != "unknown" else ["industry_name_unavailable"],
    }


def build_normalized_payload(symbol: str, board: str, start_date: str, end_date: str) -> dict[str, Any]:
    stock_daily = add_indicators(fetch_stock_hist(symbol, "daily", start_date, end_date))
    stock_weekly = add_indicators(fetch_stock_hist(symbol, "weekly", start_date, end_date))
    stock_monthly = add_indicators(fetch_stock_hist(symbol, "monthly", start_date, end_date))
    if len(stock_daily) < 250:
        raise ValueError("not enough daily history to compute the full rule set")

    profile = fetch_stock_profile(symbol)
    benchmark_symbol, _ = BENCHMARK_MAP[board]
    index_daily = fetch_index_daily(benchmark_symbol, stock_daily["date"].min(), stock_daily["date"].max())
    latest = stock_daily.iloc[-1]
    daily_trend = classify_trend(stock_daily)
    weekly_trend = classify_trend(stock_weekly)
    monthly_trend = classify_trend(stock_monthly)
    stage = classify_stage(latest, daily_trend, weekly_trend, monthly_trend)
    candlestick_signals = detect_candlestick_signals(stock_daily, stage)
    structure_signals = detect_structure_signals(stock_daily)
    context = compute_market_context(stock_daily, index_daily, profile, board)

    prior_20 = stock_daily.iloc[-21:-1]
    prior_60 = stock_daily.iloc[-61:-1]
    breakout_level = float(prior_20["high"].max())
    support_level = float(prior_20["low"].min())
    resistance_level = float(prior_60["high"].max()) if len(prior_60) > 0 else breakout_level
    invalidation_level = float(min(support_level, latest["ma20"]))

    payload = {
        "ticker": to_exchange_ticker(symbol),
        "name": str(profile.get("股票简称", symbol)),
        "market_board": board,
        "provider": "akshare",
        "as_of_date": latest["date"].date().isoformat(),
        "daily_bars_count": int(len(stock_daily)),
        "close": float(latest["close"]),
        "prev_close": float(stock_daily.iloc[-2]["close"]),
        "high_20d": float(prior_20["high"].max()),
        "low_20d": float(prior_20["low"].min()),
        "high_60d": float(prior_60["high"].max()) if len(prior_60) > 0 else float(prior_20["high"].max()),
        "low_60d": float(prior_60["low"].min()) if len(prior_60) > 0 else float(prior_20["low"].min()),
        "gap_type": "none",
        "volume": float(latest["volume"]),
        "volume_ratio_5d": round(float(latest["volume_ratio_5d"]), 4),
        "volume_ratio_20d": round(float(latest["volume_ratio_20d"]), 4),
        "turnover_rate": round(float(latest["turnover_rate"]), 4),
        "turnover_rate_20d_avg": round(float(latest["turnover_rate_20d_avg"]), 4),
        "macd_dif": round(float(latest["macd_dif"]), 4),
        "macd_dea": round(float(latest["macd_dea"]), 4),
        "macd_hist": round(float(latest["macd_hist"]), 4),
        "macd_hist_prev": round(float(stock_daily.iloc[-2]["macd_hist"]), 4),
        "macd_cross": detect_macd_cross(stock_daily),
        "macd_divergence": detect_macd_divergence(stock_daily),
        "boll_mid": round(float(latest["boll_mid"]), 4),
        "boll_upper": round(float(latest["boll_upper"]), 4),
        "boll_lower": round(float(latest["boll_lower"]), 4),
        "boll_bandwidth_pct": round(float(latest["boll_bandwidth_pct"]), 4),
        "boll_bandwidth_pct_20d_rank": round(float(stock_daily["boll_bandwidth_pct"].tail(20).rank(pct=True).iloc[-1]), 4),
        "candlestick_signals": candlestick_signals,
        "structure_signals": structure_signals,
        "daily_trend": daily_trend,
        "weekly_trend": weekly_trend,
        "monthly_trend": monthly_trend,
        "stage": stage,
        "support_level": round(support_level, 4),
        "resistance_level": round(resistance_level, 4),
        "breakout_level": round(breakout_level, 4),
        "invalidation_level": round(invalidation_level, 4),
    }

    for window in MA_WINDOWS:
        series = stock_daily[f"ma{window}"]
        payload[f"ma{window}"] = round(float(series.iloc[-1]), 4)
        payload[f"ma{window}_slope"] = round(latest_ma_slope(series), 4)

    payload.update(context)
    return payload


def classify_score_label(total_score: int) -> str:
    if total_score >= 80:
        return "强势"
    if total_score >= 60:
        return "偏强"
    if total_score >= 40:
        return "中性震荡"
    if total_score >= 20:
        return "偏弱"
    return "回避"


def board_label(board: str) -> str:
    return {
        "main": "主板",
        "chinext": "创业板",
        "star": "科创板",
    }.get(board, board)


def trend_label(value: str) -> str:
    return {
        "up": "上行",
        "down": "下行",
        "range": "震荡",
    }.get(value, value)


def stage_label(value: str) -> str:
    return {
        "uptrend": "上升趋势",
        "uptrend_pullback": "上升趋势中的回踩",
        "range": "区间震荡",
        "rebound_in_downtrend": "下降趋势中的反弹",
        "downtrend": "下降趋势",
    }.get(value, value)


def bias_label(value: str) -> str:
    return {
        "bullish": "偏多",
        "watch": "观察",
        "bearish": "偏空",
    }.get(value, value)


def signal_label(value: str) -> str:
    mapping = {
        "none": "无",
        "golden": "金叉",
        "dead": "死叉",
        "top": "顶背离",
        "bottom": "底背离",
        "doji": "十字星",
        "hammer": "锤头",
        "hanging_man": "上吊线",
        "bullish_engulfing": "看涨吞没",
        "bearish_engulfing": "看跌吞没",
        "box_breakout": "箱体突破",
        "failed_breakout": "突破失败",
        "box_breakdown": "箱体跌破",
        "triangle_breakout": "三角形突破",
        "w_bottom": "W底",
        "m_top": "M顶",
    }
    return mapping.get(value, value)


def fmt_number(value: float) -> str:
    return f"{value:.2f}"


def infer_trigger_conditions(normalized: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    if normalized["close"] < normalized["breakout_level"]:
        conditions.append(
            f"若收盘价站上 {fmt_number(normalized['breakout_level'])}，且5日量比不低于1.5，可视为向上突破确认。"
        )
    if normalized["close"] >= normalized["support_level"]:
        conditions.append(
            f"若回踩 {fmt_number(normalized['support_level'])} 至 {fmt_number(normalized['ma20'])} 一带缩量企稳，可继续跟踪。"
        )
    if analysis["bias"] != "bearish":
        conditions.append(
            f"若跌破 {fmt_number(normalized['support_level'])} 并伴随放量走弱，需要转向谨慎。"
        )
    else:
        conditions.append(
            f"若重新站上 {fmt_number(normalized['ma20'])} 并出现MACD改善，弱势状态才有修复基础。"
        )
    return conditions


def infer_risk_flags(normalized: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if normalized["daily_trend"] != normalized["weekly_trend"]:
        flags.append("日线与周线趋势不完全一致，短线信号的持续性需要进一步确认。")
    if normalized["relative_strength_vs_index_20d"] < 0:
        flags.append("近20日相对大盘表现偏弱，个股弹性暂时不占优。")
    if normalized["industry_trend"] == "range":
        flags.append("行业趋势数据当前仅部分确认，市场环境判断以指数过滤为主。")
    if normalized["macd_divergence"] == "top":
        flags.append("存在顶背离预警，若后续放量转弱，应提高警惕。")
    if normalized["macd_divergence"] == "bottom":
        flags.append("存在底背离预警，但仍需价格和量能共振确认。")
    if normalized["close"] < normalized["ma20"]:
        flags.append("股价位于20日线下方，短线修复力度仍待观察。")
    if not flags:
        flags.append("当前未出现特别突出的额外风险项，但仍需跟踪关键位是否失守。")
    return flags


def score_status_label(value: str) -> str:
    return {
        "direct": "DIRECT",
        "neutral_untriggered": "NEUTRAL_ZERO",
        "negative_clamped": "NEGATIVE_CLAMPED_TO_ZERO",
        "positive_clamped": "POSITIVE_CLAMPED_TO_CAP",
    }.get(value, value)


def append_score_detail_lines(lines: list[str], title: str, detail: dict[str, Any]) -> None:
    lines.append(
        f"- {title}?{detail['score']}/{detail['max_score']}????{score_status_label(detail['score_status'])}??????{detail['raw_score']}?"
    )
    for reason in detail["reasons"]:
        lines.append(f"  - {reason}")


def build_chinese_report(normalized: dict[str, Any], analysis: dict[str, Any]) -> str:
    total_score = analysis["total_score"]
    score_breakdown = analysis["score_breakdown"]
    score_details = analysis["score_details"]
    candlestick = "、".join(signal_label(x) for x in analysis["signals"]["candlestick"]) if analysis["signals"]["candlestick"] else "无明确单K线信号"
    structure = "、".join(signal_label(x) for x in analysis["signals"]["structure"]) if analysis["signals"]["structure"] else "无明确结构形态确认"
    context_note = (
        f"{normalized['industry_name']}行业环境当前按部分可得公开数据处理。"
        if normalized["industry_name"] != "unknown"
        else "行业字段未稳定获取，市场环境判断主要参考对应指数。"
    )
    trigger_conditions = infer_trigger_conditions(normalized, analysis)
    risk_flags = infer_risk_flags(normalized, analysis)

    lines = [
        f"# {normalized['name']}（{normalized['ticker']}）技术诊断报告",
        "",
        "## 1. 结论",
        f"- 技术结论：{bias_label(analysis['bias'])}",
        f"- 综合评分：{total_score}/100（{classify_score_label(total_score)}）",
        (
            f"- 分项评分：趋势 {score_breakdown['trend']}/30，量价 {score_breakdown['volume_price']}/20，"
            f"指标共振 {score_breakdown['indicator_confirmation']}/20，形态位置 {score_breakdown['pattern_position']}/20，"
            f"市场环境 {score_breakdown['market_context']}/10"
        ),
        f"- 分析日期：{normalized['as_of_date']}，板块属性：{board_label(normalized['market_board'])}",
        "",
        "## 2. 分项打分理由",
    ]
    append_score_detail_lines(lines, "趋势", score_details["trend"])
    append_score_detail_lines(lines, "量价", score_details["volume_price"])
    append_score_detail_lines(lines, "指标共振", score_details["indicator_confirmation"])
    append_score_detail_lines(lines, "形态位置", score_details["pattern_position"])
    append_score_detail_lines(lines, "市场环境", score_details["market_context"])
    lines.extend([
        "",
        "## 3. 多周期趋势",
        (
            f"- 月线：{trend_label(normalized['monthly_trend'])}，长期均线参考 120日线 {fmt_number(normalized['ma120'])} / "
            f"250日线 {fmt_number(normalized['ma250'])}"
        ),
        f"- 周线：{trend_label(normalized['weekly_trend'])}，中期均线参考 60日线 {fmt_number(normalized['ma60'])}",
        (
            f"- 日线：{trend_label(normalized['daily_trend'])}，当前价格 {fmt_number(normalized['close'])}，"
            f"5/10/20/30日线分别为 {fmt_number(normalized['ma5'])} / {fmt_number(normalized['ma10'])} / "
            f"{fmt_number(normalized['ma20'])} / {fmt_number(normalized['ma30'])}"
        ),
        f"- 阶段判断：{stage_label(normalized['stage'])}",
        "",
        "## 4. 量价与指标",
        (
            f"- 量价关系：5日量比 {normalized['volume_ratio_5d']:.2f}，20日量比 {normalized['volume_ratio_20d']:.2f}，"
            f"换手率 {normalized['turnover_rate']:.2f}% ，20日均换手 {normalized['turnover_rate_20d_avg']:.2f}% 。"
        ),
        (
            f"- MACD：DIF {normalized['macd_dif']:.2f}，DEA {normalized['macd_dea']:.2f}，柱体 {normalized['macd_hist']:.2f}，"
            f"交叉状态为 {signal_label(normalized['macd_cross'])}，背离状态为 {signal_label(normalized['macd_divergence'])}。"
        ),
        (
            f"- 布林带：中轨 {fmt_number(normalized['boll_mid'])}，上轨 {fmt_number(normalized['boll_upper'])}，"
            f"下轨 {fmt_number(normalized['boll_lower'])}，带宽 {normalized['boll_bandwidth_pct']:.2f}% 。"
        ),
        "",
        "## 5. 形态与关键位置",
        f"- 单K线/组合信号：{candlestick}",
        f"- 结构形态：{structure}",
        (
            f"- 关键位置：支撑位 {fmt_number(normalized['support_level'])}，阻力位 {fmt_number(normalized['resistance_level'])}，"
            f"突破位 {fmt_number(normalized['breakout_level'])}，失效位 {fmt_number(normalized['invalidation_level'])}"
        ),
        "",
        "## 6. 市场环境",
        (
            f"- 对应基准：{normalized['benchmark_index']}（{normalized.get('benchmark_symbol', '-')}），"
            f"当前趋势为{trend_label(normalized['benchmark_trend'])}。"
        ),
        f"- 相对强弱：近20日相对基准超额 {normalized['relative_strength_vs_index_20d'] * 100:.2f}%。",
        f"- 环境说明：{context_note}",
        "",
        "## 7. 交易框架",
        f"- 当前倾向：{bias_label(analysis['bias'])}",
        "- 触发条件：",
    ])
    for item in trigger_conditions:
        lines.append(f"  - {item}")
    lines.append("- 风险提示：")
    for item in risk_flags:
        lines.append(f"  - {item}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="6-digit A-share code, optionally with suffix")
    parser.add_argument("--start-date", default=default_start_date(), help="YYYYMMDD")
    parser.add_argument("--end-date", default=date.today().strftime("%Y%m%d"), help="YYYYMMDD")
    parser.add_argument("--save-normalized", help="Optional path to write normalized JSON")
    parser.add_argument("--report", action="store_true", help="Print a Chinese technical report instead of raw JSON")
    parser.add_argument("--chart-output", help="Optional PNG path for the default technical chart")
    parser.add_argument("--skip-chart", action="store_true", help="Do not generate the default technical chart")
    parser.add_argument("--hide-boll", action="store_true", help="Do not overlay Bollinger Bands on the chart")
    args = parser.parse_args()

    symbol, board = normalize_symbol(args.symbol)
    normalized = build_normalized_payload(symbol, board, args.start_date, args.end_date)
    analysis = build_output(normalized)
    chart_path: str | None = None
    if not args.skip_chart:
        output_path = Path(args.chart_output) if args.chart_output else Path.cwd() / f"{symbol}_technical_chart.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        chart_path = str(
            plot_chart(
                symbol=symbol,
                period="daily",
                start_date=args.start_date,
                end_date=args.end_date,
                output_path=output_path,
                show_boll=not args.hide_boll,
                show_levels=True,
                title=f"{normalized['name']} ({normalized['ticker']}) Technical Chart",
            )
        )
    output = {
        "normalized": normalized,
        "analysis": analysis,
    }
    if chart_path:
        output["chart_path"] = chart_path

    if args.save_normalized:
        Path(args.save_normalized).write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.report:
        if chart_path:
            print(f"图表文件：{chart_path}\n")
        print(build_chinese_report(normalized, analysis))
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
