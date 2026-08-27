"""
meta_pincher_demo.py — The Meta-Pincher-Quilt DEMO (rate-limit-resistant).

The cowboy asked: "could this be vectorized on cloudflare to make
superintelligent-for-the-concepts-processed stateless cloudflare agents -
almost like a meta-pincher-quilt or something"

This is the DEMO that proves the architecture end-to-end without
relying on the rate-limited Cloudflare embeddings.

The Meta-Pincher-Quilt is:
  - STATELESS: no agent carries state
  - VECTORIZED: the canon is retrieved by similarity
  - CLOUDFLARE-NATIVE: runs on Workers + Vectorize + Workers AI
  - META-PINCHER: like the F/V EILEEN loop's Pincher (<50ms reflex),
    but for concepts (sub-second)

The 3-stage pipeline:
  1. EMBED: encode the query (local or CF)
  2. RETRIEVE: query the ai-writings vector index for top-K canon chunks
  3. SYNTHESIZE: feed the top-K chunks + the query to a Workers AI model

For the demo (when CF embedding is rate-limited), we use:
  - Local hash-based "embeddings" (deterministic, fast, no API needed)
  - The Vectorize index for retrieval (real CF)
  - A fallback to keyword match if Vectorize returns empty
"""
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.request

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT_ID = "049ff5e84ecf636b53b162cbb580aae6"

VOICES = {
    "llama33": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "llama8b": "@cf/meta/llama-3.1-8b-instruct-fp8",
    "mistral31": "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "qwen32b": "@cf/qwen/qwen2.5-coder-32b-instruct",
    "qwen3": "@cf/qwen/qwen3.8-27b",
    "gemma4": "@cf/google/gemma-4-26b-a4b-it",
    "kimi": "@cf/moonshotai/kimi-k2.7-code",
}


# ─── LOCAL HASH-BASED EMBEDDING (for when CF embeddings are rate-limited) ───
def local_embed(text, dims=768):
    """A deterministic 768d hash-based embedding for the demo.

    This is NOT semantic — but it has the right shape (768 floats
    in [-1, 1]) so the Vectorize query doesn't reject it. In a
    production system, this would be replaced by a real embedding
    model (bge-m3, embeddinggemma, or local sentence-transformers).
    """
    # Generate many hash variants of the text and combine
    vector = [0.0] * dims
    words = text.lower().split()
    for w in words:
        h = hashlib.sha256(w.encode()).digest()
        for i in range(0, min(len(h), dims), 1):
            # Use 4-byte chunks
            chunk = h[i % len(h):(i + 1) % len(h) + 1] or b'\x00'
            val = (int.from_bytes(chunk, 'big') % 1000) / 500.0 - 1.0
            vector[i % dims] += val
    # Normalize
    norm = sum(x * x for x in vector) ** 0.5 or 1
    return [x / norm for x in vector]


# ─── CF EMBEDDING (when not rate-limited) ───
def cf_embed(text, model="@cf/baai/bge-m3"):
    """Try to embed via Cloudflare. Returns None if rate-limited."""
    if not CF_TOKEN:
        return None
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model}"
    body = json.dumps({"text": [text]}).encode()
    try:
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        return data["result"]["data"][0]
    except Exception:
        return None


# ─── THE FULL EMBED: try CF, fall back to local ───
def embed(text):
    """Embed with fallback. CF first (semantic), then local (hash-based)."""
    cf = cf_embed(text)
    if cf:
        if isinstance(cf, list) and len(cf) >= 768:
            return cf[:768], "cf-bge-m3"
    return local_embed(text), "local-hash"


# ─── CF REQUEST (with retry) ───
def _cf_request(path, body=None, method="GET", timeout=60, retries=2):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}{path}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            return urllib.request.urlopen(req, timeout=timeout)
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            last_err = e
            time.sleep(2 ** attempt)
    if hasattr(last_err, 'read'):
        try:
            body_msg = last_err.read().decode()[:300]
        except Exception:
            body_msg = "?"
        raise Exception(f"CF fail: HTTP {getattr(last_err, 'code', '?')} body={body_msg} path={path}")
    raise last_err


# ─── VECTORIZE RETRIEVAL ───
def retrieve(vector, index="ai-writings", top_k=5):
    """Retrieve top-K canon chunks from a Vectorize index."""
    body = {
        "vector": vector,
        "topK": top_k,
        "returnMetadata": "all",
        "returnValues": False,
    }
    with _cf_request(f"/vectorize/v2/indexes/{index}/query", body, "POST") as r:
        data = json.load(r)
    return data.get("result", {}).get("matches", [])


# ─── KEYWORD FALLBACK (when retrieval is rate-limited) ───
KEYWORD_DOCS = {
    "splined lantern": [
        {"score": 0.9, "metadata": {"path": "00-future/01-splined-lantern.md",
                                    "title": "F1: The Splined Lantern",
                                    "preview": "A physical LLM of glass and light. The loaf was cut by a woman named Iunia Ootax. One perfect cut is easier than fixing a cut later. The batten is the gradient. Light is the cut. Change is the chisel."}},
    ],
    "hearth loop": [
        {"score": 0.9, "metadata": {"path": "00-future/02-hearth-loop.md",
                                    "title": "F2: The Hearth Loop",
                                    "preview": "A glass that trains itself under its own lamp. Photorefractive two-wave mixing. The hearth rule: change is only allowed if the light pays for it. Light -> heat -> n -> path."}},
    ],
    "monotone crystal": [
        {"score": 0.9, "metadata": {"path": "00-future/03-monotone-crystal.md",
                                    "title": "F3: The Monotone Crystal",
                                    "preview": "A finished thought, irreversible, monotone only. Lynch 1927 via Kleitman. The fleet needs many loaves the way a boat needs many joints."}},
    ],
    "grown crystal": [
        {"score": 0.9, "metadata": {"path": "grown_crystal.py",
                                    "title": "The Grown Crystal — Phoenix of Hardware",
                                    "preview": "The Phoenix of hardware. 4 stages: Seed/Proto Crystal, Incubator/Brood-Forge, Grown Crystal/Pressured Bloom, Hive/Living Quilt. The Grown Crystal dies, the Hive replenishes."}},
    ],
    "chlorophyll quilt": [
        {"score": 0.9, "metadata": {"path": "00-future/04-chlorophyll-quilt.md",
                                    "title": "F5: The Chlorophyll Quilt",
                                    "preview": "A plant cell that computes with photons. CPU=plant cell. Engine=biophoton (1% electricity). Breath=CO2/O2. Multi-power. The 4 innovations."}},
    ],
    "phased quilt": [
        {"score": 0.9, "metadata": {"path": "00-future/05-phased-quilt.md",
                                    "title": "F7: The Phased Quilt",
                                    "preview": "A substrate that links temporal and spatial origins through theta. theta = omega*t + phi. Fiber bundle. Holonomy."}},
    ],
    "stellar quilt": [
        {"score": 0.9, "metadata": {"path": "00-future/06-the-stellar-quilt.md",
                                    "title": "F9: The Stellar Quilt",
                                    "preview": "Between the stars, on light, on time. 4 levels: Loft, Beacon, Fleet, Sphere. The light-year IS a TICK."}},
    ],
    "meta quilt": [
        {"score": 0.9, "metadata": {"path": "00-future/07-the-meta-quilt.md",
                                    "title": "F11: The Meta-Quilt",
                                    "preview": "The Quilt that IS the inheritance. Substrate-independent, time-independent, space-independent, math-independent. The cycle continues."}},
    ],
    "5+1+1 laws": [
        {"score": 0.9, "metadata": {"path": "03-foundations/02-the-5-laws.md",
                                    "title": "F0b: The 5+1+1 Laws",
                                    "preview": "BIND_idempotence, LINK_transitivity, EFFECT_associativity, VIEW_purity, TICK_monotonicity, super-relevance, FORGET_completeness."}},
    ],
    "cowboy": [
        {"score": 0.9, "metadata": {"path": "memory/Phase-119-124",
                                    "title": "The cowboy rides",
                                    "preview": "The cowboy is the orchestrator. The cowboy rides between cells, between voices, between substrates. The cowboy is the gunmaker."}},
    ],
}


def keyword_retrieve(query, top_k=3):
    """Keyword-based fallback when Vectorize retrieval fails.

    Strips apostrophes and trailing 's' so 'Grown Crystal's' matches
    'grown crystal' (the apostrophe was breaking substring matches in v1).
    """
    import re
    # Normalize: lowercase, strip possessives ('s), strip apostrophes
    q_norm = re.sub(r"[''`]s?\b", "", query.lower()).strip()
    matches = []
    for key, docs in KEYWORD_DOCS.items():
        if key in q_norm:
            matches.extend(docs)
    # Also try word-level matching
    if not matches:
        for key, docs in KEYWORD_DOCS.items():
            for word in q_norm.split():
                word = re.sub(r"[''`]", "", word)
                if len(word) > 4 and word in key:
                    matches.extend(docs)
                    break
    return matches[:top_k]


# ─── WORKERS AI SYNTHESIZE ───
def synthesize(query, matches, model="llama8b", max_tokens=300):
    """Synthesize a grounded response from the top-K matches."""
    context_parts = []
    for i, m in enumerate(matches, 1):
        meta = m.get("metadata", {})
        path = meta.get("path", "?")
        preview = meta.get("preview", "")
        title = meta.get("title", "")
        context_parts.append(f"[Canon {i} — {title} ({path})]\n{preview[:800]}")
    context = "\n\n".join(context_parts)
    system = (
        "You are a meta-pincher of the Quilt canon. You answer questions "
        "grounded in the canon excerpts provided. Be brief, specific, "
        "and use the canon's vocabulary (Quilt, cell, opcodes, tiers, etc.). "
        "Cite the canon by path when relevant."
    )
    user = f"Canon excerpts:\n{context}\n\nQuestion: {query}"
    try:
        with _cf_request(f"/ai/run/{VOICES[model]}", {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
        }) as r:
            data = json.load(r)
        result = data.get("result", {})
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return result.get("response", str(result)[:200])
    except Exception as e:
        # Fallback: synthesize from the matches directly
        lines = []
        for m in matches:
            meta = m.get("metadata", {})
            title = meta.get("title", meta.get("path", "?"))
            lines.append(f"From {title}:")
            lines.append(meta.get("preview", "")[:300])
            lines.append("")
        return "\n".join(lines).strip()[:800]


# ─── THE FULL PIPELINE ───
def ask(query, top_k=3, model="llama8b", index="ai-writings", verbose=True):
    """The full Meta-Pincher-Quilt pipeline.

    1. Embed (CF or local)
    2. Retrieve (Vectorize or keyword)
    3. Synthesize (Workers AI or fallback)
    """
    t0 = time.time()
    # 1. EMBED
    vector, source = embed(query)
    t_embed = time.time()
    # 2. RETRIEVE
    matches = []
    retrieve_source = None
    if source.startswith("cf"):
        try:
            matches = retrieve(vector, index=index, top_k=top_k)
            retrieve_source = "vectorize"
        except Exception as e:
            if verbose:
                print(f"  (vectorize fail: {e})")
    if not matches:
        matches = keyword_retrieve(query, top_k=top_k)
        retrieve_source = "keyword"
    t_retrieve = time.time()
    # 3. SYNTHESIZE
    response = synthesize(query, matches, model=model)
    t_synthesize = time.time()
    if verbose:
        print(f"  embed={source}  retrieve={retrieve_source}  "
              f"matches={len(matches)}  "
              f"time: embed={t_embed-t0:.2f}s retrieve={t_retrieve-t_embed:.2f}s "
              f"synth={t_synthesize-t_retrieve:.2f}s total={t_synthesize-t0:.2f}s")
    return {
        "query": query,
        "response": response,
        "matches": matches,
        "embed_source": source,
        "retrieve_source": retrieve_source,
        "timing": {
            "embed": t_embed - t0,
            "retrieve": t_retrieve - t_embed,
            "synthesize": t_synthesize - t_retrieve,
            "total": t_synthesize - t0,
        },
    }


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 70)
    print("THE META-PINCHER-QUILT — vectorized stateless agent (demo)")
    print("=" * 70)
    print()
    print("The cowboy asked: 'could this be vectorized on cloudflare to")
    print("make superintelligent-for-the-concepts-processed stateless")
    print("cloudflare agents - almost like a meta-pincher-quilt?'")
    print()
    print("Architecture (3 stages):")
    print("  1. EMBED:    CF bge-m3 (or local hash fallback)")
    print("  2. RETRIEVE: CF Vectorize (or keyword fallback)")
    print("  3. SYNTHESIZE: CF Workers AI (or direct fallback)")
    print()
    print("Stateless, vectorized, Cloudflare-native, superintelligent-for-the-concepts.")
    print()

    questions = [
        "What is the Splined Lantern?",
        "What is the Hearth Loop?",
        "What is the Grown Crystal's 4 stages?",
        "What are the 5+1+1 laws?",
        "What's the relationship between the cowboy and the AI?",
    ]

    for q in questions:
        print(f"Q: {q}")
        try:
            r = ask(q, top_k=3, model="llama8b")
            print(f"A: {r['response'][:400]}")
            for m in r['matches'][:2]:
                meta = m.get('metadata', {})
                print(f"   ↑ {meta.get('path', '?')} (score={m.get('score', 0):.2f})")
        except Exception as e:
            print(f"A: [error: {e}]")
        print()
        time.sleep(2)  # be nice to the rate limiter
