#!/usr/bin/env python3
"""
theta_math.py — The math of framings.

A spinning disc is a depth sounder. The disc measures time
in one rotation and depth in the axis orientation. The
phase angle theta is the link between the two origins
(temporal, spatial).

This script shows the math:
  1. A spinning disc as a clock
  2. The disc as a depth sounder (its axis orientation)
  3. The link between the two (theta)
  4. A 2D field of discs (a quilt of framings)
  5. The "wound" — a cell whose frame doesn't agree with
     its neighbors (curvature)

The principle: every quilt is a framing. Every framing is
a coordinate system. The math of framings is theta.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. A single spinning disc as a clock + depth sounder
# ============================================================
def spinning_disc(t, omega=2 * np.pi / 1.0, phi=0.0):
    """Position of a marker on a spinning disc at time t.

    omega: angular velocity (rad/sec). 2π/1 = 1 Hz.
    phi: phase offset (rad) — the disc's orientation at t=0.

    Returns (x, y, theta) where theta is the angle.
    """
    theta = omega * t + phi
    x = np.cos(theta)
    y = np.sin(theta)
    return x, y, theta


def demo_single_disc():
    print("=" * 60)
    print("  1. A spinning disc: clock + depth sounder")
    print("=" * 60)
    # 1 second at 1 Hz
    times = np.linspace(0, 1, 11)
    for t in times:
        x, y, theta = spinning_disc(t)
        print(f"  t={t:.1f}s  θ={theta:.3f} rad  marker=({x:.3f}, {y:.3f})")
    print()
    print("  The disc is the clock. Each rotation is 1 second.")
    print("  The marker is the time hand.")
    print("  The disc's AXIS (a 3D vector) is the depth sounder.")
    print("  The phase theta links time to space.")
    print()


# ============================================================
# 2. Two discs: the link between them
# ============================================================
def two_discs_link(t, omega1, phi1, omega2, phi2):
    """Two discs. The theta between them is the link.

    Each disc has its own clock and depth. The phase difference
    between them is the math of their relationship.
    """
    x1, y1, t1 = spinning_disc(t, omega1, phi1)
    x2, y2, t2 = spinning_disc(t, omega2, phi2)
    return {
        "disc1": (x1, y1, t1),
        "disc2": (x2, y2, t2),
        "delta_theta": t1 - t2,  # the link
    }


def demo_two_discs():
    print("=" * 60)
    print("  2. Two discs: the link between them")
    print("=" * 60)
    # Disc 1: 1 Hz, starts at 0
    # Disc 2: 1 Hz, starts at π/4 (45° offset)
    t = 0.5  # half a second in
    link = two_discs_link(t, 2 * np.pi, 0.0, 2 * np.pi, np.pi / 4)
    print(f"  Disc 1: x={link['disc1'][0]:.3f}, y={link['disc1'][1]:.3f}, θ={link['disc1'][2]:.3f}")
    print(f"  Disc 2: x={link['disc2'][0]:.3f}, y={link['disc2'][1]:.3f}, θ={link['disc2'][2]:.3f}")
    print(f"  Δθ (the link): {link['delta_theta']:.3f} rad = {np.degrees(link['delta_theta']):.1f}°")
    print()
    print("  The link is constant. Δθ is the relationship between the two discs.")
    print("  In a consistent substrate, the link holds across all neighbors.")
    print()


# ============================================================
# 3. A 2D field of discs (a quilt of framings)
# ============================================================
def field_of_discs(n=8, omega=2 * np.pi, jitter=0.0, seed=0):
    """An n×n grid of spinning discs.

    Each disc has a phase offset. In a consistent field,
    the phase varies smoothly. In a wounded field, one
    disc has a phase that doesn't match its neighbors.
    """
    rng = np.random.default_rng(seed)
    phases = rng.uniform(-jitter, jitter, (n, n))
    # Smooth gradient: phase is also a function of position
    for i in range(n):
        for j in range(n):
            phases[i, j] += (i + j) * 0.1
    return phases


def demo_field():
    print("=" * 60)
    print("  3. A 2D field of discs (the quilt of framings)")
    print("=" * 60)
    n = 8
    phases = field_of_discs(n, jitter=0.05, seed=42)

    # Compute the link between each pair of adjacent discs
    print(f"  {n}×{n} grid. Each disc has a phase offset.")
    print()
    print(f"  Phase at (0,0): {phases[0,0]:.3f}")
    print(f"  Phase at (3,3): {phases[3,3]:.3f}")
    print(f"  Phase at (7,7): {phases[7,7]:.3f}")
    print()
    # The "gradient" — how phase changes across the field
    grad_y = np.diff(phases, axis=0)
    grad_x = np.diff(phases, axis=1)
    print(f"  Avg |∂θ/∂y|: {np.abs(grad_y).mean():.4f}  (small = consistent)")
    print(f"  Avg |∂θ/∂x|: {np.abs(grad_x).mean():.4f}  (small = consistent)")
    print()
    print("  When the gradient is small, the field is flat: the")
    print("  substrate is consistent. When it's large, there's")
    print("  a wound — a cell whose frame doesn't agree with")
    print("  its neighbors. The cowboy heals the wound.")
    print()


# ============================================================
# 4. The wound: a cell whose frame doesn't agree
# ============================================================
def wounded_field(n=8):
    """A field with one wounded disc (a 2π phase jump)."""
    phases = field_of_discs(n, jitter=0.05, seed=42)
    # Inject a wound at (4, 4) — a 2π jump
    wound_i, wound_j = 4, 4
    phases[wound_i, wound_j] += 2 * np.pi
    return phases, (wound_i, wound_j)


def demo_wound():
    print("=" * 60)
    print("  4. The wound — a cell whose frame doesn't agree")
    print("=" * 60)
    phases, wound = wounded_field()
    wi, wj = wound

    # Check the gradient around the wound
    print(f"  Wound at ({wi}, {wj}), phase = {phases[wi, wj]:.3f}")
    print()
    print(f"  Neighbors:")
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = wi + di, wj + dj
        if 0 <= ni < phases.shape[0] and 0 <= nj < phases.shape[1]:
            dtheta = phases[ni, nj] - phases[wi, wj]
            dtheta = (dtheta + np.pi) % (2 * np.pi) - np.pi  # wrap
            print(f"    ({ni}, {nj}): phase={phases[ni,nj]:.3f}, Δθ={dtheta:+.3f}")
    print()
    print("  The wound shows up as a large Δθ with one or more")
    print("  neighbors. In a consistent substrate, |Δθ| < π.")
    print("  The wound-heal: recall the wounded cell's lineage,")
    print("  retire it, spawn a blastema with the right phase.")
    print()


# ============================================================
# 5. Theta as a function of a vector (the relationship)
# ============================================================
def theta_from_relationship(p1, p2):
    """Theta between two positions is a vector in 2D space.

    The theta is the angle of the vector from p1 to p2.
    The relationship is the vector itself.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx)
    return r, theta


def demo_theta_vector():
    print("=" * 60)
    print("  5. Theta as a function of a vector (the relationship)")
    print("=" * 60)
    # Sun and Earth
    sun = (0, 0)
    earth = (1, 0)
    r, theta = theta_from_relationship(sun, earth)
    print(f"  Sun → Earth: r={r:.3f}, θ={theta:.3f} rad ({np.degrees(theta):.1f}°)")

    # Sun and Mars
    mars = (1.5, 0.5)
    r, theta = theta_from_relationship(sun, mars)
    print(f"  Sun → Mars:  r={r:.3f}, θ={theta:.3f} rad ({np.degrees(theta):.1f}°)")

    # Earth and Mars (the relationship, not the absolute)
    r, theta = theta_from_relationship(earth, mars)
    print(f"  Earth → Mars: r={r:.3f}, θ={theta:.3f} rad ({np.degrees(theta):.1f}°)")
    print()
    print("  In a solar system, every body has a position. Every")
    print("  pair of bodies has a relationship (a vector). Every")
    print("  vector has a theta. The math of the orbits is the")
    print("  math of thetas — one for each pair, evolving over")
    print("  time, with spin within spin within spin.")
    print()
    print("  The substrate is the same. Every cell has a position")
    print("  (its name, its value). Every pair of cells has a")
    print("  relationship (a LINK). Every relationship has a theta")
    print("  (the LINK's type, weight, contract). The math of")
    print("  the substrate is the math of thetas.")
    print()


# ============================================================
# 6. The full picture: a solar system as a quilt
# ============================================================
def solar_system_as_quilt(n_bodies=5):
    """A solar system is a quilt of bodies.

    Each body has a position and a velocity. The pair-wise
    relationships are vectors. The thetas are the angles
    of the vectors. The substrate is the math of thetas.
    """
    print("=" * 60)
    print("  6. A solar system as a quilt")
    print("=" * 60)
    rng = np.random.default_rng(7)
    bodies = []
    for i in range(n_bodies):
        r = 0.5 + i * 0.5  # orbital radius
        theta0 = rng.uniform(0, 2 * np.pi)  # initial angle
        bodies.append({"name": f"body_{i}", "r": r, "theta0": theta0})
    print(f"  {n_bodies} bodies, each on a circular orbit")
    for b in bodies:
        print(f"  {b['name']}: r={b['r']:.1f}, θ₀={np.degrees(b['theta0']):.1f}°")
    print()
    # At time t=0, compute all pair-wise thetas
    print("  Pair-wise θ at t=0:")
    for i in range(n_bodies):
        for j in range(i + 1, n_bodies):
            p1 = (bodies[i]["r"] * np.cos(bodies[i]["theta0"]),
                  bodies[i]["r"] * np.sin(bodies[i]["theta0"]))
            p2 = (bodies[j]["r"] * np.cos(bodies[j]["theta0"]),
                  bodies[j]["r"] * np.sin(bodies[j]["theta0"]))
            r, theta = theta_from_relationship(p1, p2)
            print(f"    {bodies[i]['name']} → {bodies[j]['name']}: "
                  f"r={r:.2f}, θ={np.degrees(theta):.1f}°")
    print()
    print("  The pair-wise thetas are the substrate's links.")
    print("  Each theta is a relationship. Each relationship")
    print("  is a vector in a higher-dimensional space. The")
    print("  spin within spin within spin is thetas of")
    print("  thetas of thetas — relationships of")
    print("  relationships of relationships.")
    print()


# ============================================================
# 7. The substrate as a quilt of framings (the summary)
# ============================================================
def the_principle():
    print("=" * 60)
    print("  7. The principle: the substrate is a quilt of framings")
    print("=" * 60)
    print()
    print("  Every quilt has quilts within it.")
    print("  Every SuperQuilt has quilts as its cells.")
    print("  Every framing is a coordinate system.")
    print("  Every coordinate system has:")
    print("    - a temporal origin (when the clock starts)")
    print("    - a spatial origin (where the axes point)")
    print("    - a scale (how big a unit is)")
    print("    - an orientation (which way the axes are rotated)")
    print()
    print("  A spinning disc measures:")
    print("    - time in one rotation (relative to t=0)")
    print("    - depth in the axis orientation (relative to north)")
    print("  The phase theta is the link.")
    print()
    print("  The substrate's 5 opcodes are transforms:")
    print("    - BIND: name → value (labeling)")
    print("    - LINK: cell → cell (relational)")
    print("    - EFFECT: inputs → outputs (functional)")
    print("    - VIEW: state → projection (projection)")
    print("    - TICK: moment → next moment (temporal)")
    print("  Each transform has a theta. The theta is the math")
    print("  of framings.")
    print()
    print("  The SuperInstance is the quilt of quilts.")
    print("  The quilt of quilts is the SuperQuilt.")
    print("  The SuperQuilt is the framing of framings.")
    print()
    print("  The substrate runs. The cowboy rides. The theta")
    print("  links. The chart grows.")
    print("=" * 60)


def main():
    demo_single_disc()
    demo_two_discs()
    demo_field()
    demo_wound()
    demo_theta_vector()
    solar_system_as_quilt()
    the_principle()


if __name__ == "__main__":
    main()
