#!/usr/bin/env python3
"""Recompute metrics for an explicit simulation-time window of saved raw odometry.

Example: python3 tools/analyze_samples.py results/baseline/samples.json
         results/baseline_window --start 227.94 --end 364.02
"""
import argparse
import json
from pathlib import Path

from odom_compare import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--end", type=float, required=True)
    args = parser.parse_args()
    if args.end <= args.start:
        parser.error("end must be greater than start")
    samples = json.loads(args.samples.read_text())
    selected = {name: [row for row in rows if args.start <= row[0] <= args.end]
                for name, rows in samples.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    metrics = evaluate(selected, (-0.032, 0.0, 0.078), args.output)
    metrics["analysis_window"] = {"start_sim_s": args.start, "end_sim_s": args.end,
                                   "source": str(args.samples)}
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
