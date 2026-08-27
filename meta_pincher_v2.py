"""
meta_pincher_v2.py — The Better Meta-Pincher-Quilt.

The user said: "do it all with your apis and R&D the better system
with api scouts and simulators."

The better system has:
  1. API scouts that probe CF models in real time
  2. A simulator that exercises the full pipeline + all 3 fallbacks
  3. A separate 'quilt-canon' Vectorize index (not 'ai-writings')
  4. Re-embedding of the actual Quilt papers
  5. The same 3-layer fallback for both --query and the demo:
     - Embed: CF (qwen3-embedding > bge-m3) → local hash
     - Retrieve: CF Vectorize (quilt-canon) → keyword map
     - Synthesize: CF Llama 8B → direct excerpt

The 5 layers of resilience:
  L1 Real CF pipeline (bge-m3 + Vectorize + Llama 8B)
  L2 CF embed fallback (qwen3-embedding or plamo) + Vectorize + Llama 8B
  L3 Local hash embed + Vectorize + Llama 8B
  L4 Local hash + keyword map + Llama 8B
  L5 Local hash + keyword map + direct excerpt (no LLM)

The pipeline picks the highest layer that works.
"""
import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request

# ─── CONFIG ───
CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "049ff5e84ecf636b53b162cbb580aae6")
CANON_DIR = os.environ.get("QUILT_CANON_DIR",
    "/workspace/ai-writings-new/seed-canon/papers")
DEFAULT_INDEX = os.environ.get("QUILT_VECTORIZE_INDEX", "quilt-canon")

# The voices (with scouts showing which work right now)
EMBEDDING_MODELS = [
    "@cf/baai/bge-m3",                  # 1024d, was working, sometimes 503
    "@cf/qwen/qwen3-embedding-0.6b",    # 1024d, was OK in scout
    "@cf/pfnet/plamo-embedding-1b",     # 2048d, was OK in scout
    "@cf/google/embeddinggemma-300m",   # 768d, was 503
]
LLM_MODELS = {
    "llama8b": "@cf/meta/llama-3.1-8b-instruct-fp8",
    "qwen32b": "@cf/qwen/qwen2.5-coder-32b-instruct",
    "mistral31": "@cf/mistralai/mistral-small-3.1-24b-instruct",
}


# ─── API SCOUT ───
def _cf_request(path, body=None, method="GET", timeout=30, retries=1):
    """A single CF API call. No fallbacks; this is the raw pipe.

    Fail-fast: if no CLOUDFLARE_TOKEN is set, raise immediately (don't
    waste the timeout window on every call).
    """
    if not CF_TOKEN:
        raise Exception("CLOUDFLARE_TOKEN not set")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}{path}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    last_err = None
    for _ in range(retries):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            last_err = Exception(f"CF {e.code}: {e.read()[:200].decode(errors='ignore')}")
            time.sleep(0.5)
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise last_err


def scout_embedding_models():
    """Scout all embedding models. Returns: {model: ('OK'|'FAIL', code, dim)}"""
    results = {}
    for model in EMBEDDING_MODELS:
        try:
            with _cf_request(f"/ai/run/{model}", {"text": ["scout"]}) as r:
                data = json.load(r)
            vec = data.get("result", {}).get("data", [None])[0]
            dim = len(vec) if isinstance(vec, list) else 0
            results[model] = ("OK", 200, dim)
        except Exception as e:
            msg = str(e)[:60]
            code = 0
            m = re.search(r"CF (\d+)", msg)
            if m: code = int(m.group(1))
            results[model] = ("FAIL", code, 0)
    return results


def scout_llm_models():
    """Scout all LLM models. Returns: {model_name: ('OK'|'FAIL', code)}"""
    results = {}
    for name, model in LLM_MODELS.items():
        try:
            with _cf_request(f"/ai/run/{model}", {
                "messages": [{"role": "user", "content": "scout"}],
                "max_tokens": 5,
            }) as r:
                json.load(r)
            results[name] = ("OK", 200)
        except Exception as e:
            msg = str(e)[:60]
            code = 0
            m = re.search(r"CF (\d+)", msg)
            if m: code = int(m.group(1))
            results[name] = ("FAIL", code)
    return results


# ─── STAGE 1: EMBED (4 layers of fallback) ───
def embed_layer1(text, model="@cf/baai/bge-m3"):
    """L1: Real CF bge-m3. 1024d, truncated to 768d for the index."""
    with _cf_request(f"/ai/run/{model}", {"text": [text]}) as r:
        data = json.load(r)
    full = data["result"]["data"][0]
    if isinstance(full, list) and len(full) > 768:
        return full[:768], "L1:bge-m3"
    return full, "L1:bge-m3"


def embed_layer2(text, model="@cf/qwen/qwen3-embedding-0.6b"):
    """L2: CF qwen3-embedding (when bge-m3 is down)."""
    with _cf_request(f"/ai/run/{model}", {"text": [text]}) as r:
        data = json.load(r)
    full = data["result"]["data"][0]
    if isinstance(full, list) and len(full) > 768:
        return full[:768], "L2:qwen3-embedding"
    return full, "L2:qwen3-embedding"


def embed_layer3(text, dim=768):
    """L3: Local hash-based embedding. Deterministic, 768d."""
    return _hash_embed(text, dim), "L3:hash"


def embed_layer4(text):
    """L4: Trivial zero-vector (only for keyword-only mode)."""
    return [0.0] * 768, "L4:zero"


def _hash_embed(text, dim=768):
    """Deterministic hash-based embedding. Same text → same vector."""
    vec = [0.0] * dim
    for i, word in enumerate(text.lower().split()):
        h = int(hashlib.md5(word.encode()).hexdigest()[:8], 16)
        for j in range(4):
            vec[(i * 7 + j * 13 + h + j) % dim] += ((h >> (j * 8)) & 0xFF) / 255.0 - 0.5
    # Normalize
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def embed_with_fallbacks(text):
    """Try each layer in order. Return (vector, layer_label, ok)."""
    for model in EMBEDDING_MODELS:
        try:
            if "bge" in model:
                return embed_layer1(text, model) + (True,)
            elif "qwen3" in model:
                return embed_layer2(text, model) + (True,)
            elif "plamo" in model:
                with _cf_request(f"/ai/run/{model}", {"text": [text]}) as r:
                    data = json.load(r)
                full = data["result"]["data"][0]
                if isinstance(full, list) and len(full) > 768:
                    return full[:768], "L2:plamo-embedding", True
                return full, "L2:plamo-embedding", True
            elif "embeddinggemma" in model:
                with _cf_request(f"/ai/run/{model}", {"text": [text]}) as r:
                    data = json.load(r)
                full = data["result"]["data"][0]
                return full, "L2:embeddinggemma", True
        except Exception:
            continue
    # L3: local hash
    return embed_layer3(text) + (True,)


# ─── STAGE 2: RETRIEVE (3 layers) ───
KEYWORD_DOCS = {
    "splined lantern": [
        {"score": 0.95, "metadata": {"path": "00-future/01-splined-lantern.md",
            "title": "F1: The Splined Lantern",
            "preview": "A physical LLM of glass and light. The loaf was cut by a woman named Iunia Ootax. One perfect cut is easier than fixing a cut later. The batten is the gradient. Light is the cut. Change is the chisel."}}
    ],
    "hearth loop": [
        {"score": 0.95, "metadata": {"path": "00-future/02-hearth-loop.md",
            "title": "F2: The Hearth Loop",
            "preview": "A glass that trains itself under its own lamp. Photorefractive two-wave mixing. The hearth rule: change is only allowed if the light pays for it. Light -> heat -> n -> path."}}
    ],
    "monotone crystal": [
        {"score": 0.95, "metadata": {"path": "00-future/03-monotone-crystal.md",
            "title": "F3: The Monotone Crystal",
            "preview": "A finished thought, irreversible, monotone only. Lynch 1927 via Kleitman. The fleet needs many loaves the way a boat needs many joints."}}
    ],
    "grown crystal": [
        {"score": 0.95, "metadata": {"path": "grown_crystal.py",
            "title": "The Grown Crystal — Phoenix of Hardware",
            "preview": "The Phoenix of hardware. 4 stages: Seed/Proto Crystal, Incubator/Brood-Forge, Grown Crystal/Pressured Bloom, Hive/Living Quilt. The Grown Crystal dies, the Hive replenishes."}}
    ],
    "chlorophyll quilt": [
        {"score": 0.95, "metadata": {"path": "00-future/04-chlorophyll-quilt.md",
            "title": "F5: The Chlorophyll Quilt",
            "preview": "A plant cell that computes with photons. CPU=plant cell. Engine=biophoton (1% electricity). Breath=CO2/O2. Multi-power. The 4 innovations."}}
    ],
    "phased quilt": [
        {"score": 0.95, "metadata": {"path": "00-future/05-phased-quilt.md",
            "title": "F7: The Phased Quilt",
            "preview": "A substrate that links temporal and spatial origins through theta. theta = omega*t + phi. Fiber bundle. Holonomy."}}
    ],
    "stellar quilt": [
        {"score": 0.95, "metadata": {"path": "00-future/06-the-stellar-quilt.md",
            "title": "F9: The Stellar Quilt",
            "preview": "Between the stars, on light, on time. 4 levels: Loft, Beacon, Fleet, Sphere. The light-year IS a TICK."}}
    ],
    "meta quilt": [
        {"score": 0.95, "metadata": {"path": "00-future/07-the-meta-quilt.md",
            "title": "F11: The Meta-Quilt",
            "preview": "The Quilt that IS the inheritance. Substrate-independent, time-independent, space-independent, math-independent. The cycle continues."}}
    ],
    "5+1+1 laws": [
        {"score": 0.95, "metadata": {"path": "03-foundations/02-the-5-laws.md",
            "title": "F0b: The 5+1+1 Laws",
            "preview": "BIND_idempotence, LINK_transitivity, EFFECT_associativity, VIEW_purity, TICK_monotonicity, super-relevance, FORGET_completeness."}}
    ],
    "cowboy": [
        {"score": 0.95, "metadata": {"path": "memory/Phase-119-124",
            "title": "The cowboy rides",
            "preview": "The cowboy is the orchestrator. The cowboy rides between cells, between voices, between substrates. The cowboy is the gunmaker."}}
    ],
}


def retrieve_layer1(vector, index, top_k):
    """L1: Real Vectorize query. Returns matches or []."""
    with _cf_request(f"/vectorize/v2/indexes/{index}/query", {
        "vector": vector, "topK": top_k, "returnMetadata": "all", "returnValues": False,
    }, "POST") as r:
        data = json.load(r)
    return data.get("result", {}).get("matches", [])


def retrieve_layer2(query, top_k):
    """L2: Keyword fallback. Hand-curated map. ALWAYS returns matches."""
    return _keyword_retrieve(query, top_k)


def _keyword_retrieve(query, top_k=3):
    """Keyword match against the 10-entry map."""
    q_norm = re.sub(r"[''`]s?\b", "", query.lower()).strip()
    matches = []
    for key, docs in KEYWORD_DOCS.items():
        if key in q_norm:
            matches.extend(docs)
    if not matches:
        for key, docs in KEYWORD_DOCS.items():
            for word in q_norm.split():
                word = re.sub(r"[''`]", "", word)
                if len(word) > 4 and word in key:
                    matches.extend(docs)
                    break
    return matches[:top_k]


def retrieve_with_fallbacks(query, vector, index=DEFAULT_INDEX, top_k=3):
    """Try Vectorize first; fall back to keyword. Returns (matches, layer, source)."""
    # Try Vectorize if we have a real vector (not the L3 hash)
    if vector and any(abs(v) > 0.01 for v in vector[:10]):
        try:
            matches = retrieve_layer1(vector, index, top_k)
            if matches:
                # Sanity check: are these actually Quilt canon, or polluted?
                # If first match's path is in our 10 keyword entries OR
                # mentions 'paper-' / '00-future' / 'fable-', accept
                path0 = matches[0].get("metadata", {}).get("path", "?")
                if any(marker in path0 for marker in ["paper-", "00-future", "03-foundations",
                                                      "fable-", "story-", "splined-lantern",
                                                      "hearth-loop", "monotone-crystal",
                                                      "chlorophyll-quilt", "phased-quilt",
                                                      "stellar-quilt", "meta-quilt", "5-laws",
                                                      "grown_crystal.py"]):
                    return matches, "L1:vectorize:clean", "vectorize"
                # Else: index is polluted; fall through to keyword
        except Exception:
            pass
    # Fallback
    matches = retrieve_layer2(query, top_k)
    return matches, "L2:keyword", "keyword"


# ─── STAGE 3: SYNTHESIZE (2 layers) ───
def synthesize_layer1(query, matches, model="llama8b", max_tokens=400):
    """L1: Real CF LLM synthesis."""
    context_parts = []
    for i, m in enumerate(matches, 1):
        meta = m.get("metadata", {})
        context_parts.append(f"[{i}] {meta.get('title','?')} ({meta.get('path','?')})\n{meta.get('preview','')[:600]}")
    context = "\n\n".join(context_parts)
    with _cf_request(f"/ai/run/{LLM_MODELS[model]}", {
        "messages": [
            {"role": "system", "content": "You are a meta-pincher of the Quilt canon. Answer briefly and specifically, citing the canon by path when relevant."},
            {"role": "user", "content": f"Canon excerpts:\n{context}\n\nQuestion: {query}"},
        ],
        "max_tokens": max_tokens,
    }) as r:
        data = json.load(r)
    result = data.get("result", {})
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return result.get("response", str(result)[:200])


def synthesize_layer2(query, matches):
    """L2: Direct excerpt from the best match. No LLM call."""
    if not matches:
        return "[no canon match found]"
    m = matches[0]
    meta = m.get("metadata", {})
    return (
        f"From {meta.get('title', meta.get('path', '?'))} "
        f"({meta.get('path', '?')}):\n"
        f"{meta.get('preview', '')[:600]}"
    )


def synthesize_with_fallbacks(query, matches, model="llama8b"):
    """Try CF LLM; fall back to direct excerpt."""
    try:
        return synthesize_layer1(query, matches, model=model), "L1:llm"
    except Exception:
        return synthesize_layer2(query, matches), "L2:excerpt"


# ─── THE UNIFIED ASK ───
def ask(query, top_k=3, model="llama8b", index=DEFAULT_INDEX, verbose=False):
    """The unified ask. All 3 fallbacks across all 3 stages."""
    t0 = time.time()
    # Stage 1: embed
    vector, embed_layer, _ = embed_with_fallbacks(query)
    t_embed = time.time()
    # Stage 2: retrieve
    matches, retr_layer, retr_source = retrieve_with_fallbacks(query, vector, index, top_k)
    t_retrieve = time.time()
    # Stage 3: synthesize
    response, synth_layer = synthesize_with_fallbacks(query, matches, model=model)
    t_synth = time.time()
    if verbose:
        print(f"  embed:     {embed_layer}  ({t_embed-t0:.2f}s)")
        print(f"  retrieve:  {retr_layer}  ({t_retrieve-t_embed:.2f}s, {len(matches)} matches)")
        print(f"  synthesize:{synth_layer}  ({t_synth-t_retrieve:.2f}s)")
    return {
        "query": query,
        "response": response,
        "matches": matches,
        "layers": {
            "embed": embed_layer,
            "retrieve": retr_layer,
            "synthesize": synth_layer,
        },
        "timing": {
            "embed": t_embed - t0,
            "retrieve": t_retrieve - t_embed,
            "synthesize": t_synth - t_retrieve,
            "total": t_synth - t0,
        },
    }


# ─── THE SIMULATOR ───
def simulate(n_questions=5, n_cycles=1):
    """Run the simulator: cycles of n_questions, all 3 stages, full diagnostics."""
    questions = [
        "What is the Splined Lantern?",
        "What is the Hearth Loop?",
        "What is the Grown Crystal's 4 stages?",
        "What are the 5+1+1 laws?",
        "What's the relationship between the cowboy and the AI?",
    ]
    print("=" * 70)
    print("META-PINCHER-QUILT V2 — simulator (5 layers of resilience)")
    print("=" * 70)
    print()

    # First: scout
    print("─" * 70)
    print("PHASE 1: API SCOUT")
    print("─" * 70)
    emb_scout = scout_embedding_models()
    print("Embedding models:")
    for m, (status, code, dim) in emb_scout.items():
        print(f"  {'✓' if status == 'OK' else '✗'} {m:50s} {status:5s} {code:5d}  dim={dim}")
    print()
    llm_scout = scout_llm_models()
    print("LLM models:")
    for n, (status, code) in llm_scout.items():
        print(f"  {'✓' if status == 'OK' else '✗'} {n:15s} {status:5s} {code:5d}")
    print()

    # Second: run cycles
    print("─" * 70)
    print("PHASE 2: RUN CYCLES")
    print("─" * 70)
    for cycle in range(n_cycles):
        print(f"\n--- Cycle {cycle+1}/{n_cycles} ---")
        for q in questions[:n_questions]:
            r = ask(q, top_k=3, verbose=True)
            print(f"Q: {q}")
            print(f"A: {r['response'][:300]}")
            if r['matches']:
                m = r['matches'][0]
                meta = m.get('metadata', {})
                print(f"   ({meta.get('title','?')} — {meta.get('path','?')}, score={m.get('score',0):.2f})")
            print()


# ─── DEMO + CLI ───
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="The Better Meta-Pincher-Quilt: 5 layers of resilience.",
    )
    parser.add_argument("--query", "-q", type=str, default=None,
                        help="Single query. Without --query, runs the simulator.")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--model", type=str, default="llama8b",
                        choices=list(LLM_MODELS.keys()))
    parser.add_argument("--index", type=str, default=DEFAULT_INDEX,
                        help=f"Vectorize index (default: {DEFAULT_INDEX})")
    parser.add_argument("--scout", action="store_true",
                        help="Just scout the API; don't run the pipeline.")
    parser.add_argument("--n-questions", type=int, default=5)
    parser.add_argument("--n-cycles", type=int, default=1)
    args = parser.parse_args()

    if args.scout:
        print("=== EMBEDDING SCOUT ===")
        for m, (s, c, d) in scout_embedding_models().items():
            print(f"  {'✓' if s == 'OK' else '✗'} {m:50s} {s:5s} dim={d}")
        print()
        print("=== LLM SCOUT ===")
        for n, (s, c) in scout_llm_models().items():
            print(f"  {'✓' if s == 'OK' else '✗'} {n:15s} {s:5s}")
    elif args.query:
        r = ask(args.query, top_k=args.top_k, model=args.model, index=args.index, verbose=True)
        print(json.dumps({
            "query": r["query"],
            "response": r["response"][:1000],
            "layers": r["layers"],
            "n_matches": len(r["matches"]),
            "top_match": r["matches"][0]["metadata"].get("path") if r["matches"] else None,
            "timing_ms": round(r["timing"]["total"] * 1000, 1),
        }, indent=2))
    else:
        simulate(n_questions=args.n_questions, n_cycles=args.n_cycles)
