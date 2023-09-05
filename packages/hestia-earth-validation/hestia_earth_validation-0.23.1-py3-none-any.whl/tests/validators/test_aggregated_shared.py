from hestia_earth.validation.validators.aggregated_shared import (
    validate_quality_score_min
)


def test_validate_quality_score_min_valid():
    assert validate_quality_score_min({}) is True

    cycle = {
        'aggregatedQualityScore': 3,
        'aggregatedQualityScoreMax': 5
    }
    assert validate_quality_score_min(cycle) is True

    cycle = {
        'aggregatedQualityScore': 5,
        'aggregatedQualityScoreMax': 5
    }
    assert validate_quality_score_min(cycle) is True


def test_validate_quality_score_min_invalid():
    cycle = {
        'aggregatedQualityScore': 2,
        'aggregatedQualityScoreMax': 5
    }
    assert validate_quality_score_min(cycle) == {
        'level': 'error',
        'dataPath': '.aggregatedQualityScore',
        'message': 'must be at least equal to 3',
        'params': {
            'expected': 3,
            'current': 2,
            'min': 3,
            'max': 5
        }
    }
