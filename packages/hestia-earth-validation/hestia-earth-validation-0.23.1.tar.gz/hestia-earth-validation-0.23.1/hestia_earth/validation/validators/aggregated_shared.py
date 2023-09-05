def validate_quality_score_min(data: dict, max_diff: int = 2):
    key = 'aggregatedQualityScore'
    value = data.get(key, 0)
    max_value = data.get(key + 'Max', 0)
    min_value = max_value - max_diff
    return value >= min_value or {
        'level': 'error',
        'dataPath': f".{key}",
        'message': f"must be at least equal to {min_value}",
        'params': {
            'expected': min_value,
            'current': value,
            'min': min_value,
            'max': max_value
        }
    }
