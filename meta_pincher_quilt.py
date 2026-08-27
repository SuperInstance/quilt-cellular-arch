"""
meta_pincher_quilt.py — The Meta-Pincher-Quilt.

A vectorized, stateless, Cloudflare-native agent for canon-grounded responses.

The cowboy asked: "could this be vectorized on cloudflare to make
superintelligent-for-the-concepts-processed stateless cloudflare agents-
almost like a meta-pincher-quilt or something"

The Meta-Pincher-Quilt is:
  - STATELESS: no agent carries state; state is in the vector index
  - VECTORIZED: the canon is embedded and retrieved by similarity
  - CLOUDFLARE-NATIVE: runs on Workers + Vectorize + Workers AI
  - SUPERINTELLIGENT-FOR-THE-CONCEPTS: agents are grounded in the canon
  - META-PINCHER: like the F/V EILEEN loop's Pincher (<50ms reflex),
    but for concepts (sub-200ms)

The 3-stage pipeline:
  1. EMBED: encode the query with @cf/baai/bge-base-en-v1.5 (768d)
  2. RETRIEVE: query the ai-writings vector index for top-K canon chunks
  3. SYNTHESIZE: feed the top-K chunks + the query to a Workers AI model,
                  return the grounded response

Free tier: all 3 stages run on Cloudflare's free tier.

The Quilt Codex is the canon. The Dynamic Matrix is the substrate.
The Cosmic Lattice is the index. The Meta-Pincher-Quilt rides it.
"""
import json
import os
import time
import urllib.error
import urllib.request

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT_ID = "049ff5e84ecf636b53b162cbb580aae6"  # from CF_TOKEN

VOICES = {
    "llama33": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "llama8b": "@cf/meta/llama-3.1-8b-instruct-fp8",
    "mistral31": "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "qwen32b": "@cf/qwen/qwen2.5-coder-32b-instruct",
    "qwen3": "@cf/qwen/qwen3.8-27b",
    "gemma4": "@cf/google/gemma-4-26b-a4b-it",
    "kimi": "@cf/moonshotai/kimi-k2.7-code",
}


def _cf_request(path, body=None, method="GET", timeout=90, retries=2):
    """Make a request to Cloudflare API. With retry on 400/503/timeout.

    Note: 400s can be transient (model loading, quota) so we retry once.
    Heavy use of CF free tier triggers 400s even on retry, so we keep
    retries low.
    """
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
            time.sleep(2 ** attempt)  # 1s, 2s
    if hasattr(last_err, 'read'):
        try:
            body_msg = last_err.read().decode()[:500]
        except Exception:
            body_msg = "<can't read body>"
        raise Exception(f"CF request failed after {retries} retries: "
                        f"HTTP {last_err.code if hasattr(last_err, 'code') else '?'} "
                        f"body={body_msg} path={path}")
    raise last_err


def embed(text, model="@cf/baai/bge-m3"):
    """Embed a query using Workers AI.

    Returns: list of 1024 floats (bge-m3 default).
    Note: bge-base/bge-small/embeddinggemma are 400ing on this account
    due to rate limiting. bge-m3 and qwen3-embedding work.

    The ai-writings Vectorize index is 768d, so for production we
    would either (a) re-index with 1024d, or (b) truncate the query
    vector to 768d. For the demo, we attempt (b) and document the loss.
    """
    with _cf_request(f"/ai/run/{model}", {"text": [text]}) as r:
        data = json.load(r)
    full = data["result"]["data"][0]
    # Truncate to 768d (lossy but compatible with the index)
    if isinstance(full, list) and len(full) > 768:
        return full[:768]
    return full


def retrieve(vector, index="ai-writings", top_k=5):
    """Retrieve top-K canon chunks from a Vectorize index.

    Returns: list of {id, score, path, title, preview, ...}
    """
    body = {
        "vector": vector,
        "topK": top_k,
        "returnMetadata": "all",
        "returnValues": False,
    }
    with _cf_request(f"/vectorize/v2/indexes/{index}/query", body, "POST") as r:
        data = json.load(r)
    return data.get("result", {}).get("matches", [])


def synthesize(query, matches, model="llama8b", max_tokens=512):
    """Synthesize a grounded response from the top-K matches.

    The matches are passed as context to a Workers AI model.
    Returns: the synthesized response.
    """
    # Build the context: concatenate the previews of the top matches
    context_parts = []
    for i, m in enumerate(matches, 1):
        meta = m.get("metadata", {})
        path = meta.get("path", "?")
        preview = meta.get("preview", "")
        title = meta.get("title", "")
        context_parts.append(f"[Canon {i} — {title} ({path})]\n{preview[:600]}")
    context = "\n\n".join(context_parts)
    system = (
        "You are a meta-pincher of the Quilt canon. You answer questions "
        "grounded in the canon excerpts provided. Be brief, specific, and "
        "use the canon's vocabulary (Quilt, cell, opcodes, tiers, etc.). "
        "Cite the canon by path when relevant."
    )
    user = f"Canon excerpts:\n{context}\n\nQuestion: {query}"
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


def ask(query, top_k=5, model="llama8b", index="ai-writings", verbose=True):
    """The full Meta-Pincher-Quilt pipeline.

    1. Embed the query
    2. Retrieve top-K canon chunks
    3. Synthesize a grounded response

    Returns: dict with the response, the matches used, and timing.
    """
    t0 = time.time()
    # 1. EMBED
    vector = embed(query)
    t_embed = time.time()
    # 2. RETRIEVE
    matches = retrieve(vector, index=index, top_k=top_k)
    t_retrieve = time.time()
    # 3. SYNTHESIZE
    response = synthesize(query, matches, model=model)
    t_synthesize = time.time()
    if verbose:
        print(f"  embed:     {t_embed-t0:.3f}s")
        print(f"  retrieve:  {t_retrieve-t_embed:.3f}s ({len(matches)} matches)")
        print(f"  synthesize:{t_synthesize-t_retrieve:.3f}s")
    return {
        "query": query,
        "response": response,
        "matches": matches,
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
    print("THE META-PINCHER-QUILT — a vectorized stateless agent")
    print("=" * 70)
    print()
    print("The cowboy asked: 'could this be vectorized on cloudflare to")
    print("make superintelligent-for-the-concepts-processed stateless")
    print("cloudflare agents - almost like a meta-pincher-quilt?'")
    print()
    print("Architecture:")
    print("  Query -> Embed (bge-m3, 1024d, truncated to 768)")
    print("       -> Retrieve (Vectorize: ai-writings, top-K)")
    print("       -> Synthesize (Workers AI, canon-grounded)")
    print()
    print("Try some canon-grounded questions:")
    print()

    questions = [
        "What is the Splined Lantern?",
        "What is the Hearth Loop?",
        "What is the Grown Crystal's 4 stages?",
        "What's the relationship between the cowboy and the AI?",
        "What are the 5+1+1 laws?",
    ]

    for q in questions:
        print(f"Q: {q}")
        try:
            r = ask(q, top_k=3, model="llama8b")
            print(f"A: {r['response'][:400]}")
            print(f"   (total: {r['timing']['total']:.2f}s, "
                  f"top match: {r['matches'][0]['metadata'].get('path', '?') if r['matches'] else 'none'})")
        except Exception as e:
            print(f"A: [error: {e}]")
        print()
        time.sleep(5)  # be nice to the rate limiter
