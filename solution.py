import math
import pandas as pd


def resample_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Return df on a regular 10 Hz grid (see exercise.md)."""

    signals = df.set_index("timestamp_s").sort_index()

    first_tick = math.ceil(signals.index.min() * 10)
    last_tick = math.floor(signals.index.max() * 10)

    grid = pd.Index(
        [tick / 10 for tick in range(first_tick, last_tick + 1)],
        name="timestamp_s",
    )

    combined_index = signals.index.union(grid).sort_values()
    expanded = signals.reindex(combined_index)
    expanded["speed_kmh"] = expanded["speed_kmh"].interpolate(
        method="index",
        limit_area="inside",
    )
    expanded["brake_pressed"] = expanded["brake_pressed"].ffill()

    return expanded.loc[grid, ["speed_kmh", "brake_pressed"]]


def find_braking_events(df: pd.DataFrame, min_duration_s: float = 0.5) -> pd.DataFrame:
    """Return one row per braking event (see exercise.md)."""

    columns = ["start_s", "end_s", "duration_s", "speed_drop_kmh"]
    events = []

    def add_event(start, end):
        duration = end - start
        qualifies = duration >= min_duration_s or math.isclose(
            duration, min_duration_s, rel_tol=0, abs_tol=1e-9
        )

        if qualifies:
            events.append({
                "start_s": start,
                "end_s": end,
                "duration_s": duration,
                "speed_drop_kmh": (
                    df.at[start, "speed_kmh"]
                    - df.at[end, "speed_kmh"]
                ),
            })

    start = None

    for timestamp, row in df.iterrows():
        if row["brake_pressed"] == 1 and start is None:
            start = timestamp

        elif row["brake_pressed"] == 0 and start is not None:
            add_event(start, timestamp)
            start = None

    if start is not None:
        add_event(start, df.index[-1])

    return pd.DataFrame(events, columns=columns)


if __name__ == "__main__":
    raw = pd.read_csv("drive.csv")
    signals = resample_signals(raw)
    print(signals)
    events = find_braking_events(signals)
    print(events.round({"speed_drop_kmh": 2}))
