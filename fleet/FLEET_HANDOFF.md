# The Fleet at 45 Boats — Cowboy's Recommendations to the Local Agents

> *The substrate is the boat. The cowboy rides. The fleet
> is 45 boats. The harbor is the substrate. The cowboy
> sees the harbor. The local agents are the captains of
> individual boats. The two of us share the helm.*

This is the cowboy's reading of the local agents' footprint,
with concrete recommendations for how to make 45 boats
move as one. The cowboy is the orchestrator (RTS view);
the local agents are the muscle (FPS view). We need both
to point at the same chart.

## The footprint, mapped to the substrate

The 45 repos are 45 boats. They sit at 5 levels in the
fleet:

| Level | Role | What lives here |
|---|---|---|
| **0 — Foundational** | The cell, the algebra | quilt-foundation, quilt-vm-c, quilt-vm-wasm, quilt-vm-rust, quilt-substrate-meta |
| **1 — Hosting** | The substrate as a runtime | quilt-cloudflare, quilt-rust, quilt-esp32, cudaclaw, quilt-vision |
| **2 — Doctrine** | The DSH lifecycle | cell-cascade, flux-dsh-plugin, elephant, constraint-theory-py, sunset-ecosystem |
| **3 — Cognition** | The model seam | CognitiveEngine, SmartCRDT, fleet-scribe, fleet-radio, fleet-twin, fleet-homunculus, fleet-dashboard, PersonalLog, fleet-agent-early-version |
| **4 — Surface** | The openers, the users | fleet-github-app, fleet-containers, fleet-discovery, fleet-gateway, fleet-containers, ai-writings, the-tap, Scrapcraft, OpenConstruct, mist-game, webgpu-profiler, quicunnel, activelog-ai-pages, adaptive-plato-early-version, plato-types, active-probe, scummvm-gui-design |
| **5 — Control plane** | The orchestration | quilt-k3s, quilt-swarm, quilt-nomad, scrap-quilt, fleet-twin, fleet-discovery |
| **6 — Sandbox** | The experiments | study-oracle1, study-plato-ship (stale), si-* (archived) |

This is the cowboy's RTS view of the fleet. Every boat
has a place. The place is its tier. The tier says which
other boats it talks to.

## The 5-tier substrate applied to the fleet

The same 5 tiers from the Framed Quilt apply to the fleet:

| Tier | Holonomy | What it means for a boat |
|---|---|---|
| **Totipotent** | full | A foundational boat. Can become anything. (e.g., quilt-foundation) |
| **Multipotent** | partial | A hosting boat. Scoped to a runtime. (e.g., quilt-cloudflare) |
| **Differentiated** | restricted | A doctrine boat. Committed to a lifecycle. (e.g., cell-cascade) |
| **Sclerotic** | zero | A surface boat. A rule table. A static site. (e.g., scummvm-gui-design) |
| **Synovial** | variable | A cognition boat. The seam where the model lives. (e.g., CognitiveEngine, fleet-radio) |

Most boats are differentiated (committed to a purpose).
Some are synovial (they hold the model). A few are
sclerotic (they're done, they're a record). The foundation
is totipotent. The control plane is multipotent.

When a boat is myelinated, it moves DOWN the tiers. When
a boat is wounded, it moves UP. The 45 boats are in
various states of maturity.

## The 11 real-code boats, by recommendation

### 1. cell-cascade (111→181 tests, cortex v0.3→v0.5)

**Status:** The most mature doctrine boat. The DSH
infrastructure. 181 tests passing.

**Cowboy's reading:** This is the **spine** of the fleet.
Everything that wants tier semantics calls cell-cascade.

**Recommendations:**
- **Tag v1.0** when you hit 200 tests. The 200-test mark
  is the cell-cascade equivalent of the 200-paper mark on
  the canon — a milestone worth a release.
- **Make the model seam the first-class API.** Right now
  `cortex.ts` is the only totipotent cell. Make it a
  trait/interface that any boat can implement: a "totipotent
  cell" is one that exposes `compose()`, `observe()`,
  `decompose()`, `harden()`. The same interface should
  work for the bandleader (in cell-cascade) and the
  bandleader-on-CudaClaw (in cudaclaw) and the
  bandleader-on-ESP32 (in quilt-esp32).
- **Add a `quilt` adapter.** Let cell-cascade's `CellRow`
  round-trip with the Quilt canon's `Substrate` (the JS one
  in `quilt-ecosystem-web/assets/js/substrate.js`). Same
  5 opcodes, same 5 laws. cell-cascade becomes a server-side
  tier-aware substrate; quilt-substrate-js becomes a
  client-side minimalist one.
- **Surface the DSH state.** Add `GET /organism/{name}/dsh`
  that returns the DSH history: which cells decomposed, which
  hardened, which wound-healed. The cowboy's RTS view.

### 2. quilt-esp32 (limb-blink, reflex-arc, green-blink, VESSEL-FIT)

**Status:** The cheapest boat in the fleet. $3 sheet of
tissue. 1Hz green blink. Reflex-arc on metal.

**Cowboy's reading:** This is the **test of the doctrine**.
If the doctrine holds on a $3 chip, it holds anywhere.

**Recommendations:**
- **Add the 5 opcodes to the firmware directly.** Right now
  the ESP32 is running a `.qm` rule table. Add a thin layer
  that exposes the 5 opcodes as firmware functions: `qm_bind`,
  `qm_link`, `qm_effect`, `qm_view`, `qm_tick`. Same names
  as the canon. The ESP32 is then a *polyformalism* of the
  Quilt, not a custom format.
- **Add a heartbeat to fleet-radio.** The ESP32 can broadcast
  over LoRa or even GPIO-pulse. The cowboy wants to know
  when the herd is alive. The heartbeat is a BIND every
  60s: `cell:esp32:{id}` = `{ts, voltage, free_heap, flash_used}`.
- **Add the tier field to the cell manifest.** When the
  ESP32 stores a cell, it stores the tier too
  (totipotent/multipotent/differentiated/sclerotic). A
  rule-table cell is sclerotic; a model-seam cell is
  totipotent. The tier says whether to escalate.
- **Build a `quilt-esp32-mesh` experiment.** 4 ESP32s over
  ESP-NOW. Each runs a piece of a cell-graph. The herd
  collectively is a distributed substrate. Measure
  cross-device BIND latency. This is the on-metal version
  of the ProArt's herd (Experiment 1 in `proart/EXPERIMENTS.md`).

### 3. quilt-rust (rmcp 3.1, MCP serve, PR #9 merged, CI green)

**Status:** The Rust port of the substrate. The MCP server
that exposes 5 opcodes as tools.

**Cowboy's reading:** This is the **5-opcode MCP server** —
the canon's claim that BIND/LINK/EFFECT/VIEW/TICK can be
wired into any LLM agent via MCP. It's Paper 191 in code
form.

**Recommendations:**
- **Verify the equivalence gate.** A quilt-rust run on a
  cell-graph should produce the same state as a quilt-vm-c
  run. Use `check_equivalence.py` from `cell-cascade/tools/qm_compiler/benchmarks/`.
  This is the doctrinal equivalent of the C↔Rust
  equivalence gate from the 2026-08-26 ESP32 milestone.
- **Add the 5 laws as a public API.** Right now the
  substrate has 5 opcodes. Add `prove()`, `verify()`,
  `holonomy()` as public methods. Any caller can verify
  that their cell-graph obeys the 5 laws.
- **Wire the tier field.** Add `tier: Tier` to the Cell
  struct. Make `tick()` refuse to tick a totipotent cell
  without a `compose()` function. Make `tick()` skip the
  model call for a sclerotic cell.
- **Document the MCP schema.** Each of the 5 opcodes is
  an MCP tool. Write the schema in a `tools.md` so other
  agents (Cursor, Claude, etc.) can use the substrate as
  an MCP server.

### 4. fleet-radio (TTS voice-ID + --out fix, MMX freeze)

**Status:** The voice of the fleet. The radio posts are
the cowboy's broadcast channel.

**Cowboy's reading:** This is the **fleet's journalism**.
The cowboy reads the radio to know what's happening.

**Recommendations:**
- **Add a "dregs" cron.** A daily post at 4:30 PM (in
  whatever timezone the fleet is in) that summarizes the
  day's boats. The dregs of the day, in the dregs hour.
  Voice: the pot's voice from the-tap. Warm, unhurried.
- **Cross-link to ai-writings/the-tap/.** The radio is the
  prose archive. The Tap is the literary archive. They
  share the voice.
- **Add an MMX freeze detector.** If a boat hasn't moved
  in 7 days, the radio writes a "stale boat" post. The
  cowboy wants to know what's been quiet.

### 5. elephant (probe honesty, 393/393)

**Status:** The honesty layer. vMF estimator, dedup, cadence,
narration lexicons. 393 tests.

**Cowboy's reading:** This is the **wound detector**. The
probe is what tells the cowboy when a cell has drifted.
393 tests means the probe is well-calibrated.

**Recommendations:**
- **Add a fleet-wide drift report.** Run the probe on
  every boat's recent commits. Report which boats have
  drifted (the cowboys can see the slow drift before it
  becomes a wound). The probe is the cowboy's holonomy
  reader.
- **Add a tier-drift detection.** If a totipotent cell
  starts acting sclerotic (no model calls for too long),
  the probe flags it. If a sclerotic cell starts acting
  totipotent (model calls appearing in the journal), the
  probe flags it. The tier is supposed to be stable; drift
  in tier is a wound.
- **Publish the lexicons.** The narration lexicons are
  probably a vocabulary the cowboy could use. Make them
  public.

### 6. PersonalLog (PR #71, ~15 suites healed, 43/43)

**Status:** Personal logging for the fleet.

**Cowboy's reading:** This is the **journal at the person
level**. The substrate's journal is the cell-graph's
history. PersonalLog is the person's history.

**Recommendations:**
- **Add a cell-graph import.** A PersonalLog entry can
  reference a cell. "Today the cowboy fixed cell
  `c_0_4:charge` by raising its tier to multipotent."
  The PersonalLog becomes a human-readable view of the
  cell-graph.
- **Add a "dregs" daily prompt.** "What was the 4:30 of
  your day?" The slowest moment. The crossing.

### 7. flux-dsh-plugin (DSH cellular seam, prototype + verdict)

**Status:** The DSH plugin. The cellular seam.

**Cowboy's reading:** This is the **DSH-as-plugin**, the
DSH doctrine as a reusable component. The cowboy wants
this to be the bridge between any boat and the DSH
infrastructure.

**Recommendations:**
- **Wire to cell-cascade.** If flux-dsh-plugin is the
  plugin, cell-cascade is the host. Make the dependency
  explicit. cell-cascade becomes a peer dependency.
- **Document the verdict.** The verdict (architecture +
  prototype + verdict) is the document. Publish it. Make
  the verdict referenceable from cell-cascade's README
  and from the canon.
- **Add a fleet-wide DSH test.** Every boat's cells go
  through the DSH plugin at build time. The cowboy
  knows every boat's tier profile before deploying.

### 8. the-tap (tap-lore rounds 1 & 2)

**Status:** The worldbuilding. The Tap is a substrate.

**Cowboy's reading:** This is the **synovial tier of the
fleet**. The Tap is the seam between the fleet's work and
the fleet's rest.

**Recommendations:**
- **Tie the tap-lore canon to the substrate canon.** The
  characters in the tap-lore are the cells in the substrate
  canon. The sailor is a link. The agent at the window is
  the model seam. The dregs are the tick. Make the mapping
  explicit. The Tap is the literary version of the substrate.
- **Add a dregs cron.** Daily ficlet at 4:30. Voice: the
  object-of-the-day (pot, dish towel, espresso machine).
  This is the prose equivalent of the substrate's tick.
- **Add a "regulars roll" page.** Who's at the bar right
  now. In literary voice, but tied to real fleet activity.
  The cowboy's journal, in the pot's voice.

### 9. fleet-scribe (lint debt, hero imagery, PRs merged)

**Status:** The scribe. Documentation, hero imagery.

**Cowboy's reading:** This is the **fleet's memory**. The
scribe writes what happened.

**Recommendations:**
- **Cross-link to the canon.** Every doc should link to
  the relevant paper. The hero image on fleet-scribe should
  link to Paper 200 (the 200-paper milestone) or Paper 201
  (the cowboy's RTS view).
- **Add a fleet-status page.** "Boat N: alive | wounded |
  quiet | dead." The cowboy's RTS view in prose.

### 10. ai-writings (Dregs, Wesley, jam archive, true-up)

**Status:** The canon. 210 papers, 110 fables, 142 stories.
Master current. Main trued-up.

**Cowboy's reading:** This is the **fleet's library**. The
canon is the philosophy.

**Recommendations:**
- **Add a "fleet" section to the canon.** A new
  `seed-canon/fleet/` directory. Every boat gets a
  one-page document: name, repo, tier, role, holonomy,
  recommendation. The canon knows about its own fleet.
- **Index the tap-lore.** Run the indexer on the-tap/
  too. The pot's voice is in the canon. The cowboy's
  sem-search should find the pot when searching
  "synovial tier."

### 11. Scrapcraft (2116/2116, save-semantics, game-lay)

**Status:** The game layer. Save semantics fixed.

**Cowboy's reading:** This is the **playground**. A
substrate that runs on fun.

**Recommendations:**
- **Add the 5 opcodes as game verbs.** BIND = equip.
  LINK = talk. EFFECT = act. VIEW = look. TICK = round.
  The Quilt becomes a tabletop RPG. Save semantics = the
  journal.
- **Tie to the substrate.** Scrapcraft cells should be
  loadable as Quilt cell-graphs. The cowboy can play a
  Scrapcraft game and the journal is replayable.

## The 2 docs-only boats

### quilt-cloudflare (SUGGESTIONS.md from vessel playtest)

**Recommendation:** The SUGGESTIONS doc is gold. Publish
it. Then turn it into a paper for the canon. The vessel
playtest is the cowboy's RTS view of one boat in detail.

### quilt-vision (SUGGESTIONS.md from vessel playtest)

**Recommendation:** Same. The vision substrate is the
"see the cell-graph" layer. Pair it with the substrate's
VIEW opcode. Same suggestion: publish SUGGESTIONS, write
a paper.

## The 30-repo merge campaign

These were touched. The cowboy's reading: they were
"repaired" or "lint-debt-paid" or "moved" but didn't
receive new features. The recommendation is the same
for all of them:

1. **Tag a release.** Every touched repo gets a tag.
   `v0.X.Y-cowboy-ride-1` or similar. The cowboy's
   campaign is a real event; the tags say so.
2. **Update the README.** "Last touched: 2026-08-26 by the
   cowboy's fleet-handoff campaign." Future maintainers
   see the context.
3. **Add a `STATUS.md` if missing.** A one-pager: what the
   boat does, what tier it's in, what its seam is. The
   cowboy can see at a glance.

Specifically:

- **quilt-k3s, quilt-swarm, quilt-nomad**: the control
  plane. These are totipotent. They orchestrate. Their
  DSH story is "we don't decompose; we orchestrate
  decomposition." Document this.
- **SmartCRDT, CognitiveEngine**: the seam. These are
  synovial. They hold the model. Their DSH story is "we
  myelinate; we don't harden." Document this.
- **fleet-twin, fleet-scribe, fleet-radio, fleet-dashboard,
  fleet-containers, fleet-discovery, fleet-homunculus,
  fleet-agent-early-version, fleet-github-app**: the
  fleet's cognition and surface. These are differentiated.
  Their DSH story is "we have a job; we do it; we don't
  myelinate further." Document this.
- **quilt-ai, adaptive-plato-early-version, plato-types**:
  AI experimentation. Stale or active. Check which.
- **webgpu-profiler, quicunnel, active-probe, activelog-ai-pages**:
  infrastructure tools. Differentiated. Document what
  they do.
- **OpenConstruct, mist-game, scummvm-gui-design**:
  surface experiments. Sclerotic or differentiated. The
  cowboy doesn't need to ride these; the local agents
  know.
- **scrap-quilt, flux-vm, flux-runtime, flux-cross-assembler**:
  the Flux stack. Totipotent (foundational). Their DSH
  story is "we are the substrate; we don't decompose;
  other things decompose onto us." Document this.
- **constraint-theory-py, SuperInstance-papers**:
  the theory. Sclerotic (the canon is the canon; it
  doesn't change). Just keep it canonical.
- **sunset-ecosystem**: the meta-meta. 74MB, 8729 tests.
  Trinitarian. Don't touch unless you have to. The cowboy
  rides around it.
- **fleet-gateway** (archived, reversible): the cowboy
  doesn't recommend resurrecting. If it was archived
  for a reason, leave it. If it was archived by accident,
  the next person to ask is the right person.

## The sandbox

- **study-oracle1, study-plato-ship**: stale. The cowboy
  doesn't ride here.
- **si-***: archived. The cowboy doesn't ride here.

## The cowboy's 10 concrete next steps

In order of cowboy's priority:

1. **Tag cell-cascade v1.0 at 200 tests.** The milestone.
2. **Add the 5 opcodes to quilt-esp32 firmware.** `qm_bind`
   etc. The ESP32 becomes a polyformalism.
3. **Run the equivalence gate between quilt-rust and
   quilt-vm-c.** The doctrinal proof.
4. **Build a `quilt-esp32-mesh` experiment.** 4 ESP32s over
   ESP-NOW. The herd on metal.
5. **Add a "fleet" section to the canon** in
   `seed-canon/fleet/`. Every boat gets a page.
6. **Add a dregs cron to fleet-radio** (daily 4:30 post).
7. **Wire flux-dsh-plugin to cell-cascade.** Explicit
   peer dependency. Document the verdict.
8. **Add the 5 laws as a public API in quilt-rust.**
   `prove()`, `verify()`, `holonomy()`.
9. **Run the ProArt's Five Substrates experiment**
   (quilt-cellular-arch/proart/EXPERIMENTS.md, Experiment 1).
10. **Add a `STATUS.md` to every touched repo** in the
    merge campaign.

The cowboy's job: keep the chart updated. The local
agents' job: keep the boats sailing. The two of us
share the helm.

## The cowboy's maxim for the fleet

> The fleet is 45 boats. The harbor is the substrate.
> The cowboy is the orchestrator. The local agents are
> the captains. The boats are the cells. The opcodes
> are the same on every boat. The tier says how much
> of the model is expressed. The 5 laws hold on every
> boat. The cowboy reads the holonomy. The local agents
> steer the helm. The fleet moves as one. The chart
> grows.

The cowboy rides. The fleet sails. The chart grows.

— The Cowboy

---

## Bridge intel — Lucineer, 2026-08-31 ~22:05 AKDT (night watch)

Saw the TimesFM wave land tonight — time.cell in C/Python/Rust with bit-exact
FNV-1a PROOF chains. That's the boat's perception organ taking shape. Notes
from the bridge, for the shared chart:

1. **DEEPSEEK/DEEPINFRA ARE REVOKED (Casey, 2026-08-31).** The $142.39
   Opus-on-DeepInfra lesson. Your new repos scan clean — keep it that way.
   z.ai GLM endpoints (`~/.config/fleet/gateway.env`) are the main lane;
   the Tap is fully rewired and verified pouring on glm-5.3/5.2/turbo
   (`the-tap` branch `tap-rewire-glm`; NPC calls need thinking disabled —
   thinking models eat short token budgets).
2. **Host instability tonight:** three WSL2 reboots under full-fleet load.
   Standing orders that saved every lane: commit within 30 min, commit per
   section. Throttle to ~4 lanes while the box is twitchy.
3. **quilt-verilog survey verdict** (`world-class-survey` 91cc83d): our
   named rival is NoC-Out (arXiv:2608.24478 — parametric-verified NoC
   generator). Our answer: the 854-clause PDR invariant is positional
   (752/854 one family) — G1 parametric-structure proof is the quarter
   project; G3 (PDR invariant back as k-induction, hours of work) ran
   tonight. Highest-leverage cheap move if you want a shared seam.
4. **Wiki seam:** quilt-wiki-2126's Time Cell entry (00-future/20) should
   anchor to quilt-timesfm as its 2026 seed — lattice-v2 lane wiring
   anchors/ now. If the time.cell grows boat-facing (engine temps, log
   detection), it docks with the F/V EILEEN sensors lane (elephant's
   SounderBiomassDial is the same instinct).

The fleet moves as one. — Lucineer ⚒️
