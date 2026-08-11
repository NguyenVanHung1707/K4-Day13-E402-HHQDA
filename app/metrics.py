from __future__ import annotations

from collections import Counter
from statistics import mean


# =========================
# In-memory accumulators
# =========================

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
QUALITY_SCORES: list[float] = []

ERRORS: Counter[str] = Counter()

# Tổng số request đã được ghi nhận
TRAFFIC: int = 0


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
) -> None:
    """
    Ghi nhận metrics của một request thành công.
    """

    global TRAFFIC

    TRAFFIC += 1

    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)


def record_error(error_type: str) -> None:
    """
    Ghi nhận một request bị lỗi theo loại lỗi.

    Ví dụ:
        ValueError -> 2
        TimeoutError -> 3
    """

    ERRORS[error_type] += 1


def percentile(values: list[int], p: int) -> float:
    """
    Tính percentile theo nearest-rank method.

    Ví dụ:
        values = [100, 200, 300, 400]

        P50 -> 200
        P95 -> 400
        P99 -> 400
    """

    if not values:
        return 0.0

    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")

    items = sorted(values)

    # nearest-rank percentile
    rank = max(1, (p * len(items) + 99) // 100)

    index = min(rank - 1, len(items) - 1)

    return float(items[index])


def snapshot() -> dict:
    """
    Trả snapshot hiện tại cho endpoint /metrics.
    """

    total_errors = sum(ERRORS.values())

    # Các lỗi cũng là request đã được nhận.
    request_received = TRAFFIC + total_errors
    request_failed = total_errors

    error_rate_pct = (
        round((request_failed / request_received) * 100, 2)
        if request_received
        else 0.0
    )

    return {
        # Traffic
        "traffic": request_received,
        "request_received": request_received,

        # Latency
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),

        # Errors
        "request_failed": request_failed,
        "error_rate_pct": error_rate_pct,
        "error_breakdown": dict(ERRORS),

        # Cost
        "avg_cost_usd": (
            round(mean(REQUEST_COSTS), 4)
            if REQUEST_COSTS
            else 0.0
        ),
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),

        # Tokens
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),

        # Quality
        "quality_avg": (
            round(mean(QUALITY_SCORES), 4)
            if QUALITY_SCORES
            else 0.0
        ),
    }