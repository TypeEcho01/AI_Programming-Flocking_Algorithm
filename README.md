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
- Triangle boids that point in movement direction
- Two simulation modes:
  - **classic**: standard flocking with screen wrapping
  - **challenge**: school-of-fish / drone-swarm behavior (flock + avoid predator + seek goal + stay inside arena)

## Run directly

```bash
python3 flocking_simulation.py --mode classic
python3 flocking_simulation.py --mode challenge
```

## Run with console launcher

```bash
python3 game_launcher.py
```

The launcher prompts you to choose which game mode to run.

You can also toggle mode in-app with **M**.
In challenge mode:

- a moving predator appears automatically
- left click sets a new goal point
- boids avoid boundaries using steering (no wrapping)

## Requirements

```bash
pip install pygame
```

Tune constants in `flocking_simulation.py` to compare different group behaviors.
