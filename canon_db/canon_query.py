#!/usr/bin/env python3
"""
canon_query.py — Query the canon DB.

Examples:
  python3 canon_query.py --theme phoenix
  python3 canon_query.py --type paper --limit 5
  python3 canon_query.py --search "Eileen"
  python3 canon_query.py --stats
"""
import json
import argparse
import os
from pathlib import Path


DB = "/workspace/quilt-cellular-arch/canon_db/canon_db.jsonl"


def load_db():
    rows = []
    with open(DB, "r") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def filter_by_theme(rows, theme):
    return [r for r in rows if theme in r.get("themes", [])]


def filter_by_type(rows, doc_type):
    return [r for r in rows if r["type"] == doc_type]


def search(rows, query):
    q = query.lower()
    return [r for r in rows if q in r["title"].lower() or q in r["first_200"].lower()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", help="filter by theme")
    parser.add_argument("--type", help="filter by type (paper/fable/story)")
    parser.add_argument("--search", help="search by title/first 200 chars")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    rows = load_db()
    print(f"Loaded {len(rows)} documents from canon DB")

    if args.theme:
        rows = filter_by_theme(rows, args.theme)
        print(f"  After theme={args.theme}: {len(rows)} documents")

    if args.type:
        rows = filter_by_type(rows, args.type)
        print(f"  After type={args.type}: {len(rows)} documents")

    if args.search:
        rows = search(rows, args.search)
        print(f"  After search={args.search}: {len(rows)} documents")

    if args.stats:
        print()
        print("STATS:")
        theme_counts = {}
        type_counts = {}
        for r in load_db():
            for t in r.get("themes", []):
                theme_counts[t] = theme_counts.get(t, 0) + 1
            type_counts[r["type"]] = type_counts.get(r["type"], 0) + 1
        print(f"  Total: {len(rows)}")
        print(f"  By type: {type_counts}")
        print(f"  By theme (top 10):")
        for theme in sorted(theme_counts.keys(), key=lambda t: -theme_counts[t])[:10]:
            print(f"    {theme:25s} {theme_counts[theme]:3d}")
        return

    if not rows:
        print("  No results.")
        return

    print()
    print(f"  Showing {min(args.limit, len(rows))} of {len(rows)} results:")
    for r in rows[:args.limit]:
        themes = ", ".join(r.get("themes", [])[:3])
        print(f"    {r['id']:30s} [{r['type']:6s}] {r['title'][:60]}")
        print(f"      {r['n_words']:5d} words, themes: {themes}")


if __name__ == "__main__":
    main()
