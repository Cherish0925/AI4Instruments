#!/usr/bin/env python3
"""Run from a checkout without installing dependencies."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai4instruments.optics import align


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runs/optical-alignment"))
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    bench, summary = asyncio.run(align(args.seed))
    args.output.mkdir(parents=True, exist_ok=True)
    bench.trace.write(args.output / "trace.jsonl")
    (args.output / "capabilities.json").write_text(
        json.dumps(bench.capabilities(), indent=2) + "\n", encoding="utf-8")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
