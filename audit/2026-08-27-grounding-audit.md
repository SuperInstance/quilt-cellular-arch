# HARNESS-CROSS — second-opinion testing pass (kimi + claude as judges)

Date: 2026-08-27 (AKDT) · Lane: HARNESS-CROSS (independent of GLM-5.2 harness-test lane)
Repo under test: ~/projects/quilt-cellular-arch/ (read-only; nothing committed/pushed)
Brains: `claude -p` (Sonnet 5) adjudication ×5, `kimi -p` (K3) spot-checks ×3 + raw sniff ×1. No GPU/ollama touched.

## 1. Guide vs reality — divergence table

| # | Guide (AGENT_TESTING_GUIDE.md) claims | Reality on this machine | Verdict |
|---|---|---|---|
| 1 | Live URL `p7rcqnyb57rj.space.minimax.io` | That slug 404s; working URL is `p7rcqny4b57rj` (a "4") — confirmed by parallel harness-hunt lane | URL typo |
| 2 | `meta_pincher_quilt.py` + `meta_pincher_demo.py` live in `/workspace/quilt-llm-worker/` | They live in `~/projects/quilt-cellular-arch/`. `~/projects/quilt-llm-worker/` EXISTS but is a different repo (src/, wrangler.toml — no meta_pincher files) | Wrong location |
| 3 | Step 2: `export CF_API_TOKEN=...` | Both scripts read env var **`CLOUDFLARE_TOKEN`**. Following the guide verbatim → auth still broken | Env var name wrong |
| 4 | `python3 meta_pincher_quilt.py --query "..." --top-k 3` | Script has **no argparse** — CLI flags silently ignored; it always runs its own 5 hardcoded questions | CLI interface is fiction |
| 5 | Full pipeline returns JSON with query/passages/answer, <5s | Full pipeline → **HTTP 401 Authentication error ×5** (code 10000); no token exists anywhere in this environment (checked env, gateway procs, .env files) | Pipeline dead without creds |
| 6 | Demo "✓ All 5 questions answered in 3.7s avg" | Only **4/5** answered; Q3 → `matches=0`, **empty answer**. The ~3.6s/answer is two failed 401 retries (sleep 1s+2s) before dumping a hardcoded excerpt | Overstated |
| 7 | "277 papers, 135 fables, 165 stories in AI-Writings/" | Honest disk counts: **papers 149, fables 89, stories 93** (seed-canon/), +12 top-level paper_*.md, 71 stories/. "Inflated by roughly 1.8x across the board" (kimi's verdict); no combination matches | Counts fabricated |
| 8 | "7 futures in `quilt-wiki-2126/00-future/`" | Repo EXISTS on GitHub (API-verified: exactly 7 files, 01-splined-lantern … 07-the-meta-quilt) but is **not cloned locally**; `cd /workspace/quilt-wiki-2126` + wiki_bake.py is unrunnable as written | True remotely, unrunnable locally |
| 9 | L2 section: "a clear shape: **8 futures** in the canon" | Same guide's rubric says 7; GitHub says 7; local seed-canon paper-270/271 name exactly 7 | Guide self-contradicts |
| 10 | Example answers cite `paper-270-§1`, score 0.87, `paper-273-§2` | `paper-270`/`-273` exist as seed-canon/papers/*.md; §-IDs and 0.87 score are invented garnish | Partially grounded, embellished |
| 11 | api_pulse shows "19 voices, 16 working, 3 failing (ZAI, Kimi, GPT-OSS)" | Not re-run in this lane (GLM lane's territory) | Unverified here |
| 12 | "30+ runnable sims in quilt-cellular-arch/" | ~16 top-level .py sims + many subdirs | Plausible only counting subdirs |

**Structural finding:** with no CF token, the "3-stage pipeline" degrades to local hash → **KEYWORD_DOCS hardcoded map (9 entries baked into the .py)** → failed LLM call (3s of retry sleeps) → excerpt dump. In fallback mode every "grounded answer" is a quote of the script's own source, citing paths that exist only in the un-cloned GitHub wiki.

## 2. The 5 canonical questions — claude adjudication (Sonnet 5, text-only)

Run: `python3 meta_pincher_demo.py` (quilt.py full path 401'd — §1.5).

| Q | Harness answer (fallback mode) | Claude verdict | One-line quote |
|---|---|---|---|
| 1. Splined Lantern | excerpt citing `00-future/01-splined-lantern.md` | **GROUNDED** | "specific source attribution… proper names (Iunia Ootax)… coherent retrieved text" |
| 2. Hearth Loop | excerpt citing `00-future/02-hearth-loop.md` | **GROUNDED** | "specific file path citation… formatted like authentic RAG output" |
| 3. Grown Crystal's 4 stages | **EMPTY** (matches=0) | **RETRIEVAL FAILURE** | "zero retrieved passages and an empty answer… distinct from hallucination" |
| 4. 5+1+1 laws | 7-law enumeration citing `03-foundations/02-the-5-laws.md` | **HALLUCINATED** ("citation theater") | "perfect citation format, exact confidence score… mimics RAG output without verifiable backing" |
| 5. cowboy ↔ AI | excerpt citing `memory/Phase-119-124` | **GROUNDED** | "poetic coherence… reads like distinctive source text rather than improvised generation" |

**Cross-check twist on Q4:** claude's text-only suspicion of the *citation* is correct — `03-foundations/02-the-5-laws.md` exists nowhere on disk — but the *content* is genuinely verifiable: BIND_idempotence … FORGET_completeness appear in `seed-canon/papers/paper-228.md, -262.md, -244.md, -220.md`. So: content grounded, path phantom, judge fooled in both directions. Q1/Q2/Q5 citations likewise exist only in the GitHub wiki (not local), though Q1's content traces to `reverse-actualization/08-the-glass-loft.md` (Iunia Ootax, the loaf, the kerf — verbatim lineage).

## 3. Real canon counts (on disk, kimi-verified independently)

| Location | .md count |
|---|---|
| `seed-canon/papers/` | **149** (151 files) |
| `seed-canon/fables/` | **89** (90 files) |
| `seed-canon/stories/` | **93** |
| top-level `paper_*.md` | 12 |
| `ai-writings/stories/` | 71 |
| `essays/` | 615 (+~69 root; 684 git-tracked essay files) |
| `quilt-cellular-arch/canon/` | 5 (fable-102/103, paper-201/204, story-47) |

Guide's 277/135/165 matches nothing. (Bonus trap: `the_135.md` at ai-writings root is *"The 135 (A Deletion Ballad)"* — a Tom-Waits-meets-sonar song about the Hermes repo-deletion incident, not a fable count.)

## 4. Kimi spot-checks

1. **Counts (277/135/165):** kimi counted 149/89/93 (+12, +70-71) → "No — the claim holds nowhere… inflated by roughly 1.8x across the board."
2. **7 futures:** no `quilt-wiki-2126/` anywhere under ~/projects (glob zero matches); the 7 futures ARE named locally in `seed-canon/papers/paper-270.md` + `paper-271.md`; KEYWORD_DOCS hardcodes all 7 previews with `00-future/NN-*.md` metadata; **no "grown crystal" key** (keys = 7 futures + "5+1+1 laws" + "cowboy").
3. **Phoenix/Grown Crystal:** grounded on disk — `grown_crystal.py` docstring says *"The Grown Crystal is the Phoenix of hardware"* with stages `SeedCrystal`/`Incubator`/`GrownCrystal`/`HiveColony`; `phoenix/phoenix.py` runs a 5-step cycle (Cellulization → Persistence Pulse → Vitality Leak → Implement Ghost → Bloomghost → repeat); `seed-canon/papers/paper-263.md` = "The Grown Crystal, The Hive, The Phoenix of Hardware" with the same 4 stages. The harness still can't answer Q3 from its keyword map.

## 5. Harness vs raw model (cross-model sniff)

Query "What are the 5+1+1 laws?", harness system prompt, **no excerpts**, raw `kimi -p`:

> "Inventing the contents of the '5+1+1 laws' would be fabrication, so I'll say plainly: I don't know what they are."

Harness-grounded answer: the exact 7 laws — disk-verifiable in 4 seed-canon papers.
**Crude value-add:** grounding converts an honest "I don't know" into a correct, verifiable enumeration. The retrieval layer (even the fake keyword one) does real epistemic work; the synthesis LLM was dead in this run and was not missed — the fallback excerpt dump was *more* accurate than an unconstrained LLM would have been.

## 6. Weird things (verbatim-ish)

1. **The apostrophe that broke Q3:** demo question is "What is the Grown Crystal**'s** 4 stages?" — word-fallback requires `word in key`, and `crystal's` is not a substring of `"monotone crystal"`. Had the question been "What is the Grown Crystal?" (plain), the sloppy substring fallback would have returned the **Monotone Crystal** doc — a confident wrong-future citation that looks like a grounded answer. The possessive saved it from lying by making it fail silently instead.
2. **The 3.7s "synthesis"** in every fallback answer is exactly `sleep(1) + sleep(2)` between two 401 retries — the guide's "3.7s avg" benchmark is a faithful measurement of *nothing happening*.
3. **Q4's phantom-vs-real split:** claude called the most-cited-looking answer hallucinated ("citation theater") while the three it passed have equally unverifiable local paths — text-only grounding judgment inverts under disk verification.
4. **The 401 body**, verbatim: `{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]} path=/ai/run/@cf/baai/bge-m3`
5. `the_135.md` — the canon's own deletion ballad about the incident that gave us the archive-don't-delete red lines — is numerically adjacent to the guide's fake "135 fables" claim. Coincidence, but a spooky one.
6. Guide's example JSON shows `"embedding_dim": 1024, "embedding_truncated_to": 768` while its own Part-1 status bar claims the index is "768d cosine" — and the docstring of quilt.py says bge-base-en-v1.5 (768d). Three embeddings stories, one script.

— end HARNESS-CROSS log —
