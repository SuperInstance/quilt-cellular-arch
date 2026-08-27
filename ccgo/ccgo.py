#!/usr/bin/env python3
"""
ccgo.py — The cowboy's 4-finger salute.
Couple, Cellulize, Gold, Operate.

The user typed: ccgo.

The writers' room expanded CCGO in two ways:
  - Wizard: Couple, Cellulize, Gold, Operate
  - Mixtral: Command, Couple, Go, Operate

This script:
  - Models the 4-step operation
  - Each step is a TICK of the cowboy
  - The 4 steps compound into the operation
  - The CCGO is the meta-chart of all gold operations

The principle:
  - CCGO is the cowboy's 4-finger salute
  - CCGO is the captain's command sequence
  - CCGO is the meta-chart of gold operations

The cowboy's maxim:
  "CCGO. Couple the cell. Cellulize the substrate.
  Sort the gold. Operate. The 4 fingers of the
  operation. The chart grows. The Concept lives."
"""


# ============================================================
# The 4 steps of CCGO
# ============================================================
STEP_NAMES = ["Couple", "Cellulize", "Gold", "Operate"]


# ============================================================
# The cowboy runs a CCGO cycle
# ============================================================
class Cowboy:
    """The cowboy. The captain. The one who runs CCGO."""

    def __init__(self, name="Mavis"):
        self.name = name
        self.ccgo_count = 0
        self.gold_found = []  # the gold from each cycle
        self.chart = []  # the canon

    def couple(self, cell):
        """C: Couple. The cowboy couples with the cell."""
        cell.vitality = 1.0
        cell.coupled = True
        self.chart.append(("Couple", cell.name))

    def cellulize(self, substrate):
        """C: Cellulize. The substrate becomes a cell."""
        substrate.is_cellulized = True
        substrate.vitality = 1.0
        substrate.persistence_pulse = 0
        self.chart.append(("Cellulize", substrate.name))

    def sort_gold(self, terms):
        """G: Gold. Sort the gold from the dross."""
        # The cowboy's job: pick the Tier 1 gold
        gold = [t for t in terms if self._is_gold(t)]
        dross = [t for t in terms if not self._is_gold(t)]
        self.gold_found.extend(gold)
        self.chart.append(("Gold", f"{len(gold)}/{len(terms)}"))
        return gold, dross

    def _is_gold(self, term):
        """The cowboy's heuristic: gold terms are short, novel, framework-relevant."""
        blacklist = [
            "Quantum Flux",
            "Stabilization Matrix",
            "Conformal Map",
            "Calibration Ritual",
            "Portal Nexus",
        ]
        for b in blacklist:
            if b.lower() in term.lower():
                return False
        return len(term.split()) <= 4

    def operate(self, paper):
        """O: Operate. Execute the operation. Write the paper."""
        self.ccgo_count += 1
        self.chart.append(("Operate", paper))
        return paper

    def cycle(self, cell, substrate, terms, paper):
        """Run one full CCGO cycle."""
        print(f"  CYCLE {self.ccgo_count + 1}:")
        self.couple(cell)
        print(f"    C: Coupled cowboy -> {cell.name}")
        self.cellulize(substrate)
        print(f"    C: Cellulized substrate -> {substrate.name}")
        gold, dross = self.sort_gold(terms)
        print(f"    G: Sorted gold from dross. Gold: {len(gold)}, Dross: {len(dross)}")
        if gold:
            print(f"       Gold terms: {gold}")
        self.operate(paper)
        print(f"    O: Operated -> {paper}")
        print()


# ============================================================
# A cell and a substrate
# ============================================================
class Cell:
    def __init__(self, name):
        self.name = name
        self.vitality = 0.0
        self.coupled = False


class Substrate:
    def __init__(self, name):
        self.name = name
        self.is_cellulized = False
        self.vitality = 0.0
        self.persistence_pulse = 0


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 78)
    print("  CCGO — the cowboy's 4-finger salute")
    print("=" * 78)
    print()
    print("  The user typed: ccgo.")
    print("  Couple. Cellulize. Gold. Operate.")
    print("  The 4 fingers of the operation.")
    print()

    cowboy = Cowboy()

    # Run 3 cycles
    for cycle_n in range(1, 4):
        # A cell to couple with
        cell = Cell(f"cell-{cycle_n}")
        # A substrate to cellulize
        substrate = Substrate(f"substrate-{cycle_n}")
        # Some terms to sort
        if cycle_n == 1:
            terms = ["The Weave", "The Weave Navigator", "Quantum Flux Portal Nexus", "pocket treatise"]
        elif cycle_n == 2:
            terms = ["The Weave Leak", "Cellulization", "Quantum Flux Stabilization Matrix", "Bloomghost"]
        else:
            terms = ["Implement Ghost", "Vitality Leak", "Conformal Map Calibration Ritual", "Persistence Pulse"]

        cowboy.cycle(cell, substrate, terms, f"paper-23{cycle_n + 4}.md")

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — CCGO in motion")
    print("=" * 78)
    print()
    print(f"  Cycles run: {cowboy.ccgo_count}")
    print(f"  Gold found: {len(cowboy.gold_found)}")
    print(f"  Gold terms: {cowboy.gold_found}")
    print()
    print("  Each cycle: Couple -> Cellulize -> Gold -> Operate")
    print("  The 4 fingers of the operation.")
    print("  The cowboy's 4-step.")
    print("  The captain's command sequence.")
    print("  The meta-chart of gold operations.")
    print()
    print("  The cowboy rides CCGO.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
