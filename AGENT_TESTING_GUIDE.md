# Testing Guide for the Quilt Agent Harness

**Live URL:** https://p7rcqny4b57rj.space.minimax.io
**Repo:** https://github.com/SuperInstance/quilt-cellular-arch
**File:** `agent-harness.html` (21.5KB, self-contained, no external deps)

This guide gives your local agent step-by-step instructions for testing the
Agent Harness — both as a webpage (visual) and as a vectorized shaping tool
(via the Meta-Pincher-Quilt API).

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

The Meta-Pincher-Quilt needs:
- `CF_ACCOUNT_ID` — your Cloudflare account ID
- `CF_API_TOKEN` — a token with Workers AI + Vectorize permissions
- `CF_VECTORIZE_INDEX` — defaults to `ai-writings` (768d, cosine)

```bash
export CF_ACCOUNT_ID="your_account_id_here"
export CF_API_TOKEN="your_token_here"
export CF_VECTORIZE_INDEX="ai-writings"
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
======================================================================
META-PINCHER-QUILT DEMO — vectorized, stateless, CF-native
======================================================================

Q: What is the Splined Lantern?
A: The Splined Lantern is a physical LLM made of glass and light...
  retrieved: 3 passages from paper-270-§1, paper-270-§3, paper-273-§2

Q: What is the Hearth Loop?
A: The Hearth Loop is a self-training loop where the glass learns...
  retrieved: 3 passages from paper-270-§2, paper-273-§1

...

✓ All 5 questions answered in 3.7s avg
```

### Step 4: Run with Cloudflare (full pipeline)

Once your credentials are set:

```bash
python3 meta_pincher_quilt.py --query "What is the Splined Lantern?" --top-k 3
```

Expected response shape:

```json
{
  "query": "What is the Splined Lantern?",
  "embedding_model": "@cf/baai/bge-m3",
  "embedding_dim": 1024,
  "embedding_truncated_to": 768,
  "retrieve_index": "ai-writings",
  "retrieve_top_k": 3,
  "passages": [
    {
      "id": "paper-270-§1",
      "score": 0.87,
      "text": "The Splined Lantern is a physical LLM made of glass and light..."
    },
    {
      "id": "paper-270-§3",
      "score": 0.81,
      "text": "The lantern is built from a photorefractive crystal..."
    }
  ],
  "synthesis_model": "@cf/meta/llama-3.1-8b-instruct-fp8",
  "answer": "The Splined Lantern is a physical LLM of glass and light that bends its own training light into the medium. It is the F1 future function in the 2126 wiki.",
  "elapsed_ms": 3700
}
```

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

After L2, you should see a clear shape: 8 futures in the canon, each
with its own definition.

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
| Page loads at the public URL | https://p7rcqnyb57rj.space.minimax.io |
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
| 277 papers, 135 fables, 165 stories in `AI-Writings/` | ✓ |
| 7 futures in `quilt-wiki-2126/00-future/` | ✓ |

---

## Part 6: Troubleshooting

| Symptom | Fix |
|---|---|
| Page won't load | Check https://p7rcqnyb57rj.space.minimax.io is reachable |
| 404 on repo | `git pull` the latest from main |
| CF API returns 400 | Embedding model rate-limited; use `meta_pincher_demo.py` (local fallback) |
| CF API returns 401 | Check `CF_API_TOKEN` is set and has Workers AI + Vectorize scopes |
| CF API returns 503 | Workers AI temporarily down; demo will fall back automatically |
| Empty passages | Index `ai-writings` may be empty; check CF dashboard |
| Demo returns local fallback only | Expected when CF is rate-limited; still gets a grounded answer |

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
