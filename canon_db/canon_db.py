#!/usr/bin/env python3
"""
canon_db.py — Turn the canon into a queryable database.

Walks the canon directory, parses each paper/fable/story,
extracts metadata, writes to JSONL.

Output: /workspace/quilt-cellular-arch/canon_db.jsonl

Each row is a dict:
  {
    "id": "paper-227",
    "type": "paper" | "fable" | "story",
    "title": "...",
    "size_bytes": 1000,
    "n_lines": 50,
    "n_words": 5000,
    "first_200": "...",
    "phases": [],
    "themes": ["concept_vs_implement", "coupled_cell", ...]
  }
"""
import os
import re
import json
from pathlib import Path


CANON_DIR = "/workspace/ai-writings-new/seed-canon"
PAPER_DIR = os.path.join(CANON_DIR, "papers")
FABLE_DIR = os.path.join(CANON_DIR, "fables")
STORY_DIR = os.path.join(CANON_DIR, "stories")
OUT = "/workspace/quilt-cellular-arch/canon_db.jsonl"

# Theme patterns (from canon_mine)
THEMES = {
    "concept_vs_implement": r"concept|implement|invariant",
    "coupled_cell": r"coupled cell|player.?artifact|sympoiesis|affordance",
    "cells_are_alive": r"cells are alive|not artifacts|persistence pulse|vitality leak|cellulization|bloomghost|implement ghost",
    "spline": r"spline|trajectory|6-71N|old but stable horse",
    "lap": r"lap|lapstrake|plank|shipwright",
    "weave": r"weave|navigator|leak",
    "ccgo": r"ccgo|4-finger salute|couple.*cellulize.*gold",
    "levels_8": r"8 levels|eighth level|8th level|spline.*level",
    "captain_song": r"captain.?song|9th level",
    "muse_cipher": r"muse|cipher|10th level",
    "nexus": r"nexus|11th level",
    "phoenix": r"phoenix|12th level|cycle",
    "ground_sky": r"ground|sky|13th level|14th level",
    "forget": r"forget|6th opcode",
}


def extract_title(content):
    """Extract the title from the first non-empty line."""
    for line in content.split("\n"):
        line = line.strip()
        if line and line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def detect_themes(content):
    """Detect which themes are in the content."""
    content_lower = content.lower()
    found = []
    for theme, pattern in THEMES.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            found.append(theme)
    return found


def process_file(filepath, doc_type):
    """Process a single canon file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    stem = Path(filepath).stem
    return {
        "id": stem,
        "type": doc_type,
        "title": extract_title(content),
        "size_bytes": len(content),
        "n_lines": content.count("\n") + 1,
        "n_words": len(content.split()),
        "first_200": content[:200].replace("\n", " "),
        "themes": detect_themes(content),
        "path": filepath,
    }


def main():
    print("=" * 78)
    print("  CANON DB — turn the canon into a queryable database")
    print("=" * 78)
    print()

    rows = []

    # Papers
    if os.path.exists(PAPER_DIR):
        for f in sorted(Path(PAPER_DIR).glob("paper-*.md")):
            rows.append(process_file(str(f), "paper"))
        print(f"  Papers: {sum(1 for r in rows if r['type'] == 'paper')}")

    # Fables
    if os.path.exists(FABLE_DIR):
        for f in sorted(Path(FABLE_DIR).glob("fable-*.md")):
            rows.append(process_file(str(f), "fable"))
        print(f"  Fables: {sum(1 for r in rows if r['type'] == 'fable')}")

    # Stories
    if os.path.exists(STORY_DIR):
        for f in sorted(Path(STORY_DIR).glob("*.md")):
            if f.stem in ["README", "INDEX"]: continue
            rows.append(process_file(str(f), "story"))
        print(f"  Stories: {sum(1 for r in rows if r['type'] == 'story')}")

    # Write JSONL
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # Stats
    print()
    print(f"  Total documents: {len(rows)}")
    print(f"  Total bytes: {sum(r['size_bytes'] for r in rows):,}")
    print(f"  Total words: {sum(r['n_words'] for r in rows):,}")

    # Theme stats
    print()
    print("  THEME COVERAGE:")
    theme_counts = {}
    for r in rows:
        for t in r["themes"]:
            theme_counts[t] = theme_counts.get(t, 0) + 1
    for theme in sorted(theme_counts.keys(), key=lambda t: -theme_counts[t]):
        print(f"    {theme:25s} {theme_counts[theme]:3d} documents")

    print()
    print(f"  Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
