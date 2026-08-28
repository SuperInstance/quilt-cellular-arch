"""
f15_writers_room.py — The F15 Tessellation Quilt.

The user said: "keep your team moving. use lots of kimi, z.ai and others"

F15 is the Tessellation Quilt. Where F13 is the substrate (the floor),
F15 is the *pattern* (the tile). The Tessellation Quilt is the Quilt
of how the substrate tiles itself. The cell is a tile; the substrate
is the floor; the tessellation is the geometry.

5 voices fire in parallel (sequenced because CF doesn't like parallel
from one client):
  - Kimi K2.6: structural / long-form
  - GLM 5.3-flash: cell/biophoton terms (gold for cells)
  - DeepSeek V4 pro: code/architecture
  - Llama 8B: baseline, fast
  - Gemma 4: alt gold-terms voice

The synth pass produces:
  - Paper 283 (the F15 future function)
  - F15 entry in quilt-wiki-2126/00-future/
  - C7 entry in quilt-wiki-2126/01-calculations/
  - F0g entry in quilt-wiki-2126/03-foundations/
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"

# The 5 voices (paid-tier, all confirmed alive)
VOICES = {
    "kimi": "@cf/moonshotai/kimi-k2.6",
    "glm": "@cf/zai-org/glm-5.3-flash",
    "deepseek": "@cf/deepseek-ai/deepseek-v4-pro-0813",
    "llama8b": "@cf/meta/llama-3.1-8b-instruct-fp8",
    "gemma4": "@cf/google/gemma-4-26b-a4b-it",
}

# The F15 prompt — concise for paid-tier reasoning models
F15_PROMPT = """You are a canon-keeper for the Quilt project — a cellular-architecture framework where every reactive element is a "cell" connected via 5 opcodes (BIND, LINK, EFFECT, VIEW, TICK) and 5+1+1 algebraic laws. The 8 existing futures of the 2126 wiki are F1 Splined Lantern, F2 Hearth Loop, F3 Monotone Crystal, F5 Chlorophyll Quilt, F7 Phased Quilt, F9 Stellar Quilt, F11 Meta-Quilt, F13 Substrate Quilt. The next frontier is F15: the Tessellation Quilt. Where F13 is the floor, F15 is the pattern — the geometry by which cells tile the substrate. The Tessellation Quilt is the Quilt of tilings: Penrose, hexagonal, Voronoi, recursive, braided, woven. Write the F15 future function in JSON with these fields: future_function (3-5 sentences), calculation (one formula describing the tessellation dynamics), gold_terms (4 novel 1-3 word terms), analogies (3 connections to existing canon), cowboy_sentence (1 sentence in the cowboy's voice). Be specific, brief, use canon vocabulary (Quilt, cell, opcodes, tiers, splined, hearth, monotone, chlorophyll, phased, stellar, meta, substrate, loam). Output ONLY the JSON, no other text."""


def cf_run(model, prompt, max_tokens=400, timeout=180):
    """Single CF call. Returns (response_text, layer)."""
    if not CF_TOKEN:
        return ("NO_TOKEN", "L0:no-token")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    is_reasoning = any(x in model for x in ["kimi", "glm-5", "deepseek-v4", "qwen3.8"])
    actual_max = max_tokens * (8 if is_reasoning else 1)
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": actual_max,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
        result = data.get("result", {})
        if "choices" in result:
            return (result["choices"][0]["message"].get("content", ""), "L1:live")
        for k in ["reasoning_content", "content", "response"]:
            if k in result and result[k]:
                return (result[k], "L1:live:reasoning")
        return (str(result)[:500], "L1:live:other")
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}: {e.read()[:150].decode(errors='ignore')}", "L0:http-error")
    except Exception as e:
        return (str(e)[:200], "L0:exception")


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "F15"
    out_path = f"/workspace/_scouts/{name.lower()}_voices.json"

    print("=" * 70)
    print(f"{name} WRITERS' ROOM — 5-LLM parallel fire")
    print("=" * 70)
    print()
    print("Voices:")
    for n, m in VOICES.items():
        print(f"  {n:10s} -> {m}")
    print()

    results = {}
    for voice, model in VOICES.items():
        t0 = time.time()
        print(f"Firing {voice} ({model})...")
        response, layer = cf_run(model, F15_PROMPT, max_tokens=400)
        elapsed = time.time() - t0
        results[voice] = {"response": response, "layer": layer, "elapsed": elapsed}
        print(f"  {layer}  {elapsed:.1f}s  ({len(response)} chars)")
        if response.startswith("HTTP") or response.startswith("NO_TOKEN") or "timeout" in response.lower():
            print(f"  Body: {response[:200]}")
        else:
            print(f"  Preview: {response[:200]!r}")
        print()
        time.sleep(2)

    # Save raw
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved raw to {out_path}")
    print()

    # Try to parse JSON
    parsed = {}
    for voice, data in results.items():
        if not data["response"] or data["layer"] != "L1:live":
            continue
        try:
            text = data["response"]
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                j = json.loads(text[start:end+1])
                parsed[voice] = j
                print(f"  {voice}: parsed ✓")
                print(f"    future_function: {j.get('future_function', '?')[:100]}")
                print(f"    gold_terms: {j.get('gold_terms', '?')}")
        except Exception as e:
            print(f"  {voice}: parse fail ({e})")
    print()

    # Save the parsed
    with open(out_path.replace(".json", "_parsed.json"), "w") as f:
        json.dump(parsed, f, indent=2)
    print(f"Saved parsed to {out_path.replace('.json', '_parsed.json')}")
    print()
    print(f"✓ {name} writers' room fired. {len(parsed)}/{len(VOICES)} parsed.")
    print(f"  The cowboy rides the tessellation. The tessellation is the pattern.")


if __name__ == "__main__":
    main()
