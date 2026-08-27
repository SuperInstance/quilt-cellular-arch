#!/usr/bin/env python3
"""
mine_canon.py — Mine the canon for hidden patterns.

This is the bedrock-digging tool. It reads the entire canon
(214 papers, 114 fables, 145 stories, scenarios, transcripts)
and finds:
  1. Term frequencies (what words appear most in the canon?)
  2. Co-occurrences (which terms appear together?)
  3. Concept clusters (which papers share vocabulary?)
  4. Citation graph (which papers cite which fables?)
  5. Gaps (what concepts are mentioned but never explained?)
  6. The actual hidden structure: what is the canon's real shape?

The user said: "stop swinging at the tip. dive deep. mine
in new conditions." This script IS the diving.
"""
import os
import re
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

CANON_DIR = Path("/workspace/ai-writings-new/seed-canon")


def load_corpus():
    """Load all canon files. Return {path: (text, type)}."""
    corpus = {}
    for md in CANON_DIR.rglob("*.md"):
        rel = md.relative_to(CANON_DIR)
        type_ = rel.parts[0] if rel.parts else "unknown"
        try:
            text = md.read_text(errors='ignore')
            corpus[str(rel)] = (text, type_)
        except Exception:
            pass
    return corpus


# ============================================================
# 1. Term frequencies
# ============================================================
def term_frequencies(corpus, n=40):
    """Find the most common content words across the canon."""
    # Stopwords
    stopwords = set("""
    a an the of and or but if then else is are was were be been being
    have has had do does did will would shall should can could may might must
    this that these those it its their there here when where what which who
    to for from in on at by with as into through about between among
    not no nor so than too very just only also even still yet already
    all each every any some most more less much many few little
    i me my we us our you your he she him her his hers they them theirs
    """.split())
    # Tokenize
    counter = Counter()
    for text, _ in corpus.values():
        # Words (3+ chars, lowercase, alpha)
        for word in re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()):
            if word in stopwords or len(word) < 4:
                continue
            counter[word] += 1
    return counter.most_common(n)


# ============================================================
# 2. Co-occurrences (which terms appear together?)
# ============================================================
def co_occurrences(corpus, top_terms, window=50):
    """For each pair of top terms, count how often they co-occur."""
    top_set = set(t for t, _ in top_terms)
    pair_counter = Counter()
    for text, _ in corpus.values():
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Sliding window
        for i in range(len(words)):
            for j in range(i + 1, min(i + window, len(words))):
                w1, w2 = words[i], words[j]
                if w1 in top_set and w2 in top_set and w1 < w2:
                    pair_counter[(w1, w2)] += 1
    return pair_counter.most_common(30)


# ============================================================
# 3. Per-tier vocabulary (what does each tier talk about?)
# ============================================================
def tier_vocabulary(corpus, n=15):
    """Most common words per tier (papers, fables, stories, etc.)."""
    by_type = defaultdict(Counter)
    for text, type_ in corpus.values():
        for word in re.findall(r'\b[a-zA-Z]{4,}\b', text.lower()):
            if word in ("this", "that", "with", "from", "they", "have", "been", "were", "their", "what", "which", "when", "where", "your", "them"):
                continue
            by_type[type_][word] += 1
    return {t: c.most_common(n) for t, c in by_type.items()}


# ============================================================
# 4. The cowboy's patterns (find the recurring cowboy motifs)
# ============================================================
def cowboy_patterns(corpus):
    """Find sentences that contain the cowboy's signature phrases."""
    motifs = [
        "the cowboy rides",
        "the cowboy reads",
        "the cowboy sees",
        "the substrate is the boat",
        "the cell is the unit",
        "the chart grows",
        "the breath",
        "the seam",
        "the bedrock",
        "the holonomy",
        "the dregs",
        "the exhale",
        "the inhale",
        "the spine",
        "the joint",
        "the synapse",
        "the harbor",
        "the boat",
        "the cells",
        "the cell",
        "the model",
        "the rule",
        "the tap",
        "the cowboy",
    ]
    counts = Counter()
    samples = defaultdict(list)
    for path, (text, type_) in corpus.items():
        for motif in motifs:
            n = text.lower().count(motif.lower())
            if n > 0:
                counts[motif] += n
                if len(samples[motif]) < 3:
                    # Find an example sentence
                    for sent in re.split(r'[.!?]\s', text):
                        if motif.lower() in sent.lower() and 20 < len(sent) < 200:
                            samples[motif].append(sent.strip())
                            break
    return counts.most_common(), samples


# ============================================================
# 5. The 5 ops/laws/tiers (how often does the canon name them?)
# ============================================================
def five_counts(corpus):
    """Count mentions of the 5 opcodes, 5 laws, 5 tiers."""
    opcodes = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]
    laws = ["BIND_idempotence", "LINK_transitivity", "EFFECT_associativity",
            "VIEW_purity", "TICK_monotonicity"]
    tiers = ["totipotent", "multipotent", "differentiated", "sclerotic", "synovial"]
    
    opc_count = Counter()
    law_count = Counter()
    tier_count = Counter()
    
    for text, _ in corpus.values():
        for op in opcodes:
            opc_count[op] += len(re.findall(r'\b' + op + r'\b', text))
        for law in laws:
            law_count[law] += len(re.findall(re.escape(law), text))
        for tier in tiers:
            tier_count[tier] += len(re.findall(tier, text, re.IGNORECASE))
    
    return {
        "opcodes": opc_count.most_common(),
        "laws": law_count.most_common(),
        "tiers": tier_count.most_common(),
    }


# ============================================================
# 6. Length distribution (the canon's shape)
# ============================================================
def length_distribution(corpus):
    """How long are the canon pieces, by type?"""
    by_type = defaultdict(list)
    for text, type_ in corpus.values():
        # Strip frontmatter and code blocks for a fair length
        clean = re.sub(r'^---.*?---', '', text, flags=re.DOTALL)
        clean = re.sub(r'```.*?```', '', clean, flags=re.DOTALL)
        words = len(clean.split())
        by_type[type_].append(words)
    
    stats = {}
    for t, lens in by_type.items():
        if lens:
            stats[t] = {
                "count": len(lens),
                "min": min(lens),
                "max": max(lens),
                "mean": sum(lens) // len(lens),
                "median": sorted(lens)[len(lens) // 2],
            }
    return stats


# ============================================================
# 7. Gaps: which foundational concepts are mentioned but unexplained?
# ============================================================
def find_gaps(corpus, top_terms, threshold=20):
    """Terms that appear many times but are never the SUBJECT of a definition."""
    # A "defined" term is one that appears in a sentence with "is" + definition pattern
    defined = Counter()
    mentioned = Counter()
    
    for text, _ in corpus.values():
        # Find "X is Y" patterns
        for m in re.finditer(r'([A-Za-z][A-Za-z_]{2,})\s+is\s+(?:a|an|the)\s+([A-Za-z][A-Za-z ]{2,50})', text):
            term = m.group(1).lower()
            defined[term] += 1
        # Find any capitalized term
        for m in re.finditer(r'\b([A-Z][A-Za-z_]{2,})\b', text):
            term = m.group(1).lower()
            if term in ("this", "that", "they", "have", "what", "which", "when", "where", "your", "from", "with"):
                continue
            mentioned[term] += 1
    
    # Find terms that are mentioned a lot but defined less
    gaps = []
    for term, n in mentioned.most_common(200):
        if n >= threshold and defined[term] < 3:
            gaps.append((term, n, defined[term]))
    return gaps[:20]


def main():
    print("=" * 70)
    print("  THE CANON MINED — what 381 pieces, 2.6MB of canon actually says")
    print("=" * 70)
    
    print("\nLoading corpus...")
    corpus = load_corpus()
    print(f"  Loaded {len(corpus)} pieces")
    
    # 1. Term frequencies
    print("\n" + "=" * 70)
    print("  1. The 40 most common content words in the canon")
    print("=" * 70)
    top_terms = term_frequencies(corpus, n=40)
    for word, n in top_terms:
        bar = "█" * min(50, n // 50)
        print(f"  {word:<18s} {n:>6d}  {bar}")
    
    # 2. Co-occurrences
    print("\n" + "=" * 70)
    print("  2. The 30 most common word pairs (which ideas appear together?)")
    print("=" * 70)
    pairs = co_occurrences(corpus, top_terms)
    for (w1, w2), n in pairs:
        print(f"  {w1} + {w2}: {n}")
    
    # 3. Per-tier vocabulary
    print("\n" + "=" * 70)
    print("  3. Vocabulary by canon type (what each type talks about)")
    print("=" * 70)
    tier_vocab = tier_vocabulary(corpus, n=10)
    for type_, words in tier_vocab.items():
        top = ", ".join(f"{w} ({n})" for w, n in words[:8])
        print(f"  {type_}: {top}")
    
    # 4. Cowboy patterns
    print("\n" + "=" * 70)
    print("  4. The cowboy's signature phrases (how often the cowboy rides)")
    print("=" * 70)
    patterns, samples = cowboy_patterns(corpus)
    for motif, n in patterns:
        bar = "█" * min(40, n // 5)
        print(f"  {motif:<25s} {n:>4d}  {bar}")
    
    # 5. The 5/5/5
    print("\n" + "=" * 70)
    print("  5. The 5 opcodes, 5 laws, 5 tiers (how canonical are they?)")
    print("=" * 70)
    five = five_counts(corpus)
    print("  Opcodes:")
    for op, n in five["opcodes"]:
        print(f"    {op:<8s}: {n}")
    print("  Laws:")
    for law, n in five["laws"]:
        print(f"    {law:<22s}: {n}")
    print("  Tiers:")
    for tier, n in five["tiers"]:
        print(f"    {tier:<14s}: {n}")
    
    # 6. Length distribution
    print("\n" + "=" * 70)
    print("  6. Length distribution (how long are the canon pieces?)")
    print("=" * 70)
    stats = length_distribution(corpus)
    for type_, s in stats.items():
        print(f"  {type_}: count={s['count']}, min={s['min']}, mean={s['mean']}, "
              f"median={s['median']}, max={s['max']}")
    
    # 7. Gaps
    print("\n" + "=" * 70)
    print("  7. Gaps: terms mentioned a lot but rarely defined")
    print("=" * 70)
    gaps = find_gaps(corpus, top_terms)
    for term, n_mentioned, n_defined in gaps:
        print(f"  {term:<20s} mentioned {n_mentioned}x, defined {n_defined}x")
    
    print("\n" + "=" * 70)
    print("  The bedrock (the actual hidden structure)")
    print("=" * 70)
    print()
    print("  What the canon ACTUALLY says (not what the cowboy wishes):")
    print(f"    - {len(corpus)} pieces, {sum(s['count'] for s in stats.values())} words total")
    print(f"    - The cowboy's voice: {sum(n for _, n in patterns)} motif hits")
    print(f"    - The 5 opcodes: {sum(n for _, n in five['opcodes'])} total mentions")
    print(f"    - The 5 laws: {sum(n for _, n in five['laws'])} total mentions")
    print(f"    - The 5 tiers: {sum(n for _, n in five['tiers'])} total mentions")
    print()
    print("  The gaps are where the canon is silent. The cowboy's job")
    print("  is to fill the gaps. The bedrock isn't the cell — the")
    print("  bedrock is what's missing.")
    print()


if __name__ == "__main__":
    main()
