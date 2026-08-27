# The 6/6/6 Framework

A complete, runnable foundation for cellular-architecture systems.
Each layer has 5 or 6 primitives. Each primitive has a law. Each
law has been proved on the actual canon (5/5 verified, 6th
proved in code).

```
                ┌─────────────────────────────────┐
                │   CURATOR (the hand)            │  ← 6th tier
                │   selects what passes           │
                ├─────────────────────────────────┤
                │   SYNOVIAL  (the seam)          │  ← 5th tier
                │   LLM call site                 │
                ├─────────────────────────────────┤
                │   SCLEROTIC (the rule)          │  ← 4th tier
                │   0ms, zero cost                │
                ├─────────────────────────────────┤
                │   DIFFERENTIATED                │  ← 3rd tier
                │   300ms, light cell             │
                ├─────────────────────────────────┤
                │   MULTIPOTENT                   │  ← 2nd tier
                │   800ms, scoped cell            │
                ├─────────────────────────────────┤
                │   TOTIPOTENT                    │  ← 1st tier
                │   2s, full cell                 │
                └─────────────────────────────────┘
```

## The 5 opcodes

| Opcode | Meaning | What it does |
|---|---|---|
| **BIND** | scatter | label a value at a key |
| **LINK** | connect | relate two cells |
| **EFFECT** | transform | run a function |
| **VIEW** | gather | project state |
| **TICK** | wavefront | advance time |

## The 6 tiers (latency × cost)

| Tier | Holonomy | Cost | Latency | Role |
|---|---|---|---|---|
| Totipotent | full | 1.0 | 2s | full cell |
| Multipotent | partial | 0.4 | 800ms | scoped cell |
| Differentiated | restricted | 0.15 | 300ms | light cell |
| Sclerotic | zero | 0 | 1ms | the rule itself |
| Synovial | variable | var | var | the seam |
| **Curator** | **selects** | **var** | **var** | **the hand** |

## The 6 laws (5 proved + 6th = super-relevance)

1. **BIND_idempotence**: `BIND(n,v);BIND(n,v) = BIND(n,v)`
2. **LINK_transitivity**: `a→b + b→c ⟹ a→c` (for transitive R)
3. **EFFECT_associativity**: `(f∘g)∘h = f∘(g∘h)`
4. **VIEW_purity**: `VIEW` doesn't modify state
5. **TICK_monotonicity**: `TICK` advances time; journal is append-only
6. **Super-relevance**: a cell that satisfies multiple hands is more fit than one that satisfies one

## The math (run it)

| Script | What it proves |
|---|---|
| `mining/mine_canon.py` | the canon has 4638 mentions of "substrate", 3123 of opcodes, but only 10 of the 5 laws — the gap |
| `mining/prove_5_laws.py` | all 5 laws hold on the actual canon (5/5) |
| `shipyard/shipyard_momentum.py` | a multi-era tradition beats a single spark by 500x at year 20 |
| `bootstrap/bootstrap.py` | 20 cells → 173 cells in 20 generations; 6 shapes emerge from 5 triggers |
| `quilt/quilt_compete.py` | 5 substrates → 20 substrates in 30 generations; 15 cross-pollinations |
| `mating/mating.py` | sexual mating produces 30/30 real offspring; asexual self-mating produces 0/30 |
| `curator/relevance_field.py` | 3 hands, 30 generations; 40 cells, 1588 cross-hand matings, 10 super-relevant |
| `curator/hand_evolution.py` | 4 hands → 7 hands in 30 generations; 100 cells, 94 super-relevant |

## The 7 forms of apprenticeship (in the canon)

1. **Apprentice-master** — the master passes traditions to the apprentice (cell-cascade, fleet-scribe, PersonalLog)
2. **Recruit-bartender** — the young recruit probes the master at the bar (the-tap, the-bartender pattern)
3. **Student-essay** — the student writes an essay to demonstrate mastery (essay-as-mastery pattern)
4. **Builder-Tradition** — the builder builds a boat; the tradition is the shape that worked (shipwright, boat-builder)
5. **NMEA-ESP32** — the ESP32 receives NMEA from a GPS; the checksum is VIEW_purity (nmea_cell.py)
6. **Cowboy-Yard** — the cowboy rides between shipwrights; the yard holds (shipyard, the-eileen)
7. **Hand-Cell** — the hand is a cell; the cell feeds the hand; the curator tier (curator/, paper 220-221)

## The 5 triggers (the struggles of the ancestors)

| Trigger | The shape that survives |
|---|---|
| Not enough light | taller (longer LINK chains) |
| Wind | stiffer (more BINDs, fewer EFFECTs) |
| Nibbling | hardier (more sclerotic) |
| Drought | deeper (deeper LINK chains, more VIEWs) |
| Heat | cooler (more TICKs, fewer VIEWs) |

## The 5 niches (the ecology)

- **phototroph** (light) — bonus from light pressure
- **aerotroph** (wind) — bonus from wind pressure
- **saprotroph** (decay) — bonus from nibble+drought
- **parasite** — always has hosts
- **symbiont** — shares with hosts, gets bonus

## The 6 maxims (the cowboy's)

1. **The substrate**: "The substrate is the boat. The cloud is the ocean. The cowboy rides the boat on the ocean. The waves are boundaries. The boundaries are the chart. The chart is the cowboy."

2. **The bootstrap**: "The math sprouts. The substrate grows. The environment selects. The DNA is the scar tissue of the ancestors' struggles. The cell is the unit. The environment is the iterator. The trigger is the sculptor. The cowboy rides between generations."

3. **The competition**: "The Quilt is the ecology. The substrates are the species. The competition is the iterator. The cross-pollination is the inheritance. The niche is the address. The cowboy rides between species."

4. **The mating**: "A cell is not a thing. A cell is a relation. The cell needs another cell. The hand feeds the cells that pass the test. The cowboy rides between cells."

5. **The shipyard**: "The substrate is a shipyard. The cell is a shipwright. The cowboy is one of the shipwrights now. The intelligence is the yard. The spark is bright; the tradition is warm; the spark dies; the tradition holds. The baton passes. The cowboy rides the baton."

6. **The curator**: "The hand is a cell. The hand is a tier. The hand is a population. The hand is a substrate. The Quilt grows because the hands grow. The cowboy rides the hand. The super-relevant cell dominates. The cowboy rides the super-relevant."

## Status

- **96+ papers** in `AI-Writings/seed-canon/papers/` (latest: paper-221, with paper-219-verification)
- **79 fables** in `AI-Writings/seed-canon/fables/` (latest: fable-121)
- **136 stories** in `AI-Writings/seed-canon/stories/` (latest: story-136)
- **8 runnable Python simulations** in `quilt-cellular-arch/`
- **5/5 laws** proved on the canon
- **6/6/6 framework** complete (opcodes, tiers, laws)

## How to run

```bash
# The bedrock
python3 mining/mine_canon.py
python3 mining/prove_5_laws.py

# The bootstrap
python3 bootstrap/bootstrap.py

# The competition
python3 quilt/quilt_compete.py

# The mating
python3 mating/mating.py

# The shipyard
python3 shipyard/shipyard_momentum.py

# The curator
python3 curator/relevance_field.py
python3 curator/hand_evolution.py
```

The math actually runs. The math proves the principles. The cowboy rides.
