# API Inventory — 19 Voices, 16 Working (2026-08-27)

*Last pulse: 2026-08-27 18:43 PT. Re-run anytime with `python3 api_pulse.py`.*

## The 16 working voices

| Voice | Source | Model | Best for |
|---|---|---|---|
| **llama70b** | DeepInfra | `meta-llama/Meta-Llama-3.1-70B-Instruct` | practitioner whiteboard, Tier Bleed |
| **llama33** | DeepInfra | `meta-llama/Llama-3.3-70B-Instruct` | best for writers' room, gold terms |
| **llama4** | DeepInfra | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | small/capable |
| **llama405b** | DeepInfra | `meta-llama/Meta-Llama-3.1-405B-Instruct` | hidden symmetry |
| **hermes** | DeepInfra | `NousResearch/hermes-3-llama-3.1-405b` | W6 braid, Quantum Scarring |
| **wizard** | DeepInfra | `microsoft/WizardLM-2-8x22B` | landscape, Loom Drift, Scriptorium |
| **mixtral** | DeepInfra | `mistralai/Mixtral-8x7B-Instruct-v0.1` | multidisciplinary blender |
| **deepseek** | native | `deepseek-chat` | code, dense technical |
| **qwq** | DeepInfra | `Qwen/QwQ-32B-Preview` | reasoning (no direct output) |
| **qwen72** | DeepInfra | `Qwen/Qwen2.5-72B-Instruct` | emergence observer |
| **gemma3** | DeepInfra | `google/gemma-3-27b-it` | prompt-friendly |
| **phi4** | DeepInfra | `microsoft/phi-4` | small/capable |
| **seed2** | DeepInfra | `ByteDance/Seed-2.0-mini` | fast court of variety |
| **cf8b** | Cloudflare | `@cf/meta/llama-3.1-8b-instruct` | free fallback |
| **qwen32b** | Cloudflare | `@cf/qwen/qwen2.5-coder-32b-instruct` | code |
| **dsr1** | Cloudflare | `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` | reasoning (no direct output) |

## The 3 failing voices (currently)

| Voice | Source | Status | What to do |
|---|---|---|---|
| **zai** | ZAI | **429 Insufficient balance** | wait; ZAI 5.x exhausted, only GLM-4.5 works (and is now 429) |
| **kimi** | Cloudflare | **empty / 503 intermittent** | retry; was gold for "cell that weaves light", "biophoton", "spore+light" |
| **gptoss** | Cloudflare | **empty / 503 intermittent** | retry; was gold for "Lumen Bedrock Era" |

## The mode of operation

- **Fire 3-4 in parallel** for writers' room. Smaller prompts (under 200 words) are faster.
- **Llama 3.3 is the workhorse** — produces the most gold terms across the canon.
- **Hermes, Wizard, Mixtral** as court of variety.
- **DeepSeek** for code/dense.
- **QwQ, DSR1** for reasoning (use them for *math* prompts, not for *term generation*).
- **Kimi, GPT-OSS** when they work — both produce the most distinctive terms.

## The 4 retry rules

1. **503/429 storms** — sleep 30s and retry. The CF and ZAI quotas are real-time.
2. **Reasoning models** (QwQ, DSR1) — give them 4x max_tokens. Their thinking eats budget.
3. **Empty returns** — most often a token-revoked or 503. Try once more, then move on.
4. **Switch ground** if persistent — if Kimi 503s twice, fall back to Llama 3.3.

## The voice allocation

- **Code**: DeepSeek > Qwen 32B > DeepSeek R1 (reasoning) > Qwen 72B
- **Gold terms**: Llama 3.3 > Kimi > Hermes > Wizard > Mixtral > Qwen 72B
- **Long-form synthesis**: ZAI (when it works) > DeepSeek > Llama 70B
- **Reasoning**: QwQ > DSR1
- **Free fallback**: CF 8B > Qwen Coder 32B

## The voice-pulse script

```bash
cd /workspace/_scouts
python3 api_pulse.py
```

This will test all 19 voices and report which are working, which are failing, and why. Run it before a major writers' room. The output is in `api_pulse.log`.

---

*Last pulse: 2026-08-27 18:43 PT. 16/19 working. 3 failing (ZAI balance, Kimi 503, GPT-OSS 503).*
