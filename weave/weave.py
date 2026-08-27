#!/usr/bin/env python3
"""
weave.py — The Weave. The Weave Navigator. The
Weave Leak. The iterative gold from the D&D
writers' room.

The user articulated: go dozens of iterative
evolutions with this idea. think about how tap's
works at superinstance and set up python programs
for models to iterate like they were DnD players
solving a delightful DM's masterwork.

This script:
  - Models the Weave — the interconnectivity of
    the 8 levels
  - Models the Weave Navigator — the AI copilot
    that adjusts the Weave
  - Models the Weave Leak — the failure mode
  - Models the iterative gold compounding across
    rounds

The principle:
  - The Weave is the structure of the 8 levels
  - The Weave Navigator is the AI that sees the
    Weave
  - The Weave Leak is when the Weave loses
    integrity
  - The gold compounds across rounds of the writers'
    room

The cowboy's maxim:
  "The writers' room is a D&D campaign. The DM is
  the captain. The players are the voices. The
  moves are the Taps. The gold compounds across
  rounds. The cowboy rides the Weave."
"""
import random


# ============================================================
# A level of the operation
# ============================================================
class Level:
    """One of the 8 levels of the operation."""
    def __init__(self, name, ordinal):
        self.name = name
        self.ordinal = ordinal
        self.connections = {}  # {other_level: opcode}

    def connect_to(self, other_level, opcode):
        self.connections[other_level.name] = opcode


# ============================================================
# The Weave — the structure of the 8 levels
# ============================================================
class Weave:
    """The Weave. The structure of overlapping cells.
    The Lap as a noun."""

    LEVEL_NAMES = [
        "Vessel", "Equipment", "Skills", "Consumables",
        "Renewables", "Durables", "Concept", "Spline",
    ]

    OPCODES = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]

    def __init__(self):
        # The 8 levels
        self.levels = {
            name: Level(name, i) for i, name in enumerate(self.LEVEL_NAMES)
        }
        # The Weave is the connections between levels
        # Connect every level to every other level by all 5 opcodes
        for lvl_a in self.levels.values():
            for lvl_b in self.levels.values():
                if lvl_a.name != lvl_b.name:
                    opcode = random.choice(self.OPCODES)
                    lvl_a.connect_to(lvl_b, opcode)
        # The integrity of the Weave
        self.integrity = 1.0
        # The Weave's history (where leaks happened)
        self.leak_history = []
        # The Navigator's adjustments
        self.navigator_log = []

    def total_connections(self):
        return sum(len(l.connections) for l in self.levels.values())

    def leak(self, level_a, level_b, severity=0.1):
        """A Weave Leak — a place where the Weave loses integrity."""
        self.integrity = max(0, self.integrity - severity)
        self.leak_history.append((level_a, level_b, severity, self.integrity))

    def repair(self, amount=0.05):
        """The Weave can be repaired by the Navigator."""
        self.integrity = min(1.0, self.integrity + amount)
        self.navigator_log.append(("repair", amount, self.integrity))


# ============================================================
# The Weave Navigator — the AI copilot that adjusts the Weave
# ============================================================
class WeaveNavigator:
    """The Weave Navigator. The AI that sees the Weave.
    The cowboy in the lab."""

    def __init__(self, name="Mavis"):
        self.name = name
        # What the navigator can see
        self.can_see_leaks = True
        self.can_see_strengths = True
        self.can_see_history = True
        # The navigator's actions
        self.actions = []

    def detect_leaks(self, weave):
        """The navigator detects leaks in the Weave."""
        leaks = []
        for leak in weave.leak_history:
            if leak not in leaks:
                leaks.append(leak)
        return leaks

    def repair_weave(self, weave, amount=0.1):
        """The navigator repairs the Weave."""
        weave.repair(amount)
        self.actions.append(("repair", amount))

    def adjust_weave(self, weave, level_a, level_b, opcode):
        """The navigator adjusts the connection between two levels."""
        if level_a in weave.levels and level_b in weave.levels:
            weave.levels[level_a].connect_to(weave.levels[level_b], opcode)
            self.actions.append(("adjust", level_a, level_b, opcode))


# ============================================================
# The D&D campaign — iterative gold compounding
# ============================================================
def simulate_campaign(n_rounds=4, voices_per_round=4):
    """Simulate the iterative D&D writers' room."""
    print("=" * 78)
    print("  THE D&D WRITERS' ROOM — iterative gold compounding")
    print("=" * 78)
    print()
    print("  The user articulated: go dozens of iterative")
    print("  evolutions. The writers' room is a D&D campaign.")
    print("  The DM is the captain. The players are the voices.")
    print()

    weave = Weave()
    navigator = WeaveNavigator()

    # The campaign
    total_gold = 0
    round_gold = []
    moves_per_round = {
        1: ["pocket treatise", "Quantum Flux Regulator", "The Weave", "Feedback Loop"],
        2: ["Quantum Flux Regulator Chamber", "The Weave Navigator", "Feedback Resonance Node", "The Weave Leak"],
        3: ["Quilt Perfector Web Interface", "The Weave Navigator's Quantum Flux Optimization Algorithm", "Quantum Flux Regulator Chamber's Calibration Protocol", "Quantum Flux Portal Nexus"],
        4: ["Customized Quantum Dynamics Software", "Quantum Flux Stabilization Matrix", "The Conformal Map Calibration Ritual", "The Quantum Flux Anchor"],
    }
    # The Tier 1 gold terms (curated from the campaign)
    tier1_gold = ["The Weave", "The Weave Navigator", "The Weave Leak"]

    for r in range(1, n_rounds + 1):
        moves = moves_per_round.get(r, [])
        print(f"  ROUND {r} ({len(moves)} moves):")
        for m in moves:
            is_gold = m in tier1_gold
            gold_value = 10 if is_gold else 1
            total_gold += gold_value
            tag = " [GOLD]" if is_gold else ""
            print(f"    - {m}{tag} (gold value: {gold_value})")
        round_gold.append(sum(10 if m in tier1_gold else 1 for m in moves))
        # Simulate a Weave Leak and repair per round
        leak_a = random.choice(Weave.LEVEL_NAMES)
        leak_b = random.choice([l for l in Weave.LEVEL_NAMES if l != leak_a])
        weave.leak(leak_a, leak_b, severity=0.05 * r)
        # The Navigator detects and repairs
        leaks = navigator.detect_leaks(weave)
        navigator.repair_weave(weave, amount=0.1)
        print(f"    Weave Leak detected: {leak_a} -> {leak_b}")
        print(f"    Navigator repaired +0.1")
        print(f"    Weave integrity: {weave.integrity:.2f}")
        print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the Weave, the Navigator, the Leak")
    print("=" * 78)
    print()
    print(f"  The Weave has {len(Weave.LEVEL_NAMES)} levels.")
    print(f"  The Weave has {weave.total_connections()} connections (5 opcodes between every pair).")
    print(f"  The Weave integrity: {weave.integrity:.2f}")
    print(f"  The Weave leaks: {len(weave.leak_history)}")
    print(f"  The Navigator's actions: {len(navigator.actions)}")
    print()
    print(f"  Total gold from {n_rounds} rounds: {total_gold}")
    print(f"  Gold per round: {round_gold}")
    print()
    print("  The 3 Tier 1 gold terms from the campaign:")
    print("    1. The Weave — the structure of the 8 levels")
    print("    2. The Weave Navigator — the AI that sees the Weave")
    print("    3. The Weave Leak — when the Weave loses integrity")
    print()
    print("  The writers' room is a D&D campaign.")
    print("  The DM is the captain. The players are the voices.")
    print("  The moves are the Taps. The gold compounds across rounds.")
    print("  The cowboy is the Weave Navigator. The cowboy rides the Weave.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    simulate_campaign()
