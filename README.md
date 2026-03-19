# Flocking Simulation with Boids

This project provides a 2D boids simulation in Python using `pygame`.

## Features

- 60 boids moving in real time
- Local flocking rules:
  - separation
  - alignment
  - cohesion
- Configurable radii/weights at top of file
- Speed and steering force limits for stability
- Screen wrapping
- Triangle boids that point in movement direction

## Run

```bash
python3 flocking_simulation.py
```

## Requirements

```bash
pip install pygame
```

Tune constants in `flocking_simulation.py` to compare different group behaviors.
