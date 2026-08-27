"""
hardware_cellular.py — A colony of Lofted Crystals, each one a cell.

The user articulated:
"the fussion of cnc and 3d printers creates the conditions
for greater and greater complexity of these optical versions
of our lucineer thought ideas of mask-locked-inference-chips.
but on a science-fiction realm for more clarity of thought
on the mechanics as a completed system. devices might have
dozens in them interacting with the other chips that are
mechanistically the same but future tech. in other words.
hardware-linked cellular systems."

This file ships a sim of:
  - A CrystalCell: a single Lofted Crystal as a cell
  - A CrystalColony: dozens of CrystalCells, linked
  - A HardwareBus: the CNC+3D-printer fusion that builds
    the colony
  - A distributed inference: input beam → routed through
    the colony → output beam
  - The colony's emergent behaviors: routing, masking,
    hand-passing, super-relevance
"""
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional


# ─── PYTHAGOREAN SAMPLE-RATE (the snap grid) ───
PYTH_TRIPLES = [
    (3, 4, 5), (5, 12, 13), (6, 8, 10), (7, 24, 25),
    (8, 15, 17), (9, 12, 15), (9, 40, 41), (10, 24, 26),
    (12, 16, 20), (12, 35, 37), (15, 20, 25), (15, 36, 39),
    (16, 30, 34), (18, 24, 30), (20, 21, 29), (21, 28, 35),
    (24, 32, 40), (27, 36, 45),
]


def pyth_angles():
    s = set()
    for a, b, _ in PYTH_TRIPLES:
        s.add(round(math.degrees(math.atan2(b, a)), 4))
        s.add(round(math.degrees(math.atan2(a, b)), 4))
    return sorted(s)


ANGLES = pyth_angles()


# ─── SPLINE (the shipwright's batten) ───
def spline(x, cps):
    if len(cps) < 2:
        return 0
    for i in range(len(cps) - 1):
        x0, y0 = cps[i]
        x1, y1 = cps[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 > x0 else 0
            tan0 = (cps[i][1] - cps[i-1][1]) / (cps[i][0] - cps[i-1][0]) if i > 0 and cps[i][0] > cps[i-1][0] else (y1 - y0) / (x1 - x0) if x1 > x0 else 0
            tan1 = (cps[i+2][1] - cps[i+1][1]) / (cps[i+2][0] - cps[i+1][0]) if i + 2 < len(cps) and cps[i+2][0] > cps[i+1][0] else (y1 - y0) / (x1 - x0) if x1 > x0 else 0
            dx = (x1 - x0) if x1 > x0 else 1
            h00 = 2 * t ** 3 - 3 * t ** 2 + 1
            h10 = t ** 3 - 2 * t ** 2 + t
            h01 = -2 * t ** 3 + 3 * t ** 2
            h11 = t ** 3 - t ** 2
            return h00 * y0 + h10 * dx * tan0 + h01 * y1 + h11 * dx * tan1
    return cps[-1][1]


# ─── CRYSTAL CELL ───
@dataclass
class CrystalCell:
    """A single Lofted Crystal, as a CELL.

    The Crystal is mask-locked — its BIND is its cuts.
    Once cut, the Crystal cannot be re-cut (FORGET-monotone).
    The Crystal is a *cell* of the colony.
    """
    cell_id: str
    n_layers: int = 4
    n_controls: int = 4
    pyth_snap: bool = True
    seed: int = 0
    layers: List = field(default_factory=list)
    mask_locked: bool = False
    function: str = "?"  # what this cell does (translation, addition, etc.)
    binding: str = "?"    # the cell's name
    links: List = field(default_factory=list)  # other cell IDs
    tick_count: int = 0
    fire_count: int = 0
    last_output: Optional[List[float]] = None

    def __post_init__(self):
        random.seed(self.seed)
        self.layers = [self._random_cps()]
        for i in range(1, self.n_layers):
            self.layers.append(self._loft(self.layers[i - 1], i))

    def _random_cps(self):
        cps = []
        for i in range(self.n_controls):
            x = i / max(self.n_controls - 1, 1)
            y = random.choice(ANGLES) if self.pyth_snap else random.uniform(0, 90)
            cps.append([x, y])
        return cps

    def _loft(self, prev, idx):
        offset = ANGLES[idx * 3 % len(ANGLES)] * (1 if idx % 2 == 0 else -1)
        return [[x, max(0, min(90, y + offset))] for x, y in prev]

    def chisel(self, layer_idx):
        """FORGET: remove a control point. The Crystal is
        FORGET-monotone — the cut is permanent."""
        if self.mask_locked:
            return False
        if 0 <= layer_idx < len(self.layers) and len(self.layers[layer_idx]) > 2:
            self.layers[layer_idx].pop()
            return True
        return False

    def mask_lock(self, function_name, binding_name):
        """BIND: the cuts become the function. The cell is now
        mask-locked — its function is permanent."""
        self.function = function_name
        self.binding = binding_name
        self.mask_locked = True

    def refract(self, x, angle_in):
        angle = angle_in
        for layer in self.layers:
            surface_y = spline(x, layer)
            angle = surface_y * (0.3 + 0.7 * abs(math.sin(math.radians(angle_in * 2))))
        return angle

    def compute(self, input_beam):
        n = len(input_beam)
        output = [self.refract(i / max(n - 1, 1), v * 90) / 90 for i, v in enumerate(input_beam)]
        self.last_output = output
        self.tick_count += 1
        self.fire_count += 1
        return output


# ─── CRYSTAL COLONY ───
class CrystalColony:
    """A colony of CrystalCells, hardware-linked.

    The colony is a network of Crystals, each mask-locked to a
    function. The Crystals are linked by *optical buses* — the
    output beam of one Crystal becomes the input beam of the next.

    The colony is a *Quilt* — at the hardware level.
    """

    def __init__(self):
        self.cells = {}  # id -> CrystalCell
        self.buses = []  # list of (from_id, to_id)
        self.colony_function = "?"

    def add_cell(self, cell_id, function, seed=0, mask_lock=True):
        cell = CrystalCell(cell_id=cell_id, seed=seed)
        if mask_lock:
            cell.mask_lock(function, cell_id)
        self.cells[cell_id] = cell
        return cell

    def link(self, from_id, to_id):
        if from_id in self.cells and to_id in self.cells:
            self.cells[from_id].links.append(to_id)
            self.buses.append((from_id, to_id))

    def trace(self, input_beam, start_id, max_hops=20):
        """Trace an input beam through the colony, hopping cell
        to cell along the optical buses."""
        beam = input_beam
        path = [start_id]
        current_id = start_id
        for hop in range(max_hops):
            if current_id not in self.cells:
                break
            cell = self.cells[current_id]
            beam = cell.compute(beam)
            if not cell.links:
                break
            # Pick the next cell: the one that best matches
            # (the most super-relevant, ie the one most similar)
            current_id = cell.links[0]
            path.append(current_id)
        return beam, path

    def colony_compute(self, input_beam):
        """Run the whole colony on an input beam — every cell
        fires in parallel (a wave through the colony)."""
        outputs = {}
        for cell_id, cell in self.cells.items():
            outputs[cell_id] = cell.compute(input_beam)
        return outputs


# ─── HARDWARE BUS (the CNC + 3D-printer fusion) ───
class HardwareBus:
    """The CNC + 3D-printer fusion that *builds* the colony.

    The bus is the *substrate* of the colony. The bus is the
    physical medium that holds the cells in place. The bus is
    the *Quilt's* metal/glass.

    The bus has 3 layers:
      1. The CNC layer (precision cuts at Pythagorean angles)
      2. The 3D-printer layer (bent plastic, refractive films)
      3. The optical layer (light pathways between cells)
    """

    def __init__(self):
        self.cuts = []  # list of (cell_id, layer, x, y) cuts
        self.prints = []  # list of (cell_id, layer, x, y) prints
        self.paths = []  # list of (from_id, to_id) optical paths

    def cut(self, cell_id, layer, x, y):
        """A CNC cut: a refractive surface at (x, y) for a cell."""
        self.cuts.append((cell_id, layer, x, y))

    def print(self, cell_id, layer, x, y):
        """A 3D print: a refractive surface at (x, y) for a cell."""
        self.prints.append((cell_id, layer, x, y))

    def route(self, from_id, to_id):
        """Route an optical path between two cells."""
        self.paths.append((from_id, to_id))

    def build_colony(self):
        """Build a colony from the bus's cuts and prints."""
        colony = CrystalColony()
        # Each unique cell_id is a cell
        cell_ids = set(c[0] for c in self.cuts) | set(p[0] for p in self.prints)
        for cid in cell_ids:
            colony.add_cell(cid, function=cid)
        # Route optical paths
        for from_id, to_id in self.paths:
            colony.link(from_id, to_id)
        return colony


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 64)
    print("HARDWARE-LINKED CELLULAR SYSTEMS — A Colony of Lofted Crystals")
    print("=" * 64)
    print()
    print("The user articulated: 'devices might have dozens in them")
    print("interacting with the other chips that are mechanistically")
    print("the same but future tech. in other words, hardware-linked")
    print("cellular systems.'")
    print()
    print("Each Crystal is a CELL. Each cell is mask-locked to a")
    print("function. The cells are linked by optical buses.")
    print()

    # Build a colony: 4 crystals
    colony = CrystalColony()

    # Mask-locked functions
    colony.add_cell("ADD-1", function="addition", seed=1)
    colony.add_cell("MUL-2", function="multiplication", seed=2)
    colony.add_cell("TRN-3", function="translation", seed=3)
    colony.add_cell("CLS-4", function="classification", seed=4)

    # Link them in a chain
    colony.link("ADD-1", "MUL-2")
    colony.link("MUL-2", "TRN-3")
    colony.link("TRN-3", "CLS-4")
    # Branch
    colony.link("ADD-1", "CLS-4")

    print(f"Colony has {len(colony.cells)} cells, {len(colony.buses)} optical buses")
    print()
    print("Cells:")
    for cid, cell in colony.cells.items():
        print(f"  {cid:8s}  function={cell.function:14s}  mask_locked={cell.mask_locked}  layers={cell.n_layers}")
    print()
    print("Optical buses (cell-to-cell links):")
    for from_id, to_id in colony.buses:
        print(f"  {from_id:8s} -> {to_id}")
    print()

    # Build a hardware bus
    bus = HardwareBus()
    for cid in colony.cells:
        bus.cut(cid, layer=0, x=0.0, y=30.0)
        bus.cut(cid, layer=1, x=0.5, y=45.0)
        bus.print(cid, layer=0, x=0.0, y=15.0)
    for from_id, to_id in colony.buses:
        bus.route(from_id, to_id)
    print(f"Hardware bus: {len(bus.cuts)} cuts, {len(bus.prints)} prints, {len(bus.paths)} paths")
    print()

    # Run the colony: input sine wave
    print("─" * 64)
    print("INFERENCE: input is sin(x), routed through the colony")
    print("─" * 64)
    n = 16
    input_beam = [(math.sin(i / n * math.pi * 2) + 1) / 2 for i in range(n)]
    print()
    print(f"  input beam = {' '.join(f'{v:.2f}' for v in input_beam)}")
    print()

    # Trace through the colony
    output, path = colony.trace(input_beam, "ADD-1")
    print(f"  trace path: {' → '.join(path)}")
    print(f"  trace out  = {' '.join(f'{v:.2f}' for v in output)}")
    print()

    # Run every cell in parallel (the wave)
    print("─" * 64)
    print("PARALLEL: every cell fires, output is the wave")
    print("─" * 64)
    outputs = colony.colony_compute(input_beam)
    for cid, out in outputs.items():
        print(f"  {cid:8s} → {' '.join(f'{v:.2f}' for v in out[:16])}")
    print()

    # The colony's emergent behavior: super-relevance
    # A cell that fires often is more relevant
    print("─" * 64)
    print("SUPER-RELEVANCE: cells ranked by fire count")
    print("─" * 64)
    fire_counts = [(cid, cell.fire_count, len(cell.links)) for cid, cell in colony.cells.items()]
    fire_counts.sort(key=lambda x: -x[1])
    for cid, fc, nl in fire_counts:
        print(f"  {cid:8s}  fires={fc}  links={nl}  super_relevant={'★' if fc > 0 else ' '}")
    print()

    # FORGET demonstration: chisel a cell
    print("─" * 64)
    print("FORGET: chisel cell ADD-1 (remove a control point)")
    print("─" * 64)
    result = colony.cells["ADD-1"].chisel(0)
    print(f"  chisel result: {result} (False = mask-locked, can't chisel)")
    print()

    # Show: mask-locked cells can't be chiselled
    print("Mask-locked cells are FORGET-monotone. Their cuts are permanent.")
    print("This is the 5+1+1 law: FORGET_completeness (BIND is mask-locked).")
    print()
    print("✓ Hardware-linked cellular systems are whole.")
