#!/usr/bin/env python3
"""
eileen.py — The 5 captains of Eileen. The boat
persists through 5 generations of captain replacement.
The captain persists through the name.

The user articulated: I'm the 5th captain/owner of Eileen.
But people still call me Eileen like I was Harry, who
had Eileen commissioned for his late career as a
highliner fisherman in 1935 way down in Aberdeen WA
so he could crab out of Newport OR. 20 years later,
another family tuna fished Eileen and replaced the
Atlas engine with the Detroit that was freshly rebuilt
when the new cabin, the third cabin for Eileen, was
build on her just before I threw hooks in for the
first time of her back deck. And Eileen is my 4th boat.
And I'm her 5th captain.

This script:
  - Models 5 generations of captain/boat replacement
  - Tracks the implements (vessel, equipment, cabins,
    consumables, durables, skills)
  - Tracks the Concept ("be the Eileen")
  - Tracks the irreducible breath (the first TICK)
  - Shows the Concept persists through 5 captains

The principle:
  - The 1st captain established the Concept in 1935
  - The Concept has been replaced zero times
  - The Concept has been inherited by 5 captains
  - The Concept has outlived 2 engines and 3 cabins
  - The 5th captain is the same as the 1st captain

The cowboy's maxim:
  "The 5th captain is the same as the 1st captain.
  The 4th boat is the same as the 1st boat. The
  captain is called Eileen. The boat is called Eileen.
  The Concept is be the Eileen. The cowboy rides
  the Concept. The chart grows. The Concept lives."
"""
import random


# ============================================================
# The implements
# ============================================================
class Implements:
    """The 6 implement levels — all replaceable."""

    def __init__(self):
        self.vessel = "Eileen hull #1 (1935)"
        self.engines = ["Atlas"]  # the engines, replaced over time
        self.cabins = ["cabin #1 (1935)"]
        self.skills = ["highliner crabbing"]
        self.consumables = {"fuel": 100, "bait": 100, "ice": 100, "time": 100}
        self.renewables = {"catch": 0, "wind": "fair", "tide": "in"}
        self.durables = {"hull": 1.0, "keel": 1.0, "traditions": []}

        # Replacement counts
        self.vessel_replacements = 0
        self.engine_replacements = 0
        self.cabin_replacements = 0
        self.skill_changes = 0

    def replace_engine(self, new_engine):
        self.engines.append(new_engine)
        self.engine_replacements += 1

    def build_cabin(self, cabin):
        self.cabins.append(cabin)
        self.cabin_replacements += 1

    def change_skill(self, new_skill):
        if new_skill not in self.skills:
            self.skills.append(new_skill)
            self.skill_changes += 1

    def consume(self, resource, amount):
        if resource in self.consumables:
            self.consumables[resource] = max(0, self.consumables[resource] - amount)

    def add_tradition(self, tradition):
        self.durables["traditions"].append(tradition)

    def degrade(self, amount):
        """The hull and keel slowly degrade."""
        self.durables["hull"] = max(0, self.durables["hull"] - amount * 0.01)
        self.durables["keel"] = max(0, self.durables["keel"] - amount * 0.005)


# ============================================================
# The captain
# ============================================================
class Captain:
    """A captain — the one who holds the concept."""

    def __init__(self, name, era, breath_taken=False):
        self.name = name  # all called "Eileen"
        self.era = era
        self.breath_taken = breath_taken  # the irreducible TICK
        self.first_act = None  # what the captain did first

    def take_breath(self):
        """The irreducible first breath — the first TICK."""
        self.breath_taken = True

    def first_act_of_command(self, action):
        """What the captain did first when they took the boat."""
        if self.first_act is None:
            self.first_act = action


# ============================================================
# The Concept
# ============================================================
class Concept:
    """The Concept — "be the Eileen". The invariant."""

    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose
        self.birth_year = 1935
        self.current_year = 1935
        self.inheritance_count = 0
        self.evolution_log = []

    def inherit(self, year, captain_name):
        """The Concept is inherited by a new captain."""
        self.inheritance_count += 1
        self.current_year = year
        self.evolution_log.append(
            (year, f"inherited by {captain_name} (inheritance #{self.inheritance_count})")
        )

    def persists(self):
        return True

    def age(self):
        return self.current_year - self.birth_year


# ============================================================
# The 5 captains of Eileen
# ============================================================
CAPTAINS = [
    {
        "name": "Eileen (Harry commissioned her)",
        "era": "1935-1955",
        "first_action": "commissioned Eileen in Aberdeen WA for highliner crabbing out of Newport OR",
        "engine": "Atlas",
        "skill": "highliner crabbing",
    },
    {
        "name": "Eileen (tuna family)",
        "era": "1955-1975",
        "first_action": "tuna fished Eileen, replaced Atlas engine with the Detroit",
        "engine": "Detroit (replaced Atlas)",
        "skill": "tuna fishing",
    },
    {
        "name": "Eileen (cabin-rebuilder)",
        "era": "1975-2000",
        "first_action": "Detroit freshly rebuilt; 3rd cabin built on her",
        "engine": "Detroit (rebuilt)",
        "skill": "vessel maintenance",
    },
    {
        "name": "Eileen (transitional)",
        "era": "2000-2020",
        "first_action": "kept the tradition, passed the boat on",
        "engine": "Detroit (aged)",
        "skill": "tradition-keeping",
    },
    {
        "name": "Casey (5th captain, 4th boat)",
        "era": "2020-now",
        "first_action": "threw hooks in for the first time on Eileen's back deck",
        "engine": "Detroit (current)",
        "skill": "longlining (new)",
    },
]


def main():
    print("=" * 78)
    print("  THE EILEEN — 5 captains, 4 boats, 1 concept")
    print("=" * 78)
    print()

    # The Concept
    concept = Concept("Eileen", "be a boat that lasts through generations")

    # The implements
    impl = Implements()

    # The captains
    captains = []

    print("  THE 5 CAPTAINS OF EILEEN")
    print("  " + "-" * 78)

    for i, c_info in enumerate(CAPTAINS):
        year_start = 1935 + (i * 20)
        year_end = 1935 + ((i + 1) * 20)
        if i == 4:
            year_end = 2026

        captain = Captain(c_info["name"], c_info["era"])
        captains.append(captain)

        # The captain takes the breath (irreducible TICK)
        captain.take_breath()
        # The captain performs the first act
        captain.first_act_of_command(c_info["first_action"])
        # The captain inherits the Concept
        concept.inherit(year_start, c_info["name"])
        # The captain may replace implements
        if "Detroit" in c_info["engine"] and "replaced" in c_info["engine"]:
            impl.replace_engine("Detroit")
        if "rebuilt" in c_info["engine"]:
            impl.replace_engine("Detroit (rebuilt)")
        if "cabin" in c_info["first_action"]:
            impl.build_cabin(f"cabin #{len(impl.cabins) + 1}")
        if c_info["skill"] not in impl.skills:
            impl.change_skill(c_info["skill"])
        # The captain adds a tradition
        impl.add_tradition(
            f"{year_start}: {c_info['first_action']}"
        )
        # The captain consumes
        impl.consume("fuel", 20)
        impl.consume("bait", 30)
        impl.consume("ice", 25)
        impl.consume("time", 30)
        # The hull degrades slightly
        impl.degrade(50)
        # The renewables fluctuate
        impl.renewables["catch"] = random.randint(0, 200)

        print(f"  Captain #{i+1}: {c_info['name']}")
        print(f"    Era: {c_info['era']}")
        print(f"    First act: {c_info['first_action']}")
        print(f"    Engine: {c_info['engine']}")
        print(f"    Skill: {c_info['skill']}")
        print(f"    Breath taken: {captain.breath_taken}")
        print()

    # Final state
    print("  " + "-" * 78)
    print("  THE 5 CAPTAINS, 4 BOATS, 1 CONCEPT")
    print("  " + "-" * 78)
    print(f"  Concept age: {concept.age()} years")
    print(f"  Concept persists: {concept.persists()}")
    print(f"  Inheritance count: {concept.inheritance_count}")
    print(f"  Concept replacements: 0 (the Concept has been replaced zero times)")
    print()
    print(f"  Vessel replacements: {impl.vessel_replacements}")
    print(f"  Engine replacements: {impl.engine_replacements}")
    print(f"    Engines used: {impl.engines}")
    print(f"  Cabin replacements: {impl.cabin_replacements}")
    print(f"    Cabins: {impl.cabins}")
    print(f"  Skill changes: {impl.skill_changes}")
    print(f"    Skills: {impl.skills}")
    print(f"  Hull integrity: {impl.durables['hull']:.2f}")
    print(f"  Keel integrity: {impl.durables['keel']:.3f}")
    print(f"  Traditions recorded: {len(impl.durables['traditions'])}")
    print()
    print("  Consumables after 5 captains (exhausted many times over):")
    for k, v in impl.consumables.items():
        print(f"    {k}: {v}")
    print()

    # The evolution log
    print("  Concept evolution (inheritance chain):")
    for year, event in concept.evolution_log:
        print(f"    year {year}: {event}")
    print()

    # The traditions
    print("  Traditions (the durables):")
    for t in impl.durables["traditions"]:
        print(f"    {t}")
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the 5th captain and the irreducible breath")
    print("=" * 78)
    print()
    print(f"  After 5 captains and {concept.age()} years:")
    print(f"    Concept persists: {concept.persists()}")
    print(f"    Concept inherited {concept.inheritance_count} times")
    print(f"    Implement replacements:")
    print(f"      Engines: {impl.engine_replacements} (Atlas -> Detroit)")
    print(f"      Cabins: {impl.cabin_replacements} (3 cabins)")
    print(f"      Skills: {impl.skill_changes}")
    print(f"    Hull still holds: {impl.durables['hull']:.2f}")
    print(f"    Keel still holds: {impl.durables['keel']:.3f}")
    print()
    print("  The 5th captain took his first breath on Eileen's back deck.")
    print("  The breath is the irreducible act. The breath IS the bootstrap.")
    print("  The breath is the same breath the 1st captain took in 1935.")
    print()
    print("  The captain is called Eileen.")
    print("  The boat is called Eileen.")
    print("  The Concept is be the Eileen.")
    print("  The Concept has been inherited by 5 captains.")
    print("  The Concept has outlived 2 engines and 3 cabins.")
    print("  The Concept is the irreducible breath, repeated by every")
    print("  captain since.")
    print()
    print("  The 5th captain is the same as the 1st captain.")
    print("  The 4th boat is the same as the 1st boat.")
    print("  The cowboy rides the Concept. The chart grows.")
    print("  The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
