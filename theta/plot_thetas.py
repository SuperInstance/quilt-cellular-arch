#!/usr/bin/env python3
"""
plot_thetas.py — Visualize the math of framings.

A 2D field of discs, a wounded cell, the spin within spin.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path


def plot_field_of_discs():
    """Plot the field of discs as a quiver."""
    n = 8
    rng = np.random.default_rng(42)
    phases = rng.uniform(-0.05, 0.05, (n, n))
    for i in range(n):
        for j in range(n):
            phases[i, j] += (i + j) * 0.1

    # Inject a wound at (4, 4)
    wound_i, wound_j = 4, 4
    phases[wound_i, wound_j] += 2 * np.pi

    # The arrows: each disc's phase is the angle
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Healthy field
    ax = axes[0]
    for i in range(n):
        for j in range(n):
            theta = (i + j) * 0.1
            x, y = np.cos(theta), np.sin(theta)
            ax.arrow(j, i, x * 0.3, y * 0.3,
                     head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.set_title("Healthy field: smooth phase gradient\n(the substrate is flat)")
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, n - 0.5)
    ax.invert_yaxis()
    ax.set_aspect('equal')

    # Wounded field
    ax = axes[1]
    for i in range(n):
        for j in range(n):
            theta = phases[i, j]
            x, y = np.cos(theta), np.sin(theta)
            color = 'red' if (i, j) == (wound_i, wound_j) else 'blue'
            ax.arrow(j, i, x * 0.3, y * 0.3,
                     head_width=0.1, head_length=0.1, fc=color, ec=color)
    ax.set_title(f"Wounded field: phase jump at ({wound_i}, {wound_j})\n"
                 f"(the cowboy's wound-heal target)")
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, n - 0.5)
    ax.invert_yaxis()
    ax.set_aspect('equal')

    plt.tight_layout()
    out = Path("/workspace/_scouts/theta_field.png")
    plt.savefig(out, dpi=80)
    print(f"Saved: {out}")


def plot_orbits():
    """Plot 5 orbits, each at its own theta."""
    fig, ax = plt.subplots(figsize=(8, 8))
    n = 5
    rng = np.random.default_rng(7)
    for i in range(n):
        r = 0.5 + i * 0.5
        theta0 = rng.uniform(0, 2 * np.pi)
        # The orbit
        t = np.linspace(0, 2 * np.pi, 100)
        x = r * np.cos(t + theta0)
        y = r * np.sin(t + theta0)
        ax.plot(x, y, alpha=0.6)
        # The current position
        ax.plot(r * np.cos(theta0), r * np.sin(theta0), 'o', markersize=15)
        ax.annotate(f"r={r}", (r * np.cos(theta0), r * np.sin(theta0)),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_title("5 orbits = 5 cells. The pair-wise thetas are the LINKs.\n"
                 "The math of framings is the math of thetas.")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    out = Path("/workspace/_scouts/theta_orbits.png")
    plt.savefig(out, dpi=80)
    print(f"Saved: {out}")


def plot_spin_within_spin():
    """A 3D plot: spin within spin within spin."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Three nested orbits
    for r, color in [(1.0, 'blue'), (0.5, 'green'), (0.25, 'red')]:
        t = np.linspace(0, 4 * np.pi, 200)
        # Each level spins at a different rate
        omega = 2 * np.pi / (r * 2)  # inner = faster
        x = r * np.cos(t * omega)
        y = r * np.sin(t * omega)
        z = r * np.sin(t * omega / 2)  # 3D wobble
        ax.plot(x, y, z, color=color, alpha=0.7, label=f"r={r}")

    ax.set_title("Spin within spin within spin\n"
                 "(the math of framings, in 3D)")
    ax.legend()
    out = Path("/workspace/_scouts/theta_spin.png")
    plt.savefig(out, dpi=80)
    print(f"Saved: {out}")


if __name__ == "__main__":
    plot_field_of_discs()
    plot_orbits()
    plot_spin_within_spin()
