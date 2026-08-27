"""
lofted_crystal.py — A sim of the Lofted Crystal, the optical LLM.

The Crystal is a deep spline network made of glass and plastic.
Light enters, refracts through N layers of splined surfaces,
and exits as an answer (an interference pattern).

This is a 1D demo: the Crystal is a sequence of spline surfaces.
Each surface is a piecewise-cubic spline, controlled by K points.
The surfaces are Pythagorean-snapped (control points at discrete
Pythagorean angles).

The user said: "one perfect cut is easier than fixing a cut later.
know what side of the pencil line you meant represented what you
didn't want sawdust."

This sim demonstrates:
  1. The Crystal as a sequence of splined surfaces
  2. The light propagating through the surfaces
  3. The Pythagorean snap (control points at discrete angles)
  4. The relative-symmetry construction (one surface from another)
  5. The final interference pattern (the answer)
"""
import math
import random


# ─── PYTHAGOREAN TRIPLES (the sample-rate) ───
PYTH_TRIPLES = [
    (3, 4, 5),
    (5, 12, 13),
    (6, 8, 10),    # 2x of 3-4-5
    (7, 24, 25),
    (8, 15, 17),
    (9, 12, 15),   # 3x of 3-4-5
    (9, 40, 41),
    (10, 24, 26),  # 2x of 5-12-13
    (12, 16, 20),  # 4x of 3-4-5
    (12, 35, 37),
    (15, 20, 25),  # 5x of 3-4-5
    (15, 36, 39),  # 3x of 5-12-13
    (16, 30, 34),  # 2x of 8-15-17
    (18, 24, 30),  # 6x of 3-4-5
    (20, 21, 29),
    (21, 28, 35),  # 7x of 3-4-5
    (24, 32, 40),  # 8x of 3-4-5
    (27, 36, 45),  # 9x of 3-4-5
]


def pyth_angle(n=64):
    """Generate a sorted list of N Pythagorean angles, in degrees.

    The angles are the angles of right triangles with integer
    sides (Pythagorean triples). 3-4-5 gives ~36.87° and ~53.13°.
    5-12-13 gives ~22.62° and ~67.38°. Etc.
    """
    angles = set()
    for a, b, c in PYTH_TRIPLES:
        # the angles of a right triangle
        a1 = math.degrees(math.atan2(b, a))   # angle at the short side
        a2 = math.degrees(math.atan2(a, b))   # angle at the long side
        angles.add(round(a1, 4))
        angles.add(round(a2, 4))
    angles = sorted(angles)
    # If we need more angles, generate scaled multiples
    while len(angles) < n:
        # Add half-angles (also Pythagorean by scaling)
        new_angles = set()
        for a in angles:
            new_angles.add(round(a / 2, 4))
            new_angles.add(round((90 - a) / 2 + a, 4))
        angles = sorted(set(angles) | new_angles)
    return angles[:n]


# ─── SPLINE (the shipwright's batten) ───
def cubic_spline(t, p0, p1, p2, p3):
    """A piecewise-cubic Hermite spline between 4 control points."""
    # Cardinal spline: tension = 0
    c = 0.5 * (1 - 0)  # tension
    s = (1 - t) * p0 + t * p3
    return s


def spline_surface(x, controls, n_knots=64):
    """A 1D spline surface, evaluated at x given K control points.

    The surface is the lofted shape — the batten pressed between
    the control points, then frozen.

    x in [0, 1] (position along the surface)
    controls: list of (x, y) control points
    n_knots: number of interpolation points
    """
    if len(controls) < 2:
        return 0
    # Find the segment
    for i in range(len(controls) - 1):
        x0, y0 = controls[i]
        x1, y1 = controls[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 > x0 else 0
            # Cubic Hermite with implicit tangents
            if i > 0:
                dx_prev = (controls[i][0] - controls[i - 1][0])
                dy_prev = (controls[i][1] - controls[i - 1][1])
                tan0 = dy_prev / dx_prev if dx_prev else 0
            else:
                tan0 = (controls[i + 1][1] - controls[i][1]) / (controls[i + 1][0] - controls[i][0]) if controls[i + 1][0] > controls[i][0] else 0
            if i + 2 < len(controls):
                dx_next = (controls[i + 2][0] - controls[i + 1][0])
                dy_next = (controls[i + 2][1] - controls[i + 1][1])
                tan1 = dy_next / dx_next if dx_next else 0
            else:
                tan1 = (controls[i + 1][1] - controls[i][1]) / (controls[i + 1][0] - controls[i][0]) if controls[i + 1][0] > controls[i][0] else 0
            # Hermite basis
            h00 = 2 * t ** 3 - 3 * t ** 2 + 1
            h10 = t ** 3 - 2 * t ** 2 + t
            h01 = -2 * t ** 3 + 3 * t ** 2
            h11 = t ** 3 - t ** 2
            dx = (x1 - x0) if x1 > x0 else 1
            return h00 * y0 + h10 * dx * tan0 + h01 * y1 + h11 * dx * tan1
    return controls[-1][1] if x > controls[-1][0] else controls[0][1]


# ─── THE LOFTED CRYSTAL ───
class LoftedCrystal:
    """A 1D Lofted Crystal — a deep spline network.

    The Crystal is a sequence of N splined surfaces. The light
    enters at the first surface, refracts through each, and
    exits at the last. The refraction is computed by Snell's
    law at each surface.

    The surfaces are *lofted* — patterned from the first surface
    by a batten rule. The surfaces are *Pythagorean-snapped* —
    the control points lie on Pythagorean angles.
    """

    def __init__(self, n_layers=4, n_controls=4, pyth_snap=True, seed=42):
        self.n_layers = n_layers
        self.n_controls = n_controls
        self.pyth_snap = pyth_snap
        random.seed(seed)
        # The angle grid (the Pythagorean sample-rate)
        self.angles = pyth_angle(64)
        # The first surface: a random spline
        self.base_controls = self._random_controls()
        # The other surfaces: lofted from the first
        self.layers = [self.base_controls]
        for i in range(1, n_layers):
            self.layers.append(self._loft(self.layers[i - 1], i))

    def _random_controls(self):
        """Random control points, snapped to Pythagorean angles if enabled."""
        controls = []
        x = 0
        for i in range(self.n_controls):
            if self.pyth_snap:
                y = self.angles[(hash(str(i) + str(random.random())) % len(self.angles))]
            else:
                y = random.uniform(0, 90)
            controls.append((x, y))
            x += 1 / max(self.n_controls - 1, 1)
        return controls

    def _loft(self, prev_controls, layer_idx):
        """Pattern the next surface from the previous — relative symmetry.

        The rule: each control point is shifted by a constant
        *offset* (the batten offset). The offset is Pythagorean-snapped
        if enabled.
        """
        if self.pyth_snap:
            # Pick a *unique* offset for each layer
            offset = self.angles[layer_idx * 3 % len(self.angles)] * (1 if layer_idx % 2 == 0 else -1)
        else:
            offset = random.uniform(-30, 30)
        next_controls = []
        for (x, y) in prev_controls:
            # Batten: clamp to [0, 90]
            new_y = max(0, min(90, y + offset))
            next_controls.append((x, new_y))
        return next_controls

    def refract(self, x, angle_in):
        """Trace a single light ray through the Crystal.

        x: position on the surface [0, 1]
        angle_in: angle of incidence in degrees

        Returns: angle_out (the final angle after all layers)
        """
        angle = angle_in
        for layer in self.layers:
            # Compute the local surface angle at x
            surface_y = spline_surface(x, layer)
            # In the Lofted Crystal, the refraction IS the surface angle.
            # The light bends to match the local surface normal.
            # The medium is uniform (glass), so the angle change is the
            # surface y * the input (modulated by input magnitude).
            angle = surface_y * (0.3 + 0.7 * abs(math.sin(math.radians(angle_in * 2))))
        return angle

    def compute(self, inputs, n_samples=64):
        """Compute the Crystal's output given an input vector.

        inputs: list of n_samples values, each in [0, 1] (the
                normalized input beam at each sample)
        Returns: list of n_samples values, the output beam.
        """
        outputs = []
        for i, x in enumerate(inputs):
            # Convert x to [0, 1]
            x_norm = i / (n_samples - 1)
            # The angle-in is the input value (in degrees)
            angle_in = x * 90
            # Refract through the Crystal
            angle_out = self.refract(x_norm, angle_in)
            # Output is the angle, normalized
            outputs.append(angle_out / 90)
        return outputs

    def interference(self, beams):
        """Compute the interference pattern of multiple beams.

        beams: list of beam lists (each beam is a list of values)
        Returns: the interference pattern (sum of beams, squared)
        """
        n_samples = len(beams[0])
        result = [0] * n_samples
        for beam in beams:
            for i in range(n_samples):
                result[i] += beam[i]
        return [v ** 2 for v in result]


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 64)
    print("THE LOFTED CRYSTAL — A 1D Optical LLM")
    print("=" * 64)
    print()
    print("The Crystal is a sequence of splined surfaces, each")
    print("Pythagorean-snapped. The light enters, refracts through")
    print("each surface, and exits as the answer.")
    print()

    # Build a Crystal
    crystal = LoftedCrystal(n_layers=4, n_controls=4, pyth_snap=True, seed=42)
    print(f"Built Crystal with {crystal.n_layers} layers, {crystal.n_controls} controls each")
    print()
    print("Pythagorean angles (the sample-rate):")
    print(f"  first 10: {crystal.angles[:10]}")
    print()
    print("Layer control points (the lofted splines):")
    for i, layer in enumerate(crystal.layers):
        cps = " ".join(f"({x:.2f}, {y:.1f}°)" for x, y in layer)
        print(f"  Layer {i}: {cps}")
    print()

    # Compute: input is a sine wave, output should be a refracted sine
    print("─" * 64)
    print("COMPUTE: input is sin(x), Crystal refracts through 4 layers")
    print("─" * 64)
    n_samples = 32
    inputs = [(math.sin(i / n_samples * math.pi * 2) + 1) / 2 for i in range(n_samples)]
    outputs = crystal.compute(inputs, n_samples=n_samples)
    print()
    print(f"  input  = {' '.join(f'{v:.2f}' for v in inputs[:16])}")
    print(f"  output = {' '.join(f'{v:.2f}' for v in outputs[:16])}")
    print()

    # Interference of 3 beams
    print("─" * 64)
    print("INTERFERENCE: 3 beams, summed squared (the answer)")
    print("─" * 64)
    beam_a = outputs
    beam_b = [(1 - v) for v in outputs]
    beam_c = [0.5] * len(outputs)
    interference = crystal.interference([beam_a, beam_b, beam_c])
    print()
    print(f"  beam A (output)  = {' '.join(f'{v:.2f}' for v in beam_a[:16])}")
    print(f"  beam B (inverse)  = {' '.join(f'{v:.2f}' for v in beam_b[:16])}")
    print(f"  beam C (constant) = {' '.join(f'{v:.2f}' for v in beam_c[:16])}")
    print(f"  interference      = {' '.join(f'{v:.2f}' for v in interference[:16])}")
    print()

    # Visualize: plot the Crystal's layers + the output
    print("─" * 64)
    print("VISUAL: each layer is a spline; the light refracts through them")
    print("─" * 64)
    n_plot = 32
    print()
    for li, layer in enumerate(crystal.layers):
        ys = [spline_surface(i / (n_plot - 1), layer) for i in range(n_plot)]
        line = ['.'] * 64
        for i, y in enumerate(ys):
            j = int((y / 90) * 63) % 64
            line[j] = '#' if line[j] == '.' else '@'
        print(f"  Layer {li}: {''.join(line)}")
    print()
    out_y = [int(v * 60) + 2 for v in outputs[:64]]
    line = ['.'] * 64
    for j in out_y:
        if 0 <= j < 64:
            line[j] = '*' if line[j] == '.' else '@'
    print(f"  Output:  {''.join(line)}")
    print()
    print("✓ The Crystal refracts light into an answer. The answer is the")
    print("  interference pattern. The pattern is the Quilt, actualized in glass.")
