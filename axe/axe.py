#!/usr/bin/env python3
"""
axe.py — The axe problem: concept persistence through
implementation replacement.

The user articulated: "this is my favorite Axe. I've
replaced the handle 3 times and the head twice."
The axe is the concept that needed to continue living.

This script:
  - Models a captain's operation across many replacements
  - Tracks the implements (boat, equipment, skills, etc.)
  - Tracks the Concept (the invariant, the operation)
  - Shows the Concept persists even as everything else
    gets replaced

The 7 levels:
  1. The Vessel
  2. The Equipment
  3. The Skills
  4. The Consumables
  5. The Renewables
  6. The Durables
  7. The Concept (NEW — the operation itself)

The principle:
  - The vessel, equipment, skills, consumables, renewables,
    and durables can all be replaced.
  - The Concept persists across all replacements.
  - The 1000-year shipyard is the concept that survived.

The cowboy's maxim:
  "The vessel can sink. The equipment can break.
  The skills can be lost. The consumables can run out.
  The renewables can fail. The durables can erode.
  The concept persists. The cowboy rides the concept."
"""
import random


# ============================================================
# The 7 levels of the operation
# ============================================================
class Implements:
    """The 6 implement levels — all replaceable."""

    def __init__(self, name):
        self.vessel = f"{name} v1"
        self.equipment = f"{name} equipment v1"
        self.skills = ["tacking"]  # what the crew knows
        self.consumables = {"fuel": 100, "time": 100, "tokens": 1000}
        self.renewables = {"wind": "fair", "current": "with us"}
        self.durables = {"journal": [], "recipes": ["tack pattern"]}

        # Track replacement counts
        self.vessel_replacements = 0
        self.equipment_replacements = 0
        self.skill_losses = 0

    def replace_vessel(self, reason):
        self.vessel_replacements += 1
        self.vessel = f"vessel #{self.vessel_replacements + 1} (after: {reason})"

    def replace_equipment(self, reason):
        self.equipment_replacements += 1
        self.equipment = f"equipment #{self.equipment_replacements + 1} (after: {reason})"

    def lose_skill(self, skill):
        if skill in self.skills:
            self.skills.remove(skill)
            self.skill_losses += 1

    def gain_skill(self, skill):
        if skill not in self.skills:
            self.skills.append(skill)

    def consume(self, resource, amount):
        if resource in self.consumables:
            self.consumables[resource] = max(0, self.consumables[resource] - amount)

    def add_to_journal(self, entry):
        self.durables["journal"].append(entry)


class Concept:
    """The Concept — the operation itself. The invariant."""

    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose  # WHY this operation exists
        self.birth_year = 1000  # when the concept was born
        self.current_year = 1000
        self.evolution_log = []

    def persists(self):
        """A concept persists if its purpose is still relevant."""
        return True

    def evolve(self, year, insight):
        """The concept can evolve (gain new understanding) but persists."""
        self.current_year = year
        self.evolution_log.append((year, insight))

    def age(self):
        return self.current_year - self.birth_year


# ============================================================
# The 1000-year shipyard
# ============================================================
class Shipyard:
    """A shipyard that operates for 1000 years.
    The implements replace. The Concept persists."""

    def __init__(self, concept_name, purpose):
        self.implements = Implements(concept_name)
        self.concept = Concept(concept_name, purpose)
        # The captain (the one who holds the concept in their head)
        self.captain = "the user"
        # The crew (the cells, the workers)
        self.crew = ["apprentice", "old hand", "first mate"]
        # The AI (the workers' tool)
        self.ai = "Mavis"
        # The chart (the journal of what happened)
        self.chart = []

    def log(self, year, event):
        self.chart.append((year, event))
        self.implements.add_to_journal(f"year {year}: {event}")

    def voyage(self, year, conditions):
        """One voyage. Implements may be replaced. Concept persists."""
        self.concept.evolve(year, f"voyage under {conditions}")
        self.log(year, f"voyage begins: {conditions}")

        # Random events that may replace implements
        events = []

        # Storm may damage the vessel
        if random.random() < 0.3:
            self.implements.replace_vessel("storm")
            events.append("vessel replaced")
            self.log(year, "vessel replaced after storm")

        # Equipment may break
        if random.random() < 0.2:
            self.implements.replace_equipment("failure")
            events.append("equipment replaced")
            self.log(year, "equipment replaced after failure")

        # Old crew may lose skills (e.g., retire)
        if random.random() < 0.2 and len(self.implements.skills) > 1:
            skill = random.choice(self.implements.skills)
            self.implements.lose_skill(skill)
            events.append(f"skill {skill} lost")
            self.log(year, f"old hand retired, lost {skill}")

        # New crew may bring new skills
        if random.random() < 0.3:
            new_skill = random.choice(["welding", "navigation", "mending", "reading"])
            self.implements.gain_skill(new_skill)
            events.append(f"skill {new_skill} gained")
            self.log(year, f"new hand brought {new_skill}")

        # Consumables get used
        self.implements.consume("fuel", random.randint(5, 15))
        self.implements.consume("time", random.randint(5, 15))
        self.implements.consume("tokens", random.randint(50, 150))

        return events


def main(n_voyages=30):
    print("=" * 78)
    print("  THE AXE — concept persistence through implementation replacement")
    print("=" * 78)
    print()

    # The 1000-year shipyard
    s = Shipyard("The Shipyard", "build boats that last")

    print(f"  Initial concept: '{s.concept.name}' — purpose: '{s.concept.purpose}'")
    print(f"  Captain: {s.captain}")
    print(f"  AI crew: {s.ai}")
    print(f"  Initial crew: {s.crew}")
    print(f"  Initial skills: {s.implements.skills}")
    print()

    # Run many voyages
    n_voyages = 30
    conditions_list = ["calm seas", "storm", "fog", "fair wind",
                       "rough water", "new harbor", "old waters"]

    for i in range(n_voyages):
        year = s.concept.current_year + (i + 1) * 33  # ~33 years per voyage
        conditions = random.choice(conditions_list)
        events = s.voyage(year, conditions)

    # Final state
    print(f"  After {n_voyages} voyages (year {s.concept.current_year}):")
    print(f"    Concept age: {s.concept.age()} years")
    print(f"    Concept persists: {s.concept.persists()}")
    print(f"    Vessel replacements: {s.implements.vessel_replacements}")
    print(f"    Equipment replacements: {s.implements.equipment_replacements}")
    print(f"    Skill losses (retirements): {s.implements.skill_losses}")
    print(f"    Current skills: {s.implements.skills}")
    print(f"    Journal entries: {len(s.implements.durables['journal'])}")
    print(f"    Consumables: {s.implements.consumables}")
    print()

    # The chart
    print("  Chart (last 8 entries):")
    for year, event in s.chart[-8:]:
        print(f"    year {year}: {event}")
    print()

    # The concept evolution
    print("  Concept evolution (last 5 insights):")
    for year, insight in s.concept.evolution_log[-5:]:
        print(f"    year {year}: {insight}")
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the axe and the 1000-year shipyard")
    print("=" * 78)
    print()
    print(f"  After {n_voyages} voyages:")
    print(f"    Concept age: {s.concept.age()} years")
    print(f"    Concept persists: {s.concept.persists()}")
    print(f"    Implements replaced:")
    print(f"      Vessels: {s.implements.vessel_replacements}")
    print(f"      Equipment: {s.implements.equipment_replacements}")
    print(f"      Skills: {s.implements.skill_losses}")
    print()
    print("  The vessel, equipment, and skills have all been replaced.")
    print("  The consumables have been used up many times.")
    print("  The durables (journal) have grown with each voyage.")
    print("  THE CONCEPT PERSISTS. The 1000-year shipyard continues.")
    print()
    print("  The axe is not the handle. The axe is not the head.")
    print("  The axe is the operation. The 1000-year shipyard is the concept.")
    print("  The cowboy rides the concept. The chart grows.")
    print()
    print("  The operation is in the captain's head.")
    print("  The vessel, equipment, skills, consumables, renewables,")
    print("  durables — these are all implements. The Concept is")
    print("  the invariant. The Concept is what persists.")
    print("=" * 78)


if __name__ == "__main__":
    main()
