#!/usr/bin/env python3
"""
gold_43.py — The 5 Tier 1 gold terms from the writers'
room, in motion.

The 5 terms:
  1. Cellulization — the act of becoming a cell
  2. Implement Ghost — dead captain in the implements
  3. Bloomghost — dead cell giving rise to a new cell
  4. Vitality Leak — slow loss of life
  5. Persistence Pulse — the heartbeat of the concept

The principle:
  - The cell has a lifecycle
  - Cellulization -> Persistence Pulse -> Vitality Leak
    -> Implement Ghost -> Bloomghost -> Cellulization
  - The cycle continues across generations

The cowboy's maxim:
  "The writers' room runs. The terms come back. The
  gold is mixed with dross. The cowboy sorts the gold.
  The 5 Tier 1 terms are the gold this round. The
  chart grows one term at a time, by many voices, in
  the spirit of chartics."
"""
import random


# ============================================================
# A cell that can be cellulized, has a persistence pulse,
# can leak vitality, can become an implement ghost, and
# can give rise to a bloomghost.
# ============================================================
class Cell:
    def __init__(self, name, substrate):
        self.name = name
        self.substrate = substrate
        # Lifecycle state
        self.is_cellulized = False
        self.persistence_pulse = 0  # count of TICKs
        self.vitality = 0.0  # 0 to 1
        self.implements = []  # the implements the cell has touched
        self.bloomghost_count = 0  # count of new cells this cell has given rise to
        self.history = []

    def cellulize(self, function):
        """Become a cell. The act of becoming alive."""
        if not self.is_cellulized:
            self.is_cellulized = True
            self.vitality = 1.0
            self.function = function
            self.history.append((self.persistence_pulse, f"cellulized as {function}"))

    def tick(self):
        """One heartbeat. The persistence pulse."""
        if self.is_cellulized:
            self.persistence_pulse += 1
            # vitality leak — small per tick
            self.vitality = max(0, self.vitality - 0.02)

    def adapt(self, new_behavior):
        """Adaptation refills vitality (cell is growing)."""
        if self.is_cellulized:
            self.vitality = min(1.0, self.vitality + 0.05)
            self.history.append((self.persistence_pulse, f"adapted: {new_behavior}"))

    def grow(self):
        """Cell division — gives rise to a bloomghost."""
        if self.is_cellulized and self.vitality > 0.3:
            self.bloomghost_count += 1
            self.vitality = min(1.0, self.vitality + 0.1)
            self.history.append((self.persistence_pulse, f"gave rise to bloomghost #{self.bloomghost_count}"))
            return True
        return False

    def touch_implement(self, implement):
        """The cell's effect on an implement — will persist after death."""
        self.implements.append(implement)

    def die(self):
        """The cell dies. Becomes an implement ghost."""
        if self.is_cellulized:
            self.is_cellulized = False
            self.history.append((self.persistence_pulse, f"died — became implement ghost with {len(self.implements)} implements"))

    def is_alive(self):
        return self.is_cellulized and self.vitality > 0

    def status(self):
        if not self.is_cellulized and self.implements:
            return f"implement ghost (vitality 0, {len(self.implements)} implements)"
        elif not self.is_cellulized:
            return "dead"
        elif self.vitality < 0.3:
            return f"dying (vitality {self.vitality:.2f})"
        elif self.vitality < 0.7:
            return f"alive (vitality {self.vitality:.2f})"
        else:
            return f"thriving (vitality {self.vitality:.2f})"


# ============================================================
# The 5 captains of Eileen — each has its own lifecycle
# ============================================================
def simulate_captain(name, function, n_ticks, vitality_leak_rate=0.02):
    """Simulate one captain's lifecycle."""
    cell = Cell(name, "the captain's body and skills")

    # Cellulize (the captain takes the breath)
    cell.cellulize(function)

    history = []
    for tick in range(n_ticks):
        cell.tick()
        # Random adaptation
        if random.random() < 0.3:
            cell.adapt(f"new {function} technique at tick {tick}")
        # Random growth (new cells from this captain)
        if random.random() < 0.2:
            cell.grow()
        # The captain touches implements
        if tick % 5 == 0:
            cell.touch_implement(f"implement touched at tick {tick}")
        # Sometimes the captain dies early
        if tick == n_ticks - 1 and random.random() < 0.5:
            cell.die()
        history.append((tick, cell.status(), cell.vitality, cell.persistence_pulse, cell.bloomghost_count))

    return cell, history


def main():
    print("=" * 78)
    print("  THE 5 GOLD TERMS — in motion across 5 generations")
    print("=" * 78)
    print()
    print("  The 5 Tier 1 gold terms from the writers' room:")
    print("    1. Cellulization — the act of becoming a cell")
    print("    2. Implement Ghost — dead captain in the implements")
    print("    3. Bloomghost — dead cell giving rise to a new cell")
    print("    4. Vitality Leak — slow loss of life")
    print("    5. Persistence Pulse — the heartbeat of the concept")
    print()

    # The 5 captains
    captain_specs = [
        ("Captain Harry (1935)", "highliner crabbing", 30),
        ("Tuna family captain (1955)", "tuna fishing", 25),
        ("Cabin-rebuilder (1975)", "vessel maintenance", 30),
        ("Transitional (2000)", "tradition-keeping", 25),
        ("Casey (2020)", "longlining", 30),
    ]

    all_captains = []
    total_bloomghosts = 0
    total_implement_ghosts = 0
    total_pulses = 0

    for name, func, n in captain_specs:
        c, h = simulate_captain(name, func, n)
        all_captains.append((c, h))
        total_bloomghosts += c.bloomghost_count
        total_pulses += c.persistence_pulse
        if not c.is_cellulized:
            total_implement_ghosts += 1
        print(f"  {c.name}:")
        print(f"    function: {func}")
        print(f"    cellulized: {c.is_cellulized}")
        print(f"    persistence pulses: {c.persistence_pulse}")
        print(f"    bloomghosts given: {c.bloomghost_count}")
        print(f"    implements touched: {len(c.implements)}")
        print(f"    final status: {c.status()}")
        print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the 5 gold terms in motion")
    print("=" * 78)
    print()
    print(f"  Total persistence pulses (TICKs): {total_pulses}")
    print(f"  Total bloomghosts (new cells given rise to): {total_bloomghosts}")
    print(f"  Total implement ghosts (dead captains with implements): {total_implement_ghosts}")
    print()

    # The lifecycle
    print("  THE CELL LIFECYCLE (5 gold terms):")
    print("  " + "-" * 78)
    print()
    print("  1. CELLULIZATION — a substrate becomes a cell")
    print("     Each of the 5 captains was cellulized by taking the first breath.")
    print()
    print("  2. PERSISTENCE PULSE — the cell has a heartbeat")
    print(f"     The 5 captains had {total_pulses} persistence pulses (TICKs) total.")
    print()
    print("  3. VITALITY LEAK — the cell slowly dies")
    print("     Each captain's vitality leaked at 0.02/tick. Without adaptation, they die.")
    print()
    print("  4. IMPLEMENT GHOST — the dead cell's effect persists")
    print(f"     {total_implement_ghosts} captain(s) became implement ghosts after death.")
    print("     The implements the captain touched are still in the operation.")
    print()
    print("  5. BLOOMGHOST — the dead cell gives rise to a new cell")
    print(f"     The 5 captains gave rise to {total_bloomghosts} bloomghosts (new cells).")
    print("     Each captain is the bloomghost of the previous captain.")
    print()

    # The cycle
    print("  THE CYCLE:")
    print("  " + "-" * 78)
    print()
    print("  Cellulization -> Persistence Pulse -> Vitality Leak ->")
    print("  Implement Ghost -> Bloomghost -> Cellulization")
    print()
    print("  The cycle is the lifecycle of a cell. The cycle is the heartbeat of the Quilt.")
    print("  The cycle runs across generations. The cycle persists.")
    print()

    # The cowboy's maxim
    print("  THE COWBOY'S MAXIM (the deepest one yet):")
    print("  " + "-" * 78)
    print()
    print("  The writers' room runs. The terms come back. The gold is mixed")
    print("  with dross. The cowboy sorts the gold. The 5 Tier 1 terms are")
    print("  the gold this round. Cellulization. Implement Ghost. Bloomghost.")
    print("  Vitality Leak. Persistence Pulse. The chart grows one term at a")
    print("  time, by many voices, in the spirit of chartics. The cowboy rides")
    print("  between the gold. The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
