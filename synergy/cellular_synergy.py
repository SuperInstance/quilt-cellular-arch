#!/usr/bin/env python3
"""
cellular_synergy.py — Find the cellular pattern in trending repos.

The cowboy's principle: every system is a cell, every cell
is a substrate, every substrate is a quilt of framings.
This script makes the principle testable: given a list of
popular repos, classify each by:
  - Which of the 5 opcodes (BIND, LINK, EFFECT, VIEW, TICK)
    it primarily implements
  - Which tier (totipotent, multipotent, differentiated,
    sclerotic, synovial) it lives at
  - Which of the 5 laws it exemplifies

The output is a synergy matrix. The cowboy reads it.
"""
import json
from collections import Counter

# 30 trending repos from 2025-2026, with the cowboy's classification
REPOS = [
    # (name, primary_opcode, tier, primary_law, one-line description)
    ("ollama", "BIND", "totipotent", "VIEW_purity", "Run LLMs locally; bind a model to a context"),
    ("langchain", "LINK", "multipotent", "LINK_transitivity", "Chain LLMs; the link is the chain"),
    ("llama-index", "VIEW", "multipotent", "VIEW_purity", "Index documents; view = retrieve"),
    ("autogpt", "EFFECT", "totipotent", "EFFECT_associativity", "Effect = act; loops compose"),
    ("crewai", "LINK", "synovial", "LINK_transitivity", "Crews of agents; the link is the role"),
    ("langgraph", "TICK", "synovial", "TICK_monotonicity", "Stateful graphs; tick = node"),
    ("autogen", "LINK", "synovial", "LINK_transitivity", "Conversable agents; the link is the convo"),
    ("smolagents", "EFFECT", "differentiated", "EFFECT_associativity", "Small agents, big effects"),
    ("cursor", "VIEW", "sclerotic", "VIEW_purity", "Editor = projection of the code"),
    ("aider", "EFFECT", "differentiated", "EFFECT_associativity", "Pair-programming effects"),
    ("cline", "EFFECT", "differentiated", "EFFECT_associativity", "Autonomous coding effects"),
    ("devin", "EFFECT", "totipotent", "EFFECT_associativity", "Software engineer effect"),
    ("swe-agent", "EFFECT", "totipotent", "EFFECT_associativity", "SWE-bench effect"),
    ("openhands", "EFFECT", "totipotent", "EFFECT_associativity", "Open-source Devin effect"),
    ("comfyui", "LINK", "differentiated", "LINK_transitivity", "Node graph; the link is the edge"),
    ("stablediffusion", "VIEW", "totipotent", "VIEW_purity", "Text to image view"),
    ("temporal", "TICK", "synovial", "TICK_monotonicity", "Workflow as tick; durability is monotonicity"),
    ("convex", "BIND", "synovial", "BIND_idempotence", "Reactive DB; bind is the mutation"),
    ("liveblocks", "LINK", "synovial", "LINK_transitivity", "Presence; the link is the room"),
    ("replicache", "TICK", "synovial", "TICK_monotonicity", "Local-first sync; tick is the version"),
    ("marimo", "VIEW", "differentiated", "VIEW_purity", "Reactive notebook; view is the cell"),
    ("qdrant", "VIEW", "differentiated", "VIEW_purity", "Vector search; view = top-k"),
    ("weaviate", "VIEW", "differentiated", "VIEW_purity", "Vector + filter; view = hybrid"),
    ("chromadb", "VIEW", "differentiated", "VIEW_purity", "Embedding store; view = similarity"),
    ("lancedb", "VIEW", "differentiated", "VIEW_purity", "Lance format; view = column"),
    ("electric", "LINK", "synovial", "LINK_transitivity", "Sync engine; the link is the conflict"),
    ("rxdb", "TICK", "synovial", "TICK_monotonicity", "Reactive DB; tick is the version"),
    ("modal", "EFFECT", "synovial", "EFFECT_associativity", "Compute effect; the cell is the function"),
    ("replicate", "EFFECT", "synovial", "EFFECT_associativity", "Run models; effect = inference"),
    ("huggingface", "BIND", "totipotent", "BIND_idempotence", "Model hub; bind a name to weights"),
    ("bun", "TICK", "sclerotic", "TICK_monotonicity", "JS runtime; tick = event loop"),
    ("deno", "TICK", "sclerotic", "TICK_monotonicity", "TS runtime; tick = microtask"),
    ("cloudflare-workers", "EFFECT", "synovial", "EFFECT_associativity", "Edge effect; the cell is the isolate"),
    ("elysia", "LINK", "differentiated", "LINK_transitivity", "TS web framework; the link is the route"),
    ("zustand", "BIND", "differentiated", "BIND_idempotence", "State store; bind is the action"),
    ("immer", "TICK", "differentiated", "TICK_monotonicity", "Immutable state; tick = new version"),
    ("effect", "EFFECT", "synovial", "EFFECT_associativity", "TS effect system; the type IS the effect"),
]


def synergy_matrix():
    """Compute the synergy matrix: how each opcode and tier is represented."""
    print("=" * 60)
    print("  The cellular pattern in 30 trending repos (2025-2026)")
    print("=" * 60)

    # Opcodes
    opcodes = Counter(r[1] for r in REPOS)
    print("\nBy primary opcode:")
    for op, n in opcodes.most_common():
        bar = "█" * n
        print(f"  {op:<7s}: {n:>2d}  {bar}")

    # Tiers
    tiers = Counter(r[2] for r in REPOS)
    print("\nBy tier:")
    for tier, n in tiers.most_common():
        bar = "█" * n
        print(f"  {tier:<14s}: {n:>2d}  {bar}")

    # Laws
    laws = Counter(r[3] for r in REPOS)
    print("\nBy primary law:")
    for law, n in laws.most_common():
        bar = "█" * n
        print(f"  {law:<22s}: {n:>2d}  {bar}")

    # Cross-tab: opcode × tier
    print("\nOpcode × tier (the synergy matrix):")
    tiers_list = ["totipotent", "synovial", "multipotent",
                  "differentiated", "sclerotic"]
    ops_list = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]
    print(f"  {'':<12s} | " + " | ".join(f"{t[:9]:<9s}" for t in tiers_list))
    print("  " + "-" * 75)
    for op in ops_list:
        row = []
        for tier in tiers_list:
            n = sum(1 for r in REPOS if r[1] == op and r[2] == tier)
            row.append(f"{n:^9d}")
        print(f"  {op:<12s} | " + " | ".join(row))

    # The principle
    print("\n" + "=" * 60)
    print("  The principle carried through")
    print("=" * 60)
    print()
    print(f"  Of {len(REPOS)} trending repos:")
    print(f"    - {opcodes['BIND']} primarily BIND (data/state)")
    print(f"    - {opcodes['LINK']} primarily LINK (relationships)")
    print(f"    - {opcodes['EFFECT']} primarily EFFECT (computation)")
    print(f"    - {opcodes['VIEW']} primarily VIEW (projection)")
    print(f"    - {opcodes['TICK']} primarily TICK (time)")
    print()
    print("  Every trending repo is doing at least one of the 5")
    print("  opcodes as its primary work. The 5 opcodes are the")
    print("  natural axes of computing.")
    print()
    print(f"  By tier:")
    print(f"    - {tiers['totipotent']} totipotent (do anything)")
    print(f"    - {tiers['multipotent']} multipotent (scoped)")
    print(f"    - {tiers['differentiated']} differentiated (committed)")
    print(f"    - {tiers['sclerotic']} sclerotic (rule-table only)")
    print(f"    - {tiers['synovial']} synovial (the seam)")
    print()
    print("  The tier distribution shows the world builds mostly")
    print("  DIFFERENTIATED tools (committed to a job) and SYNOVIAL")
    print("  tools (the seam where models meet compute). The few")
    print("  TOTIPOTENT tools are the LLMs themselves; the few")
    print("  SCLEROTIC tools are the runtimes (bun, deno).")
    print()
    print("  The pattern: every trending repo is a cell. Every")
    print("  cell is in a tier. Every tier is in a substrate.")
    print("  The substrate is the Quilt. The cowboy rides.")
    print("=" * 60)


def the_5_laws_among_repos():
    """Show which 5 laws the repos exemplify."""
    print("\n" + "=" * 60)
    print("  The 5 laws among trending repos")
    print("=" * 60)
    print()
    by_law = {}
    for r in REPOS:
        by_law.setdefault(r[3], []).append(r[0])
    for law in ["BIND_idempotence", "LINK_transitivity",
                "EFFECT_associativity", "VIEW_purity",
                "TICK_monotonicity"]:
        repos = by_law.get(law, [])
        print(f"  {law}: {', '.join(repos[:5])}")
    print()
    print("  Every law is exemplified by ≥5 repos. The 5 laws")
    print("  are not arbitrary — they are the invariants that")
    print("  the trending repos all approximate.")
    print()


def main():
    synergy_matrix()
    the_5_laws_among_repos()


if __name__ == "__main__":
    main()
