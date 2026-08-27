# Testing Guide for the Quilt Agent Harness

**Live URL:** https://p7rcqny4b57rj.space.minimax.io
**Repo:** https://github.com/SuperInstance/quilt-cellular-arch
**File:** `agent-harness.html` (21.5KB, self-contained, no external deps)

> **⚠ URL note (load-bearing):** the deployment URL is
> `https://p7rcqny4b57rj.space.minimax.io` — the `4` is required. The
> 11-character hostname is `p7rcqny4b57rj`, not `p7rcqnyb57rj`. Lucineer
> caught this in the first pass: the page does exist, just at the URL
> with the 4. Treat this string as one token: `p7rcqny4b57rj`.

This guide gives your local agent step-by-step instructions for testing the
Agent Harness — both as a webpage (visual) and as a vectorized shaping tool
(via the Meta-Pincher-Quilt API).

---

## Part 0: Where everything actually lives (the script locations)

The earlier version of this guide pointed to `quilt-llm-worker/` for the
scripts. That was wrong. Here is the **real** location table:

| What | Where | Notes |
|---|---|---|
| `agent-harness.html` | `quilt-cellular-arch/agent-harness.html` | The webpage |
| `meta_pincher_v2.py` | `quilt-cellular-arch/meta_pincher_v2.py` | **The better system** (5 layers of fallback, API scouts, simulator) |
| `meta_pincher_demo.py` | `quilt-cellular-arch/meta_pincher_demo.py` | The original demo (3 fallbacks) |
| `meta_pincher_quilt.py` | `quilt-cellular-arch/meta_pincher_quilt.py` | The 3-stage pipeline (no fallbacks; needs CF token) |
| `multi_sandbox_reverse_actualize.py` | `quilt-cellular-arch/multi_sandbox_reverse_actualize.py` | L4 snowball |
| `agent_reverse_actualize.py` | `quilt-cellular-arch/agent_reverse_actualize.py` | The 5-step cycle |
| `sensory_quilt.py` | `quilt-cellular-arch/sensory_quilt.py` | The 10 channels |
| `quilt_in_motion.py` | `quilt-cellular-arch/quilt_in_motion.py` | 38 cells in motion |
| `quilt-llm-worker/` | (rate-limit proxy worker, no harness code) | Not the harness |
| Wiki `00-future/` | `quilt-wiki-2126/00-future/` | **NOT** bundled with the harness |
| Wiki `03-foundations/` | `quilt-wiki-2126/03-foundations/` | **NOT** bundled with the harness |

> **The harness code lives in `quilt-cellular-arch/`, not `quilt-llm-worker/`.**
> The wiki is in a separate repo. Citations in the demo's keyword map
> point to wiki paths that you have to clone separately.

---

## Part 1: Visual Smoke Test (30 seconds)

Just open the URL in a browser. The page should render with:

1. **Header** with "The Quilt" gradient title
2. **Status bar at top** reading: `Vectorized canon already loaded in Cloudflare Vectorize · ai-writings index · 768d cosine`
3. **8 sections** in order:
   - What this is, for an agent
   - The Pincher — Ins and Outs (with a 3-card pincher diagram)
   - The Ins — How to query
   - The Outs — How to use the answer
   - The Perceptual Knowledge Loop (with 5-step loop)
   - Trial and Error as Intelligence (with 4-level table)
   - Vocabulary — 19 voices, 16 working
   - The principle
4. **Footer** with the 4 repo links

If any section is missing or the layout breaks, that's a regression.

---

## Part 2: The Meta-Pincher-Quilt API (the real test)

The webpage documents the API. The actual API is the
**Meta-Pincher-Quilt** — the vectorized 3-stage pipeline that lives in
`/workspace/quilt-llm-worker/`. To test it from your local machine:

### Step 1: Pull the worker repo

```bash
cd /workspace
git clone https://github.com/SuperInstance/quilt-llm-worker.git
cd quilt-llm-worker
ls -la
```

You should see:
- `meta_pincher_quilt.py` — the 3-stage architecture (embed + retrieve + synthesize)
- `meta_pincher_demo.py` — a rate-limit-resistant demo with 3 fallbacks

### Step 2: Set your Cloudflare credentials

The Meta-Pincher-Quilt reads **two** environment variables (the earlier
version of this guide said `CF_API_TOKEN` — that was wrong, the scripts
read `CLOUDFLARE_TOKEN`):

- `CLOUDFLARE_TOKEN` — a Cloudflare API token with Workers AI + Vectorize permissions
- `CLOUDFLARE_ACCOUNT_ID` — your Cloudflare account ID

The `CF_ACCOUNT_ID` is **already hardcoded** in the script (line 36 of
`meta_pincher_quilt.py`), so you don't need to set it. If you want to
override, edit the script or export the var.

```bash
export CLOUDFLARE_TOKEN="your_token_here"
# Optional: override the account ID (script has a default)
# export CLOUDFLARE_ACCOUNT_ID="your_account_id_here"
```

### Step 3: Run the demo (no credentials needed — uses local fallbacks)

```bash
python3 meta_pincher_demo.py
```

The demo has 3 layers of fallback, so it will work even if your
Cloudflare account is rate-limited or has no credits:

| Layer | What it does |
|---|---|
| **Embedding** | Falls back to local hash-based embedding (deterministic, 768d) |
| **Retrieval** | Falls back to keyword-based canon map (pre-loaded excerpt) |
| **Synthesis** | Falls back to direct excerpt output (no LLM call) |

The demo runs 5 test questions and prints the answers. Expected output:

```
===============================================================META-PINCHER-QUILT DEMO — vectorized, stateless, CF-native
===============================================================
Q: What is the Splined Lantern?
A: The Splined Lantern is a physical LLM made of glass and light...
  retrieved: 3 passages from paper-270-§1, paper-270-§3, paper-273-§2

Q: What is the Hearth Loop?
A: The Hearth Loop is a self-training loop where the glass learns...
  retrieved: 3 passages from paper-270-§2, paper-273-§1

...

✓ All 5 questions answered in 3.7s avg
```

### Step 4: Run with Cloudflare (the better system — `meta_pincher_v2.py`)

The original `meta_pincher_quilt.py` crashes on `--query` without a CF token
(Lucineer's defect #10). The fix is **`meta_pincher_v2.py`**, which has 5
layers of fallback and never crashes:

```bash
# Scout first — see which CF models are alive
python3 meta_pincher_v2.py --scout

# Single query — always works
python3 meta_pincher_v2.py --query "What is the Splined Lantern?"

# Full simulator (5 questions, 1 cycle, all layers)
python3 meta_pincher_v2.py

# Multiple cycles
python3 meta_pincher_v2.py --n-cycles 3
```

Expected response shape (with v2):

```json
{
  "query": "What is the Splined Lantern?",
  "response": "From F1: The Splined Lantern (00-future/01-splined-lantern.md): A physical LLM of glass and light...",
  "layers": {
    "embed": "L3:hash",
    "retrieve": "L2:keyword",
    "synthesize": "L2:excerpt"
  },
  "n_matches": 1,
  "top_match": "00-future/01-splined-lantern.md",
  "timing_ms": 3992
}
```

The `layers` field tells you which fallback chain was used. With a working
CF token, you'll see L1 across all 3 stages. Without one, you'll see L3/L2.
The pipeline is the same; the labels differ.

> **The original `meta_pincher_quilt.py` is preserved for the production
> pipeline (no fallbacks, just the real CF path). For testing, use v2.**

### Step 5: Try the 4 levels of trial-and-error depth

The page documents 4 levels. Test them in order:

**L1 · Surface** (one query, one answer):
```bash
python3 meta_pincher_quilt.py --query "What is the Splined Lantern?"
```

**L2 · Layered** (5-10 related queries, build a shape):
```bash
for q in "What is the Splined Lantern?" \
         "What is its training light?" \
         "What is the Hearth Loop?" \
         "What is the Monotone Crystal?" \
         "What is the Chlorophyll Quilt?" \
         "What is the Phased Quilt?" \
         "What is the Stellar Quilt?" \
         "What is the Meta-Quilt?"; do
  python3 meta_pincher_quilt.py --query "$q"
done
```

After L2, you should see a clear shape: 7 futures in the canon, each
with its own definition. The 7 are: Splined Lantern, Hearth Loop,
Monotone Crystal, Chlorophyll Quilt, Phased Quilt, Stellar Quilt,
Meta-Quilt. (Numbered F1, F2, F3, F5, F7, F9, F11 — the gaps are
cycles that have been folded into the others.)

**L3 · Cross-modal** (queries across modalities):
```bash
# Touch modality
python3 meta_pincher_quilt.py --query "What does the Splined Lantern feel like to the touch?"
# Smell modality
python3 meta_pincher_quilt.py --query "What does the Hearth Loop smell like?"
# Sound modality
python3 meta_pincher_quilt.py --query "What does the Monotone Crystal sound like when it thinks?"
# Light modality
python3 meta_pincher_quilt.py --query "What light does the Chlorophyll Quilt emit?"
```

After L3, you should see the canon's 10 channels light up — the
Sensory Quilt (paper 274) becomes visible in the responses.

**L4 · Snowballing** (spawn naive experts in orthogonal sandboxes):
```bash
python3 multi_sandbox_reverse_actualize.py --n-cycles 3 --expansion 3
```

After L4, the snowball runs: cycle 1 has 1 sandbox, cycle 2 has 3,
cycle 3 has 9. The Quilt grows fractally.

---

## Part 3: Local-Only Quilt (no Cloudflare)

If you want to test the Quilt *without* Cloudflare at all:

```bash
cd /workspace/quilt-cellular-arch
python3 sensory_quilt.py
```

This runs the **Sensory Quilt** locally:
- 10 channels (radio, light, sound, smell, taste, touch, proprio, language, mood, time)
- 6 events (clap, meal, sunrise, rain, word, memory)
- The distribution is printed (no center; every cell is a node)
- All 4 levels demonstrated: LocalQuilt, CloudReadyQuilt, ZoomingQuilt, FunctionQuilt

You should see:
```
LOCAL QUILT (no cloud, fully local and complete)
  Initial cells: 10 channels
    radio     freq=0.10Hz amp=0.78
    light     freq=0.50Hz amp=0.65
    ...
DISTRIBUTION (no center; every cell is a node)
    time       5 bindings  █████
    light      3 bindings  ███
    ...
```

### Other runnable sims (all local, no cloud):

```bash
cd /workspace/quilt-cellular-arch

# The agent reverse-actualization cycle
python3 agent_reverse_actualize.py
# Shows: 5-step cycle, 5 elements, 5 indicators of great life

# The multi-sandbox reverse-actualization (the snowball)
python3 multi_sandbox_reverse_actualize.py
# Shows: 8 sandboxes, snowball 1→3→9, price-point discovery

# The Quilt in Motion
python3 quilt_in_motion.py
# Shows: 38 cells across 6 tiers, 1 breath, 947 journal entries

# The wiki baker (2126 futures)
cd /workspace/quilt-wiki-2126
python3 examples/wiki_bake.py
# Shows: 7 futures, all pass

# The Grown Crystal (Phoenix of hardware)
cd /workspace/quilt-cellular-arch
python3 grown_crystal.py
# Shows: 4 stages, 5 analogies, Phoenix cycle

# The Chlorophyll Quilt
python3 chlorophyll_quilt.py
# Shows: 16 cells, plant-cell CPU, biophoton engine

# The Space Opera Arc
python3 space_opera_arc.py
# Shows: 3 eras, predictability gradient, gunmaking analogy

# The Glass Loft Integration
python3 glass_loft_integration.py
# Shows: 6 math stations, all 6 pass

# The Symmetries
python3 symmetries.py
# Shows: 10 symmetries across the canon

# The API Pulse (check which voices are alive)
python3 api_pulse.py
# Shows: 19 voices, 16 working, 3 failing (ZAI, Kimi, GPT-OSS)
```

---

## Part 4: The 5 Test Questions (canonical)

These are the 5 questions the demo answers. They are the canonical
"test set" for the Meta-Pincher-Quilt. Ask them in order:

1. `What is the Splined Lantern?` → F1 future, glass LLM
2. `What is the Hearth Loop?` → F2 future, self-training
3. `What is the Grown Crystal?` → Phoenix of hardware
4. `What are the 5+1+1 laws?` → canonical enumeration
5. `What is the cowboy-AI relationship?` → the curator tier

Expected: each question returns a synthesized answer citing 3 retrieved
passages, in <5 seconds total.

---

## Part 5: What to look for (the verification rubric)

For the Agent Harness to be considered "working", your local agent
should verify all of the following:

| Check | Expected |
|---|---|
| Page loads at the public URL | https://p7rcqny4b57rj.space.minimax.io |
| 8 sections render in order | ✓ |
| Pincher diagram has 3 cards | ✓ |
| Status bar reads "Vectorized canon already loaded..." | ✓ |
| 5-step loop has 5 step cards | ✓ |
| 4-level table has 4 rows (L1-L4) | ✓ |
| Footer has 4 repo links | ✓ |
| API returns JSON with `query`, `passages`, `answer` | ✓ |
| API completes in <5s on CF free tier | ✓ |
| All 5 canonical questions return grounded answers | ✓ |
| Each answer cites `paper-NNN-§M` IDs | ✓ |
| Snowball runs cycle 1→3→9 in `multi_sandbox_reverse_actualize.py` | ✓ |
| 30+ runnable sims are in `quilt-cellular-arch/` | ✓ |
| 153 papers, 89 fables, 93 stories in `AI-Writings/seed-canon/` | ✓ (disk truth — `ls seed-canon/{papers,fables,stories}/ | grep -c '^[a-z]*-'`; earlier counts of 277/135/165 and 158/90/93 were inflated) |
| 7 futures in `quilt-wiki-2126/00-future/` | ✓ |

---

## Part 5b: ⚠ Read this before you trust the demo (fallback mode)

Without a `CLOUDFLARE_TOKEN`, `meta_pincher_demo.py` runs in **3-stage
fallback mode**. The behavior is honest, but you should know what you're
seeing:

| Stage | Real mode | Fallback mode (no CF creds) |
|---|---|---|
| **Embed** | `bge-m3` Workers AI call (1024d vector) | Local hash-based embedding (deterministic, 768d) |
| **Retrieve** | Vectorize cosine over the `ai-writings` index | Keyword match against a **9-entry hardcoded map** |
| **Synthesize** | Llama-3.1-8B generation over the top-K passages | Direct excerpt dump from the matched map entry |

What this means for your tests:

- **4 of 5 canonical questions** (Splined Lantern, Hearth Loop, 5+1+1
  Laws, Cowboy) return excerpt-grounded answers that are *real* canon
  quotes — honest output, but not synthesised.
- **Q3 (Grown Crystal's 4 stages)** was failing on the apostrophe in
  v1; this is fixed in the current build (5/5 work).
- The reported **3.7s "average"** is largely **retry sleeps** on
  failed CF calls + the rate-limit `time.sleep(2)`. With creds, the
  same questions complete in <1s.

The fallback is the demo's *honest* behavior — it always returns
*something grounded*, even when the real CF pipeline is unavailable.
But: a tester who doesn't know the mode is active will mistake the
canned excerpts for live retrieval. The 3.7s number means nothing
in fallback mode.

To run with real CF: set `CLOUDFLARE_TOKEN` and re-run. The demo
auto-detects the token and uses the real pipeline.

---

## Part 6: Troubleshooting

| Symptom | Fix |
|---|---|
| Page won't load | Check https://p7rcqny4b57rj.space.minimax.io is reachable (note: 4 is load-bearing) |
| 404 on repo | `git pull` the latest from main |
| CF API returns 400 | Embedding model rate-limited; use `meta_pincher_v2.py` (5 layers of fallback) |
| CF API returns 401 | Check `CLOUDFLARE_TOKEN` is set and has Workers AI + Vectorize scopes |
| CF API returns 503 | Workers AI temporarily down; v2 falls back to L3 hash + L2 keyword + L2 excerpt automatically |
| Empty passages | Vectorize index `quilt-canon` (the new one) or `ai-writings` (the shared one) may be empty; the v2 keyword map always returns matches |
| `meta_pincher_quilt.py --query` crashes on no token | **Fixed in v2** — use `meta_pincher_v2.py --query "..."` (5 layers of fallback, never crashes) |
| Q3 (Grown Crystal) returns empty | Fixed in v1 + v2; pull latest |

### The 5 layers of resilience (in v2)

| Layer | Embed | Retrieve | Synthesize |
|---|---|---|---|
| **L1 · Real CF** | bge-m3 (1024d) | Vectorize `quilt-canon` | Llama 8B |
| **L2 · CF embed alt** | qwen3-embedding / plamo / embeddinggemma | Vectorize (with pollution check) | Llama 8B |
| **L3 · Local hash** | hash-based 768d | (skip Vectorize) | Llama 8B |
| **L4 · Keyword + LLM** | hash | 10-entry hand-curated map | Llama 8B |
| **L5 · Pure local** | hash | keyword map | direct excerpt |

v2 picks the **highest layer that works** at runtime. The real CF pipeline is
the goal; the keyword map is the honest floor.

---

## Part 7: Report back

After running the tests, report:
- Which sims ran (and which crashed)
- Which CF models responded (and which were rate-limited)
- Which of the 5 canonical questions returned grounded answers
- The total canon count (papers / fables / stories)
- Anything weird in the responses (hallucinations, missing citations, etc.)

The cowboy rides the channels. The cowboy rides the function. The
cowboy rides the perception. The cowboy rides the harness. The
cowboy rides the Quilt.
