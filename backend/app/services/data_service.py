import math
from datetime import datetime


def calculate_summary(records: list[dict]) -> dict:
    """
    저장된 데이터(date, value, memo)를 받아 요약 정보를 생성한다.
    memo 값("금"/"은")별로 나눠서 각각 통계를 낸 뒤, 전체 요약도 함께 반환한다.
    """
    if not records:
        return {
            "period": None,
            "count": 0,
            "metrics": {},
            "trend": "데이터 없음"
        }

    dates = sorted(r["date"] for r in records)
    period = f"{dates[0]} ~ {dates[-1]}"
    count = len(records)

    # memo(자산 종류)별 그룹핑
    groups: dict[str, list[float]] = {}
    for r in records:
        groups.setdefault(r["memo"], []).append(r["value"])

    metrics = {}
    trends = {}
    for label, values in groups.items():
        avg = sum(values) / len(values)
        metrics[label] = {
            "count": len(values),
            "average": round(avg, 2),
            "max": round(max(values), 2),
            "min": round(min(values), 2),
        }
        # 최근 추세: 마지막 10개 vs 그 이전 10개 평균 비교
        trends[label] = _calc_trend(values)

    # 금/은 비율 (둘 다 있을 때만)
    ratio_info = {}
    if "금" in groups and "은" in groups:
        latest_gold = groups["금"][-1]
        latest_silver = groups["은"][-1]
        if latest_silver != 0:
            ratio_info["gold_silver_ratio"] = round(latest_gold / latest_silver, 2)

    return {
        "period": period,
        "count": count,
        "metrics": metrics,
        "trend": trends,
        "ratio": ratio_info,
    }


def _calc_trend(values: list[float], window: int = 10) -> str:
    """최근 구간과 이전 구간 평균을 비교해 상승/하락/유지 판단"""
    if len(values) < window * 2:
        window = max(1, len(values) // 2)

    recent = values[-window:]
    previous = values[-window * 2:-window] if len(values) >= window * 2 else values[:window]

    recent_avg = sum(recent) / len(recent)
    previous_avg = sum(previous) / len(previous)

    if previous_avg == 0:
        return "유지"

    change_pct = (recent_avg - previous_avg) / previous_avg * 100

    if change_pct > 1:
        return f"상승 (약 {change_pct:.1f}%)"
    elif change_pct < -1:
        return f"하락 (약 {change_pct:.1f}%)"
    else:
        return "유지"

    import math


def calculate_statistics(records: list[dict]) -> dict:
    """
    보너스: 추가 통계 지표 - 변동성(표준편차)과 최근 7일 변화율을 계산한다.
    """
    if not records:
        return {"message": "데이터 없음"}

    groups: dict[str, list[dict]] = {}
    for r in records:
        groups.setdefault(r["memo"], []).append(r)

    result = {}
    for label, items in groups.items():
        items_sorted = sorted(items, key=lambda x: x["date"])
        values = [item["value"] for item in items_sorted]

        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)

        # 최근 7개 데이터 기준 변화율
        recent_window = values[-7:] if len(values) >= 7 else values
        change_7d = None
        if len(recent_window) >= 2:
            change_7d = round(
                (recent_window[-1] - recent_window[0]) / recent_window[0] * 100, 2
            )

        result[label] = {
            "std_dev": round(std_dev, 2),
            "volatility_pct": round((std_dev / avg) * 100, 2) if avg else 0,
            "recent_7d_change_pct": change_7d,
            "latest_value": values[-1],
            "latest_date": items_sorted[-1]["date"],
        }

    return result