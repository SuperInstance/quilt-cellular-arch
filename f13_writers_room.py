"""
f13_writers_room.py — The F13 Substrate Quilt Writers' Room.

The user said: "keep your team moving. use lots of kimi, z.ai and others"

The F13 Substrate Quilt is the next frontier. The wiki has 7 futures;
F13 will be the 8th. The substrate is the *ground* under every cell;
the substrate is what makes the cell *happen*. F13 is the Quilt
of substrates.

The 4-LLM writers' room fires 4 voices in parallel:
  - Kimi K2.6: long-form, structural
  - GLM 5.3-flash: cell/biophoton terms (the cowboy's gold for cells)
  - DeepSeek V4 pro: code/architecture
  - Llama 3.3 70B: gold terms (alt)

The synth pass produces:
  - Paper 282 (the F13 future function)
  - F13 entry in quilt-wiki-2126/00-future/
  - C9 entry in quilt-wiki-2126/01-calculations/
  - M6 entry in quilt-wiki-2126/02-mathematics/
  - F0f entry in quilt-wiki-2126/03-foundations/

The principle:
  F13 is the substrate. The substrate is the function. The function
  is the quilt. The quilt is the inheritance.
"""
import json
import os
import time
import urllib.request
import urllib.error

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"

# The 4 voices (paid-tier, all confirmed alive in scout)
VOICES = {
    "kimi": "@cf/moonshotai/kimi-k2.6",
    "glm": "@cf/zai-org/glm-5.3-flash",
    "deepseek": "@cf/deepseek-ai/deepseek-v4-pro-0813",
    "llama8b": "@cf/meta/llama-3.1-8b-instruct-fp8",  # reliable, used as baseline
    "gemma4": "@cf/google/gemma-4-26b-a4b-it",  # alt gold-terms voice
}

# The F13 prompt — concise for paid-tier reasoning models
F13_PROMPT = """You are a canon-keeper for the Quilt project — a cellular-architecture framework where every reactive element is a "cell" connected via 5 opcodes (BIND, LINK, EFFECT, VIEW, TICK) and 5+1+1 algebraic laws. The 7 existing futures of the 2126 wiki are F1 Splined Lantern, F2 Hearth Loop, F3 Monotone Crystal, F5 Chlorophyll Quilt, F7 Phased Quilt, F9 Stellar Quilt, F11 Meta-Quilt. The next frontier is F13: the Substrate Quilt. The substrate is the ground under every cell; the substrate is what makes the cell happen. Write the F13 future function in JSON with these fields: future_function (3-5 sentences), calculation (one formula), gold_terms (4 novel 1-3 word terms), analogies (3 connections to existing canon), cowboy_sentence (1 sentence in the cowboy's voice). Be specific, brief, use canon vocabulary (Quilt, cell, opcodes, tiers, splined, hearth, monotone, chlorophyll, phased, stellar, meta). Output ONLY the JSON, no other text."""


def cf_run(model, prompt, max_tokens=400, timeout=180):
    """Single CF call. Returns (response_text, layer)."""
    if not CF_TOKEN:
        return ("NO_TOKEN", "L0:no-token")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    # Reasoning models need 8x tokens; non-reasoning need 1x
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
        # Reasoning models return content in `reasoning_content`
        for k in ["reasoning_content", "content", "response"]:
            if k in result and result[k]:
                return (result[k], "L1:live:reasoning")
        return (str(result)[:500], "L1:live:other")
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}: {e.read()[:150].decode(errors='ignore')}", "L0:http-error")
    except Exception as e:
        return (str(e)[:200], "L0:exception")


def main():
    print("=" * 70)
    print("F13 SUBSTRATE QUILT — 4-LLM writers' room")
    print("=" * 70)
    print()
    print("Voices:")
    for n, m in VOICES.items():
        print(f"  {n:10s} -> {m}")
    print()

    # Fire 4 in sequence (CF doesn't like parallel from one client)
    results = {}
    for name, model in VOICES.items():
        t0 = time.time()
        print(f"Firing {name} ({model})...")
        response, layer = cf_run(model, F13_PROMPT, max_tokens=800)
        elapsed = time.time() - t0
        results[name] = {"response": response, "layer": layer, "elapsed": elapsed}
        print(f"  {layer}  {elapsed:.1f}s  ({len(response)} chars)")
        if response.startswith("HTTP") or response.startswith("NO_TOKEN"):
            print(f"  Body: {response[:200]}")
        else:
            # Show first 200 chars
            print(f"  Preview: {response[:200]!r}")
        print()
        time.sleep(2)  # be nice to the rate limiter

    # Save raw results
    out_path = "/workspace/_scouts/f13_voices.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved raw results to {out_path}")
    print()

    # Try to parse each as JSON; if not, save the raw
    for name, data in results.items():
        if data["layer"] != "L1:live":
            continue
        text = data["response"]
        # Try to extract JSON from the response
        try:
            # Find first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                j = json.loads(text[start:end+1])
                print(f"  {name}: parsed JSON ✓")
                print(f"    future_function: {j.get('future_function', '?')[:100]}")
                print(f"    gold_terms: {j.get('gold_terms', '?')}")
        except Exception as e:
            print(f"  {name}: JSON parse failed ({e}); raw text saved")
    print()

    print("✓ F13 writers' room fired. Synth pass to follow.")
    print("  The cowboy rides the substrate. The substrate is the function.")


if __name__ == "__main__":
    main()
