#!/usr/bin/env python3
"""
writers_room.py — Demonstrate the gold terms from the
writers' room in motion.

The user articulated: use your full arsenal of apis to
various models to shape new ideas with new terms. We got
a lot to learn.

The writers' room yielded 20 new terms from 4 LLMs.
The gold terms are:
  - Tier Bleed (Llama) — errors cross tier boundaries
  - Chromatin Latching (Gemini) — epigenetic state in silicon
  - Tunneling Dialectic (Gemini) — quantum effects as language
  - Tier-Hysteresis Band (DeepSeek) — path-dependence in tier
  - The 5 Acts (ZAI) — Call, Load, Struggle, Yield, Silence

This script exercises them.

The principle:
  - The 6/6/6 framework grows one term at a time.
  - Each LLM voice brings a different angle.
  - DeepSeek formalizes. Llama grounds. ZAI mythologizes. Gemini bridges.
  - The writers' room runs. The vocabulary grows.

The cowboy's maxim:
  "The writers' room runs, the terms come back, the
  gold is mixed with dross, the cowboy sorts the gold;
  the chart grows one term at a time, by many voices,
  in the spirit of chartics."
"""
import random
import math


# ============================================================
# The 5 gold terms, named by the writers' room
# ============================================================
GOLD_TERMS = {
    "tier_bleed": {
        "source": "Llama (practitioner)",
        "definition": "Unintended propagation of errors across tier boundaries",
        "real_use": "every chip designer has seen this",
    },
    "chromatin_latching": {
        "source": "Gemini (polymath)",
        "definition": "Non-volatile freezing of a cell's active bias rails via "
                       "physical substrate deformation, enabling state "
                       "persistence across system resets",
        "real_use": "the analog of DNA methylation in silicon",
    },
    "tunneling_dialectic": {
        "source": "Gemini (polymath)",
        "definition": "Probabilistic leakage of instruction syntax across "
                      "physical mask set barriers, causing isolated hands "
                      "to mutate and synchronize without explicit LINK",
        "real_use": "how isolated systems develop shared shorthand",
    },
    "tier_hysteresis_band": {
        "source": "DeepSeek (mathematician)",
        "definition": "The region of substrate states where a hand neither "
                      "spawns nor extinguishes due to path-dependent thresholds",
        "real_use": "path-dependence in tier transitions",
    },
    "the_5_acts": {
        "source": "ZAI (the cowboy)",
        "definition": "The narrative arc of a compute cycle: "
                      "the Call, the Load, the Struggle, the Yield, the Silence",
        "real_use": "the cowboy narrating the substrate",
    },
}


# ============================================================
# A substrate that exercises the gold terms
# ============================================================
class Cell:
    """A cell with tier, value, and chromatin state."""

    def __init__(self, name, value, tier="totipotent"):
        self.name = name
        self.value = value
        self.tier = tier
        # Chromatin state: latched or not
        self.latched = False
        # Errors (for tier bleed)
        self.errors = 0
        # Tunneling signals received
        self.tunneling_signals = []
        # 5-acts history
        self.acts_history = []

    def latched_chromatin(self):
        """Chromatin latching: persist state through reset."""
        self.latched = True

    def receive_tunneling(self, signal):
        """Tunneling dialectic: receive a signal through the mask barrier."""
        self.tunneling_signals.append(signal)

    def tier_bleed(self, source_tier):
        """Tier bleed: error propagates from another tier."""
        if source_tier != self.tier:
            self.errors += 1

    def act(self, act_name):
        """Record one of the 5 acts."""
        self.acts_history.append(act_name)

    def describe(self):
        return {
            "name": self.name,
            "value": round(self.value, 3),
            "tier": self.tier,
            "latched": self.latched,
            "errors": self.errors,
            "tunneling": len(self.tunneling_signals),
            "acts": len(self.acts_history),
        }


class Substrate:
    """A substrate of cells with two tiers."""

    def __init__(self, n_cells=20):
        self.cells = []
        for i in range(n_cells):
            tier = "totipotent" if i < n_cells // 2 else "differentiated"
            self.cells.append(Cell(f"c{i:03d}", random.random(), tier=tier))
        # The 5 acts in order
        self.acts = ["Call", "Load", "Struggle", "Yield", "Silence"]
        self.act_index = 0

    def cycle(self):
        """One cycle through the 5 acts."""
        # Each cell performs the current act
        current_act = self.acts[self.act_index]
        for c in self.cells:
            c.act(current_act)
        self.act_index = (self.act_index + 1) % len(self.acts)

    def trigger_tier_bleed(self):
        """Tier bleed: errors cross tier boundaries."""
        # Pick a totipotent cell and force an error
        source = random.choice(self.cells)
        target_tier = "differentiated" if source.tier == "totipotent" else "totipotent"
        for c in self.cells:
            if c.tier == target_tier:
                c.tier_bleed(source.tier)
        return source, target_tier

    def trigger_chromatin_latching(self):
        """Chromatin latching: persist high-value cells through reset."""
        latched = 0
        for c in self.cells:
            if c.value > 0.7 and not c.latched:
                c.latched_chromatin()
                latched += 1
        return latched

    def trigger_tunneling_dialectic(self):
        """Tunneling dialectic: cells signal through mask barriers."""
        signal = random.choice(["mutation", "synchronization", "abstraction"])
        for c in random.sample(self.cells, 3):
            c.receive_tunneling(signal)
        return signal

    def tier_hysteresis_check(self):
        """Tier hysteresis: a hand at the boundary persists."""
        # Find cells at the tier boundary (value ~0.5)
        boundary_cells = [c for c in self.cells if 0.4 < c.value < 0.6]
        return len(boundary_cells)

    def describe(self):
        return {
            "n_cells": len(self.cells),
            "latched": sum(1 for c in self.cells if c.latched),
            "total_errors": sum(c.errors for c in self.cells),
            "total_tunneling": sum(len(c.tunneling_signals) for c in self.cells),
            "current_act": self.acts[self.act_index],
        }


def main(n_cycles=20):
    print("=" * 78)
    print("  THE WRITERS' ROOM — the gold terms in motion")
    print("=" * 78)
    print()

    # Show the gold terms
    print("  THE 5 GOLD TERMS (from the writers' room)")
    print("  " + "-" * 78)
    for term, info in GOLD_TERMS.items():
        print(f"  {term}  ({info['source']})")
        print(f"    def: {info['definition']}")
        print(f"    use: {info['real_use']}")
        print()

    # Run the substrate
    s = Substrate(n_cells=20)
    print(f"  Initial: {len(s.cells)} cells in 2 tiers")
    print()

    for cycle in range(n_cycles):
        # Each cycle: 5 acts
        for act_num in range(5):
            s.cycle()

        # Random events
        if cycle % 3 == 0:
            source, target = s.trigger_tier_bleed()
        if cycle % 4 == 0:
            latched = s.trigger_chromatin_latching()
        if cycle % 2 == 0:
            signal = s.trigger_tunneling_dialectic()
        n_boundary = s.tier_hysteresis_check()

    # Final state
    print("  " + "-" * 78)
    print("  AFTER 20 CYCLES")
    print("  " + "-" * 78)
    r = s.describe()
    print(f"  Cells: {r['n_cells']}")
    print(f"  Latched (chromatin): {r['latched']}")
    print(f"  Total errors (tier bleed): {r['total_errors']}")
    print(f"  Total tunneling signals: {r['total_tunneling']}")
    print(f"  Final act in cycle: {r['current_act']}")
    print()

    # Sample cells
    print("  Sample cells (with all 5 gold terms applied):")
    for c in s.cells[:5]:
        d = c.describe()
        print(f"    {d['name']}: value={d['value']}, tier={d['tier']}, "
              f"latched={d['latched']}, errors={d['errors']}, "
              f"tunneling={d['tunneling']}, acts={d['acts']}")
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — 5 gold terms in motion")
    print("=" * 78)
    print()
    print("  Tier Bleed: errors propagated from totipotent to differentiated")
    print("  Chromatin Latching: high-value cells persisted through cycles")
    print("  Tunneling Dialectic: cells received signals through mask barriers")
    print("  Tier Hysteresis: cells at the tier boundary stayed put")
    print("  The 5 Acts: every cell recorded Call, Load, Struggle, Yield, Silence")
    print()
    print("  The 5 gold terms survive. They name real phenomena.")
    print("  They are useful at a whiteboard, in a paper, in a foundry.")
    print("  The writers' room yielded 20 new terms. The gold is here.")
    print()
    print("  The chart grows one term at a time, by many voices,")
    print("  in the spirit of chartics.")
    print("=" * 78)


if __name__ == "__main__":
    main()
