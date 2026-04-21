import json
from pathlib import Path
from statistics import mean, pstdev


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_text(path, text):
    Path(path).write_text(text, encoding="utf-8")


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def safe_divide(numerator, denominator, default=0.0):
    if denominator in (0, None):
        return default
    return numerator / denominator


def moving_average(values, window):
    if not values:
        return 0.0
    if len(values) < window:
        return mean(values)
    return mean(values[-window:])


def ema(values, window):
    if not values:
        return []
    alpha = 2.0 / (window + 1.0)
    current = values[0]
    result = [current]
    for value in values[1:]:
        current = alpha * value + (1.0 - alpha) * current
        result.append(current)
    return result


def latest_macd_state(close_history):
    if len(close_history) < 5:
        return "neutral"
    ema12 = ema(close_history, 12)
    ema26 = ema(close_history, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal_line = ema(macd_line, 9)
    if macd_line[-1] > signal_line[-1] and macd_line[-1] > 0:
        return "bullish"
    if macd_line[-1] < signal_line[-1] and macd_line[-1] < 0:
        return "bearish"
    return "neutral"


def bollinger_position(close_history, window=20):
    if not close_history:
        return 0.0
    values = close_history[-window:] if len(close_history) >= window else close_history
    mid = mean(values)
    deviation = pstdev(values) if len(values) > 1 else 0.0
    if deviation == 0:
        return 0.0
    return (close_history[-1] - mid) / (2.0 * deviation)


def latest_volume_ratio(volume_history):
    if not volume_history:
        return 0.0
    base = moving_average(volume_history, 5)
    return safe_divide(volume_history[-1], base)


def correlation(series_a, series_b):
    if not series_a or not series_b:
        return 0.0
    size = min(len(series_a), len(series_b))
    a_values = series_a[-size:]
    b_values = series_b[-size:]
    mean_a = mean(a_values)
    mean_b = mean(b_values)
    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(a_values, b_values))
    std_a = sum((a - mean_a) ** 2 for a in a_values) ** 0.5
    std_b = sum((b - mean_b) ** 2 for b in b_values) ** 0.5
    if std_a == 0 or std_b == 0:
        return 0.0
    return cov / (std_a * std_b)


def shift_series_pair(series_a, series_b, lag):
    if lag == 0:
        size = min(len(series_a), len(series_b))
        return series_a[-size:], series_b[-size:]
    if lag > 0:
        size = min(len(series_a), len(series_b) - lag)
        return series_a[:size], series_b[lag:lag + size]
    lag = abs(lag)
    size = min(len(series_a) - lag, len(series_b))
    return series_a[lag:lag + size], series_b[:size]


def best_lead_lag(series_a, series_b, max_lag=5):
    best = {"lag": 0, "correlation": correlation(series_a, series_b)}
    for lag in range(-max_lag, max_lag + 1):
        left, right = shift_series_pair(series_a, series_b, lag)
        if len(left) < 5 or len(right) < 5:
            continue
        corr_value = correlation(left, right)
        if abs(corr_value) > abs(best["correlation"]):
            best = {"lag": lag, "correlation": corr_value}
    return best


def percentile_rank(values, target):
    if not values:
        return 0.0
    lower = sum(1 for value in values if value <= target)
    return 100.0 * lower / len(values)
