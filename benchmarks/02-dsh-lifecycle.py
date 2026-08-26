#!/usr/bin/env python3
"""
bench_02_dsh.py — DSH (Decompose-Synthesize-Harden) lifecycle simulator.

A cell starts as an "immature stem cell" containing a large model.
Through DSH, it becomes a "mature cell" with mostly algorithmic body
and a small model at its joints.
"""
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Any, List

@dataclass
class Cell:
    name: str
    model: Callable = None  # Adaptive behavior
    scope: str = None
    contract: dict = None
    output_history: List[Any] = field(default_factory=list)
    model_calls: int = 0
    
    def observe(self, n_contexts=100):
        """Observe the cell's output over many contexts."""
        outputs = []
        for _ in range(n_contexts):
            if self.model:
                self.model_calls += 1
                out = self.model(_)
            else:
                # Algorithmic: deterministic
                out = "deterministic"
            outputs.append(out)
        self.output_history = outputs
        # Reproducibility: most common output / total
        most_common = max(set(outputs), key=outputs.count)
        return outputs.count(most_common) / len(outputs)

    def is_algorithmic(self, threshold=0.9):
        """Cell is algorithmic if its output is reproducible."""
        if not self.output_history:
            return False
        most_common = max(set(self.output_history), key=self.output_history.count)
        return self.output_history.count(most_common) / len(self.output_history) > threshold


def mock_model(x):
    """A 'model' that mostly returns the same answer (algorithmic-like)
    with some randomness (adaptive-like)."""
    if random.random() < 0.7:
        return "fixed_answer"
    return random.choice(["answer_A", "answer_B", "answer_C"])


def fully_algorithmic(x):
    return "fixed_answer"


def fully_adaptive(x):
    return random.choice(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"])


print("=" * 60)
print("  DSH (Decompose-Synthesize-Harden) Lifecycle")
print("  Simulating 1000 TICKs on a model-bearing cell")
print("=" * 60)

# === Phase D: Decompose ===
print("\n--- D: Decompose ---")
immature = Cell(name="stem-cell", model=mock_model)
reproducibility = immature.observe(n_contexts=1000)
print(f"  Stem cell observed: reproducibility = {reproducibility:.2f}")
print(f"  Model calls during observation: {immature.model_calls}")

# === Phase S: Synthesize ===
print("\n--- S: Synthesize ---")
# The cell's recurring part becomes algorithmic
# The cell's rare part stays adaptive (becomes the joint)
if reproducibility > 0.9:
    print("  → Mostly algorithmic. Decompose into 1 algorithmic cell + 0 joints")
    new_cells = [
        Cell(name="algo-cell", model=fully_algorithmic),
    ]
elif reproducibility > 0.5:
    print("  → Mixed. Decompose into 1 algorithmic cell + 1 joint")
    new_cells = [
        Cell(name="algo-cell", model=fully_algorithmic),
        Cell(name="joint-cell", model=fully_adaptive),
    ]
else:
    print("  → Mostly adaptive. Decompose into 0 algorithmic cells + 2 joints")
    new_cells = [
        Cell(name="joint-A", model=mock_model),
        Cell(name="joint-B", model=mock_model),
    ]

for c in new_cells:
    c.observe(n_contexts=1000)
    print(f"  {c.name}: model_calls={c.model_calls}, algorithmic={c.is_algorithmic()}")

# === Phase H: Harden ===
print("\n--- H: Harden ---")
n_algorithmic = 0
n_joints = 0
total_calls_before = immature.model_calls
total_calls_after = sum(c.model_calls for c in new_cells)
for c in new_cells:
    if c.is_algorithmic():
        c.model = None  # Remove the model — it's now algorithmic
        n_algorithmic += 1
        print(f"  {c.name}: HARDENED (model removed, now pure algorithm)")
    else:
        n_joints += 1
        print(f"  {c.name}: JOINT (model retained)")

# === Report ===
print("\n" + "=" * 60)
print(f"  DSH Summary:")
print(f"    Original cell: 1 model-bearing cell, {total_calls_before} model calls")
print(f"    After DSH: {len(new_cells)} cells")
print(f"      - {n_algorithmic} algorithmic (no model)")
print(f"      - {n_joints} joints (model retained)")
print(f"    Total model calls after DSH: {total_calls_after}")
print(f"    Cost reduction: {(1 - total_calls_after / (total_calls_before * 1000)) * 100:.1f}%")
print()
print("  The cell has matured. Its body is algorithmic;")
print("  its joints remain soft. The model is at the seams,")
print("  not the center. The cowboy rides between joints.")
print("=" * 60)
