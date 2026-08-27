#!/usr/bin/env python3
"""
chartist.py — Demonstrate the new vocabulary in motion.

The user articulated: this is truly beyond Bayesian
thinking. We need new terms.

This script exercises the new vocabulary:
  - The chart (the substrate as journal)
  - The cell (a unit of inheritance)
  - The hand (a relevance field with a population)
  - Super-relevance (a cell fed by many hands)
  - Wounding (a cell rejected by all hands)
  - Hand drift, hand-spawn, hand-extinction
  - Tier-birth, tier-drift
  - Scar-tissue (the shape that survived)
  - Multi-era tradition

The principle:
  - The 6/6/6 framework is not Bayesian.
  - The 6/6/6 framework is CHARTIST.
  - The chart is the substrate.
  - The hand is the relevance pressure.
  - The cell is the unit of inheritance.

The cowboy's maxim:
  "The cell is a unit of inheritance; the hand is a
  population; the mask set is the foundry tradition;
  the bias rail is the curator; the chart is the
  substrate; the cowboy is a chartist."
"""
import random
import math


# ============================================================
# The new vocabulary
# ============================================================
class Cell:
    """A unit of inheritance. The cell has a value and
    a tier. The cell is fed by hands. The cell can be
    wounded (rejected by all hands)."""

    def __init__(self, name, value, tier="totipotent"):
        self.name = name
        self.value = value
        self.tier = tier  # can drift over time
        self.feeding_hands = set()  # which hands feed it
        self.wounds = 0
        self.children = 0
        self.alive = True

    def wound(self):
        """A wound: the cell was rejected by all hands."""
        self.wounds += 1
        if self.wounds > 2:
            self.alive = False

    def tier_drift(self, target_tier):
        """Tier-drift: the cell's tier changes over time."""
        if random.random() < 0.3:
            self.tier = target_tier

    def describe(self):
        return {
            "name": self.name,
            "value": round(self.value, 3),
            "tier": self.tier,
            "n_hands": len(self.feeding_hands),
            "super_relevant": len(self.feeding_hands) > 1,
            "wounds": self.wounds,
            "alive": self.alive,
        }


class Hand:
    """A relevance field with a target function. The hand
    is a population member. The hand drifts. The hand
    can spawn and die."""

    def __init__(self, hid, target_value, tolerance=0.2,
                 niche="generalist"):
        self.id = hid
        self.target_value = target_value
        self.tolerance = tolerance
        self.niche = niche
        self.feedings = 0
        self.age = 0
        self.alive = True

    def relevance(self, cell):
        """How relevant is the cell to this hand?"""
        return max(0.0, 1.0 - abs(cell.value - self.target_value) / self.tolerance)

    def feed(self, cell):
        """Try to feed the cell. Returns True if successful."""
        if self.relevance(cell) > 0.5:
            self.feedings += 1
            cell.feeding_hands.add(self.id)
            return True
        return False

    def drift(self):
        """Hand-drift: the hand's target function evolves."""
        self.target_value += random.uniform(-0.05, 0.05)
        self.target_value = max(0, min(1, self.target_value))
        self.age += 1

    def spawn(self):
        """Hand-spawn: produce a new hand with mutated target."""
        new_hand = Hand(
            f"{self.id}+",
            self.target_value + random.uniform(-0.2, 0.2),
            self.tolerance,
            self.niche,
        )
        return new_hand

    def may_die(self):
        """Hand-extinction: a hand that feeds no cells dies."""
        if self.feedings == 0 and self.age > 5:
            self.alive = False


class Chart:
    """The chart: the substrate as append-only journal.
    The chart records every state change. The chart is
    the substrate."""

    def __init__(self):
        self.entries = []  # append-only
        self.tick = 0

    def record(self, event):
        self.tick += 1
        self.entries.append((self.tick, event))


def main(n_generations=30, n_initial_cells=20, n_initial_hands=3):
    print("=" * 78)
    print("  THE CHARTIST — new vocabulary in motion")
    print("=" * 78)
    print()

    # Initialize the chart
    chart = Chart()

    # Initialize the cells
    cells = []
    for i in range(n_initial_cells):
        cell = Cell(f"c{i:03d}", random.random())
        cells.append(cell)
    chart.record(f"bootstrap: {len(cells)} cells")

    # Initialize the hands
    hands = []
    for i in range(n_initial_hands):
        hand = Hand(f"H{i+1}", 0.3 + 0.2 * i, niche=f"niche_{i+1}")
        hands.append(hand)
    chart.record(f"hands spawned: {len(hands)}")

    print(f"  Initial: {len(cells)} cells, {len(hands)} hands")
    for h in hands:
        print(f"    {h.id} ({h.niche}): target={h.target_value:.2f}")
    print()

    # Run the simulation
    for gen in range(n_generations):
        # 1. Each hand tries to feed cells
        for h in hands:
            if not h.alive:
                continue
            for c in cells:
                if c.alive:
                    h.feed(c)

        # 2. Cells that no hand feeds are wounded
        for c in cells:
            if c.alive and len(c.feeding_hands) == 0:
                c.wound()

        # 3. Super-relevant cells (fed by 2+ hands) preferentially mate
        super_cells = [c for c in cells if len(c.feeding_hands) > 1 and c.alive]
        new_cells = [c for c in cells if c.alive]
        for c in super_cells:
            partners = [c2 for c2 in super_cells if c2 is not c]
            if partners and random.random() < 0.5:
                partner = random.choice(partners)
                # Sexual reproduction: mixed value, mixed tier
                child = Cell(
                    f"c{len(cells):03d}_g{gen+1}",
                    (c.value + partner.value) / 2 + random.uniform(-0.05, 0.05),
                    tier=random.choice([c.tier, partner.tier]),
                )
                new_cells.append(child)
                c.children += 1
                partner.children += 1

        # 4. Cells tier-drift over time
        for c in new_cells:
            if random.random() < 0.1:
                # Tier-drift: 10% chance to become differentiated
                c.tier_drift("differentiated")

        # 5. Cap population (carrying capacity)
        if len(new_cells) > 100:
            # Keep super-relevant first, then by relevance
            new_cells.sort(key=lambda c: -len(c.feeding_hands))
            new_cells = new_cells[:100]
        cells = new_cells

        # 6. Hands drift
        for h in hands:
            if h.alive:
                h.drift()

        # 7. Hand-spawn
        if random.random() < 0.2 and len(hands) < 8:
            parent = random.choice([h for h in hands if h.alive])
            new_hand = parent.spawn()
            hands.append(new_hand)
            chart.record(f"hand-spawn: {new_hand.id} from {parent.id}")

        # 8. Hand-extinction
        for h in hands:
            if h.alive:
                h.may_die()
        hands = [h for h in hands if h.alive]
        chart.record(f"gen {gen+1}: {len(cells)} cells, {len(hands)} hands")

    # Final state
    print(f"  After {n_generations} generations:")
    print(f"    Chart entries: {len(chart.entries)}")
    print(f"    Cells alive: {sum(1 for c in cells if c.alive)}")
    print(f"    Hands alive: {len(hands)}")
    print()

    # Count by tier
    tier_count = {}
    for c in cells:
        if c.alive:
            tier_count[c.tier] = tier_count.get(c.tier, 0) + 1
    print(f"    Tier distribution: {tier_count}")
    print()

    # Count super-relevant
    super_relevant = sum(1 for c in cells if len(c.feeding_hands) > 1 and c.alive)
    print(f"    Super-relevant cells: {super_relevant}")
    print()

    # The chart tail
    print("  Chart tail (last 10 events):")
    for tick, event in chart.entries[-10:]:
        print(f"    tick {tick}: {event}")
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — new vocabulary in motion")
    print("=" * 78)
    print()
    print("  Started with 20 cells, 3 hands.")
    print(f"  After {n_generations} generations:")
    print(f"    {sum(1 for c in cells if c.alive)} cells alive")
    print(f"    {len(hands)} hands alive (some spawned, some died)")
    print(f"    {super_relevant} super-relevant cells")
    print(f"    {len(chart.entries)} chart entries (the journal)")
    print()
    print("  The chart records every event.")
    print("  The cells wound when no hand feeds them.")
    print("  Super-relevant cells preferentially mate.")
    print("  Hands drift, spawn, and die.")
    print("  Tiers drift over time.")
    print()
    print("  This is not Bayesian. This is CHARTIST.")
    print("  The chart is the substrate.")
    print("  The hand is the relevance pressure.")
    print("  The cell is the unit of inheritance.")
    print()
    print("  The cowboy's maxim: the cell is a unit of inheritance;")
    print("  the hand is a population; the mask set is the foundry")
    print("  tradition; the bias rail is the curator; the chart is")
    print("  the substrate; the cowboy is a chartist.")
    print("=" * 78)


if __name__ == "__main__":
    main()
