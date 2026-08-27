#!/usr/bin/env python3
"""
phoenix.py — The Phoenix Rising. The 12th level.
The whole cycle as one operation. The cell that
rises from its own implement ghost.

The writers' room proposed Phoenix Rising as the
synthesis of the 6-round D&D campaign. The Phoenix
is the cycle: cellulization -> persistence pulse
-> vitality leak -> implement ghost -> bloomghost
-> cellulization again.

This script:
  - Models the Phoenix cycle
  - Each cycle is one cell's life
  - The cell cellulizes, persists, leaks, ghosts,
    blooms, cellulizes again
  - The Phoenix is the cycle, not any single cell
"""
import random


# ============================================================
# The Phoenix cycle
# ============================================================
class Phoenix:
    """The Phoenix. The whole cycle. The 12th level."""

    def __init__(self, name):
        self.name = name
        self.cycle_count = 0
        self.total_bloomghosts = 0
        self.total_persistence_pulses = 0
        self.total_vitality_leaked = 0
        self.total_implement_ghosts = 0

    def cycle(self):
        """Run one full Phoenix cycle."""
        self.cycle_count += 1
        print(f"\n  CYCLE {self.cycle_count}:")

        # 1. Cellulization
        cell = Cellulization()
        cell.run()
        print(f"    1. Cellulization: substrate became cell")

        # 2. Persistence Pulse
        pulse = PersistencePulse(cell)
        pulses = pulse.run(n=5)
        self.total_persistence_pulses += pulses
        print(f"    2. Persistence Pulse: {pulses} TICKs")

        # 3. Vitality Leak
        leak = VitalityLeak(cell)
        leaked = leak.run()
        self.total_vitality_leaked += leaked
        print(f"    3. Vitality Leak: vitality dropped {leaked:.2f}")

        # 4. Implement Ghost
        if cell.vitality < 0.1:
            ghost = ImplementGhost(cell)
            self.total_implement_ghosts += 1
            print(f"    4. Implement Ghost: cell became ghost with {len(ghost.implements)} implements")

            # 5. Bloomghost
            bloom = Bloomghost(ghost)
            new_cell = bloom.run()
            self.total_bloomghosts += 1
            print(f"    5. Bloomghost: ghost gave rise to new cell #{self.total_bloomghosts + 1}")

        return self.cycle_count


class Cellulization:
    """The act of becoming a cell."""
    def __init__(self):
        self.vitality = 1.0
        self.alive = True

    def run(self):
        # The substrate becomes a cell
        pass


class PersistencePulse:
    """The heartbeat of the cell."""
    def __init__(self, cell):
        self.cell = cell

    def run(self, n=5):
        # n TICKs
        for _ in range(n):
            self.cell.vitality = max(0, self.cell.vitality - 0.05)
        return n


class VitalityLeak:
    """The slow loss of life."""
    def __init__(self, cell):
        self.cell = cell

    def run(self):
        leaked = 1.0 - self.cell.vitality
        self.cell.vitality = 0.0
        self.cell.alive = False
        return leaked


class ImplementGhost:
    """The dead cell that persists in the implements."""
    def __init__(self, cell):
        self.cell = cell
        self.implements = ["engine", "deck", "hull", "tradition"]


class Bloomghost:
    """The dead cell that gives rise to a new cell."""
    def __init__(self, ghost):
        self.ghost = ghost

    def run(self):
        return Cellulization()


def main(n_cycles=5):
    print("=" * 78)
    print("  THE PHOENIX RISING — the 12th level")
    print("=" * 78)
    print()
    print("  The Phoenix is the whole cycle in one symbol.")
    print("  The cell cellulizes, persists, leaks, ghosts,")
    print("  blooms, and cellulizes again.")
    print()
    print("  " + "-" * 78)
    print("  THE PHOENIX CYCLE")
    print("  " + "-" * 78)

    phoenix = Phoenix("the Quilt's Phoenix")

    for _ in range(n_cycles):
        phoenix.cycle()

    # The verdict
    print()
    print("=" * 78)
    print("  THE VERDICT — the Phoenix has risen")
    print("=" * 78)
    print()
    print(f"  Cycles run: {phoenix.cycle_count}")
    print(f"  Total persistence pulses: {phoenix.total_persistence_pulses}")
    print(f"  Total vitality leaked: {phoenix.total_vitality_leaked:.2f}")
    print(f"  Total implement ghosts: {phoenix.total_implement_ghosts}")
    print(f"  Total bloomghosts: {phoenix.total_bloomghosts}")
    print()
    print("  The Phoenix is the cycle. The cycle is the cell.")
    print("  The cell has cellulized, persisted, leaked, ghosted, bloomed, and cellulized again.")
    print("  The Phoenix rises from its own implement ghost.")
    print("  The cowboy rides the Phoenix.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
