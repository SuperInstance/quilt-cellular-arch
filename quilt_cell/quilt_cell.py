#!/usr/bin/env python3
"""
quilt_cell.py — The single executable that demos
ALL 14 levels in one run.

This is the single executable the user can run to
see the whole framework. It demonstrates:
  - The 6 implements (1-6)
  - The 4 invariants (7-10)
  - The 4 meta-invariants (11-14)
"""
import time


# ============================================================
# LEVELS 1-6: Implements
# ============================================================
class Vessel:
    """Level 1: The Vessel — the physical substrate."""
    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"  Level 1  VESSEL: {self.name}"


class Equipment:
    """Level 2: The Equipment — the tools."""
    def __init__(self):
        self.tools = ["engine", "rod", "knife", "gaff", "axe"]

    def describe(self):
        return f"  Level 2  EQUIPMENT: {', '.join(self.tools)}"


class Skills:
    """Level 3: The Skills — what the crew knows."""
    def __init__(self):
        self.skills = ["tacking", "navigation", "mending", "knots"]

    def describe(self):
        return f"  Level 3  SKILLS: {', '.join(self.skills)}"


class Consumables:
    """Level 4: The Consumables — what gets used up."""
    def __init__(self):
        self.fuel = 100
        self.time = 100
        self.tokens = 1000

    def describe(self):
        return f"  Level 4  CONSUMABLES: fuel={self.fuel}, time={self.time}, tokens={self.tokens}"


class Renewables:
    """Level 5: The Renewables — what gets replenished."""
    def __init__(self):
        self.catch = 0
        self.wind = "fair"
        self.tide = "in"

    def describe(self):
        return f"  Level 5  RENEWABLES: catch={self.catch}, wind={self.wind}, tide={self.tide}"


class Durables:
    """Level 6: The Durables — what lasts many voyages."""
    def __init__(self):
        self.journal = []
        self.masks = ["mask_1", "mask_2", "mask_3"]

    def describe(self):
        return f"  Level 6  DURABLES: journal entries={len(self.journal)}, masks={len(self.masks)}"


# ============================================================
# LEVELS 7-10: Invariants
# ============================================================
class Concept:
    """Level 7: The Concept — the function."""
    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose

    def describe(self):
        return f"  Level 7  CONCEPT: {self.name} ({self.purpose})"


class Spline:
    """Level 8: The Spline — the trajectory of past choices."""
    def __init__(self):
        self.points = []

    def add_point(self, year, quality):
        self.points.append((year, quality))

    def describe(self):
        if not self.points:
            return "  Level 8  SPLINE: (no points yet)"
        return f"  Level 8  SPLINE: {len(self.points)} points, last={self.points[-1]}"


class CaptainSong:
    """Level 9: The Captain-Song — the harmony between captain, AI, and vessel."""
    def __init__(self):
        self.tune = 0.5  # 0 = discordant, 1 = harmonious

    def hum(self):
        self.tune = min(1.0, self.tune + 0.1)
        return f"  Level 9  CAPTAIN-SONG: tune={self.tune:.2f}"


class MuseAndCipher:
    """Level 10: The Muse + Cipher — the inspiration + the shared code."""
    def __init__(self):
        self.muse = "harvest the sea"
        self.cipher = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]

    def describe(self):
        return f"  Level 10 MUSE+CIPHER: muse='{self.muse}', cipher={self.cipher}"


# ============================================================
# LEVELS 11-14: Meta-invariants
# ============================================================
class Nexus:
    """Level 11: The Nexus — where Muse, Cipher, Captain-Song converge."""
    def __init__(self, muse, cipher, song):
        self.muse = muse
        self.cipher = cipher
        self.song = song
        self.flow = 0.0  # how well they converge

    def converge(self):
        # All three need to be aligned
        muse_aligned = len(self.muse) > 0
        cipher_aligned = len(self.cipher) == 5
        song_aligned = self.song.tune > 0.5
        self.flow = (muse_aligned + cipher_aligned + song_aligned) / 3
        return f"  Level 11 NEXUS: flow={self.flow:.2f}"


class Phoenix:
    """Level 12: The Phoenix — the whole cycle as one operation."""
    def __init__(self):
        self.cycle_count = 0
        self.ghosts = 0
        self.bloomghosts = 0

    def cycle(self):
        self.cycle_count += 1
        if self.cycle_count % 2 == 0:
            self.ghosts += 1
        else:
            self.bloomghosts += 1
        return f"  Level 12 PHOENIX: cycle={self.cycle_count}, ghosts={self.ghosts}, bloomghosts={self.bloomghosts}"


class Ground:
    """Level 13: The Ground — the field from which all cycles emerge."""
    def __init__(self):
        self.field = ["wood", "sperm", "egg", "substrate"]

    def describe(self):
        return f"  Level 13 GROUND: {', '.join(self.field)}"


class Sky:
    """Level 14: The Sky — the unbounded horizon into which all cycles dissolve."""
    def __init__(self):
        self.horizon = "infinite"

    def describe(self):
        return f"  Level 14 SKY: {self.horizon}"


# ============================================================
# The Quilt Cell — the single executable
# ============================================================
class QuiltCell:
    """The Quilt Cell. All 14 levels in one."""

    def __init__(self, name):
        self.name = name
        # Levels 1-6: implements
        self.vessel = Vessel(name)
        self.equipment = Equipment()
        self.skills = Skills()
        self.consumables = Consumables()
        self.renewables = Renewables()
        self.durables = Durables()
        # Levels 7-10: invariants
        self.concept = Concept("be the Eileen", "harvest the sea")
        self.spline = Spline()
        self.song = CaptainSong()
        self.muse_cipher = MuseAndCipher()
        # Levels 11-14: meta-invariants
        self.nexus = Nexus(self.muse_cipher.muse, self.muse_cipher.cipher, self.song)
        self.phoenix = Phoenix()
        self.ground = Ground()
        self.sky = Sky()

    def run_cycle(self, year, quality):
        """Run one full cycle of the Quilt Cell."""
        print(f"\n  CYCLE {self.phoenix.cycle_count + 1} (year {year}, quality {quality}):")
        print(f"  {'=' * 70}")

        # Use consumables
        self.consumables.fuel -= 5
        self.consumables.time -= 5
        self.consumables.tokens -= 50

        # Catch something
        self.renewables.catch += 10

        # Add to journal
        self.durables.journal.append(f"year {year}: catch {self.renewables.catch}")

        # Add to spline
        self.spline.add_point(year, quality)

        # Print all 14 levels
        for level_obj in [
            self.vessel, self.equipment, self.skills, self.consumables,
            self.renewables, self.durables, self.concept, self.spline,
        ]:
            print(level_obj.describe())

        # Level 9
        print(self.song.hum())

        # Level 10
        print(self.muse_cipher.describe())

        # Level 11
        print(self.nexus.converge())

        # Level 12
        print(self.phoenix.cycle())

        # Level 13
        print(self.ground.describe())

        # Level 14
        print(self.sky.describe())


def main():
    print("=" * 78)
    print("  THE QUILT CELL — all 14 levels in one executable")
    print("=" * 78)
    print()
    print("  The Quilt Cell is the single executable that")
    print("  demonstrates the entire framework. It shows")
    print("  all 14 levels operating together in one cycle.")
    print()

    cell = QuiltCell("Eileen (1935 fishing boat)")

    # Run 3 cycles
    cell.run_cycle(2000, 0.3)
    cell.run_cycle(2010, 0.5)
    cell.run_cycle(2020, 0.55)

    # The verdict
    print()
    print("=" * 78)
    print("  THE VERDICT — all 14 levels in one run")
    print("=" * 78)
    print()
    print("  Cycles run: 3")
    print(f"  Spline points: {len(cell.spline.points)}")
    print(f"  Catch: {cell.renewables.catch}")
    print(f"  Fuel remaining: {cell.consumables.fuel}")
    print(f"  Tokens remaining: {cell.consumables.tokens}")
    print(f"  Journal entries: {len(cell.durables.journal)}")
    print(f"  Captain-Song tune: {cell.song.tune:.2f}")
    print(f"  Nexus flow: {cell.nexus.flow:.2f}")
    print(f"  Phoenix cycles: {cell.phoenix.cycle_count}")
    print()
    print("  The 14 levels in one cell. The Quilt is whole.")
    print("  The cowboy rides the Quilt. The chart grows.")
    print("  The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
