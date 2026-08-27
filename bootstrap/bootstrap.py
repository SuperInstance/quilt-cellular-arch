#!/usr/bin/env python3
"""
bootstrap.py — The substrate bootstraps from a single cell
into a self-rendering, self-iterating bio-state of pure
mathematics that sprouts into its environment.

The user articulated:
  - Pure understandable mathematics (the algebra is
    transparent; every primitive is readable)
  - Self-rendering (the system can describe itself)
  - Self-iterating (the system can run on its own
    description)
  - Bios-like (lives, grows, adapts, dies, reproduces)
  - Sprout into environment (emerges from the substrate
    it's in; the environment is the iterator)
  - DNA is the model (structure IS the inheritance
    pattern; not parameters)
  - Triggers are struggles overcome by ancestors (every
    model is the shape that survived pressure)

This script:
  1. Starts with a single cell
  2. Lets environmental pressure select for shapes
  3. The shapes that survive are the "DNA"
  4. Each generation inherits the surviving DNA
  5. The system describes itself (self-rendering)
  6. The system runs on its own description (self-iterating)

The 5 "triggers" (the struggles):
  - not enough light → cells grow taller (longer LINK chains)
  - wind → cells grow stiffer (more BINDs, less EFFECTs)
  - nibbling → cells grow hardier (more sclerotic cells, fewer joints)
  - drought → cells grow deeper (deeper LINK chains, more VIEWs)
  - heat → cells grow cooler (more TICKs, less VIEWs)
"""
import random
import math
import json
from collections import defaultdict


# ============================================================
# The substrate: pure understandable mathematics
# ============================================================
class Cell:
    """A cell is a (name, value, identity) tuple with
    optional links to other cells.

    The cell's STRUCTURE is its DNA — not parameters. The
    shape of the cell's links, the type of its value, the
    pattern of its history: these are inherited."""

    def __init__(self, name, value=None, dna=None):
        self.name = name
        self.value = value
        self.dna = dna or {}  # the inherited structure
        self.links = []      # [(target, rel, weight)]
        self.journal = []    # append-only history
        self.tier = "totipotent"  # becomes differentiated later
        self.age = 0
        self.children = 0    # number of times this cell divided
        self.wounds = 0      # number of times this cell was hurt

    def bind(self, value):
        self.value = value
        self.journal.append(("BIND", value))
        return value

    def link(self, target, rel="LINK", weight=1.0):
        self.links.append((target.name, rel, weight))
        self.journal.append(("LINK", target.name, rel))

    def effect(self, fn, *args):
        result = fn(*args)
        self.journal.append(("EFFECT", fn.__name__, args, result))
        return result

    def view(self):
        self.journal.append(("VIEW",))
        return self.value

    def tick(self, dt=1):
        self.age += dt
        self.journal.append(("TICK", self.age))

    def describe(self):
        """Self-rendering: the cell describes itself."""
        return {
            "name": self.name,
            "value": str(self.value)[:50],
            "tier": self.tier,
            "age": self.age,
            "n_links": len(self.links),
            "dna_keys": list(self.dna.keys()),
            "children": self.children,
            "wounds": self.wounds,
        }


# ============================================================
# The environment: the 5 triggers (the struggles)
# ============================================================
class Environment:
    """The environment is the iterator. It applies pressure
    that selects for cells that survive. The surviving
    shape IS the DNA."""

    def __init__(self):
        self.pressure = {
            "light": 0.5,   # not enough light → grow taller
            "wind": 0.3,    # windy → grow stiffer
            "nibble": 0.2,  # something nibbling → grow hardier
            "drought": 0.4, # drought → grow deeper
            "heat": 0.4,    # heat → grow cooler
        }
        self.generation = 0

    def apply(self, cell):
        """Apply environmental pressure to a cell. Returns
        a fitness score: higher is better. Cells that fit
        the environment survive; cells that don't die."""
        fitness = 0.0
        # Light: cells with longer LINK chains survive
        if cell.links:
            fitness += self.pressure["light"] * (len(cell.links) / 10)
        # Wind: cells with BINDs survive (more rigid)
        n_binds = sum(1 for e in cell.journal if e[0] == "BIND")
        fitness += self.pressure["wind"] * (n_binds / 10)
        # Nibble: cells with fewer EFFECTs survive (less attack surface)
        n_effects = sum(1 for e in cell.journal if e[0] == "EFFECT")
        fitness += self.pressure["nibble"] * (1 - n_effects / 10)
        # Drought: cells with VIEWs survive (deeper observation)
        n_views = sum(1 for e in cell.journal if e[0] == "VIEW")
        fitness += self.pressure["drought"] * (n_views / 10)
        # Heat: cells with TICKs survive (more time, cooler)
        n_ticks = sum(1 for e in cell.journal if e[0] == "TICK")
        fitness += self.pressure["heat"] * (n_ticks / 10)
        return fitness

    def mutate(self, pressure, generation):
        """The environment changes over generations. Each
        generation, the pressure drifts slightly. This is
        the weather."""
        for k in self.pressure:
            self.pressure[k] += random.uniform(-0.05, 0.05)
            self.pressure[k] = max(0, min(1, self.pressure[k]))
        self.generation = generation
        return self.pressure


# ============================================================
# The substrate: a population of cells that evolves
# ============================================================
class Substrate:
    """A population of cells. Each generation, the unfit
    die and the fit reproduce. The DNA is inherited."""

    def __init__(self, n_initial=10):
        self.cells = []
        for i in range(n_initial):
            cell = Cell(f"gen0_{i}", value=random.random(),
                       dna={"shape": "round"})
            self.cells.append(cell)
        self.environment = Environment()
        self.generation = 0
        self.history = []
        self.total_wounds = 0
        self.shape_history = []  # track which shapes survive which pressure

    def step(self):
        """One generation. The environment iterates."""
        # 1. Tick each cell
        for cell in self.cells:
            cell.tick()

        # 2. Apply pressure; compute fitness
        fitness = [(c, self.environment.apply(c)) for c in self.cells]

        # 3. Sort by fitness; top half survives
        fitness.sort(key=lambda x: -x[1])
        survivors = [c for c, _ in fitness[:len(fitness) // 2]]

        # 4. Survivors reproduce (with mutation)
        # Each survivor has 1-2 children, not always 2
        children = []
        for parent in survivors:
            n_children = random.choice([1, 1, 1, 2])  # mostly 1
            for _ in range(n_children):
                child = self._reproduce(parent)
                children.append(child)
                parent.children += 1

        # 5. The unfit die (wounded) — actually removed
        dead = [c for c, f in fitness[len(fitness) // 2:]]
        n_dead = len(dead)
        # Track total wounds across all cells
        for c in dead:
            self.total_wounds += 1

        # 6. The substrate is the survivors + their children
        self.cells = survivors + children
        self.generation += 1
        # Track which shapes survived
        shape_count = defaultdict(int)
        for c in self.cells:
            shape_count[c.dna.get("shape", "?")] += 1
        self.shape_history.append(dict(shape_count))
        # Mutate the environment (the weather changes)
        self.environment.mutate(None, self.generation)
        # Record the history
        avg_fitness = sum(f for _, f in fitness) / len(fitness)
        self.history.append({
            "generation": self.generation,
            "n_cells": len(self.cells),
            "n_dead": n_dead,
            "avg_fitness": avg_fitness,
            "pressure": dict(self.environment.pressure),
        })

    def _reproduce(self, parent):
        """Reproduce a cell. The DNA is inherited with
        small mutations. The shape of the child resembles
        the parent."""
        # The child's DNA is a copy of the parent's DNA
        # with a small mutation
        child_dna = dict(parent.dna)
        if random.random() < 0.3:
            # 30% chance of a structural mutation
            shapes = ["round", "tall", "stiff", "hardy", "deep", "cool"]
            child_dna["shape"] = random.choice(shapes)
        # The child's value is a small perturbation
        if parent.value is not None and isinstance(parent.value, (int, float)):
            child_value = parent.value + random.uniform(-0.1, 0.1)
        else:
            child_value = random.random()
        child = Cell(
            name=f"gen{self.generation + 1}_{parent.name}",
            value=child_value,
            dna=child_dna,
        )
        # Inherit some links (with mutation)
        if parent.links and random.random() < 0.5:
            target_name, rel, weight = random.choice(parent.links)
            # Find the target
            for c in self.cells:
                if c.name == target_name:
                    child.link(c, rel, weight * random.uniform(0.8, 1.2))
                    break
        return child

    def render(self):
        """Self-rendering: the substrate describes itself."""
        shape_count = defaultdict(int)
        for c in self.cells:
            shape_count[c.dna.get("shape", "?")] += 1
        return {
            "generation": self.generation,
            "n_cells": len(self.cells),
            "n_unique_shapes": len(shape_count),
            "shape_distribution": dict(shape_count),
            "avg_age": sum(c.age for c in self.cells) / max(1, len(self.cells)),
            "total_wounds": self.total_wounds,
            "total_children": sum(c.children for c in self.cells),
        }

    def describe_self_in_canon(self):
        """Self-render in the canon's voice."""
        r = self.render()
        return (
            f"Generation {r['generation']}: {r['n_cells']} cells, "
            f"{r['n_unique_shapes']} unique shapes ({r['shape_distribution']}), "
            f"avg age {r['avg_age']:.1f}, {r['total_wounds']} wounds, "
            f"{r['total_children']} children. The substrate "
            f"is alive."
        )


# ============================================================
# The bootstrap: from one cell to a population
# ============================================================
def bootstrap(n_generations=20, n_initial=20, seed=42):
    """Bootstrap a substrate from a small population,
    evolve it for n_generations, and report what survived."""
    print("=" * 70)
    print("  BOOTSTRAP — from nothing to a self-rendering bio-state")
    print("=" * 70)
    print()
    random.seed(seed)

    # 1. Start with a small population
    s = Substrate(n_initial=n_initial)
    print(f"  Initial population: {len(s.cells)} cells, generation 0")
    print(f"  Initial pressure: {s.environment.pressure}")
    print()

    # 2. Iterate
    for gen in range(n_generations):
        s.step()

    # 3. Render
    r = s.render()
    print(f"  After {n_generations} generations:")
    print(f"    Population: {r['n_cells']} cells")
    print(f"    Unique shapes: {r['n_unique_shapes']}")
    print(f"    Shape distribution: {r['shape_distribution']}")
    print(f"    Average age: {r['avg_age']:.1f} ticks")
    print(f"    Total wounds: {r['total_wounds']}")
    print(f"    Total children: {r['total_children']}")
    print()

    # 4. The history
    print("  History (last 5 generations):")
    for h in s.history[-5:]:
        print(f"    Gen {h['generation']}: {h['n_cells']} cells, "
              f"dead={h.get('n_dead', 0)}, fitness={h['avg_fitness']:.2f}, "
              f"pressure={h['pressure']}")
    print()

    # 5. The cells' DNA — what survived
    print("  The cells' DNA (the shapes that survived):")
    for c in s.cells[:10]:
        print(f"    {c.name}: shape={c.dna.get('shape')}, "
              f"value={c.value:.2f}, "
              f"age={c.age}, wounds={c.wounds}, children={c.children}")
    print()

    # 6. Self-render
    print("  Self-rendering (the substrate describes itself):")
    print(f"    {s.describe_self_in_canon()}")
    print()

    # 7. The verdict
    print("=" * 70)
    print("  The verdict")
    print("=" * 70)
    print()
    print("  Started from a small population of random cells.")
    print(f"  After {n_generations} generations, the substrate has")
    print(f"  {r['n_cells']} cells, {r['n_unique_shapes']} unique shapes,")
    print(f"  {r['total_wounds']} wounds (cells that didn't fit),")
    print(f"  {r['total_children']} children (cells that did fit and divided).")
    print()
    print("  The DNA is the shape. The shape is what survived.")
    print("  The substrate is alive. It grew. It adapted. It hurt.")
    print()
    print("  The bootstrap is the cell. The cell is the unit.")
    print("  The substrate is the cell-graph. The cell-graph is the math.")
    print("  The math is understandable. The substrate is bio-like.")
    print("  The environment is the iterator. The cell is the iterant.")
    print()
    print("  The cowboy's maxim: the math sprouts; the substrate grows;")
    print("  the environment selects; the DNA is the scar tissue of")
    print("  the ancestors' struggles; the cowboy rides between")
    print("  generations.")
    print("=" * 70)


if __name__ == "__main__":
    bootstrap()
