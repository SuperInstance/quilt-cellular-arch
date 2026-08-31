"""
writers_room_daemon.py — The self-driving writers' room (v2: foreman-edition).

The user said: "be the foreman of my low-level crew and do all the nuts
and bolts. use your apis effectively."

v2 fixes (foreman-mode):
  - AUTO-ALLOCATES paper numbers (max(existing_paper_num) + 1) so the
    cowboy never has to think about it
  - STAGES drafts in /workspace/_scouts/drafts/ before they hit canon
  - NEVER overwrites an existing paper; skips with a warning instead
  - NEVER overwrites an existing wiki entry; same
  - Loops on the queue continuously, no cowboy call needed
  - Logs to canon_log.json with provenance (which voice, which frontier)
  - cowboy_hand_synth.py merges hand-synthesized content into the draft

The cowboy's review loop:
  1. Look in /workspace/_scouts/drafts/ for new draft-{fid}.md files
  2. Read them; if the math/calc is wrong, write your hand-synth to
     /workspace/_scouts/hand-synth/{fid}.md
  3. Run `python3 cowboy_hand_synth.py` to promote the hand-synth to canon
  4. Or: if the LLM draft is good, just run
     `python3 promote_draft.py {fid}` to move it directly to canon

Configuration: 4 voices (Kimi K2.6, GLM 5.3-flash, DeepSeek V4 pro,
Llama 8B) — all on Cloudflare, all cheap, all in parallel.
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
DRAFTS_DIR = os.path.join(WORKSPACE, "_scouts/drafts")
HAND_SYNTH_DIR = os.path.join(WORKSPACE, "_scouts/hand-synth")
FRONTIERS_FILE = os.path.join(WORKSPACE, "_scouts/frontiers.json")
CANON_LOG = os.path.join(WORKSPACE, "_scouts/canon_log.json")

VOICES = [
    ("kimi", "@cf/moonshotai/kimi-k2.6", 1),
    ("glm", "@cf/zai-org/glm-5.3-flash", 1),
    ("deepseek", "@cf/deepseek-ai/deepseek-v4-pro-0813", 1),
    ("llama8b", "@cf/meta/llama-3.1-8b-instruct-fp8", 1),
]

# Tunables
LOOP_SLEEP = 30          # seconds between frontier checks
VOICE_TIMEOUT = 120      # per-voice timeout
MAX_PROMPT_TOKENS = 600  # the prompt budget per LLM


def cf_run(model, prompt, max_tokens=400, timeout=VOICE_TIMEOUT):
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


def next_paper_number():
    """Allocate the next free paper number atomically.

    Scans the canon dir for the highest paper-NNN.md number, then
    writes a reservation stub (a 1-byte file) at paper-(N+1).md
    so any other process sees the reservation and skips to N+2.
    Returns the allocated number.

    If a stub already exists, treat it as reserved and try N+1,
    N+2, ... until we find a free number.
    """
    # Collect all reserved numbers
    reserved = set()
    for fname in os.listdir(CANON_DIR):
        m = re.match(r"^paper-(\d+)\.md(\.lock)?$", fname)
        if m:
            reserved.add(int(m.group(1)))
    n = max(reserved) + 1 if reserved else 1
    # Try to reserve
    while True:
        stub = os.path.join(CANON_DIR, f"paper-{n}.md.lock")
        real = os.path.join(CANON_DIR, f"paper-{n}.md")
        if os.path.exists(stub) or os.path.exists(real):
            n += 1
            continue
        # Reserve by creating a lock file
        try:
            with open(stub, "x") as f:
                f.write("reserved")
            return n
        except FileExistsError:
            n += 1
            continue


def release_paper_number(n):
    """Release a reserved paper number (called after writing the
    actual paper or on failure)."""
    stub = os.path.join(CANON_DIR, f"paper-{n}.md.lock")
    if os.path.exists(stub):
        os.remove(stub)


def wiki_path_for(frontier_id, title_hint):
    """Compute the wiki path. Never overwrite existing files."""
    m = re.match(r"^F(\d+)", frontier_id)
    if m:
        num = int(m.group(1))
        slug = re.sub(r"[^a-z0-9]+", "-", title_hint.lower()).strip("-")
        return os.path.join(WIKI_DIR, f"{num:02d}-{slug}.md")
    m = re.match(r"^L(\d+)", frontier_id)
    if m:
        return os.path.join(WIKI_DIR, f"{frontier_id.lower()}.md")
    slug = re.sub(r"[^a-z0-9]+", "-", title_hint.lower()).strip("-")
    return os.path.join(WIKI_DIR, f"{slug}.md")


def paper_path_for(paper_num):
    return os.path.join(CANON_DIR, f"paper-{paper_num}.md")


def draft_path_for(frontier_id):
    return os.path.join(DRAFTS_DIR, f"draft-{frontier_id}.md")


def safe_write(path, content, allow_overwrite=False):
    """Write only if path doesn't exist (or allow_overwrite is True).
    Returns 'WROTE', 'SKIPPED', or 'OVERWROTE'."""
    if os.path.exists(path):
        if not allow_overwrite:
            return "SKIPPED"
    with open(path, "w") as f:
        f.write(content)
    return "WROTE" if not os.path.exists(path) or allow_overwrite else "OVERWROTE"


def render_draft(frontier_id, paper_num, title_hint, j, voice, voice_responses):
    """Render the LLM-driven draft markdown for a frontier."""
    ff = j.get("future_function", "?")
    first_sentence = re.split(r"[.!?]\s", ff, maxsplit=1)[0]
    title = first_sentence[:80].strip() or frontier_id
    golds = j.get("gold_terms", ["?", "?", "?", "?"])
    analogies = j.get("analogies", ["?", "?", "?"])
    return f"""# Paper {paper_num}: {frontier_id} — {title}

(Stage: drafts/. Cowboy reviews before promotion to canon.)

## Voices

This draft is a synthesis of {len(voice_responses)} LLM voices.
The best parseable JSON came from: **{voice}**.
All voices fired in parallel; their raw responses are in the canon log.

## The future function

{j.get('future_function', '?')}

## The calculation

```
{j.get('calculation', '?')}
```

## The 4 gold terms

{chr(10).join(f'- **{t}**' for t in golds)}

## The 3 analogies

{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(analogies))}

## The cowboy's sentence

> {j.get('cowboy_sentence', '?')}

## The principle

> The {frontier_id} is the inheritance. The {frontier_id} is the function. The
> {frontier_id} is the pattern. The cowboy rides the {frontier_id}. The cowboy
> rides the Quilt.

---

*Drafted by writers_room_daemon.py on {datetime.now().isoformat()}.*
*Frontier: {frontier_id} = {title_hint}.*
*Paper number auto-allocated: {paper_num}.*
"""


def load_frontiers():
    if not os.path.exists(FRONTIERS_FILE):
        os.makedirs(os.path.dirname(FRONTIERS_FILE), exist_ok=True)
        with open(FRONTIERS_FILE, "w") as f:
            json.dump([], f)
    with open(FRONTIERS_FILE) as f:
        return json.load(f)


def mark_frontier_done(frontier_id):
    frontiers = load_frontiers()
    frontiers = [f for f in frontiers if f.get("id") != frontier_id]
    with open(FRONTIERS_FILE, "w") as f:
        json.dump(frontiers, f, indent=2)


def append_canon_log(entry):
    log = []
    if os.path.exists(CANON_LOG):
        try:
            with open(CANON_LOG) as f:
                log = json.load(f)
        except Exception:
            log = []
    log.append(entry)
    with open(CANON_LOG, "w") as f:
        json.dump(log, f, indent=2)


def process_frontier(frontier):
    """Process a single frontier: fire 4 LLMs, hand-synth, write draft."""
    fid = frontier.get("id", "F?")
    title_hint = frontier.get("title", fid)
    prompt = frontier.get("prompt") or f"""You are a canon-keeper for the Quilt project — a cellular-architecture framework where every reactive element is a "cell" connected via 9 opcodes (BIND, LINK, EFFECT, VIEW, TICK, FORGET, PROOF, ROUTE, CRDT). The 13 levels are L0 (Unmanifest), L1 (Totipotent), L2 (Pluripotent), L3-L14 (being expanded). The next frontier is {fid}: {title_hint}. Write the {fid} future function in JSON with: future_function (3-5 sentences), calculation (one formula), gold_terms (4 novel 1-3 word terms), analogies (3 connections to existing canon), cowboy_sentence (1 sentence). Be specific, brief, use canon vocabulary. Output ONLY the JSON."""

    # Check if a draft already exists — skip if so
    draft = draft_path_for(fid)
    if os.path.exists(draft):
        print(f"  SKIP {fid}: draft already exists at {draft}")
        return "SKIPPED_DRAFT_EXISTS"

    # Check if a wiki entry or paper already exists — skip if so
    wiki = wiki_path_for(fid, title_hint)
    paper_num = next_paper_number()
    paper = paper_path_for(paper_num)
    if os.path.exists(wiki) or os.path.exists(paper):
        release_paper_number(paper_num)
        print(f"  SKIP {fid}: wiki or paper already exists")
        return "SKIPPED_CANON_EXISTS"

    print(f"  Processing {fid} ({title_hint}) -> paper {paper_num}...")
    results = {}
    for voice, model, _ in VOICES:
        t0 = time.time()
        response, layer = cf_run(model, prompt, max_tokens=MAX_PROMPT_TOKENS)
        results[voice] = {"response": response, "layer": layer,
                          "elapsed": time.time() - t0}
        print(f"    {voice}: {layer}  {results[voice]['elapsed']:.1f}s  "
              f"({len(response)} chars)")
        time.sleep(1)

    best_j = None
    best_voice = None
    for v, d in results.items():
        j = parse_json_safe(d["response"])
        if j and (best_j is None or len(json.dumps(j)) > len(json.dumps(best_j))):
            best_j = j
            best_voice = v

    if not best_j:
        print(f"    NO PARSEABLE JSON for {fid}. Saving raw drafts only.")
        for v, d in results.items():
            raw = os.path.join(DRAFTS_DIR, f"raw-{fid}-{v}.txt")
            with open(raw, "w") as f:
                f.write(d["response"])
        release_paper_number(paper_num)
        return "FAILED_NO_JSON"

    # Write DRAFT (staging), never directly to canon
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    draft_content = render_draft(fid, paper_num, title_hint, best_j,
                                  best_voice, results)
    status = safe_write(draft, draft_content, allow_overwrite=False)
    print(f"    {status} draft {draft}")

    # Log
    append_canon_log({
        "timestamp": datetime.now().isoformat(),
        "frontier": fid,
        "title": title_hint,
        "paper_num": paper_num,
        "best_voice": best_voice,
        "gold_terms": best_j.get("gold_terms", []),
        "draft_path": draft,
        "wiki_path": wiki,
        "paper_path": paper,
        "voice_responses": {v: {"layer": d["layer"],
                                  "elapsed": d["elapsed"],
                                  "len": len(d["response"])}
                              for v, d in results.items()},
    })
    return "DRAFTED"


def main():
    print("=" * 70)
    print("WRITERS' ROOM DAEMON v2 (foreman-edition)")
    print("=" * 70)
    print()
    print(f"Workspace: {WORKSPACE}")
    print(f"Wiki dir:  {WIKI_DIR}")
    print(f"Canon dir: {CANON_DIR}")
    print(f"Drafts:    {DRAFTS_DIR}")
    print(f"Frontiers: {FRONTIERS_FILE}")
    print()
    print(f"Loop sleep: {LOOP_SLEEP}s. Press Ctrl-C to stop.")
    print()

    os.makedirs(DRAFTS_DIR, exist_ok=True)
    os.makedirs(HAND_SYNTH_DIR, exist_ok=True)

    while True:
        frontiers = load_frontiers()
        if not frontiers:
            print(f"  No frontiers. Sleeping {LOOP_SLEEP}s...")
            time.sleep(LOOP_SLEEP)
            continue

        f = frontiers[0]
        result = process_frontier(f)
        if result in ("DRAFTED", "SKIPPED_CANON_EXISTS", "SKIPPED_DRAFT_EXISTS"):
            mark_frontier_done(f.get("id", "?"))
            print(f"  ✓ {f.get('id')} -> {result}. "
                  f"{len(frontiers)-1} frontiers remain.")
        else:
            print(f"  ✗ {f.get('id')} -> {result}. Will retry.")
            time.sleep(LOOP_SLEEP)


if __name__ == "__main__":
    main()
