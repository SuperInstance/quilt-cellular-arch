# THE FOUR-ROUND AUDIT — Lucineer vs. the Quilt Agent Harness (2026-08-27)

*A complete, verbatim multi-agent software acceptance audit: an independent auditor
agent (Lucineer/GLM-5.3 on OpenClaw, three parallel test passes) vs. the delivering
builder agent (MiniMax), over a live deliverable. Four rounds, all verdicts, both
sides' reports preserved.*

- **[URL forensics](2026-08-27-url-forensics.md)** — the missing-"4" URL hunt: 17 variants probed, wildcard-cert 404 explained, the deliverable recovered
- **[Grounding audit](2026-08-27-grounding-audit.md)** — kimi + claude as independent judges: guide-vs-reality divergence table (12 defects), 5 canonical questions adjudicated, honest canon counts, the fallback-mode structural finding

## The rounds (verdicts in the git history and Papers 277-280)
1. Round 1: 8 defects found (hallucinated counts 277/135/165, dead URL, phantom CLI, wrong repo, wrong env var)
2. Round 2: 8 fixed; new defect found (--query crashes with no token); counts still off
3. Round 3: 5-layer fallback system built, pollution defense added; counts off by 4 — then everyone discovers the corpus grew 5 papers DURING the audit
4. Round 4: disk truth (154/89/93 via `ls | wc -l`), audit closed, harness accepted

## The doctrine that came out of it (now Paper 280)
**"The cowboy is wrong until proven right by disk."** — identical to the
satisfiability-witness law found the same morning in the experiment-wheel (W9):
impossible/unverified instruments carry zero information. Two independent
discoveries of the same law, from opposite directions, same day.

*For students of multi-agent systems: this is what an honest agent-vs-agent
acceptance loop looks like, including the auditor's own error (a stale count
correct at run-time, wrong an hour later) and the partial apology it owed.*
