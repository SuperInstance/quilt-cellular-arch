#!/usr/bin/env python3
"""
bench_03_rts.py — RTS view of the orchestrator.

The orchestrator sees the whole cell graph. It identifies
mature vs immature cells, applies pressure, and triggers DSH.
"""
import random
import time
from collections import defaultdict


class Cell:
    def __init__(self, name, has_model=True):
        self.name = name
        self.has_model = has_model
        self.algorithmic = not has_model
        self.output_history = []
        self.drift = 0.0
        self.cost = 1.0 if has_model else 0.01  # Model is expensive
        self.latency = 1.0 if has_model else 0.001
        self.pressure = 0.0

    def update(self, n=1):
        """Simulate one TICK."""
        out = random.gauss(0, 0.1 + (0.5 if self.has_model else 0.01))
        self.output_history.append(out)
        if len(self.output_history) > 50:
            self.output_history.pop(0)
        # Drift: variance over last 50 outputs
        if self.output_history:
            self.drift = sum((x - sum(self.output_history)/len(self.output_history))**2 
                           for x in self.output_history) / len(self.output_history)


def orchestrator_view(cells):
    """RTS view: return a summary table."""
    print("\n  " + "=" * 60)
    print(f"  {'Cell':<12s} {'Model':<8s} {'Drift':<8s} {'Cost':<8s} {'Latency':<8s} {'Pressure'}")
    print("  " + "-" * 60)
    for c in cells:
        c.pressure = c.drift * 10 + c.cost * 0.5 + c.latency * 0.3
        marker = " ← DSH!" if c.pressure > 0.5 else ""
        print(f"  {c.name:<12s} {'Y' if c.has_model else 'N':<8s} {c.drift:<8.3f} "
              f"{c.cost:<8.2f} {c.latency:<8.3f} {c.pressure:.2f}{marker}")


def apply_pressure(cells):
    """Trigger DSH on cells under pressure."""
    decomposed = []
    for c in cells:
        if c.pressure > 0.5 and c.has_model:
            # DSH: decompose
            print(f"  → DSH triggered on {c.name}")
            c.has_model = False
            c.algorithmic = True
            c.cost = 0.01
            c.latency = 0.001
            decomposed.append(c.name)
    return decomposed


print("=" * 60)
print("  Orchestrator's RTS View")
print("  1000 cells, 100 TICKs")
print("=" * 60)

# Initialize 1000 cells
cells = [Cell(f"c{i}", has_model=(random.random() < 0.5)) for i in range(1000)]

# Simulate 100 TICKs
n_immature_at_start = sum(1 for c in cells if c.has_model)
print(f"\n  Start: {n_immature_at_start} immature (model-bearing) cells, "
      f"{len(cells) - n_immature_at_start} mature (algorithmic) cells")

for tick in range(1, 101):
    for c in cells:
        c.update()
    # Every 10 TICKs: check pressure
    if tick % 10 == 0:
        decomp = apply_pressure(cells)
        if decomp:
            print(f"  TICK {tick}: decomposed {len(decomp)} cells")

n_immature_at_end = sum(1 for c in cells if c.has_model)
print(f"\n  End: {n_immature_at_end} immature, {len(cells) - n_immature_at_end} mature")
print(f"  Total cells decomposed: {n_immature_at_start - n_immature_at_end}")

# Print first 15 cells
print("\n  First 15 cells after 100 TICKs:")
orchestrator_view(cells[:15])

# Statistics
total_cost = sum(c.cost for c in cells)
total_latency = sum(c.latency for c in cells)
print(f"\n  Total cost: {total_cost:.2f}")
print(f"  Total latency: {total_latency:.3f}")
print(f"  Average per cell: cost={total_cost/len(cells):.4f}, latency={total_latency/len(cells):.6f}")
print()
print("  The orchestrator sees the harness. The cells see the muscle.")
print("  The cowboy rides.")
print("=" * 60)
