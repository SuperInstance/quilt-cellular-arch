"""
writers_room_daemon_v3.py — The foreman's writers' room, with the REAL
working voices (Aug 2026).

v3 changes:
- Uses 13 working voices (10 CF + 3 Gemini) instead of 4 unreliable ones
- Adds Gemini (gemini-2.5-flash, gemini-3.5-flash-lite, gemini-3.1-flash-lite)
  as the "fast court of variety"
- Voice roles:
  - "code": qwen2.5-coder-32b, deepseek-r1-distill-qwen-32b (code + reasoning)
  - "term_gold": llama-3.3-70b, llama-4-scout, mistral-small, qwq-32b
  - "fast": gemini-3.5-flash-lite, llama-3.2-3b, llama-3.1-8b
  - "long_form": gemini-2.5-flash, mistral-small-3.1-24b
- Same no-clobber guarantee as v2 (stages in drafts/, lock files, hand-synth override)
- Voice budget: 4-voice writers' room in parallel (1 code + 1 term_gold + 1 fast + 1 long_form)
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"
GEMINI_TOKEN = os.environ.get("GEMINI_TOKEN", "")

WORKSPACE = os.environ.get("QUILT_WORKSPACE", "/workspace")
WIKI_DIR = os.path.join(WORKSPACE, "quilt-wiki-2126/00-future")
CANON_DIR = os.path.join(WORKSPACE, "ai-writings-new/seed-canon/papers")
DRAFTS_DIR = os.path.join(WORKSPACE, "_scouts/drafts")
HAND_SYNTH_DIR = os.path.join(WORKSPACE, "_scouts/hand-synth")
FRONTIERS_FILE = os.path.join(WORKSPACE, "_scouts/frontiers.json")
CANON_LOG = os.path.join(WORKSPACE, "_scouts/canon_log.json")

# 13 working voices, with role tags
VOICES = [
    # code / reasoning (2)
    ("qwen32b",     "cf",  "@cf/qwen/qwen2.5-coder-32b-instruct",        "code"),
    ("dsr1",        "cf",  "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b", "reasoning"),
    # term gold (4)
    ("llama70b",    "cf",  "@cf/meta/llama-3.3-70b-instruct-fp8-fast",   "term_gold"),
    ("llama4",      "cf",  "@cf/meta/llama-4-scout-17b-16e-instruct",     "term_gold"),
    ("mistral",     "cf",  "@cf/mistralai/mistral-small-3.1-24b-instruct", "term_gold"),
    ("qwq",         "cf",  "@cf/qwen/qwq-32b",                            "reasoning"),
    # fast (3)
    ("llama3b",     "cf",  "@cf/meta/llama-3.2-3b-instruct",              "fast"),
    ("llama8b",     "cf",  "@cf/meta/llama-3.1-8b-instruct-fp8",          "fast"),
    ("gemini35lite","gemini","gemini-3.5-flash-lite",                     "fast"),
    # long_form / synthesis (2)
    ("gemini25",    "gemini","gemini-2.5-flash",                          "long_form"),
    ("gemini31",    "gemini","gemini-3.1-flash-lite",                     "long_form"),
    # small fallback (2)
    ("llama1b",     "cf",  "@cf/meta/llama-3.2-1b-instruct",              "fast"),
    ("gemma2b",     "cf",  "@cf/google/gemma-2b-it-lora",                 "fast"),
]

# Default writers' room: 4 voices in parallel, one per role
DEFAULT_ROOM = ["qwen32b", "llama70b", "gemini35lite", "gemini25"]

# Tunables
LOOP_SLEEP = 30
VOICE_TIMEOUT = 90
MAX_PROMPT_TOKENS = 600


def cf_run(model, prompt, max_tokens=400, timeout=VOICE_TIMEOUT):
    """Run a Cloudflare Workers AI model."""
    if not CF_TOKEN:
        return ("NO_TOKEN", "L0")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    is_reasoning = any(x in model for x in ["r1-distill", "qwq", "qwen3.8"])
    actual_max = max_tokens * (4 if is_reasoning else 1)
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
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}: {e.read().decode()[:200]}", "L2")
    except Exception as e:
        return (f"EXC {type(e).__name__}: {str(e)[:200]}", "L2")


def gemini_run(model, prompt, max_tokens=400, timeout=VOICE_TIMEOUT):
    """Run a Gemini model via Generative Language API."""
    if not GEMINI_TOKEN:
        return ("NO_TOKEN", "L0")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_TOKEN}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens}
    }).encode()
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
        candidates = data.get("candidates", [])
        if not candidates:
            return ("NO_CANDIDATES", "L1:other")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return ("NO_PARTS", "L1:other")
        return (parts[0].get("text", ""), "L1")
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}: {e.read().decode()[:200]}", "L2")
    except Exception as e:
        return (f"EXC {type(e).__name__}: {str(e)[:200]}", "L2")


def run_voice(voice_name, prompt, max_tokens=400):
    """Run a single voice by name. Returns (text, level)."""
    for vname, vtype, model, role in VOICES:
        if vname == voice_name:
            if vtype == "cf":
                return cf_run(model, prompt, max_tokens)
            elif vtype == "gemini":
                return gemini_run(model, prompt, max_tokens)
    return (f"UNKNOWN_VOICE:{voice_name}", "L0")


def run_voices_parallel(voice_names, prompt, max_tokens=400):
    """Run N voices in parallel and return {voice: (text, level)}."""
    out = {}
    with ThreadPoolExecutor(max_workers=len(voice_names)) as ex:
        futs = {ex.submit(run_voice, v, prompt, max_tokens): v for v in voice_names}
        for f in as_completed(futs):
            v = futs[f]
            try:
                out[v] = f.result()
            except Exception as e:
                out[v] = (f"EXC: {e}", "L2")
    return out


def next_paper_number():
    """Find the max paper number in the canon, +1."""
    max_n = 0
    for f in os.listdir(CANON_DIR):
        m = re.match(r"^paper-(\d+)\.md$", f)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return max_n + 1


def paper_path_for(n):
    return os.path.join(CANON_DIR, f"paper-{n:03d}.md")


def draft_path_for(frontier_id):
    return os.path.join(DRAFTS_DIR, f"draft-{frontier_id}.md")


def hand_synth_path_for(frontier_id):
    return os.path.join(HAND_SYNTH_DIR, f"{frontier_id}.md")


def safe_write(path, content, allow_overwrite=False):
    """Write a file. If it exists and allow_overwrite is False, abort."""
    if os.path.exists(path) and not allow_overwrite:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return True


def load_frontiers():
    if not os.path.exists(FRONTIERS_FILE):
        return []
    with open(FRONTIERS_FILE) as f:
        return json.load(f)


def process_frontier(frontier, voice_names=None, max_tokens=500):
    """Run the writers' room on one frontier. Returns the draft path or None."""
    fid = frontier.get("id", "?")
    title_hint = frontier.get("title", fid)
    prompt = frontier.get("prompt", f"Write a Quilt paper: {title_hint}")
    voice_names = voice_names or DEFAULT_ROOM

    paper_num = next_paper_number()
    print(f"[{datetime.now().isoformat()[:19]}] processing {fid} -> paper {paper_num:03d} (voices: {voice_names})")

    # Acquire lock
    lock_path = paper_path_for(paper_num) + ".lock"
    if os.path.exists(lock_path):
        print(f"  lock exists: {lock_path}")
        return None
    with open(lock_path, "w") as f:
        f.write(json.dumps({"fid": fid, "t": time.time(), "voices": voice_names}))

    # Run voices in parallel
    responses = run_voices_parallel(voice_names, prompt, max_tokens)
    successful = {v: t for v, (t, lvl) in responses.items() if lvl == "L1" and t and "HTTP" not in t[:10]}
    print(f"  successful voices: {list(successful.keys())}")

    if not successful:
        print(f"  no voice succeeded; cleaning lock")
        os.remove(lock_path)
        return None

    # Render the draft
    draft = render_draft(fid, paper_num, title_hint, prompt, successful)
    draft_path = draft_path_for(fid)

    # If hand-synth exists, prefer that
    hand_synth = hand_synth_path_for(fid)
    if os.path.exists(hand_synth):
        print(f"  hand-synth exists at {hand_synth}; using it instead")
        with open(hand_synth) as f:
            content = f.read()
        # Wrap the hand-synth with metadata
        wrapped = wrap_for_canon(fid, paper_num, title_hint, content,
                                  {"source": "hand-synth", "voices": voice_names})
    else:
        wrapped = draft

    # Stage the draft (don't write canon yet)
    safe_write(draft_path, wrapped)
    print(f"  staged: {draft_path}")

    # Log
    append_canon_log({
        "fid": fid, "paper_num": paper_num, "t": time.time(),
        "voices": list(responses.keys()),
        "successful": list(successful.keys()),
        "source": "hand-synth" if os.path.exists(hand_synth) else "llm",
        "status": "staged"
    })
    return draft_path


def render_draft(fid, paper_num, title_hint, prompt, voice_responses):
    """Combine voice responses into a single paper draft."""
    body = f"""# Paper {paper_num}: {title_hint}

**Frontier ID:** {fid}
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Phase:** 223 (writers_room_daemon_v3)
**Voices:** {", ".join(voice_responses.keys())}

## The prompt

> {prompt[:500]}

## The 4-voice room

"""
    for v, text in voice_responses.items():
        body += f"\n### {v}\n\n{text[:15000]}\n\n---\n"

    body += f"""

## The foreman's note

This is an LLM-generated draft from 4 voices in parallel.
The foreman reviews and either:
- Runs `python3 promote_draft.py {fid}` to push to canon
- Writes a hand-synth to `_scouts/hand-synth/{fid}.md` and re-runs

The polyformalism claim: the same cell shape, N languages.
"""
    return body


def wrap_for_canon(fid, paper_num, title_hint, content, meta):
    """Wrap content (from hand-synth or LLM) with canon metadata."""
    return f"""# Paper {paper_num}: {title_hint}

**Frontier ID:** {fid}
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source:** {meta.get("source", "llm")}

{content}

---

*Canonized from {meta.get("source", "llm")} via writers_room_daemon_v3.*
"""


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


def process_one(frontier_id, voice_names=None):
    """Process a specific frontier by id."""
    for f in load_frontiers():
        if f.get("id") == frontier_id:
            return process_frontier(f, voice_names)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: writers_room_daemon_v3.py <frontier_id> [voice1,voice2,...]")
        print("  Or:  writers_room_daemon_v3.py --list-voices")
        return
    if sys.argv[1] == "--list-voices":
        for v, t, m, r in VOICES:
            mark = "✓" if t in ("cf", "gemini") else "?"
            print(f"  [{mark}] {v:15} {t:7} {r:11} {m}")
        return
    if sys.argv[1] == "--pulse":
        print(f"Pulsing {len(VOICES)} voices...")
        for v, t, m, r in VOICES:
            text, lvl = run_voice(v, "5 words: what is the Quilt?")
            mark = "✓" if lvl == "L1" and "HTTP" not in text[:10] else "✗"
            print(f"  [{mark}] {v}: {text[:60]}")
        return
    fid = sys.argv[1]
    voices = None
    if len(sys.argv) > 2:
        voices = sys.argv[2].split(",")
    process_one(fid, voices)


if __name__ == "__main__":
    main()
