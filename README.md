# Braking events from a drive log

Resample recorded vehicle signals to a regular 10 Hz grid and identify braking events lasting at least 0.5 seconds. See `exercise.md` for the task and `NOTES.md` for assumptions.

## Setup

Requires Python 3.10 or newer. Run these commands from the repository folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas pytest
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Run

```sh
python solution.py
```

The script reads `drive.csv`, resamples the signals, and reports these events:

| start_s | end_s | duration_s | speed_drop_kmh |
| ---: | ---: | ---: | ---: |
| 5.1 | 8.1 | 3.0 | 18.33 |
| 20.1 | 22.6 | 2.5 | 28.80 |

Speed drops are rounded only for display. The 0.2-second press at 12.1 seconds is excluded.

## Tests

```sh
python -m pytest -q
```

Three tests use small hand-made DataFrames to check short-press filtering, speed interpolation across a NaN gap with brake-state preservation, and an event exactly at the minimum duration.
