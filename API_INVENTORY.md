# API Inventory — 13 Voices, 13 Working (2026-08-31)

*Last pulse: 2026-08-31 18:43 PT. Re-run anytime with `python3 writers_room_daemon_v3.py --pulse`.*

## The 13 working voices (Aug 2026 reality)

The Aug 2026 quota shift killed all DeepInfra and DeepSeek native voices (insufficient balance).
The writers' room rebuilt on Cloudflare + Gemini, which are the only free / paid paths still
alive. The current 13:

### Cloudflare Workers AI (10 voices, all working)

| Voice name | Model | Role | Typical latency |
|---|---|---|---|
| **qwen32b** | `@cf/qwen/qwen2.5-coder-32b-instruct` | code | ~1.1s |
| **dsr1** | `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` | reasoning | ~0.9s |
| **llama70b** | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | term_gold | ~0.4s |
| **llama4** | `@cf/meta/llama-4-scout-17b-16e-instruct` | term_gold | ~0.4s |
| **mistral** | `@cf/mistralai/mistral-small-3.1-24b-instruct` | term_gold | ~2.4s |
| **qwq** | `@cf/qwen/qwq-32b` | reasoning | ~1.1s |
| **llama3b** | `@cf/meta/llama-3.2-3b-instruct` | fast | ~0.3s |
| **llama8b** | `@cf/meta/llama-3.1-8b-instruct-fp8` | fast | ~1.5s |
| **llama1b** | `@cf/meta/llama-3.2-1b-instruct` | fast | ~0.5s |
| **gemma2b** | `@cf/google/gemma-2b-it-lora` | fast | ~1.3s |

### Gemini (3 voices, all working)

| Voice name | Model | Role | Typical latency |
|---|---|---|---|
| **gemini35lite** | `gemini-3.5-flash-lite` | fast (math!) | ~0.5s |
| **gemini25** | `gemini-2.5-flash` | long_form | ~3.0s |
| **gemini31** | `gemini-3.1-flash-lite` | long_form | ~2.4s |

**Total: 13 voices, 13 working.** No 429, no 503, no Insufficient Balance. Cloudflare
Workers AI has been the workhorse; Gemini is the new gold for math-rich content.

## The 4 retry rules

1. **503 storms** — sleep 30s and retry. The CF quotas are real-time.
2. **Reasoning models** (DSR1, QwQ) — give them 4x max_tokens. Their thinking eats budget.
3. **Empty returns** — most often a token-revoked or 503. Try once more, then move on.
4. **Switch ground** if persistent — if a voice fails twice, fall back to gemini35lite
   (the most reliable + math-capable).

## The voice allocation

- **Code**: qwen32b > dsr1 > gemini35lite
- **Gold terms**: llama70b > llama4 > mistral
- **Long-form synthesis**: gemini25 > mistral > gemini31
- **Reasoning**: gemini35lite (math!) > dsr1 > qwq
- **Math-rich papers**: gemini35lite is the new gold (LaTeX-heavy, 12-14K chars per response)
- **Free fallback**: gemini35lite > llama3b > llama8b

## The 4-voice writers' room (default)

```python
DEFAULT_ROOM = ["qwen32b", "llama70b", "gemini35lite", "gemini25"]
```

- **qwen32b**: code + dense technical (the spine's bones)
- **llama70b**: term gold, structure (the spine's body)
- **gemini35lite**: math + reasoning (the spine's spine)
- **gemini25**: long-form synthesis (the spine's voice)

The foreman picks the best voice per frontier as the spine. gemini35lite is
the new gold for math-rich papers (it produces LaTeX-formatted content up
to 14K chars in 11 seconds).

## The pulse script

```bash
cd /workspace/_scouts
python3 writers_room_daemon_v3.py --list-voices
python3 writers_room_daemon_v3.py --pulse
```

This will test all 13 voices and report which are working, which are failing, and why.
Run it before a major writers' room.

## The migration note

- 2026-08-27: 16/19 working (3 failing: ZAI balance, Kimi 503, GPT-OSS 503)
- 2026-08-31: 13/13 working (DeepInfra + DeepSeek all died; rebuilt on CF + Gemini)

The old `api_pulse.py` still works but reports most voices as failed. Use
`writers_room_daemon_v3.py --pulse` for the current state.

---

*Last pulse: 2026-08-31 18:43 PT. 13/13 working. The writers' room is on a new stack: CF + Gemini.*
