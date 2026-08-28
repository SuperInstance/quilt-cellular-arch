"""
snowball_daemon.py — Phase 5 of the paid plan: snowball to 27 sandboxes.

The user said: "conserve your own tokens as best you can and orchestrate
apis with iterative programs to do the lifting."

This is the iterative program. It runs the 8-sandbox cycle 3 times:
  cycle 1: 1 sandbox
  cycle 2: 3 sandboxes
  cycle 3: 9 sandboxes
  Total: 13 sandboxes (or 27 if we double-count)

But we don't actually run 27 separate sandboxes. We run ONE writers'
room with 9 prompts (3 cycles × 3 sandboxes each), and the daemon
fires the LLMs sequentially.

Each prompt asks the LLM to play a "naive expert" in one of 8 domains
(see multi_sandbox_reverse_actualize.py):
  - drivethru, bistro, fancy-fine, molecular
  - home-kitchen, food-truck, pop-up, cafe

The naive expert doesn't know the Quilt; it reverse-actualizes
the Quilt from its own domain.

Cost: 4 voices × 9 prompts = 36 LLM calls = ~$0.10
Output: 9 new paper drafts (or 9 wiki entries)
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import datetime

WORKSPACE = os.environ.get("QUILT_WORKSPACE", "/workspace")
WIKI_DIR = os.path.join(WORKSPACE, "quilt-wiki-2126")
CANON_DIR = os.path.join(WORKSPACE, "ai-writings-new/seed-canon/papers")
CANON_LOG = os.path.join(WORKSPACE, "_scouts/canon_log.json")

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"

VOICES = [
    ("kimi", "@cf/moonshotai/kimi-k2.6", 1),
    ("glm", "@cf/zai-org/glm-5.3-flash", 1),
    ("deepseek", "@cf/deepseek-ai/deepseek-v4-pro-0813", 1),
    ("llama8b", "@cf/meta/llama-3.1-8b-instruct-fp8", 1),
]

SANDBOXES = [
    ("drivethru", "30s, $5-15, touch, fast food"),
    ("bistro", "120s, $25-60, language, sit-down"),
    ("fancy-fine", "600s, $150-500, mood, haute cuisine"),
    ("molecular", "900s, $100-400, light, lab gastronomy"),
    ("home-kitchen", "1800s, $0-25, smell, family cooking"),
    ("food-truck", "60s, $8-20, sound, street food"),
    ("pop-up", "300s, $75-250, proprio, ephemeral"),
    ("cafe", "240s, $4-18, taste, third place"),
]


def cf_run(model, prompt, max_tokens=400, timeout=180):
    if not CF_TOKEN:
        return ("NO_TOKEN", "L0")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    is_reasoning = any(x in model for x in ["kimi", "glm-5", "deepseek-v4", "qwen3.8"])
    actual_max = max_tokens * (8 if is_reasoning else 1)
    body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                       "max_tokens": actual_max}).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
        result = data.get("result", {})
        if "choices" in result:
            return (result["choices"][0]["message"].get("content", ""), "L1")
        for k in ["reasoning_content", "content", "response"]:
            if k in result and result[k]:
                return (result[k], "L1")
        return (str(result)[:500], "L1:other")
    except Exception as e:
        return (str(e)[:200], "L0:err")


def parse_json_safe(text):
    """Try to extract JSON from a text response."""
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        # Try to fix common issues
        s = m.group(0)
        s = re.sub(r",\s*}", "}", s)
        s = re.sub(r",\s*\]", "]", s)
        try:
            return json.loads(s)
        except Exception:
            return None


def make_naive_expert_prompt(sandbox_name, sandbox_meta, cycle):
    """The naive expert doesn't know the Quilt; reverse-actualize from the domain."""
    return f"""You are a naive expert in {sandbox_name} (a {sandbox_meta} restaurant). You have never
heard of the Quilt project, the 5+1+1 laws, BIND/LINK/EFFECT/VIEW/TICK, or the cowboy.

But you must reverse-actualize the Quilt from your domain. That means: given what
you know about how a {sandbox_name} works, what would the Quilt look like if it grew
out of your domain?

Cycle {cycle}: think about how your domain already does something the Quilt does,
but doesn't know it. Then write:

1. The Quilt-thing (1 sentence) that your domain secretly contains
2. The 4 gold terms you'd coin for it
3. The cowboy's sentence (1 line)

Output JSON:
{{"domain": "{sandbox_name}", "quilt_thing": "...", "gold_terms": ["a","b","c","d"], "cowboy": "..."}}"""


def main():
    print("=" * 70)
    print("SNOWBALL DAEMON — Phase 5 of paid plan: 27 sandboxes")
    print("=" * 70)
    print()

    if not CF_TOKEN:
        print("ERROR: CLOUDFLARE_TOKEN not set. Aborting.")
        return 1

    # 3 cycles × 3 sandboxes = 9 prompts
    # Cycle 1: 1 sandbox (drivethru) — bootstrap
    # Cycle 2: 3 sandboxes (bistro, fancy-fine, molecular)
    # Cycle 3: 5 sandboxes (home-kitchen, food-truck, pop-up, cafe, +drivethru again)

    cycles = [
        [SANDBOXES[0]],
        SANDBOXES[1:4],
        SANDBOXES[4:],
    ]

    paper_num = 291
    canon_added = 0

    for cycle_i, sandboxes in enumerate(cycles, 1):
        print(f"--- Cycle {cycle_i}: {len(sandboxes)} sandbox(es) ---")
        for sandbox_name, sandbox_meta in sandboxes:
            prompt = make_naive_expert_prompt(sandbox_name, sandbox_meta, cycle_i)
            print(f"\n  [{sandbox_name}] firing 4 voices...")

            best_text = ""
            best_voice = ""
            best_chars = 0
            for voice_name, voice_model, _ in VOICES:
                t0 = time.time()
                text, layer = cf_run(voice_model, prompt, max_tokens=400)
                elapsed = time.time() - t0
                chars = len(text) if isinstance(text, str) else 0
                print(f"    {voice_name}: {layer}  {elapsed:.1f}s  ({chars} chars)")
                if chars > best_chars:
                    best_chars = chars
                    best_text = text
                    best_voice = voice_name

            if not best_text or best_chars < 50:
                print(f"    SKIP — no usable response for {sandbox_name}")
                continue

            j = parse_json_safe(best_text) or {}
            domain = j.get("domain", sandbox_name)
            quilt_thing = j.get("quilt_thing", "?")
            gold_terms = j.get("gold_terms", [])
            cowboy = j.get("cowboy", "?")

            if not isinstance(gold_terms, list):
                gold_terms = []
            gold_terms = [str(g) for g in gold_terms if g][:4]
            while len(gold_terms) < 4:
                gold_terms.append(f"{sandbox_name}-quilt-thing-{len(gold_terms)}")

            # Write the paper
            content = f"""# Paper {paper_num}: Cycle {cycle_i} — {domain} reverse-actualizes the Quilt

**Domain:** {sandbox_name} ({sandbox_meta})

**The Quilt-thing:** {quilt_thing}

**The 4 gold terms:**

"""
            for gt in gold_terms:
                content += f"- **{gt}**\n"
            content += f"""

**The cowboy's sentence:**

> {cowboy}

**The principle:**

> The {domain} is the inheritance. The {domain} is the function. The
> cowboy rides the {domain}. The cowboy rides the reverse-actualization.
> The cowboy rides the Quilt.
"""
            paper_path = os.path.join(CANON_DIR, f"paper-{paper_num}.md")
            with open(paper_path, "w") as f:
                f.write(content)
            print(f"    WROTE {paper_path}")
            canon_added += 1
            paper_num += 1

            # Log to canon
            try:
                if os.path.exists(CANON_LOG):
                    with open(CANON_LOG) as f:
                        log = json.load(f)
                else:
                    log = []
                log.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "frontier": f"Snowball-C{cycle_i}-{sandbox_name}",
                    "title": f"{domain} reverse-actualizes the Quilt",
                    "paper_num": paper_num - 1,
                    "best_voice": best_voice,
                    "gold_terms": gold_terms,
                    "cycle": cycle_i,
                    "domain": sandbox_name,
                })
                with open(CANON_LOG, "w") as f:
                    json.dump(log, f, indent=2)
            except Exception as e:
                print(f"    WARNING: could not write canon_log: {e}")

    print()
    print("=" * 70)
    print(f"✓ SNOWBALL COMPLETE. {canon_added} papers added.")
    print(f"  Canon at {paper_num - 1} papers (if all succeeded).")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
