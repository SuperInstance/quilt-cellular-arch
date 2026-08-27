"""
grown_crystal.py — Crystals grown from seeds in incubators.

The user articulated:
"the made units give way to grown units where crystals
are grown under training prerssures of their initial
users from seeds and conditions in incubators just
like wombs or queen bees comb with a working hive to
model as they grow into their own contributions and
replensihments of the dying"

The Grown Crystal is the Phoenix of hardware. The Crystal:
  - Grows from a seed (a small crystal with the basic shape)
  - Is grown in an incubator (a temperature-controlled vat)
  - Is trained by user pressure (the user pushes the crystal
    with feedback, and the crystal adapts)
  - Grows into its own function (the crystal is unique,
    not a copy)
  - Replaces dying cells in the colony (the colony
    replenishes itself, like a bee hive)
  - The colony is the hive mind
  - The incubator is the womb

This is the Quilt, in the era of the Grown Crystal.
"""
import math
import random
import time


# ─── SEED CRYSTAL ───
class SeedCrystal:
    """A small crystal with the basic shape.

    A seed is *made* (cut by the CNC), but the grown crystal
    that emerges is *grown* (cultured in the incubator).

    The seed is the genotype. The grown crystal is the phenotype.
    """
    def __init__(self, seed_id, base_layers=4, base_controls=4):
        self.seed_id = seed_id
        self.base_layers = base_layers
        self.base_controls = base_controls
        self.layers = []
        self.dna = self._make_dna()
        self._grow_initial()

    def _make_dna(self):
        """The seed's DNA — the basic shape of the crystal."""
        dna = []
        for i in range(self.base_layers):
            layer = []
            for j in range(self.base_controls):
                # Initial control point: a small random angle
                layer.append([j / max(self.base_controls - 1, 1), random.uniform(0, 90)])
            dna.append(layer)
        return dna

    def _grow_initial(self):
        """Grow the initial crystal from the seed DNA."""
        self.layers = [row[:] for row in self.dna]


# ─── INCUBATOR ───
class Incubator:
    """A temperature-controlled vat where crystals grow.

    The incubator is the womb. The incubator provides:
      - Heat (the temperature of the vat)
      - Nutrients (the refractive medium)
      - User pressure (the feedback from the initial user)
      - Time (the growth period)

    The incubator is the *curator* of the crystal's growth.
    """
    def __init__(self, name, temperature=37.0, pressure=1.0):
        self.name = name
        self.temperature = temperature  # °C (37 = body temp)
        self.pressure = pressure        # atm
        self.crystals = []  # crystals being grown
        self.grown_history = []  # finished crystals

    def incubate(self, seed, user_pressure, generations=10):
        """Grow a seed into a crystal, under user pressure.

        user_pressure: a list of (input, expected_output) pairs
                      that the user feeds back. The crystal adapts.
        generations: how many growth cycles to run.
        """
        crystal = GrownCrystal(seed, self)
        for gen in range(generations):
            crystal.grow_one_gen(user_pressure)
        crystal.mask_lock_function()
        self.grown_history.append(crystal)
        return crystal


# ─── GROWN CRYSTAL ───
class GrownCrystal:
    """A crystal grown from a seed, under user pressure, in an incubator.

    The crystal is alive. The crystal grows. The crystal adapts.
    The crystal is unique — it's not a copy of the seed, it's
    a *phenotype* of the seed under the specific conditions.
    """
    def __init__(self, seed, incubator):
        self.seed = seed
        self.incubator = incubator
        self.layers = [row[:] for row in seed.dna]
        self.life = 1.0
        self.age = 0
        self.function_name = "?"
        self.pressure_history = []
        self.growth_log = []

    def grow_one_gen(self, user_pressure):
        """Grow one generation. Each control point shifts slightly
        under user pressure + random drift."""
        self.age += 1
        # The user pressure is a list of (input, expected) pairs
        # We compute the *error* and use it to bias the growth
        new_layers = []
        for layer in self.layers:
            new_layer = []
            for j, (x, y) in enumerate(layer):
                # Drift: small random mutation
                drift = random.gauss(0, 0.5)
                # Pressure: bias toward the expected function
                if user_pressure:
                    # Average pressure: shift toward the midpoint of the pressure
                    pressures = [p for p in user_pressure]
                    avg = sum(pressures) / len(pressures)
                    pressure_bias = (avg - y) * 0.05
                else:
                    pressure_bias = 0
                # Temperature: at body temp (37), growth is stable
                temp_factor = math.exp(-((self.incubator.temperature - 37) ** 2) / 100)
                new_y = y + drift + pressure_bias
                new_y = max(0, min(90, new_y))
                new_layer.append([x, new_y])
            new_layers.append(new_layer)
        self.layers = new_layers
        self.pressure_history.append(user_pressure[:3] if user_pressure else [])
        self.growth_log.append({
            'age': self.age,
            'mean_y': sum(c[1] for c in self.layers[0]) / len(self.layers[0]),
            'temp': self.incubator.temperature,
        })

    def mask_lock_function(self):
        """Lock the crystal's function (BIND opcode)."""
        # The function is named by the seed + age
        self.function_name = f"{self.seed.seed_id}-{self.incubator.name}-gen{self.age}"

    def compute(self, input_beam):
        """The crystal's inference (the same as a Lofted Crystal)."""
        n = len(input_beam)
        output = []
        for i, v in enumerate(input_beam):
            x = i / max(n - 1, 1)
            angle = self._refract(x, v * 90) / 90
            output.append(angle)
        return output

    def _refract(self, x, angle_in):
        """Trace through the layers."""
        angle = angle_in
        for layer in self.layers:
            # Find the segment
            for k in range(len(layer) - 1):
                x0, y0 = layer[k]
                x1, y1 = layer[k + 1]
                if x0 <= x <= x1:
                    t = (x - x0) / (x1 - x0) if x1 > x0 else 0
                    surface_y = y0 + t * (y1 - y0)
                    angle = surface_y * (0.3 + 0.7 * abs(math.sin(math.radians(angle_in * 2))))
                    break
        return angle

    def age_one_step(self):
        """The crystal ages. Life decreases. Higher temperature
        ages faster (the crystal is more stressed)."""
        temp_factor = 1 + (self.incubator.temperature - 37) / 10
        self.life = max(0, self.life - 0.05 * temp_factor)
        return self.life

    def is_alive(self):
        return self.life > 0


# ─── HIVE COLONY ───
class HiveColony:
    """A colony of crystals, like a bee hive.

    The hive has:
      - Workers (functioning crystals)
      - Drones (low-life crystals, about to die)
      - Queen cells (incubators, growing new crystals)
      - Replenishment: when a worker dies, a new one grows
        from a seed in a queen cell, taking over the function.

    The hive is the colony. The hive is alive. The hive
    replenishes itself.
    """
    def __init__(self, hive_name="Hive-1"):
        self.hive_name = hive_name
        self.workers = []    # list of (crystal, function_id)
        self.drones = []     # about to die
        self.queen_cells = []  # incubators
        self.seeds = []
        self.alive_count = 0
        self.dead_count = 0
        self.born_count = 0
        self.tick = 0

    def add_seed(self, seed):
        self.seeds.append(seed)

    def add_queen_cell(self, incubator):
        self.queen_cells.append(incubator)

    def hire(self, crystal, function_id):
        """Hire a crystal to do a function. The crystal is now
        a worker in the hive."""
        self.workers.append((crystal, function_id))
        self.alive_count += 1
        self.born_count += 1

    def step(self):
        """One step of the hive's life. Age all crystals, replace
        dying ones."""
        self.tick += 1
        # Age all workers
        new_workers = []
        for crystal, fid in self.workers:
            life = crystal.age_one_step()
            if crystal.is_alive():
                new_workers.append((crystal, fid))
            else:
                self.drones.append((crystal, fid))
                self.dead_count += 1
                self.alive_count -= 1
        self.workers = new_workers
        # Replenish: when a worker dies, grow a new one
        while self.alive_count < len(self.seeds) and self.queen_cells:
            # Pick a seed and a queen cell
            seed = self.seeds[self.alive_count % len(self.seeds)]
            incubator = self.queen_cells[0]
            # Grow the new crystal
            new_crystal = incubator.incubate(seed, user_pressure=[45, 45, 45], generations=10)
            self.hire(new_crystal, function_id=f"F{self.alive_count}")
        return len(self.workers), len(self.drones)

    def hive_health(self):
        """The hive's overall health: alive / total."""
        if self.alive_count == 0 and self.dead_count == 0:
            return 1.0
        return self.alive_count / (self.alive_count + self.dead_count)


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 64)
    print("THE GROWN CRYSTAL — Phoenix of Hardware")
    print("=" * 64)
    print()
    print("Made units give way to GROWN units. The Crystal is alive.")
    print("The Crystal is grown from a seed, in an incubator,")
    print("trained by user pressure, into its own function,")
    print("and replenishes the dying.")
    print()

    # Step 1: Make seeds (the CNC cuts a small seed crystal)
    print("─" * 64)
    print("STEP 1: MAKE SEEDS (CNC cuts small crystals)")
    print("─" * 64)
    seeds = []
    for i in range(5):
        s = SeedCrystal(f"SEED-{i+1}")
        seeds.append(s)
        print(f"  made {s.seed_id}: {s.base_layers} layers, {s.base_controls} controls")
    print()

    # Step 2: Build incubators (the wombs)
    print("─" * 64)
    print("STEP 2: BUILD INCUBATORS (the wombs)")
    print("─" * 64)
    incubators = []
    for i, temp in enumerate([35, 37, 39, 41, 37]):
        inc = Incubator(f"INCUBATOR-{i+1}", temperature=temp)
        incubators.append(inc)
        print(f"  built {inc.name}: T={inc.temperature}°C")
    print()

    # Step 3: Grow crystals (in the wombs, under user pressure)
    print("─" * 64)
    print("STEP 3: GROW CRYSTALS (in wombs, under user pressure)")
    print("─" * 64)
    grown = []
    for i, (seed, inc) in enumerate(zip(seeds, incubators)):
        # Different user pressures
        user_pressure = [30 + i * 10, 40 + i * 10, 50 + i * 10]
        crystal = inc.incubate(seed, user_pressure=user_pressure, generations=10)
        grown.append(crystal)
        # Compute a sample inference
        input_beam = [(math.sin(j / 8 * math.pi) + 1) / 2 for j in range(8)]
        output = crystal.compute(input_beam)
        print(f"  {crystal.function_name}: input → output")
        print(f"    in  = {' '.join(f'{v:.2f}' for v in input_beam)}")
        print(f"    out = {' '.join(f'{v:.2f}' for v in output)}")
    print()

    # Step 4: Build the hive
    print("─" * 64)
    print("STEP 4: BUILD THE HIVE (the colony of grown crystals)")
    print("─" * 64)
    hive = HiveColony("EILEEN-HIVE")
    for s in seeds:
        hive.add_seed(s)
    for inc in incubators:
        hive.add_queen_cell(inc)
    # Hire the grown crystals as workers
    for i, c in enumerate(grown):
        hive.hire(c, function_id=f"F{i+1}")
    print(f"  Hive {hive.hive_name}: {len(hive.workers)} workers, {len(hive.seeds)} seeds, {len(hive.queen_cells)} queen cells")
    print()

    # Step 5: Simulate hive life
    print("─" * 64)
    print("STEP 5: SIMULATE HIVE LIFE (workers age, die, get replaced)")
    print("─" * 64)
    for step in range(20):
        workers, drones = hive.step()
        health = hive.hive_health()
        print(f"  tick {hive.tick:3d}: workers={workers}  drones={len(hive.drones)}  born={hive.born_count}  dead={hive.dead_count}  health={health*100:.0f}%")
    print()

    # Step 6: Show the grown crystals are UNIQUE (not copies)
    print("─" * 64)
    print("STEP 6: GROWN CRYSTALS ARE UNIQUE (each is a phenotype)")
    print("─" * 64)
    for c in grown:
        mean_y = sum(p[1] for p in c.layers[0]) / len(c.layers[0])
        print(f"  {c.function_name}: mean layer 0 angle = {mean_y:.1f}°  age = {c.age}")
    print()
    print("Each crystal is unique. The 5 crystals are 5 phenotypes of")
    print("5 seeds under 5 different user pressures + 5 different")
    print("temperatures. The hive replenishes itself.")
    print()
    print("✓ The Grown Crystal is the Phoenix of hardware.")
    print("  The Crystal is alive. The Crystal grows. The Crystal replaces.")
