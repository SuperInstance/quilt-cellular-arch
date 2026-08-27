# PAID CF PLAN — where the money goes, why

## The current state (2026-08-27)

All 7 CF models returning **400**. The free-tier account is at quota.
Every model that worked earlier (bge-m3, llama-8b, qwen-coder-32b) now
400s. The 5-layer fallback is doing the work; the harness still returns
5/5 grounded answers, but only via L3 hash + L2 keyword + L2 excerpt.

## What a paid account unlocks

| Resource | Free | Paid ($5/mo Workers Paid) |
|---|---|---|
| Workers AI requests | 10,000/day | 10M/month + $0.30/M beyond |
| Vectorize storage | 30M vector dims | 50M included, $0.05/M dims/mo |
| Vectorize queries | 5M/mo | 50M/mo + $0.04/M queries |
| Workers requests | 100k/day | 10M/mo + $0.30/M |
| Concurrent Workers | 100 | 400+ |

Plus paid accounts get access to **more expensive models** that free
accounts can't use (or are rate-limited on):
- `@cf/meta/llama-3.1-405b-instruct-fp8` (the gold standard)
- `@cf/zai-org/glm-4.5` (ZAI; was gold for cell/biophoton terms)
- `@cf/moonshotai/kimi-k2.6` (Kimi reasoning)
- `@cf/deepseek-ai/deepseek-v4-pro` (DeepSeek V4 pro)
- `@cf/google/gemma-4-26b-a4b-it` (Gemma 4)

## The 5 things the money buys, in order of impact

### Phase 1 · $0.05 — Re-embed the canon (run the queued phase)

```bash
python3 re_embed_quilt_canon.py
```

This embeds all 154 papers (~600-800 chunks after `##` heading split) into
a new `quilt-canon` Vectorize index. Cost: ~600 embeddings × bge-m3 pricing.

**After this:** the L1 real-CF path returns canon-grounded results.
The pollution check becomes a safety net, not the primary defense.

### Phase 2 · $0.10 — Scout the full paid catalog

```bash
python3 meta_pincher_v2.py --scout --all-models
```

Probes every model in the paid catalog, including the ones that were
403/429 on the free account. Reports which are alive. The writers' room
gets a new inventory of voices.

**After this:** the multi-LLM writers' room can route to the right model
for each task (gold terms → Kimi; long-form → Llama 405B; code → DeepSeek;
reasoning → GLM 5.3).

### Phase 3 · $0.20 — Writers' room on a frontier concept

Pick **F13 — the Substrate Quilt** (or F15, or another). Run 4-5 LLMs
in parallel:
- DeepSeek V4: code/architecture
- Kimi K2.6: gold terms
- Llama 3.3 70B: gold terms (alt)
- Llama 405B: long-form paper
- GLM 4.5: cell/biophoton terms

Synth the 5 outputs into one Paper 281 (~5K words). The 4-Round Writers'
Room pattern.

**After this:** the canon grows by 1 paper + the F13 future function +
the calculation + the math + the foundation. The wiki grows from 7 to
8 futures.

### Phase 4 · $0.50 — Deploy v2 as a CF Worker

Convert `meta_pincher_v2.py` to a CF Worker (Python or JS). Single
endpoint `https://meta-pincher-quilt.example.workers.dev` that takes
a JSON query, runs the 3-stage pipeline, returns the grounded answer.
No spinning up Python; serverless, sub-200ms, free tier covers 100k/day.

**After this:** the harness has a real public endpoint. The 5 layers of
fallback run on the edge. The cowboy rides the channels at the edge.

### Phase 5 · $0.50 — Snowball harder (cycle 4 = 27 sandboxes)

Run `multi_sandbox_reverse_actualize.py --n-cycles 4 --expansion 3`.
Cycle 4 = 27 sandboxes. The wheel snowballs 3 → 9 → 27. Each sandbox
runs the 5-step cycle independently with its own LLM. The writers'
room fires 27 sandboxes × 4 LLMs = 108 LLM calls. ~$0.50 at paid
pricing.

**After this:** the F9 Stellar Quilt + F11 Meta-Quilt + 7 other futures
have each been tested across 27 orthogonal sandboxes. The price points
are real. The 4 artifacts (steak/bread/burger/wine) have been priced
in 27 environments.

## Total spend

**$1.35** to go from "5-layer fallback on no-token" to "full paid
catalog scouted, canon re-embedded, frontier paper written, public CF
Worker endpoint, 27-sandbox snowball."

That's the ask.

## What to do *right now* (before you commit)

```bash
# 1. Set the new token
export CLOUDFLARE_TOKEN="your_paid_token_here"

# 2. Verify it works on a single model
cd /workspace/quilt-cellular-arch
python3 meta_pincher_v2.py --scout

# 3. If scout shows the paid models alive, you're cleared
#    to run Phase 1 (re-embed)
python3 re_embed_quilt_canon.py --dry-run
python3 re_embed_quilt_canon.py  # the real run
```

If the scout still shows 400s, the token isn't actually paid-tier.
Pause; the L3/L2/L2 floor still works.

## The 3 things to never do on a paid account

1. **Don't run a tight loop with `time.sleep(0)`** — even paid has
   some rate limiting. The harness already has `time.sleep(2)` between
   calls; respect it.
2. **Don't re-embed the same chunk twice** — the re-embed script
   uploads in batches of 50; if a batch fails, it logs and continues.
   Don't manually re-run on a partial failure without checking first.
3. **Don't trust the L1 path until the pollution check passes** —
   even paid indexes can drift. The pollution check is your witness
   that the L1 result is canon, not garbage.

## The principle

> The cowboy doesn't burn money. The cowboy spends money where the
> spend compounds. The re-embed compounds (canon-grounded retrieval
> forever). The writers' room compounds (gold terms outlive the
> spend). The Worker compounds (sub-200ms forever). The snowball
> compounds (price points forever). The $1.35 is the seed; the
> harvest is the inheritance.
