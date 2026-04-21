#!/usr/bin/env python3
"""Deterministic scorer for the A-share technical analysis skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BLOCK_MAX = {
    "trend": 30,
    "volume_price": 20,
    "indicator_confirmation": 20,
    "pattern_position": 20,
    "market_context": 10,
}


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def finalize_block(raw_score: int, low: int, high: int, reasons: list[str]) -> tuple[int, int, str, list[str]]:
    score = clamp(raw_score, low, high)
    if not reasons:
        reasons = ["本项没有触发明显的正向或负向规则。"]
    if raw_score < low:
        score_status = "negative_clamped"
    elif raw_score == 0 and reasons == ["本项没有触发明显的正向或负向规则。"]:
        score_status = "neutral_untriggered"
    elif raw_score == score:
        score_status = "direct"
    else:
        score_status = "positive_clamped"
    if score != raw_score:
        reasons.append(f"原始分值为 {raw_score}，按区间限制调整为 {score}。")
    return raw_score, score, score_status, reasons


def score_trend(data: dict) -> tuple[int, int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    if data["close"] > data["ma20"] > data["ma60"] > data["ma120"]:
        score += 10
        reasons.append("股价位于20/60/120日线之上且均线多头排列，趋势结构加10分。")
    if data["ma20_slope"] > 0 and data["ma60_slope"] > 0:
        score += 6
        reasons.append("20日线和60日线同时上行，中期趋势斜率加6分。")
    if data["daily_trend"] == "up" and data["weekly_trend"] == "up":
        score += 6
        reasons.append("日线与周线趋势同向上行，多周期共振加6分。")
    if data["monthly_trend"] == "up":
        score += 4
        reasons.append("月线趋势向上，长期方向加4分。")
    if data["stage"] in {"uptrend", "uptrend_pullback"}:
        score += 4
        reasons.append("当前阶段属于上升趋势或上升趋势中的回踩，阶段判定加4分。")

    if data["close"] < data["ma20"] < data["ma60"] < data["ma120"]:
        score -= 10
        reasons.append("股价位于20/60/120日线下方且均线空头排列，趋势结构减10分。")
    if data["ma20_slope"] < 0 and data["ma60_slope"] < 0:
        score -= 6
        reasons.append("20日线和60日线同时下行，中期趋势斜率减6分。")
    if data["daily_trend"] == "down" and data["weekly_trend"] == "down":
        score -= 6
        reasons.append("日线与周线趋势同向下行，多周期共振减6分。")
    if data["monthly_trend"] == "down":
        score -= 4
        reasons.append("月线趋势向下，长期方向减4分。")
    if data["stage"] == "downtrend":
        score -= 4
        reasons.append("当前阶段属于下降趋势，阶段判定减4分。")
    return finalize_block(score, 0, 30, reasons)


def score_volume_price(data: dict) -> tuple[int, int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    if data["close"] > data["breakout_level"] and data["volume_ratio_5d"] >= 1.5:
        score += 8
        reasons.append("股价已放量突破突破位，量价配合加8分。")
    if data["close"] >= data["breakout_level"] * 0.98 and data["volume_ratio_20d"] >= 1.2:
        score += 4
        reasons.append("股价已逼近突破位且20日量能明显放大，视为强势蓄势加4分。")
    if data["close"] >= data["ma10"] and data["volume_ratio_5d"] <= 0.9:
        score += 5
        reasons.append("股价位于10日线之上且短期量能收敛，符合缩量回踩/整理特征，加5分。")
    if data["close"] > data["support_level"] and data["prev_close"] <= data["support_level"] and data["volume_ratio_5d"] >= 1.2:
        score += 4
        reasons.append("股价从支撑位附近反弹并伴随放量，反弹确认加4分。")
    if data["turnover_rate"] > data["turnover_rate_20d_avg"] and data["close"] > data["prev_close"]:
        score += 3
        reasons.append("上涨日换手高于20日均值，资金参与度改善，加3分。")

    if data["close"] < data["support_level"] and data["volume_ratio_5d"] >= 1.5:
        score -= 8
        reasons.append("股价放量跌破支撑位，破位特征明显，减8分。")
    if data["close"] > data["prev_close"] and data["volume_ratio_5d"] < 0.8:
        score -= 5
        reasons.append("上涨但量能偏弱，存在虚涨风险，减5分。")
    if (
        data["close"] < data["prev_close"]
        and data["close"] < data["breakout_level"] * 0.97
        and data["high_20d"] >= data["resistance_level"]
        and data["volume_ratio_5d"] >= 1.2
    ):
        score -= 4
        reasons.append("冲击阻力后回落且放量，接近假突破/受阻回落，减4分。")
    if data["close"] < data["prev_close"] and data["volume_ratio_5d"] >= 2.0:
        score -= 3
        reasons.append("下跌日出现明显放量，存在情绪化抛压，减3分。")
    return finalize_block(score, 0, 20, reasons)


def score_indicator(data: dict) -> tuple[int, int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    if data["macd_cross"] == "golden" and data["macd_hist"] > data["macd_hist_prev"]:
        score += 6
        reasons.append("MACD处于金叉且红柱继续放大，指标共振加6分。")
    if data["macd_hist"] > 0 and data["macd_hist"] > data["macd_hist_prev"]:
        score += 5
        reasons.append("MACD红柱处于扩张状态，动能改善加5分。")
    if data["macd_hist"] > 0 and data["macd_dif"] > data["macd_dea"]:
        score += 4
        reasons.append("DIF位于DEA上方，MACD维持强势结构，加4分。")
    if data["close"] > data["boll_mid"]:
        score += 5
        reasons.append("股价位于布林中轨之上，趋势延续特征加5分。")
    if data["close"] >= data["boll_upper"] * 0.98 and data["daily_trend"] == "up":
        score += 3
        reasons.append("上升趋势中股价贴近布林上轨，按强势延续而非超买处理，加3分。")
    if data["boll_bandwidth_pct_20d_rank"] <= 0.2 and data["boll_bandwidth_pct"] > 0:
        score += 4
        reasons.append("布林带处于低分位后开始扩张，存在波动放大特征，加4分。")
    if data["macd_divergence"] == "bottom" and data["close"] >= data["support_level"]:
        score += 4
        reasons.append("MACD出现底背离且价格未失守支撑，修复预期加4分。")

    if data["macd_cross"] == "dead" and data["macd_hist"] < data["macd_hist_prev"]:
        score -= 6
        reasons.append("MACD处于死叉且绿柱扩大，指标走弱减6分。")
    if data["close"] < data["boll_mid"]:
        score -= 5
        reasons.append("股价位于布林中轨下方，短线偏弱减5分。")
    if (
        data["close"] < data["prev_close"]
        and data["close"] < data["boll_upper"] * 0.97
        and data["high_20d"] >= data["boll_upper"]
        and data["daily_trend"] != "up"
    ):
        score -= 5
        reasons.append("接近布林上轨后明显回落，且不处于上升趋势，按受阻处理减5分。")
    if data["macd_divergence"] == "top":
        score -= 4
        reasons.append("MACD出现顶背离预警，减4分。")
    if data["close"] < data["boll_lower"] and data["daily_trend"] == "down":
        score -= 4
        reasons.append("下降趋势中股价运行到布林下轨下方，弱势延续减4分。")
    return finalize_block(score, 0, 20, reasons)


def score_pattern_position(data: dict) -> tuple[int, int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    candles = set(data.get("candlestick_signals", []))
    structures = set(data.get("structure_signals", []))

    if "w_bottom" in structures and data["close"] > data["breakout_level"] and data["volume_ratio_5d"] >= 1.3:
        score += 8
        reasons.append("W底形态完成且放量突破颈线，形态确认加8分。")
    if candles & {"hammer", "bullish_engulfing", "morning_star"} and data["close"] >= data["support_level"]:
        score += 6
        reasons.append("支撑位附近出现看涨反转K线，形态位置加6分。")
    if structures & {"box_breakout", "triangle_breakout"} and data["close"] > data["breakout_level"]:
        score += 5
        reasons.append("箱体或三角形向上突破得到确认，结构加5分。")
    if data["close"] >= data["high_20d"]:
        score += 4
        reasons.append("股价强势站上近20日高点，位置优势加4分。")

    if "m_top" in structures and data["close"] < data["support_level"] and data["volume_ratio_5d"] >= 1.3:
        score -= 8
        reasons.append("M顶形态完成且跌破颈线，结构转弱减8分。")
    if candles & {"hanging_man", "bearish_engulfing", "evening_star"} and data["close"] <= data["resistance_level"]:
        score -= 6
        reasons.append("阻力位附近出现看跌反转K线，形态位置减6分。")
    if "failed_breakout" in structures:
        score -= 5
        reasons.append("出现突破失败信号，减5分。")
    if data["close"] <= data["low_20d"]:
        score -= 4
        reasons.append("股价跌破近20日低点，位置转弱减4分。")
    return finalize_block(score, 0, 20, reasons)


def score_market_context(data: dict) -> tuple[int, int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    if data["benchmark_trend"] == "up":
        score += 4
        reasons.append("对应基准指数处于上行状态，环境加4分。")
    if data["industry_trend"] == "up":
        score += 3
        reasons.append("行业趋势向上，环境加3分。")
    if data["relative_strength_vs_index_20d"] > 0:
        score += 2
        reasons.append("近20日相对基准取得超额收益，强弱比较加2分。")
    if data["relative_strength_vs_industry_20d"] > 0:
        score += 1
        reasons.append("近20日相对行业取得超额收益，强弱比较加1分。")

    if data["benchmark_trend"] == "down":
        score -= 4
        reasons.append("对应基准指数走弱，环境减4分。")
    if data["industry_trend"] == "down":
        score -= 3
        reasons.append("行业趋势走弱，环境减3分。")
    if data["relative_strength_vs_index_20d"] < 0:
        score -= 2
        reasons.append("近20日跑输基准指数，强弱比较减2分。")
    if data["relative_strength_vs_industry_20d"] < 0:
        score -= 1
        reasons.append("近20日跑输行业，强弱比较减1分。")
    return finalize_block(score, 0, 10, reasons)


def classify_bias(total_score: int, data: dict) -> str:
    major_bearish = data["close"] < data["support_level"] and data["macd_cross"] == "dead"
    strong_trend_setup = (
        data["close"] > data["ma20"]
        and data["daily_trend"] == "up"
        and data["weekly_trend"] == "up"
        and data["monthly_trend"] != "down"
        and data["relative_strength_vs_index_20d"] > 0
    )
    if (total_score >= 70 or (total_score >= 55 and strong_trend_setup)) and not major_bearish:
        return "bullish"
    if major_bearish:
        return "bearish"
    if strong_trend_setup:
        return "watch"
    if total_score < 35:
        return "bearish"
    return "watch"


def build_output(data: dict) -> dict:
    trend_raw, trend_score, trend_status, trend_reasons = score_trend(data)
    volume_raw, volume_score, volume_status, volume_reasons = score_volume_price(data)
    indicator_raw, indicator_score, indicator_status, indicator_reasons = score_indicator(data)
    pattern_raw, pattern_score, pattern_status, pattern_reasons = score_pattern_position(data)
    context_raw, context_score, context_status, context_reasons = score_market_context(data)

    score_breakdown = {
        "trend": trend_score,
        "volume_price": volume_score,
        "indicator_confirmation": indicator_score,
        "pattern_position": pattern_score,
        "market_context": context_score,
    }
    score_details = {
        "trend": {"raw_score": trend_raw, "score": trend_score, "max_score": BLOCK_MAX["trend"], "score_status": trend_status, "reasons": trend_reasons},
        "volume_price": {"raw_score": volume_raw, "score": volume_score, "max_score": BLOCK_MAX["volume_price"], "score_status": volume_status, "reasons": volume_reasons},
        "indicator_confirmation": {"raw_score": indicator_raw, "score": indicator_score, "max_score": BLOCK_MAX["indicator_confirmation"], "score_status": indicator_status, "reasons": indicator_reasons},
        "pattern_position": {"raw_score": pattern_raw, "score": pattern_score, "max_score": BLOCK_MAX["pattern_position"], "score_status": pattern_status, "reasons": pattern_reasons},
        "market_context": {"raw_score": context_raw, "score": context_score, "max_score": BLOCK_MAX["market_context"], "score_status": context_status, "reasons": context_reasons},
    }
    total_score = sum(score_breakdown.values())
    bias = classify_bias(total_score, data)
    return {
        "ticker": data["ticker"],
        "name": data["name"],
        "as_of_date": data["as_of_date"],
        "bias": bias,
        "total_score": total_score,
        "score_breakdown": score_breakdown,
        "score_details": score_details,
        "stage": data["stage"],
        "trend_summary": {
            "daily": data["daily_trend"],
            "weekly": data["weekly_trend"],
            "monthly": data["monthly_trend"],
        },
        "key_levels": {
            "support": data["support_level"],
            "resistance": data["resistance_level"],
            "breakout": data["breakout_level"],
            "invalidation": data["invalidation_level"],
        },
        "signals": {
            "candlestick": data.get("candlestick_signals", []),
            "structure": data.get("structure_signals", []),
            "macd_cross": data["macd_cross"],
            "macd_divergence": data["macd_divergence"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to normalized JSON input")
    args = parser.parse_args()

    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    result = build_output(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
