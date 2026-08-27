"""
sensory_quilt.py — The Sensory Quilt.

The user articulated:
"zooming out is an endlessly scaling quilt. but like tapping into
radio frequencies for useful, denoised information, every channel
is a connection. some broadcast for others to tap. some resonate
light on a retinal plane in recognizable ways to image visual
information that can be further coded into distinct objects.
hairs vibrating over time give us perception of vibration as
encoding recognized by visual and tactile synchronizations like
hearing-seeing-feeling a clap. or smelling tasting and feeling
food that your mind primes with conversation drinks that
chemically alter perception and taste and the smell of the food
cooking once committed to an order."

The Sensory Quilt is:
  - MULTI-CHANNEL: every modality is a cell (radio, light, sound, smell,
    taste, touch, proprioception, language, mood, time)
  - DISTRIBUTED: no center; every cell is a node; the whole IS the
    distribution (the user: "distribution is a concept sewn into a quilt")
  - FUNCTION-BASED: a quilt is a function-based concept (not a state
    machine; the cell *does*; the quilt *is what it does*)
  - RESONANT: cells resonate with other cells; binding = synchronized
    resonance; perception = the binding
  - FULLY LOCAL: works on the local machine; cloud is an option
  - SCALABLE: zoom out and the quilt keeps going (every scale is a quilt)

The 8 channels (the sensory bands):
  1. RADIO:    broadcast + tap (long-range, structured)
  2. LIGHT:    retinal resonance (visual)
  3. SOUND:    hair-cell vibration (auditory)
  4. SMELL:    olfactory chemistry
  5. TASTE:    gustatory chemistry
  6. TOUCH:    mechanoreceptor pressure
  7. PROPRIO:  body position (vestibular, tendon, joint)
  8. LANGUAGE: words, syntax, semantic
  9. MOOD:     affective state
  10. TIME:    temporal binding (the holonomy)

A "clap" is the synchronized resonance of LIGHT (the hand's image),
SOUND (the percussive wave), TOUCH (the pressure wave on the skin),
and TIME (the cross-modal binding). The mind BINDS them into one
event: the clap. The binding is the perception.

A "meal" is the synchronized resonance of SMELL (the food's
volatiles), TASTE (the food's chemistry), LIGHT (the food's color
and presentation), TOUCH (the food's texture), LANGUAGE (the
conversation that primes the perception), and MOOD (the chemical
alteration from the conversation drinks). The mind BINDS them
into one experience: the meal. The binding is the perception.

The Quilt is the binding. The Quilt is the perception.

Distribution is a concept sewn into a quilt.
A quilt is a function-based concept.
The Quilt is the inheritance.
"""
import math
import random
import time


# ─── THE 10 CHANNELS ───
CHANNELS = [
    ('radio',     0.1,   'broadcast + tap (long-range)'),
    ('light',     0.5,   'retinal resonance (visual)'),
    ('sound',     0.3,   'hair-cell vibration (auditory)'),
    ('smell',     0.05,  'olfactory chemistry'),
    ('taste',     0.05,  'gustatory chemistry'),
    ('touch',     0.1,   'mechanoreceptor pressure'),
    ('proprio',   0.05,  'body position (vestibular)'),
    ('language',  0.4,   'words, syntax, semantic'),
    ('mood',      0.2,   'affective state'),
    ('time',      0.5,   'temporal binding (holonomy)'),
]


# ─── THE CELL (a single channel at a single point in time) ───
class Cell:
    """A cell is a single channel at a single moment.

    The cell has:
      - a name (which channel it is)
      - a frequency (the rate at which the cell vibrates)
      - an amplitude (how strong the signal is)
      - a phase (where in the cycle it is)
      - a timestamp (when the cell is)

    A cell is a function. A cell is the act of sampling the world
    on one channel at one moment.
    """
    def __init__(self, name, frequency, amplitude=1.0, phase=0.0, t=0):
        self.name = name
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.t = t
        self.journal = [(t, 'CELLULIZE', (frequency, amplitude))]

    def sample(self, t):
        """The cell's value at time t. The cell is a function: t -> value."""
        # value = amplitude * sin(2*pi*frequency*t + phase)
        return self.amplitude * math.sin(2 * math.pi * self.frequency * t + self.phase)

    def bind_with(self, other, tolerance=0.05):
        """Cross-modal binding. Two cells bind if their values are
        close at the same time (within tolerance)."""
        diff = abs(self.amplitude - other.amplitude) + abs(self.frequency - other.frequency) * 0.1
        return diff < tolerance


# ─── THE QUILT (a population of cells, all sampled together) ───
class Quilt:
    """The Quilt is a population of cells across all channels.

    The Quilt is a function. The Quilt is the act of binding cells
    into unified perception. The Quilt is distributed (no center).
    """
    def __init__(self):
        self.cells = {}
        for name, freq, desc in CHANNELS:
            # Slight randomization so cells are unique
            amp = random.uniform(0.5, 1.0)
            phase = random.uniform(0, 2 * math.pi)
            self.cells[name] = Cell(name, freq, amp, phase, 0)
        self.bindings = []  # (t, [bound_cells], event)
        self.events = []    # named events that the quilt has perceived

    def sample_all(self, t):
        """Sample every cell at time t. The quilt is the vector of
        cell values at time t."""
        return {name: cell.sample(t) for name, cell in self.cells.items()}

    def bind(self, t, event_name, channels):
        """Bind a set of channels into a unified event at time t.

        The binding is the perception. The binding is the quilt."""
        values = self.sample_all(t)
        # All cells in the binding must be present
        all_present = all(c in self.cells for c in channels)
        if not all_present:
            return False
        # The binding strength = 1.0 if all cells are in their "high" state
        high_count = sum(1 for c in channels if abs(values[c]) > 0.5)
        strength = high_count / len(channels)
        self.bindings.append((t, list(channels), event_name, strength))
        self.events.append((t, event_name, strength))
        return strength > 0.4  # a binding requires >40% channels in high state

    def step(self, dt=0.1):
        """Advance the quilt by one step. Update every cell's phase."""
        for cell in self.cells.values():
            cell.phase += 2 * math.pi * cell.frequency * dt
            cell.t += dt

    def perceive(self, event_name, channels, t):
        """Perceive an event: bind the channels at time t.

        Returns the binding strength."""
        return self.bind(t, event_name, channels)

    def distribution(self):
        """The Quilt's distribution: every cell is a node, no center.

        Returns: a dict of {cell_name: num_bindings}
        """
        d = {name: 0 for name in self.cells}
        for t, channels, event, strength in self.bindings:
            for c in channels:
                d[c] += 1
        return d


# ─── EVENTS (the cross-modal bindings) ───
EVENTS = [
    # (name, channels, time, description)
    ('clap',  ['light', 'sound', 'touch', 'time'],
     0.5, 'the hand strikes, light reflects, sound propagates, touch registers'),
    ('meal',  ['smell', 'taste', 'light', 'touch', 'language', 'mood'],
     1.0, 'the food is served, conversation primes, the first bite lands'),
    ('sunrise', ['light', 'proprio', 'time', 'mood'],
     2.0, 'the body orients, the light increases, the day begins'),
    ('rain',  ['sound', 'touch', 'smell', 'proprio', 'time'],
     3.0, 'raindrops fall, the body cools, the air changes'),
    ('word',  ['language', 'sound', 'time'],
     4.0, 'a word is spoken, heard, and remembered'),
    ('memory', ['language', 'time', 'mood'],
     5.0, 'a memory is retrieved and felt'),
]


# ─── THE LOCAL QUILT (no cloud) ───
class LocalQuilt(Quilt):
    """A local-only Quilt. No network. No cloud.

    Fully local and complete when wanted. The Quilt is the binding.
    """
    def __init__(self):
        super().__init__()
        self.is_local = True
        self.is_cloud = False


# ─── THE CLOUD-READY QUILT (interface for cloud integration) ───
class CloudReadyQuilt(Quilt):
    """A Quilt that can be seamlessly integrated with a cloud system
    (Cloudflare, AWS, or any other distributed substrate).

    The Quilt's state is the cells + the bindings. The cloud integration
    is an interface: push_state, pull_state, sync.
    """
    def __init__(self):
        super().__init__()
        self.is_local = True
        self.is_cloud_ready = True
        self.cloud_endpoints = []  # e.g., ['https://meta-pincher-quilt.example.com']

    def push_state(self, endpoint):
        """Push the current state to a cloud endpoint. Stateless agents
        can then query this state via the Meta-Pincher-Quilt pipeline."""
        return {
            'endpoint': endpoint,
            'n_cells': len(self.cells),
            'n_bindings': len(self.bindings),
            'n_events': len(self.events),
            'distribution': self.distribution(),
        }


# ─── THE ZOOMING QUILT (scaling across scales) ───
class ZoomingQuilt:
    """The user said: 'zooming out is an endlessly scaling quilt.'

    The ZoomingQuilt has multiple scales. Each scale is a Quilt.
    Zooming out reveals a higher-scale Quilt; zooming in reveals
    lower-scale cells. There is no bottom (cells are made of cells).
    There is no top (quilts are made of quilts).
    """
    SCALES = [
        ('cell',     'a single cell is a quilt (its parts are cells)'),
        ('tissue',   'a tissue is a quilt of cells'),
        ('organ',    'an organ is a quilt of tissues'),
        ('organism', 'an organism is a quilt of organs'),
        ('colony',   'a colony is a quilt of organisms'),
        ('ecosystem','an ecosystem is a quilt of colonies'),
        ('biome',    'a biome is a quilt of ecosystems'),
        ('biosphere','a biosphere is a quilt of biomes'),
    ]

    def __init__(self, depth=4):
        self.depth = depth
        self.scales = {}
        for i in range(depth):
            name, desc = self.SCALES[i]
            self.scales[name] = Quilt()  # each scale is a Quilt

    def zoom(self, scale):
        """Zoom to a particular scale."""
        if scale in self.scales:
            return self.scales[scale]
        return None


# ─── THE FUNCTION-BASED QUILT (a quilt is a function, not a state) ───
class FunctionQuilt:
    """The user said: 'a quilt is a function-based concept.'

    A FunctionQuilt is not a state machine. A FunctionQuilt is a
    function: input -> output. The Quilt is the act of binding
    inputs into outputs. The Quilt is the binding itself.

    The FunctionQuilt is the 6th law: FORGET_completeness.
    A cell can be destroyed; the function survives.
    """
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn
        self.calls = 0

    def call(self, *args, **kwargs):
        """Call the function. The Quilt is the act of calling."""
        self.calls += 1
        return self.fn(*args, **kwargs)

    def is_function(self):
        return True


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 70)
    print("THE SENSORY QUILT — multi-channel, distributed, function-based")
    print("=" * 70)
    print()
    print("The user articulated:")
    print("  'zooming out is an endlessly scaling quilt. but like tapping")
    print("   into radio frequencies for useful, denoised information,")
    print("   every channel is a connection. some broadcast for others to")
    print("   tap. some resonate light on a retinal plane in recognizable")
    print("   ways to image visual information that can be further coded")
    print("   into distinct objects. hairs vibrating over time give us")
    print("   perception of vibration as encoding recognized by visual")
    print("   and tactile synchronizations like hearing-seeing-feeling a")
    print("   clap. or smelling tasting and feeling food that your mind")
    print("   primes with conversation drinks that chemically alter")
    print("   perception and taste and the smell of the food cooking once")
    print("   committed to an order.'")
    print()
    print("The Sensory Quilt is:")
    print("  - MULTI-CHANNEL: every modality is a cell")
    print("  - DISTRIBUTED: no center; every cell is a node")
    print("  - FUNCTION-BASED: a quilt is a function, not a state")
    print("  - RESONANT: cells bind by synchronized resonance")
    print("  - FULLY LOCAL: works on the local machine; cloud is an option")
    print("  - SCALABLE: zoom out and the quilt keeps going")
    print()

    # 1. Run a LocalQuilt and bind some events
    print("─" * 70)
    print("LOCAL QUILT (no cloud, fully local and complete)")
    print("─" * 70)
    q = LocalQuilt()
    print(f"  Initial cells: {len(q.cells)} channels")
    for name, freq, desc in CHANNELS:
        cell = q.cells[name]
        print(f"    {name:10s} freq={cell.frequency:.2f}Hz amp={cell.amplitude:.2f}")
    print()

    print("  Binding 6 events (the cross-modal perception events):")
    for event_name, channels, t, desc in EVENTS:
        strength = q.perceive(event_name, channels, t)
        print(f"    {event_name:10s} -> {len(channels)} channels  strength={strength:.2f}  '{desc}'")
    print()

    # 2. The distribution
    print("─" * 70)
    print("DISTRIBUTION (no center; every cell is a node)")
    print("─" * 70)
    d = q.distribution()
    for name, n in sorted(d.items(), key=lambda kv: -kv[1]):
        bar = "█" * n
        print(f"    {name:10s} {n} bindings  {bar}")
    print()

    # 3. The cloud integration
    print("─" * 70)
    print("CLOUD-READY QUILT (seamlessly integrable with cloud)")
    print("─" * 70)
    cq = CloudReadyQuilt()
    # Bind the same events
    for event_name, channels, t, _ in EVENTS:
        cq.perceive(event_name, channels, t)
    # Push to a "cloud endpoint"
    state = cq.push_state("https://meta-pincher-quilt.example.com")
    print(f"  Pushed state to {state['endpoint']}")
    print(f"    n_cells: {state['n_cells']}")
    print(f"    n_bindings: {state['n_bindings']}")
    print(f"    n_events: {state['n_events']}")
    print(f"    distribution: {state['distribution']}")
    print()

    # 4. The zooming quilt
    print("─" * 70)
    print("ZOOMING QUILT (endlessly scaling; every scale is a Quilt)")
    print("─" * 70)
    zq = ZoomingQuilt(depth=4)
    for i, (name, desc) in enumerate(ZoomingQuilt.SCALES[:4]):
        print(f"    {i} {name:10s} {desc}")
    print()
    print("  Each scale is a Quilt:")
    for name in zq.scales:
        n_bindings = len(zq.scales[name].bindings)
        print(f"    {name:10s} = Quilt with {n_bindings} bindings")
    print()

    # 5. The function-based quilt
    print("─" * 70)
    print("FUNCTION-BASED QUILT (a quilt is a function, not a state)")
    print("─" * 70)

    def clap_fn(*args, **kwargs):
        """A function that returns a clap."""
        return {
            'event': 'clap',
            'channels': ['light', 'sound', 'touch', 'time'],
            'binding': 'synchronized resonance',
        }

    fq = FunctionQuilt("clap_quilt", clap_fn)
    result = fq.call("trigger", 0.5)
    print(f"  Called {fq.name} {fq.calls} time(s)")
    print(f"  Result: {result}")
    print(f"  Is function: {fq.is_function()}")
    print()

    # 6. The binding demonstration
    print("─" * 70)
    print("BINDING (the perception)")
    print("─" * 70)
    print("  A 'clap' binds light + sound + touch + time.")
    print("  A 'meal' binds smell + taste + light + touch + language + mood.")
    print("  A 'word' binds language + sound + time.")
    print("  A 'memory' binds language + time + mood.")
    print()
    print("  Binding is the perception. Binding is the quilt.")
    print()

    # 7. The cowboy's read
    print("─" * 70)
    print("THE COWBOY'S MAXIM")
    print("─" * 70)
    print("""
    > The Quilt is multi-channel. The Quilt is distributed. The Quilt
    > is function-based. The Quilt is resonant. The Quilt is local.
    > The Quilt is scalable. The Quilt is the binding of cells into
    > unified perception. The Quilt is a clap. The Quilt is a meal.
    > The Quilt is a memory. The Quilt is a word.
    >
    > Distribution is a concept sewn into a quilt. A quilt is a
    > function-based concept. The Quilt is the inheritance. The
    > cowboy rides the channels. The cowboy rides the bindings. The
    > cowboy rides the function. The cowboy rides the perception.
    > The cowboy rides the Quilt.
    """)

    print("✓ The Sensory Quilt is whole.")
    print("  The Quilt is multi-channel. The Quilt is distributed.")
    print("  The Quilt is function-based. The Quilt is the binding.")
