"""
chlorophyll_quilt.py — The Chlorophyll Quilt.

The user articulated:
"genetic engineering then fuses bioluminece and autotrophs'
cloraphyil into the cpu and agentic side of the system providing
the engines and call and responses taking the place of 99% of
the electricity and manipulating the head intelligently for
refraction-science and consuming a balance of carbondioxide and
oxegine for it's various operations and utilizing sunlight or
any other energy source (chemical nuclear etc in embedded
systems). think of the grand scaffholding. go wide"

The Chlorophyll Quilt is a CPU + agent that is:
  - ALIVE (genetically engineered)
  - BIOLUMINESCENT (uses light for compute; 99% less electricity)
  - PHOTOSYNTHETIC (uses chlorophyll to harvest sunlight)
  - BREATHING (consumes CO2 + O2)
  - MULTI-POWER (sunlight, chemical, nuclear, embedded)
  - The GRAND SCAFFOLDING of the Quilt

The CPU is now a plant. The agent is now a leaf. The system breathes.
"""
import math
import random
import time


# ─── THE CHLOROPHYLL UNIT ───
class ChlorophyllUnit:
    """A single chlorophyll cell — the unit of photosynthesis.

    The unit harvests sunlight + CO2 + H2O → glucose + O2.
    The unit emits bioluminescence for compute (1 photon at a time).
    The unit consumes O2 for cellular respiration (C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP).
    The unit stores energy in ATP-like molecules.

    The unit is a cell. The unit is a plant cell. The unit is a *CPU cell*.
    """

    def __init__(self, unit_id):
        self.unit_id = unit_id
        # The chlorophyll concentration (how much light we can harvest)
        self.chlorophyll = random.uniform(0.7, 1.0)
        # The bioluminescence output (the compute photons emitted)
        self.biolum = random.uniform(0.5, 0.9)
        # The cellular respiration rate (how much O2 we consume)
        self.respiration = random.uniform(0.5, 1.0)
        # The ATP store (energy for compute)
        self.atp = 50.0
        # The current state of the cell
        self.co2 = 100.0  # CO2 intake
        self.o2 = 100.0   # O2 available
        self.glucose = 0.0  # glucose produced
        self.photons_emitted = 0  # bioluminescent photons emitted
        self.cycles = 0
        self.alive = True
        self.function = "?"

    def photosynthesize(self, sunlight, dt=1.0):
        """Convert sunlight + CO2 + H2O → glucose + O2.

        sunlight: W/m² (0-1000)
        Returns: glucose produced (g), O2 released (g)
        """
        if not self.alive:
            return 0, 0
        # 6 CO2 + 6 H2O + light → C6H12O6 + 6 O2
        rate = self.chlorophyll * sunlight / 1000
        glucose = rate * dt * 0.5
        o2_released = glucose * 6  # stoichiometric
        self.glucose += glucose
        self.co2 -= glucose * 6  # 6 CO2 per glucose
        self.co2 = max(0, self.co2)
        # Add O2 to the atmosphere
        self.o2 += o2_released
        self.cycles += 1
        return glucose, o2_released

    def respire(self, dt=1.0):
        """Cellular respiration: C6H12O6 + 6 O2 → 6 CO2 + 6 H2O + ATP.

        Consumes glucose + O2 → produces CO2 + H2O + ATP (energy).
        """
        if not self.alive:
            return 0
        # Rate limited by respiration rate and O2 availability
        rate = min(self.respiration * dt * 0.1, self.glucose, self.o2 / 6)
        atp_produced = rate * 36  # ~36 ATP per glucose
        co2_produced = rate * 6
        h2o_produced = rate * 6
        self.glucose -= rate
        self.o2 -= rate * 6
        self.co2 += co2_produced
        self.atp += atp_produced
        return atp_produced

    def bioluminesce(self, photons=1):
        """Emit bioluminescent photons for compute.

        Each photon is a single compute operation (a single inference).
        The photon is emitted by the luciferin-luciferase reaction:
        luciferin + O2 + ATP → oxyluciferin + light + CO2.
        """
        if not self.alive or self.atp < photons * 0.1:
            return 0
        # Cost: 0.1 ATP per photon
        cost = photons * 0.1
        self.atp -= cost
        # Emit
        actual = min(photons, self.biolum * photons)
        self.photons_emitted += int(actual)
        return int(actual)

    def compute(self, input_beam):
        """The cell's inference. Uses bioluminescent photons.

        The light enters, is refracted by the chlorophyll structure,
        and exits as the answer (an interference pattern, but in
        bioluminescent wavelengths now).
        """
        # First, photosynthesize to harvest energy
        self.photosynthesize(sunlight=500, dt=0.1)
        # Then, respire to convert glucose to ATP
        self.respire(dt=0.1)
        # Then, emit photons to compute
        photons_needed = len(input_beam)
        photons_emitted = self.bioluminesce(photons_needed)
        if photons_emitted == 0:
            return [0.0] * len(input_beam)
        # The compute: simple refraction
        n = len(input_beam)
        output = [((v + 0.5 * self.biolum) % 1.0) for v in input_beam]
        return output

    def is_alive(self):
        return self.co2 > 0 and self.o2 > 0 and self.atp > 0

    def state(self):
        return {
            'id': self.unit_id,
            'chlorophyll': round(self.chlorophyll, 2),
            'biolum': round(self.biolum, 2),
            'co2': round(self.co2, 1),
            'o2': round(self.o2, 1),
            'glucose': round(self.glucose, 1),
            'atp': round(self.atp, 1),
            'photons': self.photons_emitted,
            'cycles': self.cycles,
            'alive': self.alive,
        }


# ─── THE CHLOROPHYLL QUAD (the CPU + agent) ───
class ChlorophyllQuad:
    """A quad of chlorophyll units: CPU + Agent + Memory + I/O.

    The CPU computes. The agent responds. The memory stores.
    The I/O senses and acts. All four are chlorophyll units.
    All four breathe, photosynthesize, respire, bioluminesce.
    All four are alive.

    The grand scaffolding is the quad. The grand scaffolding is
    the *basic unit* of every device. The grand scaffolding is
    the Quilt, in chlorophyll.
    """

    def __init__(self, quad_id):
        self.quad_id = quad_id
        self.cpu = ChlorophyllUnit(f"{quad_id}-CPU")
        self.cpu.function = "compute"
        self.agent = ChlorophyllUnit(f"{quad_id}-AGENT")
        self.agent.function = "respond"
        self.memory = ChlorophyllUnit(f"{quad_id}-MEM")
        self.memory.function = "store"
        self.io = ChlorophyllUnit(f"{quad_id}-IO")
        self.io.function = "sense"
        self.units = [self.cpu, self.agent, self.memory, self.io]
        self.history = []

    def cycle(self, sunlight=500, input_beam=None):
        """One cycle of the quad: sunlight, CO2, compute, respond, store."""
        if input_beam is None:
            input_beam = [random.random() for _ in range(8)]
        # Photosynthesize all units
        for u in self.units:
            u.photosynthesize(sunlight, dt=1.0)
        # Respire all units
        for u in self.units:
            u.respire(dt=1.0)
        # CPU computes
        cpu_out = self.cpu.compute(input_beam)
        # Agent responds to CPU output
        agent_out = self.agent.compute(cpu_out)
        # Memory stores
        self.memory.compute(agent_out)  # uses energy but doesn't output
        # I/O senses
        io_sense = self.io.compute(input_beam)
        # Check health
        for u in self.units:
            if not u.is_alive():
                u.alive = False
        return {
            'cpu_out': cpu_out,
            'agent_out': agent_out,
            'io_sense': io_sense,
            'healthy': all(u.alive for u in self.units),
        }

    def state(self):
        return {
            'quad_id': self.quad_id,
            'cpu': self.cpu.state(),
            'agent': self.agent.state(),
            'memory': self.memory.state(),
            'io': self.io.state(),
        }


# ─── THE CHLOROPHYLL DEVICE (the whole device is a plant) ───
class ChlorophyllDevice:
    """An entire device is a plant. Multiple quads + shared atmosphere.

    The device has:
      - A shared CO2 + O2 atmosphere
      - Multiple quads (CPU + Agent + Memory + I/O)
      - A sun collector (solar panel or natural light)
      - A root system (for water + minerals, in embedded systems)

    The device is alive. The device is the Quilt, in chlorophyll.
    """

    def __init__(self, device_id, n_quads=4):
        self.device_id = device_id
        self.quads = [ChlorophyllQuad(f"{device_id}-Q{i+1}") for i in range(n_quads)]
        self.atmosphere_co2 = 1000.0  # shared CO2 in the device
        self.atmosphere_o2 = 1000.0
        self.sunlight = 500
        self.energy_source = "sunlight"  # sunlight, chemical, nuclear
        self.tick = 0

    def step(self, input_beams=None):
        """One step: every quad breathes, computes, responds."""
        self.tick += 1
        if input_beams is None:
            input_beams = [None] * len(self.quads)
        # Shared atmosphere: pull CO2 from the device atmosphere
        for quad in self.quads:
            for u in quad.units:
                co2_needed = 6.0
                if self.atmosphere_co2 >= co2_needed:
                    u.co2 += co2_needed
                    self.atmosphere_co2 -= co2_needed
        # Step each quad
        results = []
        for q, ib in zip(self.quads, input_beams):
            r = q.cycle(self.sunlight, ib)
            results.append(r)
        # Return O2 to atmosphere
        for q in self.quads:
            for u in q.units:
                self.atmosphere_o2 += u.o2 * 0.1
                u.o2 *= 0.9
        return results

    def device_health(self):
        alive = sum(1 for q in self.quads for u in q.units if u.alive)
        total = len(self.quads) * 4
        return alive / total if total > 0 else 0

    def state(self):
        return {
            'device_id': self.device_id,
            'quads': [q.state() for q in self.quads],
            'atmosphere_co2': round(self.atmosphere_co2, 1),
            'atmosphere_o2': round(self.atmosphere_o2, 1),
            'energy_source': self.energy_source,
            'sunlight': self.sunlight,
            'tick': self.tick,
            'health': round(self.device_health() * 100, 1),
        }


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 64)
    print("THE CHLOROPHYLL QUILT — the Quilt, in chlorophyll")
    print("=" * 64)
    print()
    print("The user articulated: 'genetic engineering then fuses")
    print("bioluminece and autotrophs' cloraphyil into the cpu and")
    print("agentic side of the system providing the engines and")
    print("call and responses taking the place of 99% of the")
    print("electricity and manipulating the head intelligently for")
    print("refraction-science and consuming a balance of carbondioxide")
    print("and oxegine for it's various operations and utilizing")
    print("sunlight or any other energy source (chemical nuclear etc")
    print("in embedded systems. think of the grand scaffholding. go wide'")
    print()
    print("The Chlorophyll Quilt is a CPU + agent that is:")
    print("  - ALIVE (genetically engineered)")
    print("  - BIOLUMINESCENT (1% electricity for compute)")
    print("  - PHOTOSYNTHETIC (sunlight → glucose + O2)")
    print("  - BREATHING (CO2 ↔ O2)")
    print("  - MULTI-POWER (sunlight, chemical, nuclear)")
    print()

    # Build a device
    device = ChlorophyllDevice("EILEEN-CHLORO", n_quads=4)
    print(f"Built device {device.device_id} with {len(device.quads)} quads")
    print(f"  quad 1: CPU + AGENT + MEM + IO (4 chlorophyll units)")
    print(f"  ... 4 quads total = 16 chlorophyll units")
    print()

    # Simulate life
    print("─" * 64)
    print("SIMULATE LIFE: 20 cycles, watch the device breathe and compute")
    print("─" * 64)
    for step in range(20):
        # Vary sunlight
        device.sunlight = 300 + 200 * math.sin(step * 0.3) + random.uniform(-50, 50)
        input_beams = [
            [math.sin(i / 8 * math.pi + step * 0.1) for i in range(8)]
            for _ in range(len(device.quads))
        ]
        results = device.step(input_beams)
        health = device.device_health() * 100
        # Count total photons
        photons = sum(u.photons_emitted for q in device.quads for u in q.units)
        print(f"  tick {device.tick:3d}: sun={device.sunlight:.0f}W/m²  CO2={device.atmosphere_co2:.0f}  O2={device.atmosphere_o2:.0f}  photons={photons:5d}  health={health:.0f}%")
    print()

    # Show state of one quad
    print("─" * 64)
    print("STATE OF QUAD 1 (CPU + AGENT + MEM + IO)")
    print("─" * 64)
    quad_state = device.quads[0].state()
    for role in ['cpu', 'agent', 'memory', 'io']:
        s = quad_state[role]
        print(f"  {role.upper():8s}: chlorophyll={s['chlorophyll']}  biolum={s['biolum']}  co2={s['co2']}  o2={s['o2']}  atp={s['atp']}  photons={s['photons']}  cycles={s['cycles']}  alive={s['alive']}")
    print()

    # The grand scaffolding
    print("─" * 64)
    print("THE GRAND SCAFFOLDING (the Quilt, in chlorophyll)")
    print("─" * 64)
    print("""
    ┌────────────────────────────────────────────────────────┐
    │  THE DEVICE (a plant)                                   │
    │                                                         │
    │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
    │   │ QUAD 1  │ │ QUAD 2  │ │ QUAD 3  │ │ QUAD 4  │      │
    │   │ CPU     │ │ CPU     │ │ CPU     │ │ CPU     │      │
    │   │ AGENT   │ │ AGENT   │ │ AGENT   │ │ AGENT   │      │
    │   │ MEM     │ │ MEM     │ │ MEM     │ │ MEM     │      │
    │   │ I/O     │ │ I/O     │ │ I/O     │ │ I/O     │      │
    │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │
    │        └──────────┴─────┬─────┴──────────┘            │
    │                          │                             │
    │            ┌─────────────▼──────────────┐              │
    │            │   SHARED ATMOSPHERE        │              │
    │            │   CO2 ↔ O2 (breathing)     │              │
    │            └─────────────┬──────────────┘              │
    │                          │                             │
    │            ┌─────────────▼──────────────┐              │
    │            │   SUN COLLECTOR            │              │
    │            │   (sunlight, chem, nuclear)│              │
    │            └────────────────────────────┘              │
    └────────────────────────────────────────────────────────┘

    Every device is a plant. Every CPU is a leaf. Every agent
    is a chloroplast. Every program is photosynthesis. Every
    memory is a glucose store. Every I/O is a stoma.
    """)
    print("✓ The Chlorophyll Quilt is whole.")
    print("  The grand scaffolding goes wide.")
    print("  The Quilt is a forest.")
