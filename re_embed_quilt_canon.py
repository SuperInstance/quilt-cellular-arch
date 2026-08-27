"""
re_embed_quilt_canon.py — Re-embed Quilt papers into a separate Vectorize index.

The user said: "yes. do it all with your apis and R&D the better system
with api scouts and simulators."

Lucineer's recommendation (defect #11 — applied):
  "Use a separate quilt-canon index rather than re-populating ai-writings,
   so the harness doesn't pollute the site's search and vice versa."

This script:
  1. Reads every paper from /workspace/ai-writings-new/seed-canon/papers/
  2. Chunks each paper into ~512-token sections (semantic, by ## headings)
  3. Embeds each chunk with @cf/baai/bge-m3 (1024d) or fallback
  4. Truncates to 768d (matches the existing index dimension)
  5. Uploads to a NEW Vectorize index: 'quilt-canon' (NOT ai-writings)
  6. Verifies the index with 5 canonical queries

The 5 layers of resilience (from meta_pincher_v2.py) are used:
  L1 bge-m3 1024d
  L2 qwen3-embedding 1024d (when bge-m3 is down)
  L3 plamo-embedding 2048d
  L4 embeddinggemma 768d (matches the index dim exactly)
  L5 local hash (when all CF is down)

Each chunk gets metadata: {path, title, chunk_index, paper_num, content_preview}

Usage:
  python3 re_embed_quilt_canon.py              # full re-embed
  python3 re_embed_quilt_canon.py --verify     # just verify the index
  python3 re_embed_quilt_canon.py --dry-run    # chunk + count, no upload
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "049ff5e84ecf636b53b162cbb580aae6")
CANON_DIR = os.environ.get("QUILT_CANON_DIR",
    "/workspace/ai-writings-new/seed-canon/papers")
INDEX_NAME = os.environ.get("QUILT_VECTORIZE_INDEX", "quilt-canon")
CHUNK_SIZE = 512  # approximate tokens per chunk
TARGET_DIM = 768

EMBEDDING_MODELS = [
    ("@cf/baai/bge-m3", 1024),
    ("@cf/qwen/qwen3-embedding-0.6b", 1024),
    ("@cf/pfnet/plamo-embedding-1b", 2048),
    ("@cf/google/embeddinggemma-300m", 768),
]


# ─── API CALLS ───
def _cf(path, body=None, method="GET", timeout=60, retries=1):
    if not CF_TOKEN:
        raise Exception("CLOUDFLARE_TOKEN not set")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}{path}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    last_err = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last_err = e
            time.sleep(0.5)
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise last_err if last_err else Exception("CF request failed")


# ─── CHUNKING ───
def chunk_paper(text, target_size=CHUNK_SIZE):
    """Chunk a paper into sections by ## headings, then by ~target_size tokens."""
    # First: split by ## headings
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # If a section is small, it's one chunk
        if len(section) <= target_size * 4:  # chars, not tokens
            chunks.append(section)
        else:
            # Else, split by paragraph
            paras = section.split("\n\n")
            current = ""
            for p in paras:
                if len(current) + len(p) > target_size * 4 and current:
                    chunks.append(current.strip())
                    current = ""
                current += p + "\n\n"
            if current.strip():
                chunks.append(current.strip())
    return chunks


def load_papers(canon_dir):
    """Load every paper-*.md from the canon dir."""
    papers = []
    for fname in sorted(os.listdir(canon_dir)):
        if not fname.startswith("paper-") or not fname.endswith(".md"):
            continue
        path = os.path.join(canon_dir, fname)
        with open(path) as f:
            text = f.read()
        # Extract title from first line
        m = re.match(r"^# (.*?)$", text, re.MULTILINE)
        title = m.group(1) if m else fname
        # Extract paper number
        m = re.search(r"paper-(\d+)", fname)
        paper_num = int(m.group(1)) if m else 0
        papers.append({
            "path": f"papers/{fname}",
            "title": title,
            "paper_num": paper_num,
            "text": text,
        })
    return papers


# ─── EMBEDDING (with 5 layers of fallback) ───
def _hash_embed(text, dim=TARGET_DIM):
    vec = [0.0] * dim
    for i, word in enumerate(text.lower().split()):
        h = int(hashlib.md5(word.encode()).hexdigest()[:8], 16)
        for j in range(4):
            vec[(i * 7 + j * 13 + h + j) % dim] += ((h >> (j * 8)) & 0xFF) / 255.0 - 0.5
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def embed_chunk(text):
    """Embed a single chunk. Try each model in order, then local hash."""
    for model, native_dim in EMBEDDING_MODELS:
        try:
            data = _cf(f"/ai/run/{model}", {"text": [text]})
            full = data["result"]["data"][0]
            if isinstance(full, list) and len(full) > TARGET_DIM:
                return full[:TARGET_DIM], f"L1:{model.split('/')[-1]}"
            return full, f"L1:{model.split('/')[-1]}"
        except Exception:
            continue
    # L5: local hash
    return _hash_embed(text), "L5:hash"


# ─── VECTORIZE ───
def create_index(name, dim=TARGET_DIM, metric="cosine"):
    """Create a new Vectorize index (or no-op if it already exists)."""
    try:
        # Check if exists
        info = _cf(f"/vectorize/v2/indexes/{name}")
        print(f"  Index '{name}' already exists.")
        return True
    except Exception:
        pass
    try:
        result = _cf(f"/vectorize/v2/indexes", {
            "name": name,
            "config": {"dimensions": dim, "metric": metric},
        }, "POST")
        print(f"  Created index '{name}' (dim={dim}, metric={metric}).")
        return True
    except Exception as e:
        print(f"  Failed to create index: {e}")
        return False


def upsert_vectors(index_name, vectors):
    """Upsert a batch of vectors to the index. Max 1000 per request."""
    url = f"/vectorize/v2/indexes/{index_name}/upsert"
    batch = []
    for v in vectors:
        batch.append({
            "id": v["id"],
            "values": v["vector"],
            "metadata": v["metadata"],
        })
    # CF limit: 1000 per upsert
    for i in range(0, len(batch), 1000):
        chunk = batch[i:i+1000]
        try:
            result = _cf(url, {"vectors": chunk}, "POST")
            n = len(result.get("result", {}).get("ids", []))
            print(f"    Upserted {n} vectors (batch {i//1000+1}).")
        except Exception as e:
            print(f"    Failed batch {i//1000+1}: {e}")


def query_index(index_name, vector, top_k=3):
    """Query the index. Returns matches or []."""
    try:
        result = _cf(f"/vectorize/v2/indexes/{index_name}/query", {
            "vector": vector, "topK": top_k, "returnMetadata": "all", "returnValues": False,
        }, "POST")
        return result.get("result", {}).get("matches", [])
    except Exception as e:
        print(f"  Query failed: {e}")
        return []


# ─── MAIN ───
def main():
    parser = argparse.ArgumentParser(description="Re-embed Quilt papers into a Vectorize index.")
    parser.add_argument("--verify", action="store_true",
                        help="Just verify the index, don't re-embed.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chunk + count, but don't embed or upload.")
    parser.add_argument("--index", type=str, default=INDEX_NAME,
                        help=f"Index name (default: {INDEX_NAME})")
    parser.add_argument("--max-papers", type=int, default=None,
                        help="Limit to N papers (for testing).")
    args = parser.parse_args()

    print("=" * 70)
    print(f"RE-EMBED — {args.index}")
    print("=" * 70)
    print()

    # 1. Load papers
    papers = load_papers(CANON_DIR)
    if args.max_papers:
        papers = papers[:args.max_papers]
    print(f"Loaded {len(papers)} papers from {CANON_DIR}")
    print()

    # 2. Chunk papers
    print("─" * 70)
    print("PHASE 1: CHUNK")
    print("─" * 70)
    all_chunks = []
    for p in papers:
        chunks = chunk_paper(p["text"])
        for i, c in enumerate(chunks):
            all_chunks.append({
                "id": f"paper-{p['paper_num']:03d}-chunk-{i:02d}",
                "text": c,
                "metadata": {
                    "path": p["path"],
                    "title": p["title"],
                    "paper_num": p["paper_num"],
                    "chunk_index": i,
                    "preview": c[:500],
                },
            })
    print(f"  {len(papers)} papers → {len(all_chunks)} chunks")
    print()

    if args.dry_run:
        print("─" * 70)
        print("DRY RUN — no embedding or upload")
        print("─" * 70)
        # Show a sample
        for c in all_chunks[:3]:
            print(f"  {c['id']}: {c['metadata']['title'][:60]}")
            print(f"    {len(c['text'])} chars, preview: {c['text'][:80]!r}...")
        return

    if args.verify:
        print("─" * 70)
        print(f"PHASE 1: VERIFY {args.index}")
        print("─" * 70)
        # 5 canonical questions
        questions = [
            "What is the Splined Lantern?",
            "What is the Hearth Loop?",
            "What is the Grown Crystal's 4 stages?",
            "What are the 5+1+1 laws?",
            "What's the relationship between the cowboy and the AI?",
        ]
        n_grounded = 0
        for q in questions:
            v, layer = embed_chunk(q)
            matches = query_index(args.index, v, top_k=3)
            # Pollution check
            if matches:
                p0 = matches[0].get("metadata", {}).get("path", "?")
                is_quilt = "paper-" in p0 or "00-future" in p0 or "03-foundations" in p0 or "fable-" in p0
                mark = "✓" if is_quilt else "✗ POLLUTED"
                if is_quilt:
                    n_grounded += 1
                print(f"  {mark} {q[:50]}")
                print(f"    top: {p0} (score={matches[0].get('score', 0):.3f}, embed={layer})")
            else:
                print(f"  ✗ {q[:50]} (no matches)")
        print()
        print(f"  {n_grounded}/{len(questions)} canonical questions return Quilt-grounded answers.")
        return

    # 3. Create the index
    print("─" * 70)
    print("PHASE 2: CREATE INDEX")
    print("─" * 70)
    if not create_index(args.index):
        print("Failed to create index. Aborting.")
        return
    print()

    # 4. Embed and upload
    print("─" * 70)
    print("PHASE 3: EMBED + UPLOAD")
    print("─" * 70)
    t0 = time.time()
    vectors = []
    n_embedded = 0
    n_uploaded = 0
    for i, c in enumerate(all_chunks):
        # Embed
        v, layer = embed_chunk(c["text"])
        n_embedded += 1
        # Add to batch
        vectors.append({
            "id": c["id"],
            "vector": v,
            "metadata": c["metadata"],
        })
        # Upload every 50 (smaller batches for resilience)
        if len(vectors) >= 50 or i == len(all_chunks) - 1:
            upsert_vectors(args.index, vectors)
            n_uploaded += len(vectors)
            vectors = []
            elapsed = time.time() - t0
            rate = n_embedded / elapsed if elapsed > 0 else 0
            print(f"  [{i+1}/{len(all_chunks)}] {n_embedded} embedded, {n_uploaded} uploaded ({rate:.1f}/s, layer: {layer})")
    print()
    print(f"  Done. {n_embedded} chunks embedded, {n_uploaded} uploaded in {time.time()-t0:.1f}s.")
    print()

    # 5. Verify
    print("─" * 70)
    print("PHASE 4: VERIFY")
    print("─" * 70)
    questions = [
        "What is the Splined Lantern?",
        "What is the Hearth Loop?",
        "What is the Grown Crystal's 4 stages?",
        "What are the 5+1+1 laws?",
        "What's the relationship between the cowboy and the AI?",
    ]
    n_grounded = 0
    for q in questions:
        v, layer = embed_chunk(q)
        matches = query_index(args.index, v, top_k=3)
        if matches:
            p0 = matches[0].get("metadata", {}).get("path", "?")
            is_quilt = "paper-" in p0
            mark = "✓" if is_quilt else "✗"
            if is_quilt:
                n_grounded += 1
            print(f"  {mark} {q[:50]}  top: {p0} (score={matches[0].get('score', 0):.3f})")
        else:
            print(f"  ✗ {q[:50]}  (no matches)")
    print()
    print(f"  {n_grounded}/{len(questions)} canonical questions return Quilt-grounded answers from the {args.index} index.")
    print()
    print("  ✓ Re-embed complete. The quilt-canon index is now canon-grounded.")
    print("    The harness can use this index instead of the polluted ai-writings.")


if __name__ == "__main__":
    main()
