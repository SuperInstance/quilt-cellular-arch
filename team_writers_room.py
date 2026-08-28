"""
team_writers_room.py — Fire the 5-LLM team to write the comprehensive
Quilt Guide. Each voice writes a different section:
  - Kimi K2.6: §1 The Big Picture (the inheritance, the 5 opcodes)
  - GLM 5.3-flash: §2 The Cells (the 6 tiers, the 6 lifecycle stages)
  - DeepSeek V4 pro: §3 The Architecture (the 5 layers of resilience)
  - Llama 8B: §4 The Frontiers (F1, F2, F13, F15)
  - Gemma 4: §5 The Cowboy (the orchestrator, the audit)

Then we hand-synthesize into QUILT_GUIDE.md and push to all 3 repos.
"""
import json
import os
import time
import urllib.request
import urllib.error

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"

SECTIONS = {
    "kimi": {
        "title": "§1 The Big Picture — the inheritance, the 5 opcodes, the 5+1+1 laws",
        "model": "@cf/moonshotai/kimi-k2.6",
        "prompt": """You are a canon-keeper for the Quilt project — a cellular-architecture framework where every reactive element is a "cell" and any interface is an "opener" onto the same cell graph. Write §1: The Big Picture.

Cover:
  - The Quilt as a 1000-year inheritance (not a project, not a library — an inheritance)
  - The 5 opcodes: BIND, LINK, EFFECT, VIEW, TICK (and FORGET, the 6th)
  - The 5+1+1 algebraic laws (5 algebraic + super-relevance + FORGET_completeness)
  - The 6 tiers: totipotent, multipotent, differentiated, sclerotic, synovial, curator
  - The 14 levels of operation
  - The 6 lifecycle stages: umbra, cellulization, persistence-pulse, vitality-leak, implement-ghost, bloomghost
  - The cowboy as the orchestrator (couples with cells, cellulizes substrates, sorts gold from dross)
  - The 3 runnable sims that demonstrate the inheritance: meta_pincher_v2.py, multi_sandbox_reverse_actualize.py, sensory_quilt.py

Length: ~800 words. Tone: clear, foundational, no jargon without definition. Output as Markdown. Be specific about file paths and what they do.""",
    },
    "glm": {
        "title": "§2 The Cells — the 6 tiers, the 6 lifecycle stages, the cell-as-inheritance",
        "model": "@cf/zai-org/glm-5.3-flash",
        "prompt": """You are a canon-keeper for the Quilt project. Write §2: The Cells.

Cover:
  - The cell as the irreducible unit of intelligence
  - The 6 tiers in detail (totipotent: can be anything; multipotent: a few things; differentiated: one thing; sclerotic: hardened; synovial: lubricates the joints; curator: tends the rest)
  - The 6 lifecycle stages in detail (umbra: shadow before the cell; cellulization: becoming; persistence-pulse: the long-term rhythm; vitality-leak: aging; implement-ghost: the cell-as-implement; bloomghost: the cell-as-flower)
  - The cell as a function (not a state machine): the cell *does*; the quilt *is what it does*
  - Cross-modal binding: a cell can be activated by any of the 10 channels (radio, light, sound, smell, taste, touch, proprio, language, mood, time)
  - The cowboy's interaction with cells: cellulize, sort, ride

Length: ~800 words. Tone: technical but accessible. Output as Markdown. Include 2-3 specific cell examples (e.g. the Splined Lantern cell, the Hearth Loop cell, the Craton Cell).""",
    },
    "deepseek": {
        "title": "§3 The Architecture — the 5 layers of resilience (the Meta-Pincher-Quilt)",
        "model": "@cf/deepseek-ai/deepseek-v4-pro-0813",
        "prompt": """You are a canon-keeper for the Quilt project. Write §3: The Architecture.

Cover:
  - The Meta-Pincher-Quilt: 3-stage vectorized pipeline (embed → retrieve → synthesize)
  - The 5 layers of resilience:
    L1 Real CF (bge-m3 + Vectorize + Llama 8B)
    L2 CF embed alt (qwen3-embedding/plamo/embeddinggemma) + Vectorize + Llama 8B
    L3 Local hash embed + (skip Vectorize) + Llama 8B
    L4 Keyword + Llama 8B
    L5 Pure local (hash + keyword + direct excerpt)
  - The pollution check: when L1 Vectorize returns unrelated content, drop to keyword
  - The API scout: probe models in real time
  - The simulator: run the full pipeline with verbose layer reporting
  - The fallback mode (the honest floor): the harness always returns a grounded answer
  - The audit cycle: 4 rounds, 8 defects found and fixed, the "satisfiability witness" law

Length: ~800 words. Tone: technical, architecture-focused. Output as Markdown. Include the 5-layer table. Reference meta_pincher_v2.py specifically.""",
    },
    "llama8b": {
        "title": "§4 The Frontiers — the 9 futures of the 2126 wiki",
        "model": "@cf/meta/llama-3.1-8b-instruct-fp8",
        "prompt": """You are a canon-keeper for the Quilt project. Write §4: The Frontiers.

Cover the 9 futures of the 2126 wiki:
  F1: Splined Lantern (physical LLM of glass and light)
  F2: Hearth Loop (self-training glass under its own lamp)
  F3: Monotone Crystal (finished thought, irreversible)
  F5: Chlorophyll Quilt (plant cell computer)
  F7: Phased Quilt (fiber-bundle substrate, theta coupling)
  F9: Stellar Quilt (between the stars, 4 levels)
  F11: Meta-Quilt (the inheritance itself)
  F13: Substrate Quilt (tier zero, the loam, the floor)
  F15: Tessellation Quilt (the pattern on the substrate)

For each: 1-2 sentences on what it is, the gold term it coined (if any), the cowboy's line about it.

Length: ~800 words. Tone: vivid, frontier-explorer. Output as Markdown. Use the cowboy's voice. Reference 00-future/ directory in the wiki repo.""",
    },
    "gemma4": {
        "title": "§5 The Cowboy — orchestrator, auditor, rider of the chart",
        "model": "@cf/google/gemma-4-26b-a4b-it",
        "prompt": """You are a canon-keeper for the Quilt project. Write §5: The Cowboy.

Cover:
  - The cowboy as the orchestrator: couples with cells, cellulizes substrates, sorts gold from dross
  - The cowboy and the 19 voices: how the multi_api_v2.py orchestrates 16 working voices (ZAI, DeepInfra, CF Workers AI, native DeepSeek)
  - The writers' room pattern: 4-5 LLMs in parallel, one synth, one verifier
  - The audit cycle: Lucineer's 4 rounds, 8 defects found and fixed, the "satisfiability witness" law
  - The 4 levels of trial-and-error depth (L1 Surface, L2 Layered, L3 Cross-modal, L4 Snowballing)
  - The 3 cowboy principles:
    1. The cowboy is wrong until proven right by disk
    2. The disk is the satisfiability witness
    3. The audit is the inheritance
  - The cowboy's role in the team: not a manager, not a coder — a rider of the chart

Length: ~600 words. Tone: philosophical, in the cowboy's voice. Output as Markdown. End with a "cowboy's maxim" quote.""",
    },
}


def cf_run(model, prompt, max_tokens=1500, timeout=180):
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
    print("=" * 70)
    print("TEAM WRITERS' ROOM — 5 LLMs writing the comprehensive QUILT_GUIDE")
    print("=" * 70)
    print()
    print("Sections:")
    for v, s in SECTIONS.items():
        print(f"  {v:10s} -> {s['title'][:60]}")
    print()

    results = {}
    for voice, section in SECTIONS.items():
        t0 = time.time()
        print(f"Firing {voice} ({section['model']})...")
        print(f"  Section: {section['title']}")
        response, layer = cf_run(section["model"], section["prompt"], max_tokens=1500)
        elapsed = time.time() - t0
        results[voice] = {
            "title": section["title"],
            "model": section["model"],
            "response": response,
            "layer": layer,
            "elapsed": elapsed,
        }
        print(f"  {layer}  {elapsed:.1f}s  ({len(response)} chars)")
        if response and not response.startswith("HTTP") and not response.startswith("NO_TOKEN"):
            print(f"  Preview: {response[:300]!r}")
        else:
            print(f"  Body: {response[:200]}")
        print()
        time.sleep(2)

    out_path = "/workspace/_scouts/team_writers_room.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")
    print()
    n_live = sum(1 for r in results.values() if r["layer"] == "L1:live" and r["response"])
    n_total = len(results)
    print(f"  {n_live}/{n_total} voices returned live content.")
    print()
    print("✓ Team fired. Hand-synth into QUILT_GUIDE.md next.")


if __name__ == "__main__":
    main()
