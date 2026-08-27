#!/usr/bin/env python3
"""
quilt_compete.py — Multiple substrates compete within a
shared Quilt, exchanging DNA, sharing resources, evolving
together. The competition IS the iterator.

The user articulated: "make these compete with each other
within quilt systems to iteratively grow themselves."

This script models:
  - Many substrates living in a shared Quilt
  - Each substrate is a population of cells
  - The Quilt has shared resources (nutrients, light,
    space)
  - Substrates compete for resources
  - Substrates exchange DNA when they meet (cross-pollination)
  - Substrates can be parasitic or symbiotic
  - Substrates evolve to fill niches
  - The Quilt is the ecology; the substrates are the species

The math:
  - Each substrate has a fitness = (own cells × resources)
    - (competitor cells × competition coefficient)
  - Each generation:
    1. Substrates compete for resources
    2. Cells that don't get enough die
    3. Cells that thrive divide
    4. Substrates meet at the seams (LINKs) and exchange DNA
    5. New substrates can form (speciation)
  - The Quilt is the iterator

The principle:
  - The Quilt is not a single substrate. The Quilt is a
    quilt OF substrates.
  - The competition is not adversarial. The competition is
    ecological.
  - The substrates are not isolated. The substrates share
    resources and exchange DNA.
  - The Quilt grows because the substrates grow.

The cowboy's maxim:
  "The Quilt is the ecology. The substrates are the species.
  The competition is the iterator. The cross-pollination is
  the inheritance. The niche is the address. The cowboy
  rides between species."
"""
import random
import math
from collections import defaultdict


# ============================================================
# The cell: pure understandable mathematics
# ============================================================
class Cell:
    """A cell is a (name, value, dna) tuple with links."""

    def __init__(self, name, value=None, dna=None, substrate_id=None):
        self.name = name
        self.value = value or random.random()
        self.dna = dict(dna or {"shape": "round"})
        self.substrate_id = substrate_id
        self.links = []
        self.journal = []
        self.tier = "totipotent"
        self.age = 0
        self.children = 0
        self.wounds = 0

    def bind(self, value):
        self.value = value
        self.journal.append(("BIND", value))

    def link(self, target, rel="LINK"):
        self.links.append((target.name, rel, target.substrate_id))

    def tick(self, dt=1):
        self.age += dt
        self.journal.append(("TICK", self.age))

    def describe(self):
        return {
            "name": self.name,
            "value": round(self.value, 3),
            "shape": self.dna.get("shape"),
            "substrate": self.substrate_id,
            "age": self.age,
            "n_links": len(self.links),
        }


# ============================================================
# The substrate: a population of cells
# ============================================================
class Substrate:
    """A substrate is a population of cells. Each substrate
    has its own DNA pool (the union of all its cells' DNA)."""

    def __init__(self, sid, n_cells=10, niche=None):
        self.id = sid
        self.niche = niche or "generalist"
        self.cells = []
        for i in range(n_cells):
            cell = Cell(
                name=f"{sid}_{i}",
                value=random.random(),
                dna={"shape": "round", "niche": self.niche},
                substrate_id=sid,
            )
            self.cells.append(cell)
        self.history = []
        self.total_wounds = 0
        self.total_children = 0
        self.alive = True

    def __len__(self):
        return len(self.cells)

    def dna_pool(self):
        """All unique shapes in this substrate."""
        return list(set(c.dna.get("shape", "?") for c in self.cells))

    def share(self, other):
        """Cross-pollination: exchange DNA with another substrate.
        Returns a new substrate (the offspring of the cross)."""
        if not self.cells or not other.cells:
            return None
        # Pick a parent from each
        a = random.choice(self.cells)
        b = random.choice(other.cells)
        # Mix the DNA
        mixed = dict(a.dna)
        for k, v in b.dna.items():
            if k not in mixed or random.random() < 0.5:
                mixed[k] = v
        # Make a new substrate
        new_id = f"{a.substrate_id}+{b.substrate_id}"
        new_niche = a.dna.get("niche") or b.dna.get("niche") or "hybrid"
        new_sub = Substrate(new_id, n_cells=1, niche=new_niche)
        new_sub.cells[0].dna = mixed
        return new_sub

    def mutate(self, pressure):
        """Mutate each cell's value with environmental pressure."""
        for c in self.cells:
            if "light" in pressure and random.random() < pressure["light"]:
                c.dna["shape"] = "tall"
            if "wind" in pressure and random.random() < pressure["wind"]:
                c.dna["shape"] = "stiff"
            if "nibble" in pressure and random.random() < pressure["nibble"]:
                c.dna["shape"] = "hardy"
            if "drought" in pressure and random.random() < pressure["drought"]:
                c.dna["shape"] = "deep"
            if "heat" in pressure and random.random() < pressure["heat"]:
                c.dna["shape"] = "cool"
            c.value += random.uniform(-0.05, 0.05)
            c.tick()

    def compete(self, available_resources):
        """Each cell competes for a share of available resources.
        Returns cells that survived and cells that died."""
        if not self.cells:
            return [], []
        # Each cell needs a small amount; if total demand is met,
        # everyone survives
        total_demand = sum(c.value for c in self.cells) * 0.5
        if total_demand <= available_resources:
            # Plenty of resources; everyone survives
            return list(self.cells), []
        # Otherwise, sort by value; top half survives
        sorted_cells = sorted(self.cells, key=lambda c: -c.value)
        n_survive = max(1, int(len(sorted_cells) * (available_resources / total_demand)))
        survivors = sorted_cells[:n_survive]
        dead = sorted_cells[n_survive:]
        for c in dead:
            c.wounds += 1
            self.total_wounds += 1
        return survivors, dead

    def reproduce(self, survivors):
        """Each survivor has 1-2 children with mutated DNA."""
        children = []
        for parent in survivors:
            n = random.choice([1, 1, 1, 2])
            for _ in range(n):
                child_dna = dict(parent.dna)
                if random.random() < 0.3:
                    shapes = ["round", "tall", "stiff", "hardy", "deep", "cool"]
                    child_dna["shape"] = random.choice(shapes)
                child = Cell(
                    name=f"{parent.name}_c{parent.children}",
                    value=parent.value + random.uniform(-0.1, 0.1),
                    dna=child_dna,
                    substrate_id=self.id,
                )
                children.append(child)
                parent.children += 1
                self.total_children += 1
        return children

    def die(self):
        """The substrate goes extinct."""
        self.alive = False


# ============================================================
# The Quilt: the shared ecology
# ============================================================
class Quilt:
    """A Quilt is a shared environment where many substrates
    compete, exchange DNA, and evolve together."""

    def __init__(self, total_resources=100.0, n_initial_substrates=5):
        self.total_resources = total_resources
        self.resources = total_resources
        self.substrates = {}
        self.sid_counter = 0
        # Initial substrates: each occupies a different niche
        niches = ["phototroph", "aerotroph", "saprotroph", "parasite", "symbiont"]
        for i in range(n_initial_substrates):
            niche = niches[i % len(niches)]
            self._spawn(niche=niche)
        self.generation = 0
        self.pressure = {
            "light": 0.5, "wind": 0.3, "nibble": 0.2,
            "drought": 0.4, "heat": 0.4,
        }
        self.history = []
        self.extinctions = 0
        self.speciations = 0

    def _spawn(self, n_cells=10, niche=None, parent_ids=None):
        """Spawn a new substrate."""
        self.sid_counter += 1
        sid = f"S{self.sid_counter:03d}"
        if parent_ids:
            sid = f"{parent_ids[0]}x{parent_ids[1]}"
        sub = Substrate(sid, n_cells=n_cells, niche=niche or "generalist")
        self.substrates[sid] = sub
        return sub

    def step(self):
        """One generation in the Quilt."""
        self.generation += 1

        # 1. The environment shifts (the weather)
        for k in self.pressure:
            self.pressure[k] += random.uniform(-0.05, 0.05)
            self.pressure[k] = max(0, min(1, self.pressure[k]))

        # 2. Each substrate mutates and competes
        survivors_by_sub = {}
        for sid, sub in list(self.substrates.items()):
            if not sub.alive:
                continue
            sub.mutate(self.pressure)
            # Substrates in favorable niches get more resources
            niche_bonus = {
                "phototroph": self.pressure["light"] * 0.4,
                "aerotroph": self.pressure["wind"] * 0.4,
                "saprotroph": (self.pressure["nibble"] + self.pressure["drought"]) * 0.3,
                "parasite": 0.15,  # parasites always have something to feed on
                "symbiont": 0.25,  # symbionts share with hosts
            }.get(sub.niche, 0.1)
            # Carrying capacity penalty: large substrates are penalized
            # (intraspecific competition)
            size_penalty = max(0.5, 1.0 - len(sub) * 0.02)
            available = max(0.5, self.resources * (niche_bonus + 0.05) * size_penalty)
            survivors, dead = sub.compete(available)
            survivors_by_sub[sid] = survivors
            # Substrate dies if too few cells survive
            if len(survivors) < 1:
                sub.die()
                self.extinctions += 1

        # 3. Substrates reproduce
        new_cells_by_sub = {}
        for sid, sub in list(self.substrates.items()):
            if not sub.alive or sid not in survivors_by_sub:
                continue
            children = sub.reproduce(survivors_by_sub[sid])
            new_cells_by_sub[sid] = survivors_by_sub[sid] + children
            sub.cells = new_cells_by_sub[sid]

        # 4. Substrates meet at the seams (cross-pollination)
        # Cap the total number of substrates to prevent explosion
        if len([s for s in self.substrates.values() if s.alive]) >= 20:
            return
        alive_subs = [s for s in self.substrates.values() if s.alive and len(s) > 0]
        if len(alive_subs) >= 2:
            # Pick pairs to exchange DNA (small, bounded rate)
            n_crosses = min(2, len(alive_subs) // 2)
            for _ in range(n_crosses):
                a, b = random.sample(alive_subs, 2)
                # Cross with moderate probability
                if self._compatible(a, b) or random.random() < 0.2:
                    new_sub = a.share(b)
                    if new_sub:
                        new_sub.id = f"X{self.sid_counter:03d}"
                        self.sid_counter += 1
                        new_sub.niche = "hybrid"
                        # Give the new substrate a small head start
                        for c in new_sub.cells:
                            c.value += 0.2
                        self.substrates[new_sub.id] = new_sub
                        self.speciations += 1
                        # Stop if we're at the cap
                        if len([s for s in self.substrates.values() if s.alive]) >= 20:
                            return

        # 5. Resources regenerate (the environment's bounty)
        # More substrates = more total demand, but the Quilt also produces
        self.resources = min(self.total_resources * 1.5,
                            self.resources * 1.05 + 10)

        # 6. Record history
        self._record()

    def _compatible(self, a, b):
        """Two substrates are compatible if they can exchange DNA."""
        # Symbiont pairs with anything
        if a.niche == "symbiont" or b.niche == "symbiont":
            return True
        # Parasite pairs with anything (to feed on)
        if a.niche == "parasite" or b.niche == "parasite":
            return random.random() < 0.3
        # Otherwise, similar niches can cross
        return a.niche == b.niche or random.random() < 0.1

    def _record(self):
        n_alive = sum(1 for s in self.substrates.values() if s.alive)
        total_cells = sum(len(s) for s in self.substrates.values() if s.alive)
        niches = defaultdict(int)
        for s in self.substrates.values():
            if s.alive:
                niches[s.niche] += 1
        shapes = defaultdict(int)
        for s in self.substrates.values():
            if s.alive:
                for c in s.cells:
                    shapes[c.dna.get("shape", "?")] += 1
        self.history.append({
            "generation": self.generation,
            "n_substrates": n_alive,
            "n_cells": total_cells,
            "niches": dict(niches),
            "shapes": dict(shapes),
            "extinctions": self.extinctions,
            "speciations": self.speciations,
        })

    def render(self):
        n_alive = sum(1 for s in self.substrates.values() if s.alive)
        total_cells = sum(len(s) for s in self.substrates.values() if s.alive)
        niches = defaultdict(int)
        shapes = defaultdict(int)
        for s in self.substrates.values():
            if s.alive:
                niches[s.niche] += 1
                for c in s.cells:
                    shapes[c.dna.get("shape", "?")] += 1
        return {
            "generation": self.generation,
            "n_substrates": n_alive,
            "n_cells": total_cells,
            "niches": dict(niches),
            "shapes": dict(shapes),
            "extinctions": self.extinctions,
            "speciations": self.speciations,
        }


# ============================================================
# The main competition
# ============================================================
def main(n_generations=30):
    print("=" * 70)
    print("  THE QUILT — many substrates compete and grow together")
    print("=" * 70)
    print()

    q = Quilt(total_resources=100, n_initial_substrates=5)

    print(f"  Initial: {len(q.substrates)} substrates, "
          f"{sum(len(s) for s in q.substrates.values())} cells")
    for sid, s in q.substrates.items():
        print(f"    {sid} ({s.niche}): {len(s)} cells, "
              f"shapes={s.dna_pool()}")
    print()

    for gen in range(n_generations):
        q.step()

    # Final state
    r = q.render()
    print(f"  After {n_generations} generations:")
    print(f"    Substrates: {r['n_substrates']} "
          f"({r['extinctions']} extinct, {r['speciations']} speciated)")
    print(f"    Total cells: {r['n_cells']}")
    print(f"    Niches: {r['niches']}")
    print(f"    Shapes: {r['shapes']}")
    print()

    # The history (last 8 generations)
    print("  History (last 8 generations):")
    for h in q.history[-8:]:
        print(f"    Gen {h['generation']:>3d}: "
              f"{h['n_substrates']} subs, {h['n_cells']:>4d} cells, "
              f"niches={h['niches']}, "
              f"ext={h['extinctions']}, spec={h['speciations']}")
    print()

    # The substrates (alive)
    print("  The substrates (alive):")
    for sid, s in q.substrates.items():
        if s.alive:
            print(f"    {sid} ({s.niche}): {len(s)} cells, "
                  f"shapes={s.dna_pool()}, "
                  f"wounds={s.total_wounds}, children={s.total_children}")
    print()

    # The verdict
    print("=" * 70)
    print("  The verdict")
    print("=" * 70)
    print()
    print(f"  Started with 5 substrates in 5 niches.")
    print(f"  After {n_generations} generations:")
    print(f"    {r['n_substrates']} substrates alive")
    print(f"    {r['extinctions']} extinctions")
    print(f"    {r['speciations']} speciations (cross-pollinations)")
    print(f"    {r['n_cells']} total cells across the Quilt")
    print()
    print("  The Quilt is not a single substrate. The Quilt is a")
    print("  quilt OF substrates. The substrates compete for")
    print("  resources. The substrates exchange DNA at the seams.")
    print("  The substrates speciate. The substrates go extinct.")
    print("  The Quilt grows because the substrates grow.")
    print()
    print("  The competition is the iterator.")
    print("  The cross-pollination is the inheritance.")
    print("  The niche is the address.")
    print("  The Quilt is the ecology.")
    print()
    print("  The cowboy's maxim: the Quilt is the ecology;")
    print("  the substrates are the species; the competition is")
    print("  the iterator; the cross-pollination is the")
    print("  inheritance; the cowboy rides between species.")
    print("=" * 70)


if __name__ == "__main__":
    main()
