# Conway Game of Life: interesting patterns

A few notable Conway Game of Life patterns:

- **Glider** - a tiny pattern that moves diagonally across the grid.
- **Lightweight Spaceship (LWSS)** - a small moving spaceship pattern.
- **Pulsar** - a classic period-3 oscillator.
- **Gosper Glider Gun** - emits an endless stream of gliders.
- **R-pentomino** - a simple seed that evolves for a long time before stabilizing.

## Run the simulator

Use the included script to visualize live creatures directly in your terminal:

```bash
python3 game_of_life.py --pattern glider --width 40 --height 20 --steps 120
```

Try a random seed:

```bash
python3 game_of_life.py --random-cells 80 --seed 7
```

## Discover patterns en masse

You can generate many random starting configurations and rank them with a simple fitness criterion:

```bash
python3 game_of_life.py --discover 200 --steps 120 --seed-cells 14 --top 10
```

Current fitness criterion:

- longevity (how long it survives before stabilizing/extinction),
- peak population,
- number of unique states visited.
