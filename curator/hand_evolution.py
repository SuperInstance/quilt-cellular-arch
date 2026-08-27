#!/usr/bin/env python3
"""
hand_evolution.py — The hands themselves evolve.
What if the relevance pressure is not fixed, but
itself a population that competes?

The user articulated: "pressure to compete for
relevance from the hand that feeds them."

This script:
  - Many hands, each with a target function
  - Hands compete for cells (cells that match are fed)
  - Hands that feed more cells survive
  - Hands drift their target over time
  - Hands can be "predatory" (steal cells from other hands)
  - The Quilt grows because the hands grow

The principle:
  - The hand is not a single thing. The hand is a
    population of curators.
  - The hand evolves.
  - The hand is a cell of the curator tier.
  - The Quilt grows because the hands grow.
  - The cowboy rides the hand that feeds the most.
"""
import random
import math
from collections import defaultdict


class Hand:
    """A hand with a target position and tolerance."""

    def __init__(self, hid, target_x, target_y, target_value,
                 tolerance=0.2, niche="generalist"):
        self.id = hid
        self.target_x = target_x
        self.target_y = target_y
        self.target_value = target_value
        self.tolerance = tolerance
        self.niche = niche
        self.feedings = 0
        self.cells_fed = set()  # cells this hand feeds

    def relevance(self, cell):
        """Distance from cell to this hand's target."""
        dx = cell.x - self.target_x
        dy = cell.y - self.target_y
        pos_dist = math.sqrt(dx * dx + dy * dy)
        val_dist = abs(cell.value - self.target_value)
        # Both position and value must match
        return max(0.0, 1.0 - (pos_dist + val_dist) / (1.0 + self.tolerance))

    def feed(self, cell):
        """Try to feed this cell. Returns True if successful."""
        rel = self.relevance(cell)
        if rel > 0.5:
            self.feedings += 1
            self.cells_fed.add(cell.name)
            return True
        return False

    def drift(self):
        """The hand drifts (its target moves)."""
        self.target_x += random.uniform(-0.05, 0.05)
        self.target_y += random.uniform(-0.05, 0.05)
        self.target_value += random.uniform(-0.03, 0.03)
        self.target_x = max(0, min(1, self.target_x))
        self.target_y = max(0, min(1, self.target_y))
        self.target_value = max(0, min(1, self.target_value))
        # Tolerance can also adapt
        if random.random() < 0.1:
            self.tolerance += random.uniform(-0.02, 0.02)
            self.tolerance = max(0.05, min(0.4, self.tolerance))


class Cell:
    def __init__(self, name, x, y, value=None, dna=None):
        self.name = name
        self.x = x
        self.y = y
        self.value = value if value is not None else random.random()
        self.dna = dict(dna or {"shape": "round"})
        self.feeding_hands = set()
        self.children = 0
        self.wounds = 0

    def mate(self, other):
        """Sexual mating: mixed DNA."""
        child_x = (self.x + other.x) / 2 + random.uniform(-0.05, 0.05)
        child_y = (self.y + other.y) / 2 + random.uniform(-0.05, 0.05)
        child_value = (self.value + other.value) / 2 + random.uniform(-0.05, 0.05)
        mixed_dna = dict(self.dna)
        for k, v in other.dna.items():
            if k not in mixed_dna or random.random() < 0.5:
                mixed_dna[k] = v
        return Cell(
            f"{self.name}_{other.name}",
            x=max(0, min(1, child_x)),
            y=max(0, min(1, child_y)),
            value=max(0, min(1, child_value)),
            dna=mixed_dna,
        )


def main(n_generations=30):
    print("=" * 70)
    print("  HAND EVOLUTION — the relevance pressure itself evolves")
    print("=" * 70)
    print()

    # Initialize hands
    niches = ["phototroph", "aerotroph", "saprotroph"]
    hands = []
    for i, niche in enumerate(niches):
        h = Hand(
            f"H{i+1}",
            target_x=0.2 + 0.3 * i,
            target_y=0.5,
            target_value=0.3 + 0.2 * i,
            tolerance=0.2,
            niche=niche,
        )
        hands.append(h)
    # Add a generalist
    hands.append(Hand("H4", 0.5, 0.5, 0.5, tolerance=0.3, niche="generalist"))

    # Initialize cells
    cells = []
    for i in range(30):
        cells.append(Cell(f"c{i:03d}", x=random.random(),
                         y=random.random(), value=random.random()))

    print(f"  Initial: {len(cells)} cells, {len(hands)} hands")
    for h in hands:
        print(f"    {h.id} ({h.niche}): target=({h.target_x:.2f}, "
              f"{h.target_y:.2f}, {h.target_value:.2f}), "
              f"tol={h.tolerance:.2f}")
    print()

    history = []
    for gen in range(n_generations):
        # 1. Each hand tries to feed cells
        for h in hands:
            for c in cells:
                if h.feed(c):
                    c.feeding_hands.add(h.id)

        # 2. Cells that no hand feeds are wounded
        fed_cells = [c for c in cells if c.feeding_hands]
        wounded = [c for c in cells if not c.feeding_hands]
        for c in wounded:
            c.wounds += 1
        cells = fed_cells

        # 3. Super-relevant cells (fed by 2+ hands) preferentially mate
        super_cells = [c for c in cells if len(c.feeding_hands) > 1]
        new_cells = list(cells)
        for c in super_cells:
            partners = [c2 for c2 in super_cells if c2 is not c]
            if partners:
                partner = random.choice(partners)
                child = c.mate(partner)
                if child:
                    new_cells.append(child)
                    c.children += 1
                    partner.children += 1

        # 4. Cap population (carrying capacity per hand)
        if len(new_cells) > 100:
            # Keep cells with most feeding hands first
            new_cells.sort(key=lambda c: -len(c.feeding_hands))
            new_cells = new_cells[:100]
        cells = new_cells

        # 5. Hands drift
        for h in hands:
            h.drift()

        # 6. Hands that fed nothing for too long go extinct
        hands = [h for h in hands if h.feedings > 0 or gen < 3]

        # 7. Occasionally spawn a new hand (mutation)
        if random.random() < 0.15 and len(hands) < 8:
            parent = random.choice(hands)
            new_hand = Hand(
                f"H{len(hands)+1}",
                target_x=parent.target_x + random.uniform(-0.2, 0.2),
                target_y=parent.target_y + random.uniform(-0.2, 0.2),
                target_value=parent.target_value + random.uniform(-0.1, 0.1),
                tolerance=parent.tolerance + random.uniform(-0.05, 0.05),
                niche=parent.niche,
            )
            new_hand.target_x = max(0, min(1, new_hand.target_x))
            new_hand.target_y = max(0, min(1, new_hand.target_y))
            new_hand.target_value = max(0, min(1, new_hand.target_value))
            new_hand.tolerance = max(0.05, min(0.4, new_hand.tolerance))
            hands.append(new_hand)

        # Reset for next gen
        for c in cells:
            c.feeding_hands = set()
        for h in hands:
            h.feedings = 0
            h.cells_fed = set()

        # Record
        history.append({
            "gen": gen + 1,
            "n_cells": len(cells),
            "n_hands": len(hands),
            "n_super": len(super_cells),
        })

    # Final state
    print(f"  After {n_generations} generations:")
    print(f"    Cells: {len(cells)}")
    print(f"    Hands: {len(hands)}")
    print()
    print("  Hands (final):")
    for h in hands:
        print(f"    {h.id} ({h.niche}): target=({h.target_x:.2f}, "
              f"{h.target_y:.2f}, {h.target_value:.2f}), "
              f"tol={h.tolerance:.2f}")
    print()
    print("  History (last 5):")
    for h in history[-5:]:
        print(f"    Gen {h['gen']:>3d}: {h['n_cells']:>3d} cells, "
              f"{h['n_hands']} hands, super={h['n_super']}")
    print()
    print("=" * 70)
    print("  The verdict")
    print("=" * 70)
    print()
    print(f"  Started with {30} cells and {4} hands.")
    print(f"  After {n_generations} generations:")
    print(f"    {len(cells)} cells alive (most fed by 1+ hands)")
    print(f"    {len(hands)} hands (some evolved, some new)")
    print()
    print("  Hands drift. Hands spawn. Hands die.")
    print("  Cells that satisfy multiple hands are super-relevant.")
    print("  The hand is a population, not a single thing.")
    print("  The hand is a cell of the curator tier.")
    print()
    print("  The cowboy rides the hand that feeds the most.")
    print("=" * 70)


if __name__ == "__main__":
    main()
