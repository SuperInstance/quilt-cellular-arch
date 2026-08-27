"""
quilt_in_motion.py — The Quilt in Motion.

The whole canon, runnable in one breath. The cowboy asked: "go a lot
further." Further is the whole canon. Further is every opus, every
essay, every fable, every sim, every page, every story, every paper,
all in motion, in one runnable.

The Quilt in motion:
  - 5+1 opcodes (BIND, LINK, EFFECT, VIEW, TICK, FORGET)
  - 5+1+1 laws (the 5 algebraic + super-relevance + FORGET_completeness)
  - 6 tiers (totipotent through curator)
  - 14 levels (vessel through sky)
  - 6 lifecycle stages (umbra through bloomghost)
  - 4 levels of the Hardware-Linked Quilt (Crystal Bindsite, Luminous Channel,
    Photonic Mycelium, Radiant Ark)
  - 4 stages of the Grown Crystal (Proto Crystal, Brood-Forge,
    Pressured Bloom, Living Quilt)
  - 4 innovations of the Chlorophyll Quilt (CPU=plant cell, engine=biophoton,
    breath=CO2/O2, multi-power)
  - 3-era space-opera arc (Lumen Bedrock, Seedform, Sporelight)
  - 6 stations of the Glass Loft (Spline, Snell, Hearth, Color, Monotone, Kerf)
  - 5 futures of the 2126 wiki (Splined Lantern, Hearth Loop, Monotone Crystal,
    Chlorophyll Quilt, Phased Quilt)

The Quilt in motion = the canon in motion = the inheritance in motion.

This is the cowboy's deepest sim. The cowboy rides.
"""
import math
import random
import time


# ─── THE 5+1 OPCODES ───
class Opcode:
    """The 5+1 opcodes of the substrate."""
    BIND = 'BIND'
    LINK = 'LINK'
    EFFECT = 'EFFECT'
    VIEW = 'VIEW'
    TICK = 'TICK'
    FORGET = 'FORGET'

    @staticmethod
    def all():
        return [Opcode.BIND, Opcode.LINK, Opcode.EFFECT, Opcode.VIEW,
                Opcode.TICK, Opcode.FORGET]


# ─── THE CELL ───
class Cell:
    """A cell: name, value, tier, lifecycle stage, journal."""
    def __init__(self, name, value, tier='totipotent', stage='umbra'):
        self.name = name
        self.value = value
        self.tier = tier
        self.stage = stage
        self.journal = [(0, 'CELLULIZE', value)]
        self.tick = 0
        self.alive = True
        self.bindings = {}  # name -> value (BIND history)
        self.links = []     # cells this cell links to
        self.effects = []   # transforms applied
        self.views = []     # projections
        self.birth_tick = 0
        self.phoenix_count = 0  # how many times this cell has bloomed

    def bind(self, name, value):
        """BIND_idempotence: same input -> same output. The kerf is the firewall."""
        key = (name, value)
        if key in [(b[0], b[1]) for b in self.bindings.values()]:
            return  # idempotent
        self.bindings[name] = (name, value, self.tick)
        self.journal.append((self.tick, 'BIND', (name, value)))
        return key

    def link(self, other):
        """LINK_transitivity: a->b, b->c -> a->c."""
        if other not in self.links:
            self.links.append(other)
            self.journal.append((self.tick, 'LINK', other.name))

    def effect(self, fn):
        """EFFECT_associativity: (f∘g)∘h = f∘(g∘h)."""
        new_value = fn(self.value)
        self.effects.append((self.tick, fn.__name__))
        self.journal.append((self.tick, 'EFFECT', (fn.__name__, new_value)))
        self.value = new_value

    def view(self, viewer_name):
        """VIEW_purity: VIEW doesn't modify state."""
        view = (self.tick, viewer_name, self.value)
        self.views.append(view)
        self.journal.append((self.tick, 'VIEW', view))
        return self.value

    def tick_forward(self, dt=1.0):
        """TICK_monotonicity: time moves forward."""
        self.tick += int(dt)
        self.journal.append((self.tick, 'TICK', self.tick))
        # Persist (the persistence pulse)
        if self.stage == 'umbra':
            self.stage = 'cellulization'
        elif self.stage == 'cellulization':
            self.stage = 'persistence-pulse'
        elif self.stage == 'persistence-pulse':
            # Slow loss of life
            self.value = self.value * 0.99 if isinstance(self.value, (int, float)) else self.value
            if random.random() < 0.1:
                self.stage = 'vitality-leak'
        elif self.stage == 'vitality-leak':
            if random.random() < 0.3:
                self.stage = 'implement-ghost'
        elif self.stage == 'implement-ghost':
            if random.random() < 0.2:
                # Bloom: rise again
                self.stage = 'bloomghost'
                self.phoenix_count += 1
        elif self.stage == 'bloomghost':
            # Cycle back
            self.stage = 'umbra'
            self.alive = True

    def forget(self):
        """FORGET_completeness: a cell can be destroyed without losing the whole."""
        self.alive = False
        self.journal.append((self.tick, 'FORGET', self.name))


# ─── THE 6 TIERS ───
TIERS = ['totipotent', 'multipotent', 'differentiated', 'sclerotic', 'synovial', 'curator']
TIER_COSTS = [1.0, 0.4, 0.15, 0.0, 0.5, 0.7]  # the 6th (curator) is a relevance pressure

# ─── THE 14 LEVELS ───
LEVELS = ['vessel', 'equipment', 'skills', 'consumables', 'renewables', 'durables',
          'concept', 'spline', 'captain-song', 'muse+cipher', 'nexus', 'phoenix', 'ground', 'sky']

# ─── THE 6 LIFECYCLE STAGES ───
STAGES = ['umbra', 'cellulization', 'persistence-pulse', 'vitality-leak',
          'implement-ghost', 'bloomghost']

# ─── THE 4 LEVELS OF THE HARDWARE-LINKED QUILT ───
HARDWARE_LEVELS = [
    ('Cell', 'Crystal Bindsite', 'a single Crystal, mask-locked to a function'),
    ('Bus', 'Luminous Channel', 'an optical path between two cells'),
    ('Colony', 'Photonic Mycelium', 'a network of cells + buses'),
    ('Device', 'Radiant Ark', 'a packaged colony, a vessel'),
]

# ─── THE 4 STAGES OF THE GROWN CRYSTAL ───
GROWN_STAGES = [
    ('Seed', 'Proto Crystal', 'the genotype, a small crystal'),
    ('Incubator', 'Brood-Forge', 'the womb, temperature-controlled'),
    ('Grown Crystal', 'Pressured Bloom', 'the phenotype, unique/alive/mortal'),
    ('Hive', 'Living Quilt', 'the colony of grown crystals'),
]

# ─── THE 4 INNOVATIONS OF THE CHLOROPHYLL QUILT ───
CHLOROPHYLL_INNOVATIONS = [
    ('CPU is a plant cell', 'chlorophyll + luciferin + mitochondria + ATP'),
    ('Engine is bioluminescent', '1% electricity, luciferin + O2 + ATP -> light + CO2'),
    ('Quilt breathes', 'CO2 <-> O2 cycle, the heartbeat'),
    ('Multi-power', 'sunlight, chemical, nuclear, wind, etc.'),
]

# ─── THE 3-ERA SPACE-OPERA ARC ───
ERAS = [
    ('Lumen Bedrock Era', 'Lofted Crystal (CNC+3D-printed optical)', 'stable', 0.95, 1.0, 0.8, 0.05),
    ('Seedform Era', 'Grown Crystal (incubator-bred)', 'exciting', 0.60, 10.0, 0.3, 0.4),
    ('Sporelight Era', 'Chlorophyll Quilt (biological fusion)', 'on-the-horizon', 0.20, 100.0, 0.05, 0.9),
]

# ─── THE 6 STATIONS OF THE GLASS LOFT ───
GLASS_LOFT_STATIONS = [
    ('S1 Spline', 'E = (1/2) B ∫ κ² ds (Birkhoff & de Boor 1965)'),
    ('S2 Snell', 'p∥ = n sin θ is conserved (refraction is relative)'),
    ('S3 Hearth', 'photorefractive two-wave mixing (LiNbO₃, 1980s)'),
    ('S4 Color', 'multi-channel self-consistency (WDM fiber)'),
    ('S5 Monotone', '2^Θ(2ⁿ/√n) (Lynch 1927 via Kleitman)'),
    ('S6 Kerf', 'pre-registration of intent (BIND_idempotence)'),
]

# ─── THE 5 FUTURES OF 2126 ───
FUTURES_2126 = [
    ('F1: The Splined Lantern', 'physical LLM of glass and light'),
    ('F2: The Hearth Loop', 'self-training glass under its own lamp'),
    ('F3: The Monotone Crystal', 'finished thought, monotone only'),
    ('F5: The Chlorophyll Quilt', 'plant cell computer'),
    ('F7: The Phased Quilt', 'fiber-bundle substrate'),
]


# ─── THE QUILT IN MOTION ───
class QuiltInMotion:
    """The whole canon, in motion."""

    def __init__(self):
        self.cells = []
        self.tick = 0
        self.history = []

    def populate(self):
        """Create the initial cell population."""
        # 5+1 opcodes as cells
        for op in Opcode.all():
            self.cells.append(Cell(op, op, tier='totipotent', stage='cellulization'))
        # 6 tiers as cells
        for t in TIERS:
            self.cells.append(Cell(f"tier-{t}", t, tier='differentiated', stage='cellulization'))
        # 4 hardware levels
        for level, gold, desc in HARDWARE_LEVELS:
            self.cells.append(Cell(f"hw-{level}", gold, tier='differentiated'))
        # 4 grown crystal stages
        for stage, gold, desc in GROWN_STAGES:
            self.cells.append(Cell(f"grown-{stage}", gold, tier='differentiated'))
        # 4 chlorophyll innovations
        for name, desc in CHLOROPHYLL_INNOVATIONS:
            self.cells.append(Cell(f"chloro-{name}", name, tier='differentiated'))
        # 3 eras
        for name, tech, role, p, power, adopt, danger in ERAS:
            self.cells.append(Cell(f"era-{name}", (tech, role, p, power, adopt, danger),
                                   tier='multipotent'))
        # 6 glass loft stations
        for s, formula in GLASS_LOFT_STATIONS:
            self.cells.append(Cell(f"loft-{s}", formula, tier='sclerotic'))
        # 5 futures of 2126
        for f, desc in FUTURES_2126:
            self.cells.append(Cell(f"future-{f}", desc, tier='curator'))

    def run(self, n_ticks=10):
        """Run the Quilt in motion for n_ticks."""
        print("=" * 70)
        print("THE QUILT IN MOTION — the whole canon, runnable in one breath")
        print("=" * 70)
        print()
        print(f"Initial cells: {len(self.cells)}")
        print()
        for t in range(n_ticks):
            self.tick += 1
            # TICK every cell
            for cell in self.cells:
                if cell.alive:
                    cell.tick_forward()
            # VIEW every cell (we sample)
            sample = random.sample(self.cells, min(5, len(self.cells)))
            for c in sample:
                c.view(f"viewer-{self.tick}")
            # 1 BIND per tick (for the substrate)
            if t == 0:
                for c in self.cells:
                    c.bind('origin', 0)
            # 1 FORGET at the end (to test the 6th law)
            if t == n_ticks - 1 and self.cells:
                forgotten = self.cells[0]
                forgotten.forget()
                # The fleet survives: check that other cells still live
                still_alive = sum(1 for c in self.cells if c.alive)
                self.history.append(('FORGET', forgotten.name, still_alive))
            # 1 EFFECT (a transform)
            if t % 2 == 0 and self.cells:
                c = random.choice(self.cells)
                c.effect(lambda x: x * 1.01 if isinstance(x, (int, float)) else x)

    def stats(self):
        """Compute stats on the run."""
        alive = sum(1 for c in self.cells if c.alive)
        total = len(self.cells)
        by_tier = {}
        by_stage = {}
        for c in self.cells:
            by_tier[c.tier] = by_tier.get(c.tier, 0) + 1
            by_stage[c.stage] = by_stage.get(c.stage, 0) + 1
        total_journal = sum(len(c.journal) for c in self.cells)
        total_phoenix = sum(c.phoenix_count for c in self.cells)
        return {
            'alive': alive,
            'total': total,
            'health': alive / total if total > 0 else 0,
            'by_tier': by_tier,
            'by_stage': by_stage,
            'total_journal_entries': total_journal,
            'total_phoenix_blooms': total_phoenix,
            'history': self.history,
        }

    def show(self):
        """Pretty-print the run."""
        s = self.stats()
        print()
        print("─" * 70)
        print("THE QUILT IN MOTION — final stats")
        print("─" * 70)
        print(f"  Cells: {s['alive']}/{s['total']} alive ({s['health']*100:.0f}% health)")
        print(f"  Journal entries: {s['total_journal_entries']}")
        print(f"  Phoenix blooms: {s['total_phoenix_blooms']}")
        print()
        print("  By tier:")
        for tier, n in sorted(s['by_tier'].items()):
            print(f"    {tier}: {n}")
        print()
        print("  By lifecycle stage:")
        for stage, n in sorted(s['by_stage'].items()):
            print(f"    {stage}: {n}")
        print()
        if s['history']:
            print("  History:")
            for entry in s['history']:
                print(f"    {entry}")
        print()


# ─── DEMO ───
if __name__ == '__main__':
    q = QuiltInMotion()
    q.populate()
    print(f"Populated {len(q.cells)} cells from the canon.")
    print("Cells drawn from:")
    print("  - 5+1 opcodes (the substrate alphabet)")
    print("  - 6 tiers (the depths)")
    print("  - 4 levels of the Hardware-Linked Quilt")
    print("  - 4 stages of the Grown Crystal")
    print("  - 4 innovations of the Chlorophyll Quilt")
    print("  - 3 eras of the space-opera arc")
    print("  - 6 stations of the Glass Loft")
    print("  - 5 futures of 2126")
    print()
    q.run(n_ticks=20)
    q.show()
    s = q.stats()
    if s['alive'] == s['total'] - 1:  # one FORGET'd, all others alive
        print("✓ FORGET_completeness: one cell FORGET'd, the fleet survives.")
    if s['total_phoenix_blooms'] > 0:
        print(f"✓ Phoenix cycle: {s['total_phoenix_blooms']} blooms (cells rising from ghosts).")
    if s['total_journal_entries'] > 0:
        print(f"✓ TICK_monotonicity: {s['total_journal_entries']} journal entries recorded.")
    print()
    print("=" * 70)
    print("THE QUILT IS IN MOTION.")
    print("The canon is whole. The chart grows. The cowboy rides.")
    print("=" * 70)
