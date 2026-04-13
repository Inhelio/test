#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass


Cell = tuple[int, int]
Grid = set[Cell]


PATTERNS: dict[str, Grid] = {
    "glider": {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)},
    "lwss": {(1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (4, 1), (4, 2), (0, 3), (3, 3)},
    "pulsar": {
        (2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0),
        (0, 2), (5, 2), (7, 2), (12, 2),
        (0, 3), (5, 3), (7, 3), (12, 3),
        (0, 4), (5, 4), (7, 4), (12, 4),
        (2, 5), (3, 5), (4, 5), (8, 5), (9, 5), (10, 5),
        (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
        (0, 8), (5, 8), (7, 8), (12, 8),
        (0, 9), (5, 9), (7, 9), (12, 9),
        (0, 10), (5, 10), (7, 10), (12, 10),
        (2, 12), (3, 12), (4, 12), (8, 12), (9, 12), (10, 12),
    },
    "r_pentomino": {(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)},
}


@dataclass(frozen=True)
class DiscoveryResult:
    fitness: int
    classification: str
    longevity: int
    peak_population: int
    pattern: Grid


def next_generation(cells: Grid, width: int, height: int) -> Grid:
    counts: dict[Cell, int] = {}
    for x, y in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    counts[(nx, ny)] = counts.get((nx, ny), 0) + 1

    return {
        cell
        for cell, neighbors in counts.items()
        if neighbors == 3 or (neighbors == 2 and cell in cells)
    }


def render(cells: Grid, width: int, height: int) -> str:
    live, dead = "█", " "
    lines = []
    for y in range(height):
        lines.append("".join(live if (x, y) in cells else dead for x in range(width)))
    return "\n".join(lines)


def random_pattern(width: int, height: int, live_cells: int, rng: random.Random) -> Grid:
    max_cells = width * height
    live_cells = min(live_cells, max_cells)
    all_positions = [(x, y) for y in range(height) for x in range(width)]
    return set(rng.sample(all_positions, k=live_cells))


def analyze_pattern(initial: Grid, width: int, height: int, steps: int) -> DiscoveryResult:
    cells = set(initial)
    seen: dict[frozenset[Cell], int] = {frozenset(cells): 0}
    peak_population = len(cells)
    classification = "chaotic"
    longevity = steps

    for generation in range(1, steps + 1):
        cells = next_generation(cells, width, height)
        peak_population = max(peak_population, len(cells))
        if not cells:
            classification = "dies_out"
            longevity = generation
            break

        key = frozenset(cells)
        if key in seen:
            period = generation - seen[key]
            longevity = generation
            classification = "still_life" if period == 1 else f"oscillator(period={period})"
            break
        seen[key] = generation

    fitness = longevity + peak_population + len(seen)
    return DiscoveryResult(
        fitness=fitness,
        classification=classification,
        longevity=longevity,
        peak_population=peak_population,
        pattern=set(initial),
    )


def centered_pattern(pattern: Grid, width: int, height: int) -> Grid:
    if not pattern:
        return set()
    max_x = max(x for x, _ in pattern)
    max_y = max(y for _, y in pattern)
    offset_x = max(0, (width - max_x - 1) // 2)
    offset_y = max(0, (height - max_y - 1) // 2)
    return {(x + offset_x, y + offset_y) for x, y in pattern}


def run_simulation(cells: Grid, width: int, height: int, steps: int, delay: float) -> None:
    state = set(cells)
    for generation in range(steps):
        print("\033[H\033[J", end="")
        print(f"Conway's Game of Life - generation {generation}")
        print(render(state, width, height))
        time.sleep(delay)
        state = next_generation(state, width, height)


def discover_patterns(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    results: list[DiscoveryResult] = []
    for _ in range(args.discover):
        pattern = random_pattern(args.width, args.height, args.seed_cells, rng)
        results.append(analyze_pattern(pattern, args.width, args.height, args.steps))

    top = sorted(results, key=lambda result: result.fitness, reverse=True)[: args.top]
    print(f"Top {len(top)} discovered patterns by fitness:")
    for idx, result in enumerate(top, start=1):
        print(
            f"{idx}. fitness={result.fitness} class={result.classification} "
            f"longevity={result.longevity} peak={result.peak_population} initial_cells={len(result.pattern)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conway's Game of Life simulator and pattern discovery.")
    parser.add_argument("--width", type=int, default=40, help="Grid width.")
    parser.add_argument("--height", type=int, default=20, help="Grid height.")
    parser.add_argument("--steps", type=int, default=80, help="Simulation steps to run.")
    parser.add_argument("--delay", type=float, default=0.08, help="Delay in seconds between generations.")
    parser.add_argument("--pattern", choices=sorted(PATTERNS), default="glider", help="Seed pattern.")
    parser.add_argument("--random-cells", type=int, default=0, help="Use a random seed with this many live cells.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--discover", type=int, default=0, help="Generate N random seeds and score them.")
    parser.add_argument("--seed-cells", type=int, default=12, help="Live cells per generated seed in discovery mode.")
    parser.add_argument("--top", type=int, default=10, help="How many top discovery results to show.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.discover > 0:
        discover_patterns(args)
        return

    rng = random.Random(args.seed)
    if args.random_cells > 0:
        cells = random_pattern(args.width, args.height, args.random_cells, rng)
    else:
        cells = centered_pattern(PATTERNS[args.pattern], args.width, args.height)
    run_simulation(cells, args.width, args.height, args.steps, args.delay)


if __name__ == "__main__":
    main()
