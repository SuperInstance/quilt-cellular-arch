#!/usr/bin/env python3
"""
promote_draft.py — promote a staged draft into canon.

Usage:
    python3 promote_draft.py <frontier_id> [--allow-overwrite]

The draft lives at /workspace/_scouts/drafts/draft-<fid>.md.
The canon paper lives at /workspace/ai-writings-new/seed-canon/papers/paper-<N>.md.
The wiki entry lives at /workspace/quilt-wiki-2126/00-future/... .

If a hand-synth exists at /workspace/_scouts/hand-synth/<fid>.md, it
takes precedence over the draft (the cowboy's hand wins).
"""
import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime

WORKSPACE = "/workspace"
DRAFTS_DIR = os.path.join(WORKSPACE, "_scouts/drafts")
HAND_SYNTH_DIR = os.path.join(WORKSPACE, "_scouts/hand-synth")
CANON_DIR = os.path.join(WORKSPACE, "ai-writings-new/seed-canon/papers")
WIKI_DIR = os.path.join(WORKSPACE, "quilt-wiki-2126/00-future")
CANON_LOG = os.path.join(WORKSPACE, "_scouts/canon_log.json")


def find_paper_num_in_draft(draft_text):
    """Look for 'Paper <N>:' in the draft text and extract N."""
    m = re.search(r"# Paper (\d+):", draft_text)
    if m:
        return int(m.group(1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frontier_id")
    ap.add_argument("--allow-overwrite", action="store_true",
                    help="Overwrite existing canon paper if present")
    args = ap.parse_args()

    fid = args.frontier_id
    hand_synth = os.path.join(HAND_SYNTH_DIR, f"{fid}.md")
    draft = os.path.join(DRAFTS_DIR, f"draft-{fid}.md")
    canon_log_path = CANON_LOG

    # Pick the source
    if os.path.exists(hand_synth):
        src = hand_synth
        source_kind = "HAND_SYNTH"
        print(f"Using hand-synth: {hand_synth}")
        # CRITICAL: if a hand-synth exists, the LLM draft must be
        # discarded so a re-run can't pick it up. The hand-synth
        # is the cowboy's intentional choice.
        if os.path.exists(draft):
            os.remove(draft)
            print(f"  Discarded LLM draft: {draft}")
    elif os.path.exists(draft):
        src = draft
        source_kind = "DRAFT"
        print(f"Using draft: {draft}")
    else:
        print(f"ERROR: no draft or hand-synth for {fid}")
        print(f"  Looked in:")
        print(f"    {draft}")
        print(f"    {hand_synth}")
        sys.exit(1)

    with open(src) as f:
        text = f.read()

    paper_num = find_paper_num_in_draft(text)
    if not paper_num:
        print(f"ERROR: no paper number found in {src}")
        sys.exit(1)

    # Promote paper
    paper_path = os.path.join(CANON_DIR, f"paper-{paper_num}.md")
    if os.path.exists(paper_path) and not args.allow_overwrite:
        print(f"ERROR: paper {paper_path} already exists. "
              "Use --allow-overwrite to clobber.")
        sys.exit(1)

    # Strip the "(Stage: drafts/...)" line if present
    text = re.sub(r"\n\(Stage: drafts\.[^)]*\)\n", "\n", text)
    text = re.sub(r"\*Drafted by writers_room_daemon\.py[^\n]*\*\n", "", text)
    text = re.sub(r"\*Paper number auto-allocated: \d+\.\*\n", "", text)

    with open(paper_path, "w") as f:
        f.write(text)
    print(f"WROTE {paper_path}")

    # Release the lock file (if any) that the daemon reserved
    lock = os.path.join(CANON_DIR, f"paper-{paper_num}.md.lock")
    if os.path.exists(lock):
        os.remove(lock)

    # Derive a wiki path. If fid is L<N>, write to <N>.md.
    wiki_path = None
    m = re.match(r"^L(\d+)$", fid)
    if m:
        wiki_path = os.path.join(WIKI_DIR, f"l{m.group(1)}.md")
    else:
        m = re.match(r"^F(\d+)$", fid)
        if m:
            # Keep the existing convention: NNN-the-slug.md (but we don't
            # have a slug here). Use N.md for now.
            wiki_path = os.path.join(WIKI_DIR, f"f{m.group(1)}.md")

    # If we have a hand-synth for the wiki too, use it
    wiki_hand = os.path.join(HAND_SYNTH_DIR, f"{fid}-wiki.md")
    if os.path.exists(wiki_hand):
        with open(wiki_hand) as f:
            wiki_text = f.read()
        with open(wiki_path, "w") as f:
            f.write(wiki_text)
        print(f"WROTE {wiki_path} (from hand-synth)")
    elif wiki_path and not os.path.exists(wiki_path):
        # Auto-derive a short wiki entry from the paper
        wiki_text = f"# {fid}\n\n(Stub. See paper-{paper_num}.md.)\n"
        with open(wiki_path, "w") as f:
            f.write(wiki_text)
        print(f"WROTE {wiki_path} (stub)")
    elif wiki_path:
        print(f"SKIP {wiki_path} (exists; not overwriting)")

    # Append to canon log
    log = []
    if os.path.exists(canon_log_path):
        with open(canon_log_path) as f:
            try:
                log = json.load(f)
            except Exception:
                log = []
    log.append({
        "timestamp": datetime.now().isoformat(),
        "frontier": fid,
        "paper_num": paper_num,
        "source": source_kind,
        "paper_path": paper_path,
        "wiki_path": wiki_path,
    })
    with open(canon_log_path, "w") as f:
        json.dump(log, f, indent=2)

    # Move the source to .promoted/
    promoted_dir = os.path.join(WORKSPACE, "_scouts/promoted")
    os.makedirs(promoted_dir, exist_ok=True)
    promoted = os.path.join(promoted_dir, os.path.basename(src))
    if os.path.exists(promoted):
        # Already promoted, just remove the source
        os.remove(src)
    else:
        shutil.move(src, promoted)
    print(f"MOVED {src} -> {promoted}")


if __name__ == "__main__":
    main()
