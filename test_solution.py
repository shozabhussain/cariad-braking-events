"""Three focused tests using small, hand-made DataFrames."""

import pandas as pd
import pytest

from solution import find_braking_events, resample_signals


def test_short_press_is_ignored():
    signals = pd.DataFrame(
        {
            "speed_kmh": [50, 49, 48, 47],
            "brake_pressed": [0, 1, 1, 0],
        },
        index=[1.0, 1.1, 1.2, 1.3],
    )

    result = find_braking_events(signals)

    # The press lasts 0.2 seconds, below the default 0.5-second minimum.
    assert result.empty
    assert list(result.columns) == [
        "start_s", "end_s", "duration_s", "speed_drop_kmh",
    ]


def test_resampling_fills_nan_gap_and_preserves_brake_state():
    raw = pd.DataFrame(
        {
            "timestamp_s": [1.0, 1.15, 1.4],
            "speed_kmh": [50, float("nan"), 30],
            "brake_pressed": [0, 1, 0],
        }
    )

    result = resample_signals(raw)

    assert list(result.columns) == ["speed_kmh", "brake_pressed"]
    assert result.index.tolist() == pytest.approx([1.0, 1.1, 1.2, 1.3, 1.4])
    # Speed falls by 5 km/h per 0.1 seconds across the missing measurement.
    assert result["speed_kmh"].tolist() == pytest.approx([50, 45, 40, 35, 30])
    # The press at 1.15 takes effect at 1.2 on the output grid, not at 1.1.
    assert result["brake_pressed"].tolist() == [0, 0, 1, 1, 0]


def test_event_at_minimum_duration_is_kept():
    signals = pd.DataFrame(
        {
            "speed_kmh": [100, 50, 48, 46, 44, 42, 40],
            "brake_pressed": [0, 1, 1, 1, 1, 1, 0],
        },
        index=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    )

    result = find_braking_events(signals)

    assert len(result) == 1
    # Start at the first 1; end at the first following 0.
    assert result.iloc[0].to_dict() == pytest.approx({
        "start_s": 0.1,
        "end_s": 0.6,
        "duration_s": 0.5,
        "speed_drop_kmh": 10.0,
    })
