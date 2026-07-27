"""Telemetry timing analysis for the recorded driving scenarios.

Every timing figure quoted in the README is produced by this script, so the
claims can be re-verified from the repository without a vehicle. Standard
library only: it runs without the virtual environment.

Usage:
    cd data-tools
    python analyze_telemetry.py
"""

import csv
import glob
import os
import statistics

# --- configuration ---
CSV_PATH = r"./CSV_files"
AUDIO_BLOCK = 64 / 48000.0  # Max signal vector at 48 kHz, in seconds
RECORD_SLEEP = 0.05         # fixed sleep in rec_data.py, in seconds
PID_COUNT = 3               # rpm, engine_load, speed


def percentile(values, p):
    """Linear-interpolated percentile (avoids a numpy dependency)."""
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    k = (len(ordered) - 1) * p / 100.0
    low = int(k)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (k - low)


def load_runs():
    """Read every CSV into a list of (name, timestamps, rpm, load, speed)."""
    runs = []
    for path in sorted(glob.glob(os.path.join(CSV_PATH, "*.csv"))):
        with open(path, mode="r") as file:
            rows = list(csv.DictReader(file))
        if len(rows) < 3:
            continue
        runs.append((
            os.path.basename(path),
            [float(r["timestamp"]) for r in rows],
            [float(r["rpm"]) for r in rows],
            [float(r["engine_load"]) for r in rows],
            [float(r["speed"]) for r in rows],
        ))
    return runs


def report_sampling(runs):
    """Effective frame rate and jitter of the OBD-II acquisition loop."""
    print("=" * 78)
    print("SAMPLING INTERVAL")
    print("=" * 78)
    print(f"{'run':<34}{'frames':>8}{'dur_s':>8}{'median_ms':>11}{'max_ms':>9}{'Hz':>7}")

    all_deltas = []
    total_frames = 0
    total_duration = 0.0

    for name, t, _, _, _ in runs:
        deltas = [b - a for a, b in zip(t, t[1:])]
        all_deltas += deltas
        total_frames += len(t)
        total_duration += t[-1] - t[0]
        print(f"{name:<34}{len(t):>8}{t[-1] - t[0]:>8.1f}"
              f"{statistics.median(deltas) * 1000:>11.1f}{max(deltas) * 1000:>9.1f}"
              f"{len(t) / (t[-1] - t[0]):>7.2f}")

    median = statistics.median(all_deltas)
    print("-" * 78)
    print(f"runs: {len(runs)} | frames: {total_frames} | "
          f"total driving time: {total_duration / 60:.1f} min")
    print(f"median interval : {median * 1000:.1f} ms  ->  {1 / median:.2f} Hz effective")
    print(f"mean interval   : {statistics.mean(all_deltas) * 1000:.1f} ms")
    print(f"std deviation   : {statistics.pstdev(all_deltas) * 1000:.1f} ms")
    print(f"p99 / max       : {percentile(all_deltas, 99) * 1000:.1f} ms / "
          f"{max(all_deltas) * 1000:.1f} ms "
          f"({max(all_deltas) / median:.2f}x median)")

    for threshold in (0.100, 0.150, 0.200):
        late = sum(1 for d in all_deltas if d > threshold)
        print(f"frames later than {threshold * 1000:.0f} ms: {late} "
              f"({100.0 * late / len(all_deltas):.2f}%)")

    print(f"\naudio blocks ({AUDIO_BLOCK * 1000:.2f} ms) elapsing between two telemetry frames:")
    print(f"  median {median / AUDIO_BLOCK:.0f} | "
          f"p99 {percentile(all_deltas, 99) / AUDIO_BLOCK:.0f} | "
          f"worst {max(all_deltas) / AUDIO_BLOCK:.0f}")

    return median


def report_pid_cost(median_interval):
    """Cost of each OBD-II round-trip, and the price of requesting more PIDs.

    rec_data.py issues PID_COUNT blocking queries and then sleeps a fixed
    RECORD_SLEEP, so the round-trip cost is what the measured interval has in
    excess of that sleep.
    """
    print("\n" + "=" * 78)
    print("COST OF ONE OBD-II ROUND-TRIP")
    print("=" * 78)

    per_pid = (median_interval - RECORD_SLEEP) / PID_COUNT
    print(f"{PID_COUNT} PIDs + {RECORD_SLEEP * 1000:.0f} ms sleep = "
          f"{median_interval * 1000:.0f} ms  ->  {per_pid * 1000:.1f} ms per round-trip\n")
    print(f"{'PIDs':>6}{'record loop':>16}{'live loop':>16}")

    for count in range(1, 7):
        # the live bridge subtracts query time from a 50 ms target, the
        # recorder does not: below 50 ms of queries the live loop still closes
        # on time, above it the deadline is missed and the rate degrades.
        record = count * per_pid + RECORD_SLEEP
        live = max(count * per_pid, RECORD_SLEEP)
        marker = "  <- current" if count == PID_COUNT else ""
        print(f"{count:>6}{1 / record:>13.2f} Hz{1 / live:>13.2f} Hz{marker}")


def report_resolution(runs):
    """Quantisation and per-frame movement of each control signal."""
    print("\n" + "=" * 78)
    print("CONTROL SIGNAL RESOLUTION")
    print("=" * 78)
    print(f"{'signal':<14}{'distinct':>10}{'min_step':>10}{'frames_changed':>16}"
          f"{'p99_jump':>10}{'max_jump':>10}")

    for index, label in ((2, "rpm"), (3, "engine_load"), (4, "speed")):
        values, steps = [], []
        for run in runs:
            series = run[index]
            values += series
            steps += [abs(b - a) for a, b in zip(series, series[1:])]
        moving = [s for s in steps if s > 0]
        print(f"{label:<14}{len(set(values)):>10}{min(moving):>10.3f}"
              f"{100.0 * len(moving) / len(values):>15.1f}%"
              f"{percentile(steps, 99):>10.2f}{max(steps):>10.2f}")

    print("\nspeed hold times at steady cruise (how long one value persists):")
    for name, t, _, _, speed in runs:
        if not name.startswith(("03_", "04_", "05_", "14_")):
            continue
        holds, run_length = [], 1
        for previous, current in zip(speed, speed[1:]):
            if current == previous:
                run_length += 1
            else:
                holds.append(run_length)
                run_length = 1
        holds.append(run_length)
        interval = statistics.median([b - a for a, b in zip(t, t[1:])])
        print(f"  {name:<34}{len(set(speed)):>3} distinct values | "
              f"mean {statistics.mean(holds):.1f} frames | "
              f"longest {max(holds)} frames ({max(holds) * interval:.1f} s frozen)")


def report_dropouts(runs):
    """Null OBD-II responses, which reach the synthesiser as a hard zero.

    A frame reporting zero RPM while the vehicle is moving cannot be a real
    engine state, so it isolates lost responses from genuine telemetry.
    """
    print("\n" + "=" * 78)
    print("DROPPED FRAMES")
    print("=" * 78)

    total = 0
    for name, t, rpm, load, speed in runs:
        events = [i for i in range(len(rpm)) if rpm[i] == 0 and speed[i] > 0]
        if not events:
            continue
        total += len(events)
        gaps = [b - a for a, b in zip(events, events[1:])]
        concurrent = sum(1 for i in events if load[i] == 0)
        lengths = set()
        run_length = 1
        for a, b in zip(events, events[1:]):
            if b == a + 1:
                run_length += 1
            else:
                lengths.add(run_length)
                run_length = 1
        lengths.add(run_length)

        print(f"\n{name}")
        print(f"  events            : {len(events)}, first at t={t[events[0]]:.1f} s")
        print(f"  event length      : {sorted(lengths)} frame(s)")
        print(f"  rpm and load both zero in the same frame: {concurrent}")
        if gaps:
            print(f"  spacing in frames : {sorted(set(gaps))}")
            multiples = all(g % 128 == 0 for g in gaps)
            print(f"  all spacings are exact multiples of 128 frames: {multiples}")

    print(f"\ntotal frames reporting zero RPM while moving: {total}")


def main():
    runs = load_runs()
    if not runs:
        print(f"Error: no CSV files found in {CSV_PATH}")
        return

    median_interval = report_sampling(runs)
    report_pid_cost(median_interval)
    report_resolution(runs)
    report_dropouts(runs)


if __name__ == "__main__":
    main()
