"""Simple console app that lets users choose which boids game mode to run."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("flocking_simulation.py")


def run_mode(mode: str) -> int:
    command = [sys.executable, str(SCRIPT_PATH), "--mode", mode]
    return subprocess.call(command)


def main() -> None:
    if not SCRIPT_PATH.exists():
        print("Could not find flocking_simulation.py in this folder.")
        return

    menu = {
        "1": "classic",
        "2": "challenge",
        "q": "quit",
    }

    while True:
        print("\n=== Boids Game Launcher ===")
        print("1) Classic Flocking")
        print("2) Challenge (Predator + Goal)")
        print("q) Quit")
        choice = input("Choose a game mode: ").strip().lower()

        if choice not in menu:
            print("Invalid choice. Please select 1, 2, or q.")
            continue

        mode = menu[choice]
        if mode == "quit":
            print("Goodbye!")
            return

        print(f"Launching {mode} mode... Close the pygame window to return here.")
        exit_code = run_mode(mode)
        if exit_code != 0:
            print(f"The game exited with code {exit_code}.")


if __name__ == "__main__":
    main()
