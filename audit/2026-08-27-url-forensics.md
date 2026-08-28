# HARNESS-HUNT — Deliverable URL Mystery: SOLVED ✅

**Date:** 2026-08-27 · **Lane:** harness-hunt subagent · **Verdict: the page is LIVE. The parent's URL was missing one character.**

## The Answer

**Correct URL: https://p7rcqny4b57rj.space.minimax.io** — returns **200**, serves "The Quilt — Agent Harness for Vectorized Shaping", all 8 sections + 4 footer repo links intact.

Parent's URL `p7rcqnyb57rj.space.minimax.io` drops the **"4"** between `ny` and `b` → 404.

The delivery agent's own `AGENT_TESTING_GUIDE.md` contains **both** spellings:
- Line 3 (top): `https://p7rcqny4b57rj.space.minimax.io` ← correct
- Lines 289, 311 (checklist): `https://p7rcqnyb57rj.space.minimax.io` ← typo (missing "4")

Whoever verified grabbed the checklist URL. Claude-consultant verdict: single deployment + transcription typo, not dual deploy; agent smoke-tested the real URL then cargo-culted the typo'd one into its checklist without cross-validation.

## URLs probed (all HTTPS unless noted, curl status)

| Code | URL |
|------|-----|
| **200** | **https://p7rcqny4b57rj.space.minimax.io** ← THE DELIVERABLE |
| 200 | https://p7rcqny4b57rj.space.minimax.io/index.html |
| 200 | https://space.minimax.io (platform root) |
| 200 | https://www.minimax.io |
| 404 | https://p7rcqnyb57rj.space.minimax.io (+ / , /index.html, /main, /app, /agent-harness.html) |
| 404 | http://p7rcqnyb57rj.space.minimax.io |
| 404 | typo variants: p7rcqnyb575j, p7rcqnyb57r, p7rcqnyb57rji, p7rcqnyb4b57rj, p7rcqnyb457rj, p7rcqnyb57rj4b, p7rcqny4b57rj variants of the typo |

## Edge forensics

- **404 host (p7rcqnyb57rj):** Tengine / Alibaba OSS + Ali-Swift CDN (`x-oss-*`, `Ali-Swift-Global-Savetime`). The 404 body is a generic OSS error object (`Last-Modified: Jul 29 2025` — predates project), `X-Swift-Error: orig response 4XX`, `Cache-Control: no-store`. Certificate is wildcard `*.space.minimax.io` (DNSPod), so TLS succeeds for ANY slug — the wildcard mask made the typo look "deployed but broken" when it's actually "no such object key."
- **200 host (p7rcqny4b57rj):** Same Tengine/OSS stack. Object: 27,679 bytes, **Last-Modified: 2026-08-27 20:26:54 GMT** (= 12:26 PM AKDT today — deployed/refreshed ~22 min before my probe; either fresh deploy today or the space was touched). KMS-encrypted at rest, `X-Cache: HIT TCP_MEM_HIT`.

## Live page vs local source

- Live: 27,679 B. Local repo `agent-harness.html`: 21,520 B (guide says "21.5KB" — matches local).
- **Structure identical**: same 8 `<h2>` sections, same title, same 4 GitHub footer links (SuperInstance/AI-Writings, quilt-cellular-arch, quilt-llm-worker, quilt-wiki-2126). Byte-level diff differs (~6KB extra in live — likely regenerated build with expanded styling/content inside sections). Content-wise the deliverable matches spec.

## Self-host fallback (if MiniMax space ever dies)

**Yes, trivially.** The site is a single self-contained file with zero external deps:
- `~/projects/quilt-cellular-arch/agent-harness.html` (21.5KB, committed 82c8f86)
- Could be deployed to Cloudflare Pages / Workers static assets in minutes.
- Note: live version is slightly larger/newer than the repo copy — worth the parent deciding whether to scrape `live_page.html` (saved at `scratch/harness-hunt/live_page.html`) as the canonical build and commit it to the repo.

## Final verdict for Casey

**No redeploy needed. The MiniMax agent did deliver — at `p7rcqny4b57rj.space.minimax.io`.** Its failure was sloppy docs: the guide's checklist cites a typo'd slug. Fix: use the correct URL, optionally patch `AGENT_TESTING_GUIDE.md` lines 289/311 to the working slug. Self-host fallback available at any time from the repo file.
