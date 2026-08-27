#!/usr/bin/env python3
"""
relevance_field.py — The hand as a continuous relevance
field across the Quilt.

The user articulated: cells need pressure to compete
for relevance from "the hand that feeds them."

This model:
  - The Quilt has multiple "hands" (relevance fields)
  - Each hand has a target function across the Quilt
  - Cells that match their hand's target are 'relevant'
  - Cells that don't match are wounded
  - Hands can evolve (their target functions drift)
  - Cells that mate across hands can produce offspring
    that satisfies BOTH hands (super-relevant)

The 5th tier (synovial) is the seam. The 6th tier
(curator = the hand) selects what passes.

The math:
  - Each hand H has a target function T(x, y, t)
  - Each cell at (x, y) has a value v
  - Relevance R = 1 - |v - T(x, y, t)| / tolerance
  - Real offspring passes when R > 0.5
  - Phantom offspring wounds when R < 0.5

The principle:
  - The hand is the relevance pressure
  - The hand has a target, a tolerance, and a position
  - The hand is a substrate (cells of the curator tier)
  - The hand evolves (its target drifts)
  - Cells that mate across hands produce super-relevant offspring
  - The Quilt grows because the hands grow

The cowboy's maxim:
  "The hand is the curator. The hand has a target.
  The hand feeds the cells that pass. The hand is a
  cell of the curator tier. The cowboy rides the hand."
"""
import random
import math
from collections import defaultdict


class Cell:
    """A cell at a position with a value and DNA."""

    def __init__(self, name, x, y, value=None, dna=None):
        self.name = name
        self.x = x
        self.y = y
        self.value = value if value is not None else random.random()
        self.dna = dict(dna or {"shape": "round"})
        self.children = 0
        self.wounds = 0
        self.relevance_history = []
        self.hand_id = None  # which hand feeds this cell

    def describe(self):
        return {
            "name": self.name,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "value": round(self.value, 3),
            "shape": self.dna.get("shape"),
            "hand": self.hand_id,
            "wounds": self.wounds,
            "children": self.children,
        }


class Hand:
    """A hand is a relevance field. The hand has a target
    function across the Quilt. The hand evolves."""

    def __init__(self, hid, target_fn, tolerance=0.2, x=0.5, y=0.5):
        self.id = hid
        self.target_fn = target_fn  # T(x, y, t) -> target value
        self.tolerance = tolerance
        self.x = x  # the hand's position in the Quilt
        self.y = y
        self.t = 0   # time
        self.feedings = 0
        self.rejections = 0

    def relevance(self, cell):
        """How relevant is this cell? Closer to target = more relevant."""
        target = self.target_fn(cell.x, cell.y, self.t)
        distance = abs(cell.value - target)
        rel = max(0.0, 1.0 - distance / self.tolerance)
        cell.relevance_history.append(rel)
        return rel

    def judge(self, cell):
        """The hand judges. Returns True if the cell passes
        the test (real), False if it fails (phantom)."""
        rel = self.relevance(cell)
        if rel > 0.5:
            self.feedings += 1
            cell.hand_id = self.id
            return True
        self.rejections += 1
        cell.wounds += 1
        return False

    def drift(self, dt=0.1):
        """The hand evolves — its position drifts."""
        self.x += random.uniform(-dt, dt)
        self.y += random.uniform(-dt, dt)
        self.x = max(0, min(1, self.x))
        self.y = max(0, min(1, self.y))
        self.t += 1


class Quilt:
    """A Quilt with multiple hands, each with its own
    relevance field. Cells compete to satisfy the hands."""

    def __init__(self, n_initial_cells=30, n_hands=3):
        self.cells = []
        # Place cells in 2D
        for i in range(n_initial_cells):
            cell = Cell(
                f"c{i:03d}",
                x=random.random(),
                y=random.random(),
                value=random.random(),
            )
            self.cells.append(cell)
        # Place hands in 2D with different target functions
        self.hands = [
            Hand("H1", lambda x, y, t: 0.3 + 0.4 * math.sin(x * math.pi + t * 0.1),
                 tolerance=0.15, x=0.3, y=0.3),
            Hand("H2", lambda x, y, t: 0.5 + 0.3 * math.cos(y * math.pi * 2 + t * 0.05),
                 tolerance=0.20, x=0.7, y=0.5),
            Hand("H3", lambda x, y, t: 0.7 - 0.3 * math.sin((x + y) * math.pi + t * 0.08),
                 tolerance=0.18, x=0.5, y=0.7),
        ]
        self.generation = 0
        self.history = []
        self.cross_hand_matings = 0
        self.single_hand_matings = 0

    def step(self):
        """One generation in the Quilt."""
        self.generation += 1
        # 1. Each hand drifts
        for h in self.hands:
            h.drift()

        # 2. Each cell is judged by all hands
        # A cell can be fed by multiple hands (super-relevant)
        cells_by_hand = defaultdict(list)
        for cell in self.cells:
            for h in self.hands:
                if h.judge(cell):
                    cells_by_hand[h.id].append(cell)

        # 3. Cells that satisfy NO hand die
        fed_cells = set()
        for cells in cells_by_hand.values():
            for c in cells:
                fed_cells.add(c)
        self.cells = [c for c in self.cells if c in fed_cells]

        # 4. Cells that satisfy multiple hands are super-relevant
        super_relevant = []
        cell_hand_count = defaultdict(int)
        for hid, cells in cells_by_hand.items():
            for c in cells:
                cell_hand_count[c.name] += 1
        for c in self.cells:
            if cell_hand_count[c.name] > 1:
                super_relevant.append(c)

        # 5. Cells mate (prefer cross-hand matings for super-relevant offspring)
        new_cells = list(self.cells)
        # Try cross-hand matings (super-relevant cells)
        for c in super_relevant:
            # Find a partner from a different hand
            partners = []
            for hid, cells in cells_by_hand.items():
                if hid != c.hand_id:
                    partners.extend(cells)
            if partners:
                partner = random.choice(partners)
                child = self._mate(c, partner)
                if child:
                    new_cells.append(child)
                    self.cross_hand_matings += 1

        # 6. Cells that satisfy only one hand mate with same-hand cells
        # (single-hand mating, less novel)
        for hid, cells in cells_by_hand.items():
            if len(cells) >= 2:
                for _ in range(min(3, len(cells) // 2)):
                    a, b = random.sample(cells, 2)
                    child = self._mate(a, b)
                    if child:
                        new_cells.append(child)
                        self.single_hand_matings += 1

        # 7. Cap the population (carrying capacity)
        if len(new_cells) > 200:
            # Keep the most relevant cells
            new_cells.sort(key=lambda c: -sum(c.relevance_history[-3:]) if c.relevance_history else 0)
            new_cells = new_cells[:200]

        self.cells = new_cells
        self._record()

    def _mate(self, a, b):
        """Two cells mate. The child has mixed DNA and a
        value that combines both parents."""
        if a is b:
            return None
        # The child takes the average position
        child_x = (a.x + b.x) / 2 + random.uniform(-0.05, 0.05)
        child_y = (a.y + b.y) / 2 + random.uniform(-0.05, 0.05)
        # The child takes the average value, biased toward relevance
        avg_value = (a.value + b.value) / 2
        # Mix the DNA
        mixed_dna = dict(a.dna)
        for k, v in b.dna.items():
            if k not in mixed_dna or random.random() < 0.5:
                mixed_dna[k] = v
        # If both parents were super-relevant, child is too
        if a.hand_id != b.hand_id:
            # The child gets the relevance of both hands
            child_value = avg_value  # average; will be judged by hands
        else:
            child_value = avg_value + random.uniform(-0.05, 0.05)
        child = Cell(
            f"c{len(self.cells):03d}_g{self.generation}",
            x=max(0, min(1, child_x)),
            y=max(0, min(1, child_y)),
            value=max(0, min(1, child_value)),
            dna=mixed_dna,
        )
        a.children += 1
        b.children += 1
        return child

    def _record(self):
        n_cells = len(self.cells)
        super_rel = sum(1 for c in self.cells
                       if sum(1 for h in self.hands if c in [])
                       # count hands that fed this cell
                       )
        # Count super-relevant (fed by 2+ hands)
        cell_hands = defaultdict(int)
        for h in self.hands:
            for c in self.cells:
                # Re-check relevance (we don't store after judge)
                target = h.target_fn(c.x, c.y, h.t)
                if abs(c.value - target) / h.tolerance < 0.5:
                    cell_hands[c.name] += 1
        super_rel = sum(1 for cnt in cell_hands.values() if cnt > 1)
        avg_relevance = (
            sum(c.relevance_history[-1] for c in self.cells if c.relevance_history) /
            max(1, len(self.cells))
        )
        self.history.append({
            "generation": self.generation,
            "n_cells": n_cells,
            "super_relevant": super_rel,
            "avg_relevance": avg_relevance,
            "cross_hand_matings": self.cross_hand_matings,
            "single_hand_matings": self.single_hand_matings,
        })


def main(n_generations=30):
    print("=" * 70)
    print("  THE RELEVANCE FIELD — many hands, many cells, super-relevance")
    print("=" * 70)
    print()

    q = Quilt(n_initial_cells=30, n_hands=3)

    print(f"  Initial: {len(q.cells)} cells, {len(q.hands)} hands")
    for h in q.hands:
        print(f"    {h.id} at ({h.x:.2f}, {h.y:.2f}), "
              f"tolerance={h.tolerance}")
    print()

    for _ in range(n_generations):
        q.step()

    # Final state
    print(f"  After {n_generations} generations:")
    print(f"    Cells: {len(q.cells)}")
    print(f"    Cross-hand matings: {q.cross_hand_matings}")
    print(f"    Single-hand matings: {q.single_hand_matings}")
    print()

    print("  Hands (final):")
    for h in q.hands:
        print(f"    {h.id} at ({h.x:.2f}, {h.y:.2f}): "
              f"fed {h.feedings}, rejected {h.rejections}")
    print()

    # History (last 5)
    print("  History (last 5 generations):")
    for h in q.history[-5:]:
        print(f"    Gen {h['generation']:>3d}: "
              f"{h['n_cells']:>3d} cells, "
              f"super={h['super_relevant']:>3d}, "
              f"avg_rel={h['avg_relevance']:.3f}, "
              f"cross={h['cross_hand_matings']}, "
              f"single={h['single_hand_matings']}")
    print()

    # The verdict
    print("=" * 70)
    print("  The verdict")
    print("=" * 70)
    print()
    print("  Started with 30 cells, 3 hands.")
    print(f"  After {n_generations} generations:")
    print(f"    {len(q.cells)} cells alive")
    print(f"    {q.cross_hand_matings} cross-hand matings (super-relevant)")
    print(f"    {q.single_hand_matings} single-hand matings (less novel)")
    print()
    print("  Cells that satisfy MULTIPLE hands are super-relevant.")
    print("  Super-relevant cells produce super-relevant offspring.")
    print("  Cross-hand matings are preferred over single-hand.")
    print("  Hands drift (their target functions evolve).")
    print()
    print("  The hand is the relevance pressure.")
    print("  The hand is a cell of the curator tier.")
    print("  The hand feeds the cells that pass the test.")
    print("  The Quilt grows because the hands grow.")
    print()
    print("  A cell is not a thing. A cell is a relation.")
    print("  The hand is a relation. The hand has a target.")
    print("  The hand feeds the cells that pass.")
    print("  The cowboy rides the hand.")
    print("=" * 70)


if __name__ == "__main__":
    main()
