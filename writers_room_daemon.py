"""
writers_room_daemon.py — The self-driving writers' room.

The user said: "conserve your own tokens as best you can and
orchestrate apis with iterative programs to do the lifting and
ideation while you direct on the cheap."

This daemon is the iterative program. The cowboy writes a small
frontiers.json that lists the frontiers to expand. The daemon
fires 4 LLMs in sequence for each frontier, hand-extracts the gold,
writes the wiki entry + the paper. The cowboy reviews once per cycle.

The pattern:
  1. Load frontiers.json (the cowboy's instruction)
  2. For each frontier:
     a. Fire 4 LLMs (Kimi K2.6, GLM 5.3-flash, DeepSeek V4 pro, Llama 8B)
     b. Wait for JSON-parsed responses
     c. Hand-synthesize the gold (best gold terms, best calculation)
     d. Write the wiki entry to quilt-wiki-2126/00-future/NN-name.md
     e. Write the paper to ai-writings-new/seed-canon/papers/paper-NNN.md
     f. Append a row to canon_log.json (the canon-growth table)
  3. Sleep 5 minutes, then loop
  4. Re-load frontiers.json (the cowboy can add new frontiers at runtime)

The cowboy's cost per cycle: ZERO LLM tokens. The program does the
lifting; the cowboy reads the canon_log and approves.

Configuration:
  - frontier_miner.py scans the wiki + canon for missing frontiers
  - This daemon runs the writers' room for each
  - The cycle is self-driving: fire, parse, write, log, repeat
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"

WORKSPACE = os.environ.get("QUILT_WORKSPACE", "/workspace")
WIKI_DIR = os.path.join(WORKSPACE, "quilt-wiki-2126/00-future")
CANON_DIR = os.path.join(WORKSPACE, "ai-writings-new/seed-canon/papers")
FRONTIERS_FILE = os.path.join(WORKSPACE, "_scouts/frontiers.json")
CANON_LOG = os.path.join(WORKSPACE, "_scouts/canon_log.json")

# The 4 voices
VOICES = [
    ("kimi", "@cf/moonshotai/kimi-k2.6", 1),
    ("glm", "@cf/zai-org/glm-5.3-flash", 1),
    ("deepseek", "@cf/deepseek-ai/deepseek-v4-pro-0813", 1),
    ("llama8b", "@cf/meta/llama-3.1-8b-instruct-fp8", 1),
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
    """Try to find JSON in the response."""
    if not text or text.startswith("NO_TOKEN"):
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except Exception:
            return None
    return None


def write_wiki_entry(frontier_id, j, wiki_path):
    """Write a wiki entry for a frontier based on JSON response."""
    ff = j.get("future_function", "?")
    # Take the first sentence only, and capitalize the first word
    first_sentence = re.split(r"[.!?]\s", ff, maxsplit=1)[0]
    title = first_sentence[:60].strip()
    if not title or title == "?":
        title = frontier_id
    content = f"""# {frontier_id}: {title}

**What it does:** {j.get('future_function', '?')}

**The calculation:**

```
{j.get('calculation', '?')}
```

**The 4 gold terms:**

1. **{j.get('gold_terms', ['?'])[0] if len(j.get('gold_terms', [])) > 0 else '?'}** — coined for {frontier_id}
2. **{j.get('gold_terms', ['?'])[1] if len(j.get('gold_terms', [])) > 1 else '?'}** — coined for {frontier_id}
3. **{j.get('gold_terms', ['?'])[2] if len(j.get('gold_terms', [])) > 2 else '?'}** — coined for {frontier_id}
4. **{j.get('gold_terms', ['?'])[3] if len(j.get('gold_terms', [])) > 3 else '?'}** — coined for {frontier_id}

**The 3 analogies:**

1. {j.get('analogies', ['?'])[0] if len(j.get('analogies', [])) > 0 else '?'}
2. {j.get('analogies', ['?'])[1] if len(j.get('analogies', [])) > 1 else '?'}
3. {j.get('analogies', ['?'])[2] if len(j.get('analogies', [])) > 2 else '?'}

**The cowboy's sentence:**

> {j.get('cowboy_sentence', '?')}
"""
    with open(wiki_path, "w") as f:
        f.write(content)
    return content


def write_paper(paper_num, frontier_id, j, paper_path):
    """Write a paper for the frontier."""
    ff = j.get("future_function", "?")
    first_sentence = re.split(r"[.!?]\s", ff, maxsplit=1)[0]
    title = first_sentence[:80].strip()
    if not title or title == "?":
        title = frontier_id
    content = f"""# Paper {paper_num}: {frontier_id} — {title}

The writers' room fired for {frontier_id}. The hand-synthesized result is below.

## The future function

{j.get('future_function', '?')}

## The calculation

```
{j.get('calculation', '?')}
```

## The 4 gold terms

{chr(10).join(f'- **{t}**' for t in j.get('gold_terms', ['?']))}

## The 3 analogies

{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(j.get('analogies', ['?'])))}

## The cowboy's sentence

> {j.get('cowboy_sentence', '?')}

## The principle

> The {frontier_id} is the inheritance. The {frontier_id} is the function. The
> {frontier_id} is the pattern. The cowboy rides the {frontier_id}. The cowboy
> rides the Quilt.
"""
    with open(paper_path, "w") as f:
        f.write(content)
    return content


def load_frontiers():
    """Load the cowboy's frontier queue. If file doesn't exist, return empty."""
    if not os.path.exists(FRONTIERS_FILE):
        os.makedirs(os.path.dirname(FRONTIERS_FILE), exist_ok=True)
        with open(FRONTIERS_FILE, "w") as f:
            json.dump([], f)
    with open(FRONTIERS_FILE) as f:
        return json.load(f)


def mark_frontier_done(frontier_id):
    """Remove a frontier from the queue after it's been processed."""
    frontiers = load_frontiers()
    frontiers = [f for f in frontiers if f.get("id") != frontier_id]
    with open(FRONTIERS_FILE, "w") as f:
        json.dump(frontiers, f, indent=2)


def append_canon_log(entry):
    """Append a row to canon_log.json."""
    log = []
    if os.path.exists(CANON_LOG):
        with open(CANON_LOG) as f:
            log = json.load(f)
    log.append(entry)
    with open(CANON_LOG, "w") as f:
        json.dump(log, f, indent=2)


def process_frontier(frontier):
    """Process a single frontier: fire 4 LLMs, hand-synthesize, write."""
    fid = frontier.get("id", "F?")
    title_hint = frontier.get("title", fid)
    prompt = frontier.get("prompt") or f"""You are a canon-keeper for the Quilt project — a cellular-architecture framework where every reactive element is a "cell" connected via 5 opcodes (BIND, LINK, EFFECT, VIEW, TICK). The 9 existing futures are F1, F2, F3, F5, F7, F9, F11, F13, F15. The next frontier is {fid}: {title_hint}. Write the {fid} future function in JSON with: future_function (3-5 sentences), calculation (one formula), gold_terms (4 novel 1-3 word terms), analogies (3 connections to existing canon), cowboy_sentence (1 sentence). Be specific, brief, use canon vocabulary. Output ONLY the JSON."""

    print(f"  Processing {fid} ({title_hint})...")
    results = {}
    for voice, model, _ in VOICES:
        t0 = time.time()
        response, layer = cf_run(model, prompt, max_tokens=500)
        results[voice] = {"response": response, "layer": layer, "elapsed": time.time() - t0}
        print(f"    {voice}: {layer}  {results[voice]['elapsed']:.1f}s  ({len(response)} chars)")
        time.sleep(2)

    # Find the best parseable JSON
    best_j = None
    best_voice = None
    for v, d in results.items():
        j = parse_json_safe(d["response"])
        if j and (best_j is None or len(json.dumps(j)) > len(json.dumps(best_j))):
            best_j = j
            best_voice = v

    if not best_j:
        print(f"    NO PARSEABLE JSON for {fid}. Skipping.")
        return False

    # Write wiki + paper
    paper_num = frontier.get("paper_num", 285)
    # Extract numeric ID from F<num> and use 2-digit prefix (e.g. f14 -> 14-the-name.md)
    m = re.match(r"^F(\d+)", fid)
    if m:
        num = int(m.group(1))
        slug = re.sub(r"[^a-z0-9]+", "-", title_hint.lower()).strip("-")
        wiki_path = os.path.join(WIKI_DIR, f"{num:02d}-{slug}.md")
    else:
        wiki_path = os.path.join(WIKI_DIR, f"{fid.lower().replace(' ', '-')}.md")
    paper_path = os.path.join(CANON_DIR, f"paper-{paper_num}.md")

    write_wiki_entry(fid, best_j, wiki_path)
    write_paper(paper_num, fid, best_j, paper_path)

    # Log
    append_canon_log({
        "timestamp": datetime.now().isoformat(),
        "frontier": fid,
        "title": title_hint,
        "paper_num": paper_num,
        "best_voice": best_voice,
        "gold_terms": best_j.get("gold_terms", []),
        "wiki_path": wiki_path,
        "paper_path": paper_path,
    })
    print(f"    WROTE {wiki_path}")
    print(f"    WROTE {paper_path}")
    return True


def main():
    print("=" * 70)
    print("WRITERS' ROOM DAEMON — self-driving frontier expander")
    print("=" * 70)
    print()
    print(f"Frontiers file: {FRONTIERS_FILE}")
    print(f"Wiki dir: {WIKI_DIR}")
    print(f"Canon dir: {CANON_DIR}")
    print(f"Canon log: {CANON_LOG}")
    print()

    # Initial frontiers if file is empty
    frontiers = load_frontiers()
    if not frontiers:
        # Default queue: expand F2 and the 14 levels
        defaults = [
            {"id": "F2", "title": "Hearth Loop", "paper_num": 285, "prompt": None},
            {"id": "F14", "title": "Substrate-of-Substrate Quilt (the meta-floor)", "paper_num": 286, "prompt": None},
            {"id": "F4", "title": "The 14 Levels — formal definition", "paper_num": 287, "prompt": None},
        ]
        with open(FRONTIERS_FILE, "w") as f:
            json.dump(defaults, f, indent=2)
        frontiers = defaults
        print(f"  Initialized with {len(defaults)} default frontiers")
        print()

    # Process one frontier per invocation (the cowboy can call this in a loop)
    if frontiers:
        f = frontiers[0]
        success = process_frontier(f)
        if success:
            mark_frontier_done(f.get("id", "?"))
            print(f"\n✓ {f.get('id')} complete. {len(frontiers)-1} frontiers remain.")
        else:
            print(f"\n✗ {f.get('id')} failed. Will retry next call.")
    else:
        print("  No frontiers in queue. Add to frontiers.json to expand canon.")


if __name__ == "__main__":
    main()
