"""Micro-benchmarks for the pure-Python StringDataDeque implementation.

This script compares ``StringDeque`` against a few hand-written strategies such
as ``str.join`` over a list or incremental writes to :class:`io.StringIO`.

Usage example::

    uv run python benchmarks/bench1.py --size 5000 --length 64 --iterations 7

The script prints a small table with the average / best runtimes and an
approximate throughput expressed in MB/s.
"""

from __future__ import annotations

import argparse
import io
import statistics
import string
import sys
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from stringdatadeque import StringDeque
else:  # pragma: no cover - convenience for direct execution
    try:
        from stringdatadeque import StringDeque
    except ModuleNotFoundError:
        _PROJECT_ROOT = Path(__file__).resolve().parents[1]
        _SRC_PATH = _PROJECT_ROOT / "src"
        if _SRC_PATH.exists():
            sys.path.insert(0, str(_SRC_PATH))
            from stringdatadeque import StringDeque
        else:  # Fall back to the original error if the repo layout is unexpected.
            raise

# Type alias for the benchmark callables - each builder receives the payload and
# separator, then returns the final formatted string so work is not optimized
# away by Python.
BenchFunc = Callable[[Sequence[str], str], str]


@dataclass
class BenchResult:
    """Container for a single benchmark result."""

    label: str
    avg_s: float
    best_s: float
    throughput_mb_s: float


def _make_payload(size: int, length: int, seed: int) -> list[str]:
    """Return deterministic pseudo-random payload chunks."""
    rng = seed & 0xFFFFFFFF
    charset = string.ascii_letters + string.digits
    payload: list[str] = []
    for _ in range(size):
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        chunk = [charset[(rng >> shift) % len(charset)] for shift in range(length)]
        payload.append("".join(chunk))
    return payload


def _bench_case(
    label: str, func: BenchFunc, payload: Sequence[str], sep: str, iterations: int
) -> BenchResult:
    """Time ``func`` with ``payload`` and return summary statistics."""
    samples: list[float] = []
    total_chars = sum(len(item) for item in payload) + max(len(payload) - 1, 0) * len(
        sep
    )
    for _ in range(iterations):
        start = perf_counter()
        func(payload, sep)
        samples.append(perf_counter() - start)
    avg = statistics.mean(samples)
    best = min(samples)
    throughput = 0.0 if avg == 0 else (total_chars / avg) / 1_000_000
    return BenchResult(label=label, avg_s=avg, best_s=best, throughput_mb_s=throughput)


# --- benchmark targets ----------------------------------------------------


def bench_stringdeque(payload: Sequence[str], sep: str) -> str:
    """Benchmark using ``StringDeque`` as the builder."""
    dq = StringDeque(sep=sep)
    for chunk in payload:
        dq += chunk
    return str(dq)


def bench_list_append_then_join(payload: Sequence[str], sep: str) -> str:
    """Benchmark using ``list`` append then ``str.join``."""
    parts = list(payload)
    return sep.join(parts)


def bench_stringio(payload: Sequence[str], sep: str) -> str:
    """Benchmark repeated writes to :class:`io.StringIO`."""
    buffer = io.StringIO()
    last = len(payload) - 1
    for idx, chunk in enumerate(payload):
        buffer.write(chunk)
        if sep and idx != last:
            buffer.write(sep)
    return buffer.getvalue()


def bench_plus_equal(payload: Sequence[str], sep: str) -> str:
    """Benchmark naive ``+=`` concatenation."""
    result = ""
    for idx, chunk in enumerate(payload):
        if idx:
            result += sep
        result += chunk
    return result


# --- CLI ------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse CLI arguments for the benchmark harness."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size",
        type=int,
        default=2_000,
        help="number of string fragments to concatenate",
    )
    parser.add_argument(
        "--length", type=int, default=32, help="length of each fragment (characters)"
    )
    parser.add_argument(
        "--sep", type=str, default="\n", help="separator inserted between fragments"
    )
    parser.add_argument(
        "--iterations", type=int, default=500, help="number of samples per benchmark"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="seed for deterministic payload generation"
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point that orchestrates payload generation and reporting."""
    args = parse_args(argv or sys.argv[1:])
    payload = tuple(_make_payload(args.size, args.length, args.seed))

    benches: list[tuple[str, BenchFunc]] = [
        ("StringDeque", bench_stringdeque),
        ("StringIO (stream)", bench_stringio),
        ("+= (naive)", bench_plus_equal),
        ("list -> join (stream)", bench_list_append_then_join),
    ]

    results = [
        _bench_case(label, func, payload, args.sep, args.iterations)
        for label, func in benches
    ]
    results.sort(key=lambda res: res.avg_s, reverse=True)

    print(f"Fragments       : {args.size}")
    print(f"Fragment length : {args.length}")
    print(f"Iterations/case : {args.iterations}")
    print(f"Separator       : {args.sep!r}")
    print()
    print(f"{'Benchmark':25} {'avg (ms)':>10} {'best (ms)':>10} {'MB/s':>10}")
    print("-" * 60)
    for res in results:
        print(
            f"{res.label:25} "
            f"{res.avg_s * 1000:10.3f} "
            f"{res.best_s * 1000:10.3f} "
            f"{res.throughput_mb_s:10.2f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
