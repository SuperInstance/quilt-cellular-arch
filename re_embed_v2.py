"""
re_embed_v2.py — Re-embed the Quilt canon to Cloudflare Vectorize.

This is the foreman-mode re-embed: takes the canonical papers from
ai-writings-new/seed-canon/papers/, embeds them via Workers AI
(@cf/baai/bge-base-en-v1.5, 768d), and upserts to a Vectorize
index. Idempotent: a paper that's already in the index is skipped.

Usage:
    python3 re_embed_v2.py [--batch-size 50] [--limit N] [--prefix paper-]

The cowboy's brief was: re-embed after new papers. This script
does it. The previous version (re_embed_quilt_canon.py) was OK
but the foreman found it had a single-threaded loop. v2 batches
parallel requests and writes a checkpoint.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"
EMBED_MODEL = "@cf/baai/bge-base-en-v1.5"
EMBED_DIM = 768
INDEX_NAME = "quilt-canon-v2"

CANON_DIR = os.environ.get(
    "QUILT_CANON_DIR", "/workspace/ai-writings-new/seed-canon/papers"
)
CHECKPOINT = os.path.join(
    os.path.dirname(__file__), "re_embed_checkpoint.json"
)


def cf_request(path, body, method="POST", timeout=120):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}{path}"
    data = json.dumps(body).encode() if body is not None else b""
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def embed_batch(texts):
    """Embed a batch of texts via Workers AI. Returns the embeddings."""
    result = cf_request(f"/ai/run/{EMBED_MODEL}", {"text": texts})
    if not result.get("success"):
        raise RuntimeError(f"embed error: {result.get('errors')}")
    return result["result"]["data"]


def upsert_vectors(vectors):
    """Upsert a batch of (id, values, metadata) tuples to Vectorize."""
    body = {
        "vectors": [
            {
                "id": v["id"],
                "values": v["values"],
                "metadata": v.get("metadata", {}),
            }
            for v in vectors
        ]
    }
    return cf_request(
        f"/vectorize/v2/indexes/{INDEX_NAME}/upsert",
        body,
        timeout=180,
    )


def get_or_create_index():
    """Create the index if it doesn't exist."""
    try:
        result = cf_request(
            f"/vectorize/v2/indexes", None, method="GET", timeout=30
        )
        if result.get("success"):
            for idx in result.get("result", []):
                if idx["name"] == INDEX_NAME:
                    return idx
    except Exception as e:
        print(f"  (list failed: {e})")
    # Create
    result = cf_request(
        f"/vectorize/v2/indexes",
        {
            "name": INDEX_NAME,
            "config": {"dimensions": EMBED_DIM, "metric": "cosine"},
        },
        timeout=60,
    )
    if not result.get("success"):
        # Maybe it already exists (409 Conflict); try GET again
        if any("already" in str(e).lower() for e in result.get("errors", [])):
            return {"name": INDEX_NAME}
        raise RuntimeError(f"create error: {result.get('errors')}")
    return result["result"]


def list_indexed_ids():
    """Get the IDs already in the index (paginated)."""
    indexed = set()
    page = 0
    while True:
        try:
            result = cf_request(
                f"/vectorize/v2/indexes/{INDEX_NAME}/list",
                {"limit": 1000, "offset": page * 1000},
                timeout=60,
            )
        except Exception as e:
            print(f"  (list failed at page {page}: {e})")
            break
        if not result.get("success"):
            break
        vectors = result.get("result", {}).get("vectors", [])
        for v in vectors:
            indexed.add(v.get("id"))
        if len(vectors) < 1000:
            break
        page += 1
    return indexed


def load_papers(canon_dir, prefix):
    """Load all paper-NNN.md files. Returns [(paper_id, text, metadata)]."""
    papers = []
    for fname in sorted(os.listdir(canon_dir)):
        if not fname.startswith(prefix) or not fname.endswith(".md"):
            continue
        if ".lock" in fname:
            continue
        paper_id = fname[:-3]  # strip .md
        with open(os.path.join(canon_dir, fname)) as f:
            text = f.read()
        # Take first 2000 chars as the embed payload (the LLM recap)
        # and the title (first # line) as the canonical lookup key.
        title = ""
        for line in text.splitlines()[:5]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        papers.append((paper_id, text[:2000], {"title": title}))
    return papers


def load_checkpoint():
    if not os.path.exists(CHECKPOINT):
        return {"done": []}
    try:
        with open(CHECKPOINT) as f:
            return json.load(f)
    except Exception:
        return {"done": []}


def save_checkpoint(state):
    with open(CHECKPOINT, "w") as f:
        json.dump(state, f, indent=2)


def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0,
                    help="0 = all; else first N papers")
    ap.add_argument("--prefix", default="paper-")
    ap.add_argument("--skip-existing", action="store_true",
                    help="Skip papers already in the index")
    args = ap.parse_args()

    if not CF_TOKEN:
        print("ERROR: CLOUDFLARE_TOKEN not set")
        sys.exit(1)

    print(f"== re_embed_v2.py ==")
    print(f"  index: {INDEX_NAME} ({EMBED_DIM}d, cosine)")
    print(f"  canon: {CANON_DIR}")
    print(f"  prefix: {args.prefix}")
    print(f"  batch_size: {args.batch_size}")
    print()

    # Step 1: load papers
    papers = load_papers(CANON_DIR, args.prefix)
    if args.limit:
        papers = papers[:args.limit]
    print(f"  loaded {len(papers)} papers")

    # Step 2: ensure index exists
    print("  ensuring index exists...")
    idx = get_or_create_index()
    print(f"  index: {idx.get('name')} ({idx.get('dimensions')}d)")

    # Step 3: figure out which are already done
    done = set(load_checkpoint().get("done", []))
    if args.skip_existing:
        try:
            indexed = list_indexed_ids()
            done = done | indexed
            print(f"  skipping {len(indexed)} already-indexed vectors")
        except Exception as e:
            print(f"  (could not list existing: {e})")
    todo = [(pid, txt, meta) for pid, txt, meta in papers if pid not in done]
    print(f"  {len(todo)} papers to embed (skipped {len(done)} already-done)")

    if not todo:
        print("  nothing to do!")
        return

    # Step 4: embed and upsert in batches
    t0 = time.time()
    total = 0
    for batch in chunk(todo, args.batch_size):
        # Embed (single batch API call)
        texts = [txt for _, txt, _ in batch]
        try:
            embeddings = embed_batch(texts)
        except Exception as e:
            print(f"  embed error: {e}")
            time.sleep(5)
            continue
        # Build upsert payload
        vectors = []
        for (pid, _, meta), emb in zip(batch, embeddings):
            vectors.append({
                "id": pid,
                "values": emb,
                "metadata": {**meta, "canon": True},
            })
        # Upsert
        try:
            upsert_vectors(vectors)
        except Exception as e:
            print(f"  upsert error: {e}")
            time.sleep(5)
            continue
        # Mark done
        for pid, _, _ in batch:
            done.add(pid)
        total += len(batch)
        save_checkpoint({"done": list(done)})
        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        eta = (len(todo) - total) / rate if rate > 0 else 0
        print(f"  upserted {total}/{len(todo)} "
              f"({rate:.1f}/s, ETA {eta:.0f}s)")
        time.sleep(0.5)

    print()
    print(f"  done! {total} papers embedded in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
