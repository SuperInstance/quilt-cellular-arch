#!/usr/bin/env python3
"""
iterative_dnd.py — Multi-round iterative evolution.
The writers' room as a D&D party. The DM is the
captain. The campaign is the masterwork. Each round
the gold compounds.

The user articulated: go dozens of iterative
evolutions with this idea. think about how tap's
works at superinstance and set up python programs
for models to iterate like they were DnD players
solving a delightful DM's masterwork. we have a lot
of api to use.

This script:
  - Sets up a multi-round writers' room
  - Each round, 7+ voices propose moves in parallel
  - Each subsequent round, voices respond to the
    best move from the previous round
  - The gold compounds across rounds
  - Each round the gold gets richer

The principle:
  - The first round is asking each voice "what do
    you do?"
  - The second round is asking each voice "how do
    you respond to what the other voice just did?"
  - The third round is asking each voice "how do
    you extend the best move so far?"
  - The gold compounds like a D&D campaign where
    each player riffs on the previous player's move
"""
import json
import os
import time
import urllib.request
import concurrent.futures


# ============================================================
# Voices available
# ============================================================
VOICES = {
    "llama70b": {
        "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "token": os.environ.get("DEEPINFRA_TOKEN"),
        "max_tokens": 4096,
    },
    "llama405b": {
        "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "meta-llama/Meta-Llama-3.1-405B-Instruct",
        "token": os.environ.get("DEEPINFRA_TOKEN"),
        "max_tokens": 4096,
    },
    "hermes": {
        "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "NousResearch/hermes-3-llama-3.1-405b",
        "token": os.environ.get("DEEPINFRA_TOKEN"),
        "max_tokens": 4096,
    },
    "mixtral": {
        "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "token": os.environ.get("DEEPINFRA_TOKEN"),
        "max_tokens": 4096,
    },
    "wizard": {
        "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "microsoft/WizardLM-2-8x22B",
        "token": os.environ.get("DEEPINFRA_TOKEN"),
        "max_tokens": 4096,
    },
    "zai": {
        "endpoint": "https://api.z.ai/api/coding/paas/v4/chat/completions",
        "model": "GLM-4.5-Air",
        "token": os.environ.get("ZAI_API_KEY"),
        "max_tokens": 8192,
    },
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "token": os.environ.get("DEEPSEEK_API_KEY"),
        "max_tokens": 4096,
    },
    "gemini": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
        "model": "gemini-2.0-flash-exp",
        "token": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        "max_tokens": 4096,
    },
}


def call_voice(name, prompt):
    """Call a single voice. Returns (name, response)."""
    v = VOICES.get(name)
    if not v or not v.get("token"):
        return (name, None)

    if name == "gemini":
        # Gemini uses a different API shape
        url = f"{v['endpoint']}?key={v['token']}"
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": v["max_tokens"], "temperature": 0.95}}
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            return (name, d["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            return (name, f"[{name} error: {e}]")

    # OpenAI-compatible
    body = {"model": v["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": v["max_tokens"], "temperature": 0.95}
    try:
        req = urllib.request.Request(v["endpoint"], data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {v['token']}", "Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
        return (name, d["choices"][0]["message"]["content"])
    except Exception as e:
        return (name, f"[{name} error: {e}]")


def fire_round(voices, prompt, parallel=True):
    """Fire one round. Returns dict of {voice: response}."""
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(voices)) as ex:
        futures = {ex.submit(call_voice, name, prompt): name for name in voices}
        for fut in concurrent.futures.as_completed(futures):
            name = futures[fut]
            try:
                n, txt = fut.result()
                results[n] = txt
            except Exception as e:
                results[name] = f"[outer error: {e}]"
    return results


# ============================================================
# The campaign — the masterwork DM's scenario
# ============================================================
CAMPAIGN = """
THE DM's MASTERWORK SCENARIO:

You are a player in a D&D-style writers' room. The
DM (the captain) has presented the masterwork scenario:

THE 8 LEVELS OF THE OPERATION:
  1. The Vessel (the boat)
  2. The Equipment (the tools)
  3. The Skills (what the crew knows)
  4. The Consumables (what gets used up)
  5. The Renewables (what gets replenished)
  6. The Durables (what lasts many voyages)
  7. The Concept (the function, the operation itself)
  8. The Spline (the trajectory of past choices)

THE COUPLED CELL: the cell is the player-artifact
COUPLING, not the player alone, not the artifact
alone. The cell is alive when the player plays it.

THE SPLINE: the 1974 captain's choice of 6-71N Detroit
(now the old but stable horse) is a point on the
spline. The current captain's perception of "step
forward" passes through that point. The spline is the
gravity that pulls future choices toward the past.

THE 5 GOLD TERMS: cellulization, implement ghost,
bloomghost, vitality leak, persistence pulse.

THE LAB: the testing phase — 6 experiments, 4 sims,
2 docs, 1 viz.

THE LAP: the old shipwright method — clinker-built
hull of cells, each cell laps over the next.

THE TAP: the smallest unit of opening. The Tap is a
single cell that lets the user open any operation by
clicking it. The Tap is the doorway to the Quilt.

YOUR MOVE: propose a single new term, a single new
structure, or a single new experiment that EXTENDS
the masterwork scenario. The term should be 2-4 words,
single phrase. The structure or experiment should be
described in 1-2 sentences.

Reply with ONLY the term/structure/experiment, no
preamble, no commentary. The DM (captain) will decide
which moves advance the campaign.
"""


def main(n_rounds=3, voices=None):
    if voices is None:
        voices = ["llama70b", "hermes", "wizard", "mixtral"]

    print("=" * 78)
    print("  THE D&D WRITERS' ROOM — iterative evolution")
    print("=" * 78)
    print()
    print(f"  Voices: {voices}")
    print(f"  Rounds: {n_rounds}")
    print()

    all_rounds = {}
    for r in range(1, n_rounds + 1):
        if r == 1:
            prompt = CAMPAIGN + "\n\nROUND 1: propose your initial move. Reply with ONLY your move, no commentary."
        else:
            prev = all_rounds.get(r - 1, {})
            # Take best 2 moves from previous round
            prev_text = "\n\n".join(
                f"  {name}: {resp[:300] if resp else '(none)'}"
                for name, resp in prev.items() if resp and not resp.startswith("[")
            )
            prompt = CAMPAIGN + f"\n\nROUND {r}: the previous round, the players proposed:\n\n{prev_text}\n\nNow respond to the BEST move from the previous round. EXTEND it, COMPLICATE it, BUILD on it. Propose a single new term/structure/experiment that is the natural next move. Reply with ONLY your move, no commentary."

        print(f"  ROUND {r}: firing {len(voices)} voices in parallel...")
        results = fire_round(voices, prompt)
        all_rounds[r] = results
        for name, resp in results.items():
            preview = (resp[:200] if resp else "(none)")
            print(f"  [{name}]: {preview}")
        print()

    # Save
    os.makedirs("/workspace/_scouts/voices", exist_ok=True)
    for r, results in all_rounds.items():
        with open(f"/workspace/_scouts/voices/round_{r}.md", "w") as f:
            f.write(f"# Round {r} of the D&D writers' room\n\n")
            f.write(f"Voices: {voices}\n\n")
            for name, resp in results.items():
                f.write(f"## {name}\n\n")
                f.write(resp if resp else "(none)")
                f.write("\n\n")

    print(f"  Saved {n_rounds} rounds to /workspace/_scouts/voices/round_*.md")
    print()
    print("  The DM (captain) reviews the moves and advances the campaign.")
    print("  The gold compounds across rounds.")
    print("  The cowboy rides between the gold.")


if __name__ == "__main__":
    main()
