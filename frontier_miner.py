"""
frontier_miner.py — The cheap frontier scanner.

The user said: "conserve your own tokens as best you can and orchestrate
apis with iterative programs to do the lifting and ideation while you
direct on the cheap."

This miner scans the wiki + canon to find missing frontiers. It doesn't
call any LLM. It just looks at filenames and numbers, then queues the
gaps into frontiers.json for the daemon to process.

The 10 frontier gaps to mine:
  1. F1, F2, ..., F15 — every odd-numbered future is a possible gap
  2. The 14 levels — every level (0-14) needs a wiki entry?
  3. The 6 lifecycle stages — every stage needs a definition
  4. The 6 tiers — every tier needs a deep-dive

The miner reads the existing wiki entries, computes the gaps, and
appends the missing frontiers to frontiers.json.
"""
import json
import os
import re
import sys

WORKSPACE = os.environ.get("QUILT_WORKSPACE", "/workspace")
WIKI_DIR = os.path.join(WORKSPACE, "quilt-wiki-2126")
FRONTIERS_FILE = os.path.join(WORKSPACE, "_scouts/frontiers.json")


def list_existing_frontiers():
    """Read 00-future/ and return set of existing frontier IDs.

    Matches both '01-splined-lantern.md' and 'f2.md' patterns.
    """
    future_dir = os.path.join(WIKI_DIR, "00-future")
    if not os.path.exists(future_dir):
        return set()
    existing = set()
    for f in os.listdir(future_dir):
        # Match patterns: "01-name.md", "1-name.md", "f1.md", "f01.md"
        m = re.match(r"^(?:f)?0*(\d+)", f, re.IGNORECASE)
        if m:
            existing.add(f"F{int(m.group(1))}")
    return existing


def mine_missing_frontiers():
    """Find missing frontier IDs in the 1-15 range."""
    existing = list_existing_frontiers()
    all_possible = {f"F{i}" for i in range(1, 17) if i not in (6, 8, 10, 12, 14)}  # gaps are by convention
    missing = sorted(all_possible - existing, key=lambda x: int(x[1:]))
    return missing, existing


def mine_missing_levels():
    """Find missing 14-level entries."""
    foundation_dir = os.path.join(WIKI_DIR, "03-foundations")
    if not os.path.exists(foundation_dir):
        return ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14"]
    existing = set()
    for f in os.listdir(foundation_dir):
        m = re.match(r"^L?(\d+)", f)
        if m:
            existing.add(int(m.group(1)))
    return [f"L{i}" for i in range(15) if i not in existing]


def load_queue():
    if not os.path.exists(FRONTIERS_FILE):
        return []
    with open(FRONTIERS_FILE) as f:
        return json.load(f)


def save_queue(q):
    with open(FRONTIERS_FILE, "w") as f:
        json.dump(q, f, indent=2)


def main():
    print("=" * 70)
    print("FRONTIER MINER — cheap scanner for canon gaps")
    print("=" * 70)
    print()
    print(f"Wiki: {WIKI_DIR}")
    print()

    # Scan missing frontiers
    missing_frontiers, existing = mine_missing_frontiers()
    print(f"  Existing frontiers: {sorted(existing)}")
    print(f"  Missing frontiers: {missing_frontiers}")
    print()

    # Scan missing levels
    missing_levels = mine_missing_levels()
    print(f"  Missing levels (0-14): {missing_levels}")
    print()

    # Load current queue
    queue = load_queue()
    existing_ids = {f.get("id") for f in queue}

    # Add missing frontiers to the queue
    paper_num = 290
    added = 0
    for fid in missing_frontiers:
        if fid in existing_ids:
            continue
        queue.append({
            "id": fid,
            "title": f"Quilt future {fid} (mined gap)",
            "paper_num": paper_num,
            "prompt": None,
        })
        paper_num += 1
        added += 1

    # Add missing levels
    for lid in missing_levels:
        if lid in existing_ids:
            continue
        queue.append({
            "id": lid,
            "title": f"Level {lid[1:]} of operation",
            "paper_num": paper_num,
            "prompt": None,
        })
        paper_num += 1
        added += 1

    if added > 0:
        save_queue(queue)
        print(f"  Added {added} frontiers to the queue.")
    else:
        print(f"  No new frontiers to add. Queue has {len(queue)} entries.")

    print(f"  Queue size: {len(queue)}")
    print()
    print("✓ Frontier miner complete. Run writers_room_daemon.py to process.")


if __name__ == "__main__":
    main()
