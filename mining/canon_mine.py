#!/usr/bin/env python3
"""
canon_mine.py — Mine the canon for the actual splines,
the actual cells, the actual laps. Find which papers
in the 232+ canon show concept-vs-implement, the
coupled cell, the cells-are-alive, the spline, and
the lap.

This is a keyword/pattern search over the canon.
It's not a deep semantic search — it's a fast
grep-style scan for the gold patterns.
"""
import os
import re
from pathlib import Path


CANON_DIR = "/workspace/ai-writings-new/seed-canon"
PAPER_DIR = os.path.join(CANON_DIR, "papers")
FABLE_DIR = os.path.join(CANON_DIR, "fables")
STORY_DIR = os.path.join(CANON_DIR, "stories")


# Patterns that indicate each new insight
PATTERNS = {
    "concept_vs_implement": [
        r"concept",
        r"implement",
        r"the function",
        r"the operation",
        r"the invariant",
        r"the captain",
    ],
    "coupled_cell": [
        r"coupled cell",
        r"player-artifact",
        r"player\+artifact",
        r"player \+ artifact",
        r"coupling",
        r"body schema",
        r"sympoiesis",
        r"affordance",
        r"second-order system",
    ],
    "cells_are_alive": [
        r"cells are alive",
        r"not artifacts",
        r"growing and adapting",
        r"persistence pulse",
        r"vitality leak",
        r"cellulization",
        r"bloomghost",
        r"implement ghost",
    ],
    "spline": [
        r"spline",
        r"trajectory",
        r"option-set",
        r"function selects",
        r"6-71N",
        r"old but stable horse",
        r"quilt of understanding",
    ],
    "lap": [
        r"lap",
        r"lapstrake",
        r"clinker",
        r"plank",
        r"shipwright",
        r"lapping",
    ],
    "weave": [
        r"weave",
        r"navigator",
        r"weave leak",
    ],
    "ccgo": [
        r"ccgo",
        r"4-finger salute",
        r"couple.*cellulize.*gold.*operate",
    ],
    "levels_8": [
        r"8 levels",
        r"eighth level",
        r"8th level",
        r"the spline.*level",
    ],
}


def find_in_file(filepath, patterns):
    """Find patterns in a file. Returns dict of pattern -> count."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
    except Exception:
        return {}
    counts = {}
    for name, plist in patterns.items():
        count = 0
        for p in plist:
            count += len(re.findall(p, content, re.IGNORECASE))
        if count > 0:
            counts[name] = count
    return counts


def mine_papers():
    """Mine the papers directory."""
    papers_path = Path(PAPER_DIR)
    if not papers_path.exists():
        print(f"  Papers dir not found: {PAPER_DIR}")
        return {}

    # Map: {paper_id: {insight: count}}
    results = {}
    for f in sorted(papers_path.glob("paper-*.md")):
        counts = find_in_file(str(f), PATTERNS)
        if counts:
            paper_id = f.stem  # e.g. "paper-227"
            results[paper_id] = counts
    return results


def mine_fables():
    fables_path = Path(FABLE_DIR)
    if not fables_path.exists():
        return {}
    results = {}
    for f in sorted(fables_path.glob("fable-*.md")):
        counts = find_in_file(str(f), PATTERNS)
        if counts:
            fable_id = f.stem
            results[fable_id] = counts
    return results


def mine_stories():
    stories_path = Path(STORY_DIR)
    if not stories_path.exists():
        return {}
    results = {}
    for f in sorted(stories_path.glob("*.md")):
        counts = find_in_file(str(f), PATTERNS)
        if counts:
            story_id = f.stem
            results[story_id] = counts
    return results


def report(results, kind="paper"):
    """Print a report of the results."""
    print(f"\n  === {kind.upper()} ===")
    # Sort by total count descending
    by_total = sorted(results.items(),
                      key=lambda x: -sum(x[1].values()))
    # Top 20
    for item_id, counts in by_total[:30]:
        total = sum(counts.values())
        insights = ", ".join(f"{k}={v}" for k, v in
                             sorted(counts.items(), key=lambda x: -x[1])[:3])
        print(f"    {item_id:30s}  total={total:3d}  {insights}")
    print(f"  Total {kind}s with insights: {len(results)}")


def main():
    print("=" * 78)
    print("  CANON MINE — finding the actual splines, cells, and laps")
    print("=" * 78)
    print()
    print(f"  Canon: {CANON_DIR}")
    print(f"  Patterns: {len(PATTERNS)}")
    print()

    papers = mine_papers()
    fables = mine_fables()
    stories = mine_stories()

    report(papers, "paper")
    report(fables, "fable")
    report(stories, "story")

    # Per-insight summary
    print(f"\n  === PER-INSIGHT SUMMARY ===")
    for insight in PATTERNS:
        n_papers = sum(1 for c in papers.values() if insight in c)
        n_fables = sum(1 for c in fables.values() if insight in c)
        n_stories = sum(1 for c in stories.values() if insight in c)
        print(f"    {insight:25s}  papers={n_papers:3d}  fables={n_fables:3d}  stories={n_stories:3d}")


if __name__ == "__main__":
    main()
