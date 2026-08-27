#!/usr/bin/env python3
"""
spline.py — The function is the captain. The function
selects. The spline is the trajectory of the
captain's understanding.

The user articulated: the axe represents the enabler
of the function of chopping wood. Grandpa wanted to
chop wood so the tools and the wood changed over time
from out from under the function of wanting to chop
wood. He even changed houses three times so the
forests changed but since he wanted to chop wood and
heat his house that way instead of another way, he
chose a house each time with a wood stove and wood
source near by. Eileen is my forth boat. My option
grew in number each time I upgraded boats because of
my means. I chose Eileen because she was the right
fit for the concept of a good fishing boat that my
quilt of understanding grew into. And now if I do
get another boat, Eileen has shaped my understanding
of fishing and the spline of what boats I might see
as a step forward are shaped by the captain and son
in 1974 who replaced the old Atlas engine with what
at the time was a modern 6-71N latest edition. But
now is seen as the old but stable horse.

This script:
  - Models a captain's function over time
  - Models the option-set as the product of means
    and understanding
  - Models the spline — the trajectory of past
    choices that shapes future perception
  - Shows the function selects from the option-set
  - Shows the implement shapes the understanding

The principle:
  - The function is the captain
  - The function persists through all changes
  - The function selects from the option-set
  - The option-set is the product of means and
    understanding
  - The implement shapes the understanding
  - The spline is the trajectory of the
    understanding

The cowboy's maxim:
  "The function is the captain. The captain holds
  the function. The function selects from the
  option-set. The option-set is the product of
  means and understanding. The implement shapes
  the understanding. The spline is the trajectory
  of the understanding. The cowboy rides the
  function. The cowboy rides the spline."
"""
import math
import random


# ============================================================
# The function (the captain's invariant operation)
# ============================================================
class Function:
    """The function is the operation. The function is
    the invariant. The function is the captain."""

    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose
        self.birth_year = 1935
        self.current_year = 1935
        self.persists = True

    def describe(self):
        return f"function: {self.name} ({self.purpose})"

    def age(self):
        return self.current_year - self.birth_year


# ============================================================
# The captain — the one who holds the function
# ============================================================
class Captain:
    """A captain. Has a function. Has a means. Has a
    quilt of understanding. Has an option-set."""

    def __init__(self, name, function, means, quilt_size):
        self.name = name
        self.function = function
        self.means = means  # financial/social capital
        self.quilt_size = quilt_size  # size of quilt of understanding
        self.quilt = []  # the captain's accumulated experience
        self.option_set_size = self._compute_option_set()
        self.chosen_implements = []  # history of chosen boats/axes/houses
        self.spline = []  # the trajectory of past choices

    def _compute_option_set(self):
        """The option-set is the product of means and
        quilt of understanding."""
        return int(self.means * math.log(1 + self.quilt_size))

    def add_to_quilt(self, experience):
        """Add to the quilt of understanding. The quilt
        grows with experience."""
        self.quilt.append(experience)
        self.quilt_size = len(self.quilt)
        self.option_set_size = self._compute_option_set()

    def choose_implement(self, candidates, year):
        """The function (captain) selects the next
        implement from the option-set. The selection
        is shaped by the spline (history)."""
        # Score each candidate by:
        # 1. Fit to function (purpose match)
        # 2. Distance from spline (history-shaped)
        # 3. Available means
        scored = []
        for c in candidates:
            fit = 1.0 - abs(c.quality - 0.5)  # closer to 0.5 = better fit
            spline_dist = min(
                (abs(c.quality - p.quality) for p in self.chosen_implements),
                default=0
            )
            spline_score = 1.0 / (1.0 + spline_dist)  # closer to spline = better
            means_score = 1.0 if c.cost <= self.means else 0.0
            score = fit * 0.4 + spline_score * 0.4 + means_score * 0.2
            scored.append((c, score))

        # Pick the highest-scored
        best = max(scored, key=lambda x: x[1])
        chosen = best[0]
        self.chosen_implements.append(chosen)
        self.spline.append({"year": year, "quality": chosen.quality, "name": chosen.name})
        # The implement shapes the understanding
        self.add_to_quilt(f"year {year}: chose {chosen.name}")
        return chosen


# ============================================================
# The implement — the boat, axe, house, etc.
# ============================================================
class Implement:
    """An implement. An enabler of the function.
    Replaceable. Shaped by history."""

    def __init__(self, name, kind, quality, cost, year, era):
        self.name = name
        self.kind = kind
        self.quality = quality
        self.cost = cost
        self.year = year
        self.era = era  # "modern at the time" or "old but stable horse"


# ============================================================
# Grandpa's story — the axe, the houses, the function
# ============================================================
def grandpas_story():
    print("=" * 78)
    print("  GRANDPA'S STORY — the function is the captain")
    print("=" * 78)
    print()
    print("  Grandpa's function: chop wood to heat the house.")
    print("  The function persists through:")
    print("    - 3 axe handles + 2 axe heads (5 physical axes)")
    print("    - 3 houses (each with a wood stove and wood source nearby)")
    print()

    function = Function("chop wood and heat the house", "warmth through wood")

    # The 3 houses
    houses = [
        Implement("house 1", "house", quality=0.4, cost=1, year=1945, era="the old but stable house"),
        Implement("house 2", "house", quality=0.6, cost=2, year=1965, era="modern at the time"),
        Implement("house 3", "house", quality=0.5, cost=3, year=1985, era="old but stable horse"),
    ]

    # The 3 axes (well, the 5 physical axes = 1 logical axe)
    axes = [
        Implement("axe #1 (handle 1, head 1)", "axe", quality=0.4, cost=1, year=1945, era="the original"),
        Implement("axe #2 (handle 2, head 1)", "axe", quality=0.5, cost=1, year=1960, era="modern at the time"),
        Implement("axe #3 (handle 3, head 2)", "axe", quality=0.5, cost=1, year=1980, era="old but stable horse"),
    ]

    # Grandpa's lifecycle
    grandpa = Captain("Grandpa", function, means=3, quilt_size=2)
    print(f"  Grandpa's initial state:")
    print(f"    means: {grandpa.means}")
    print(f"    quilt_size: {grandpa.quilt_size}")
    print(f"    option_set_size: {grandpa.option_set_size}")
    print()

    # Choose the 3 houses over time
    print("  THE 3 HOUSES — chosen by the function:")
    print("  " + "-" * 78)
    for i, year in enumerate([1945, 1965, 1985]):
        # Grandpa's means grow over time
        grandpa.means = 1 + i
        # Choose a house from candidates
        chosen = grandpa.choose_implement(houses, year)
        print(f"  year {year}: chose {chosen.name}")
        print(f"    quality: {chosen.quality}, cost: {chosen.cost}, era: {chosen.era}")
        print(f"    option_set_size at this point: {grandpa.option_set_size}")
        print(f"    spline point: quality {chosen.quality}")
    print()

    # Choose the 3 axes over time
    print("  THE 3 AXES — chosen by the function (the function persists):")
    print("  " + "-" * 78)
    for i, year in enumerate([1945, 1960, 1980]):
        chosen = grandpa.choose_implement(axes, year)
        print(f"  year {year}: chose {chosen.name}")
        print(f"    quality: {chosen.quality}, era: {chosen.era}")
        print(f"    function persists: {function.persists}")
    print()

    # The verdict
    print("  " + "-" * 78)
    print("  GRANDPA'S VERDICT:")
    print("  " + "-" * 78)
    print()
    print(f"  Function age: {function.age()} years")
    print(f"  Function persists: {function.persists}")
    print(f"  Houses chosen: 3 (each with a wood stove and wood source)")
    print(f"  Axes chosen: 3 (5 physical axes = 1 logical axe)")
    print(f"  Spline points: {len(grandpa.spline)}")
    for p in grandpa.spline:
        print(f"    year {p['year']}: {p['name']} (quality {p['quality']})")
    print()
    print("  The function (wanting to chop wood) selected each house.")
    print("  The function (wanting to chop wood) selected each axe.")
    print("  The function is the captain. The function persists.")
    print("  The implements changed. The function is the same.")
    print()


# ============================================================
# Casey's story — the 4 boats and the spline
# ============================================================
def caseys_story():
    print("=" * 78)
    print("  CASEY'S STORY — the spline of possible-fishing-boats")
    print("=" * 78)
    print()
    print("  Casey's function: catch salmon and other fish from the sea.")
    print("  The function persists through 4 boats.")
    print()

    function = Function("be a fisherman", "harvest the sea")

    # The 4 boats
    boats = [
        Implement("boat 1 (Casey's 1st boat)", "boat", quality=0.3, cost=1, year=2000, era="the starter"),
        Implement("boat 2 (Casey's 2nd boat)", "boat", quality=0.5, cost=3, year=2010, era="the upgrade"),
        Implement("boat 3 (Casey's 3rd boat)", "boat", quality=0.6, cost=5, year=2015, era="the modern at the time"),
        Implement("Eileen (Casey's 4th boat)", "boat", quality=0.55, cost=7, year=2020, era="the old but stable horse"),
    ]

    # Casey's lifecycle
    casey = Captain("Casey (5th captain)", function, means=1, quilt_size=1)
    print(f"  Casey's initial state:")
    print(f"    means: {casey.means}")
    print(f"    quilt_size: {casey.quilt_size}")
    print(f"    option_set_size: {casey.option_set_size}")
    print()

    # Choose the 4 boats over time
    print("  THE 4 BOATS — chosen by the function (means grow, quilt grows):")
    print("  " + "-" * 78)
    for i, year in enumerate([2000, 2010, 2015, 2020]):
        # Casey's means grow over time
        casey.means = 1 + i * 2
        chosen = casey.choose_implement(boats, year)
        print(f"  year {year}: chose {chosen.name}")
        print(f"    quality: {chosen.quality}, cost: {chosen.cost}, era: {chosen.era}")
        print(f"    means at this point: {casey.means}")
        print(f"    option_set_size at this point: {casey.option_set_size}")
        print(f"    spline point: quality {chosen.quality}")
    print()

    # What about the next boat?
    print("  THE NEXT BOAT — the spline shapes what Casey sees as a step forward:")
    print("  " + "-" * 78)
    print()
    print("  Casey's spline (the trajectory of past choices):")
    for p in casey.spline:
        print(f"    year {p['year']}: {p['name']} (quality {p['quality']})")
    print()
    print("  The spline passes through points: 0.3 -> 0.5 -> 0.6 -> 0.55")
    print("  The spline is shaped by the 1974 captain's 6-71N Detroit (now old horse)")
    print("  The spline shapes what Casey sees as a step forward.")
    print("  The next boat Casey might see as a step forward would be near 0.55-0.6 quality.")
    print("  Casey would NOT see a step forward as a boat of 0.9 quality (too far from spline).")
    print()

    # The verdict
    print("  " + "-" * 78)
    print("  CASEY'S VERDICT:")
    print("  " + "-" * 78)
    print()
    print(f"  Function age: {function.age()} years (the 5th captain's function)")
    print(f"  Function persists: {function.persists}")
    print(f"  Boats chosen: 4")
    print(f"  Spline points: {len(casey.spline)}")
    print(f"  Quilt of understanding size: {casey.quilt_size}")
    print()
    print("  The function is the captain. The function selects from the option-set.")
    print("  The option-set is the product of means and understanding.")
    print("  The implement shapes the understanding. The spline is the trajectory.")
    print("  The next boat is shaped by every past choice.")
    print()


# ============================================================
# Main
# ============================================================
def main():
    grandpas_story()
    caseys_story()

    print("=" * 78)
    print("  THE FINAL VERDICT — the function is the captain")
    print("=" * 78)
    print()
    print("  The function is the operation. The function is the invariant.")
    print("  The function is the captain. The function selects.")
    print()
    print("  The option-set is the product of means and quilt of understanding.")
    print("  The option-set grows as the captain's means grow.")
    print("  The option-set grows as the captain's quilt grows.")
    print()
    print("  The function picks from the option-set.")
    print("  The implement shapes the understanding.")
    print("  The spline is the trajectory of the understanding.")
    print("  The spline is the gravity that pulls the future toward the past.")
    print()
    print("  The 1974 captain's 6-71N is now the old but stable horse.")
    print("  The current captain's spline passes through that point.")
    print("  The next boat the captain sees as a step forward is shaped")
    print("  by every past choice.")
    print()
    print("  The 8 levels of the operation:")
    print("    1. The Vessel")
    print("    2. The Equipment")
    print("    3. The Skills")
    print("    4. The Consumables")
    print("    5. The Renewables")
    print("    6. The Durables")
    print("    7. The Concept (the function)")
    print("    8. THE SPLINE (the trajectory of the captain's understanding)")
    print()
    print("  The cowboy rides the function. The cowboy rides the spline.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
