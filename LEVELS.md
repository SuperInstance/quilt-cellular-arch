# LEVELS.md — The 8 Levels of the Operation

The masterwork framework is built on 8 levels. The 8 levels describe any operation the captain runs. The 8 levels are the substrate of the cowboy's understanding.

## The 8 levels

| # | Level | What it is | Replaceable? | Persists across |
|---|---|---|---|---|
| 1 | **The Vessel** | the physical substrate (the boat) | yes | generations |
| 2 | **The Equipment** | the tools (the welding kit, the engines) | yes | years |
| 3 | **The Skills** | what the crew knows (tacking, welding) | yes (lost/regained) | decades |
| 4 | **The Consumables** | what gets used up (fuel, time, tokens) | yes (used up each trip) | one trip |
| 5 | **The Renewables** | what gets replenished (the catch, the wind) | yes (renews) | one trip |
| 6 | **The Durables** | what lasts many voyages (the masks, the journals) | yes (erode eventually) | decades |
| 7 | **The Concept** | the operation itself (the captain's plan) | NO | forever |
| 8 | **The Spline** | the trajectory of the captain's understanding | NO (grows only) | forever |

## The first 6 are implements. The 7th and 8th are invariants.

The vessel, equipment, skills, consumables, renewables, and durables are all **implements** — replaceable, losable, regenerable. They are the things the captain *uses*.

The Concept (level 7) and the Spline (level 8) are **invariants** — they don't replace, they grow. The Concept is the function the captain holds. The Spline is the trajectory of the captain's understanding, shaped by every past implement.

## The grandfather's axe

The grandpa's axe has had 3 handles and 2 heads. **5 physical axes = 1 logical axe.** The axe is the operation (the enabler of the function of chopping wood). The handle and head are the implements. The function persists. The implements replace.

| The grandpa's axe | The 8 levels |
|---|---|
| The handle (3 replaced) | Level 1 (vessel) — replaceable |
| The head (2 replaced) | Level 1 (vessel) — replaceable |
| The 3 houses | Levels 1-6 (vessel/equipment/etc) — all replaceable |
| The function (chop wood) | Level 7 (Concept) — invariant |
| The trajectory (which houses chosen) | Level 8 (Spline) — grows only |

## The Eileen's 5 captains

| # | Captain | Era | The Vessel | The Equipment | The Concept | The Spline |
|---|---|---|---|---|---|---|
| 1 | Harry | 1935 | commissioned the hull | Atlas engine | highliner crabbing | first point on the spline |
| 2 | Tuna family | 1955 | maintained the hull | replaced Atlas with Detroit | tuna fishing | second point |
| 3 | Cabin-rebuilder | 1975 | rebuilt the Detroit | 3rd cabin built | vessel maintenance | third point |
| 4 | Shipwright | 1990s | replaced 25/30 planks | 6-71N Detroit | logging + shipwright | 4th point (the 6-71N is now old horse) |
| 5 | Casey | 2020 | new deck | Fred Wahl refit | Alaskan salmon trolling | 5th point |

5 captains, 4 boats, 2 engines, 3 cabins. The vessel, equipment, skills, consumables, renewables, durables all changed. **The Concept (be a fisherman) persisted. The Spline (the trajectory of choices) grew.**

## Casey's 4 boats (the spline in motion)

| # | Boat | Era | Quality | Cost | Era tag |
|---|---|---|---|---|---|
| 1 | Casey's 1st boat | 2000 | 0.3 | $1 | the starter |
| 2 | Casey's 2nd boat | 2010 | 0.5 | $3 | the upgrade |
| 3 | Casey's 3rd boat | 2015 | 0.6 | $5 | modern at the time |
| 4 | Eileen | 2020 | 0.55 | $7 | the old but stable horse |

The spline passes through points: 0.3 → 0.5 → 0.6 → 0.55. The spline is shaped by every past choice. The next boat Casey sees as a step forward is constrained to be near the spline (between 0.5 and 0.7 quality, $5-9 cost).

## The Quilt is built by lapping

Each cell is a plank. Each plank is a level-in-miniature. Each plank has all 8 levels. The 8 levels are the structure of the plank. The plank is built by lapping new planks over the old hull.

The Quilt is a lapstrake hull of cells. The 8 levels are the cell's structure. The 5 opcodes (BIND/LINK/EFFECT/VIEW/TICK) are the lap-joints that connect the planks.

## The captain and the AI

- The **captain** (the user) holds the **Concept** (level 7) and the **Spline** (level 8)
- The **AI** (the cowboy) executes the **Operation** (the implements, levels 1-6)
- The captain has physical constraints (muscles, one place at a time)
- The AI has model constraints (context window, training cutoff)
- **The captain and the AI are on the same boat.** The operation is in the captain's head. The AI is a crew member.

## The 8 levels in the writers' room

The Weave (the writers' room's structure) is the 8 levels woven together. The Weave Navigator (the AI that sees the Weave) can see the 8 levels as a unified structure. The Weave Leak is when one level loses its connection to the others.

| Weave term | Maps to |
|---|---|
| The Weave | the 8 levels as a unified structure |
| The Weave Navigator | the AI that sees the Weave |
| The Weave Leak | when one level loses its connection |

## The cowboy's maxim

> The 8 levels describe any operation. The first 6 are implements. The 7th and 8th are invariants. The function is the captain. The spline is the trajectory. The captain and the AI are on the same boat. The operation is in the captain's head. The AI is a crew member. The cowboy rides the 8 levels. The chart grows. The Concept lives.

— *Paper 232* (spline) + *Paper 227* (axe) + *Paper 228* (Eileen) + *Paper 234* (lap)
