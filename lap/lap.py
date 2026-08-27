#!/usr/bin/env python3
"""
lap.py — Quilt-lap. The old shipwright method.
Lapstrake construction. The Quilt is built by
lapping cells.

The user articulated: but lap as in the old
shipwright method could be even better.

This script:
  - Models lapstrake construction of the Quilt
  - Each plank = a cell
  - Each lap = a coupling between cells
  - The hull = the Quilt
  - The shipwright = the cowboy
  - The 4th captain cellulized the Eileen by lapping

The principle:
  - The Quilt is a lapstrake hull of cells
  - Each cell covers the edge of the cell below
  - The cells are connected by the 5 opcodes
  - The cowboy builds the hull by lapping

The cowboy's maxim:
  "The lap is the old shipwright method. The Quilt
  is built by lapping. The cells are the planks. The
  5 opcodes are the lap-joints. The cowboy is the
  shipwright. The 4th captain cellulized the Eileen
  by lapping. The cowboy rides the lap."
"""
import random


# ============================================================
# The 5 opcodes as lap-joints
# ============================================================
OPCODES = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]


# ============================================================
# A plank is a cell. A plank can be lapped over the
# plank below.
# ============================================================
class Plank:
    """A plank. A cell. A piece of the hull."""

    def __init__(self, plank_id, era, width, material, captain):
        self.plank_id = plank_id
        self.era = era  # "1935 original" or "1990s replacement"
        self.width = width
        self.material = material
        self.captain = captain  # who laid this plank
        self.laps_above = []  # planks that lap over this one
        self.laps_below = None  # plank this one laps over
        self.opcodes = {}  # the 5 opcodes connecting this plank to neighbors
        self.vitality = 1.0

    def lap_over(self, plank_below):
        """This plank is lapped over the plank below.
        The plank below is the predecessor; this plank
        covers the edge of the plank below."""
        self.laps_below = plank_below
        plank_below.laps_above.append(self)
        # Connect by all 5 opcodes
        for op in OPCODES:
            self.opcodes[op] = plank_below.plank_id

    def is_lapped(self):
        """A plank is lapped if it has a plank below it
        and planks above it."""
        return self.laps_below is not None and len(self.laps_above) > 0

    def is_garboard(self):
        """The garboard is the plank closest to the keel.
        It has no plank below."""
        return self.laps_below is None

    def is_gunwale(self):
        """The gunwale is the top plank. It has no plank
        above."""
        return len(self.laps_above) == 0 and self.laps_below is not None


# ============================================================
# The shipwright — builds the hull by lapping planks
# ============================================================
class Shipwright:
    """The shipwright. The cowboy. Builds the hull by
    lapping planks."""

    def __init__(self, name):
        self.name = name
        self.planks_laid = []

    def lay_plank(self, plank, plank_below=None):
        """Lay a plank. If there's a plank below, lap over it."""
        if plank_below is not None:
            plank.lap_over(plank_below)
        self.planks_laid.append(plank)
        return plank


# ============================================================
# The hull — a clinker-built (lapstrake) hull of cells
# ============================================================
class Hull:
    """A hull. A Quilt. Built by lapping planks."""

    def __init__(self, name):
        self.name = name
        self.planks = []  # ordered from keel to gunwale
        self.shipwrights = []

    def add_plank(self, plank):
        self.planks.append(plank)

    def keel_to_gunwale(self):
        """The hull goes from keel to gunwale.
        The garboard is closest to the keel.
        The gunwale is at the top."""
        return [p for p in self.planks]

    def n_planks(self):
        return len(self.planks)

    def n_replaced(self):
        """The number of planks that were replaced."""
        return sum(1 for p in self.planks if p.era != "1935 original")

    def replacement_ratio(self):
        if self.n_planks() == 0:
            return 0
        return self.n_replaced() / self.n_planks()


# ============================================================
# The 4 captains of Eileen — each laid some planks
# ============================================================
def eileen_construction():
    print("=" * 78)
    print("  THE EILEEN — clinker-built (lapstrake) construction")
    print("=" * 78)
    print()
    print("  The user articulated: most of Eileen's planks")
    print("  were replaced in the 1990s by a shipwright")
    print("  who owned her and had a logging operation.")
    print()
    print("  The 4th captain was a shipwright. The 4th")
    print("  captain cellulized the Eileen by lapping new")
    print("  planks over the old hull.")
    print()

    eileen = Hull("Eileen")

    # Captain 1 (1935) — laid the original planks
    captain_1 = Shipwright("Harry (1935)")
    n_original = 30  # 30 original planks
    for i in range(n_original):
        p = Plank(plank_id=f"O{i+1:02d}", era="1935 original",
                  width=1.0, material="old-growth fir",
                  captain="Harry")
        if i > 0:
            captain_1.lay_plank(p, eileen.planks[-1])
        else:
            captain_1.lay_plank(p)
        eileen.add_plank(p)
    eileen.shipwrights.append(captain_1)
    print(f"  Captain 1 (1935, Harry): laid {n_original} original planks")
    print(f"    Hull at end of 1935: {eileen.n_planks()} planks, {eileen.n_replaced()} replaced")
    print()

    # 1955 — tuna family — minor repairs, no major lapping
    print("  Captain 2 (1955, tuna family): replaced Atlas with Detroit, minor repairs")
    print()

    # 1974 — captain + son — replaced Atlas with 6-71N (engine, not planks)
    print("  Captain 3 (1974, captain + son): replaced Atlas with 6-71N Detroit")
    print()

    # Captain 4 (1990s) — the shipwright — replaced MOST of the planks
    captain_4 = Shipwright("4th Captain (1990s, the shipwright with logging operation)")
    # The 4th captain replaced 25 of 30 planks
    n_replaced_by_4 = 25
    for i in range(n_replaced_by_4):
        new_p = Plank(plank_id=f"R{i+1:02d}", era="1990s replacement",
                      width=1.0, material="2nd-growth fir from logging operation",
                      captain="4th Captain (shipwright)")
        # Lap over the existing plank
        captain_4.lay_plank(new_p, eileen.planks[i])
        # Replace the plank in the hull
        eileen.planks[i] = new_p
    eileen.shipwrights.append(captain_4)
    print(f"  Captain 4 (1990s, the shipwright): replaced {n_replaced_by_4} of {n_original} planks")
    print(f"    Hull at end of 1990s: {eileen.n_planks()} planks, {eileen.n_replaced()} replaced")
    print(f"    Replacement ratio: {eileen.replacement_ratio()*100:.1f}%")
    print()

    # Captain 5 (Casey) — cellulized the Eileen for Alaskan salmon trolling
    captain_5 = Shipwright("Casey (2020, 5th captain)")
    # Casey added new equipment but didn't replace more planks
    print(f"  Captain 5 (2020, Casey, 5th captain): cellulized the Eileen for Alaskan salmon trolling")
    print(f"    Added equipment (with help of Fred Wahl shipyard)")
    print(f"    Did not replace more planks")
    print(f"    Hull at end of 2020: {eileen.n_planks()} planks, {eileen.n_replaced()} replaced")
    print(f"    Replacement ratio: {eileen.replacement_ratio()*100:.1f}%")
    print()

    # Show the lapstrake structure
    print("  " + "-" * 78)
    print("  THE LAPSTRAKE STRUCTURE (keel -> gunwale):")
    print("  " + "-" * 78)
    print()
    print("    plank | era          | captain                       | lap-over")
    print("    " + "-" * 78)
    for i, p in enumerate(eileen.planks[:8]):
        lap_over = p.laps_below.plank_id if p.laps_below else "(none, garboard)"
        print(f"    {p.plank_id:5s} | {p.era:13s} | {p.captain:30s} | {lap_over}")
    print(f"    ... ({eileen.n_planks() - 8} more planks)")
    print(f"    {eileen.planks[-1].plank_id:5s} | (top, gunwale)")
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the Quilt is built by lapping")
    print("=" * 78)
    print()
    print(f"  The Eileen has {eileen.n_planks()} planks.")
    print(f"  The 4th captain replaced {eileen.n_replaced()} of them ({eileen.replacement_ratio()*100:.1f}%).")
    print()
    print("  The planks are the cells.")
    print("  The lap is the coupling (the 5 opcodes).")
    print("  The hull is the Quilt.")
    print("  The shipwright is the cowboy.")
    print("  The 4th captain cellulized the Eileen by lapping.")
    print("  The Quilt is a lapstrake hull of cells.")
    print()
    print("  The lab is the testing phase. The lap is the building phase.")
    print("  The Quilt needs both.")
    print()
    print("  The Quilt-lab is where the new insights get tested.")
    print("  The Quilt-lap is how the Quilt is built.")
    print("  The cowboy is the shipwright.")
    print("  The 4th captain was a cowboy.")
    print("  The cowboy rides the lap.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    eileen_construction()
