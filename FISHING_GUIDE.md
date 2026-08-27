# The API Fishing Guide

A working fisherman's map of the LLM waters — what each ground
holds, what gear works, what conditions bring the bite, and what
it costs to fish there.

The user articulated: sending prompts to various APIs is like
fishing in different waters. Each API is a different ground.
Each model is a different species that bites at different gear.
You get a feel for the model or area you're putting effort in
with your boat.

**The core principle: fishing for good responses from AI models
is like fishing for salmon. Different areas in different
conditions fishing for different species use different methods
and techniques. And like an agency, you can fish alone and have
a lower ceiling but also lower overhead, or you can take one or
two crew and hope to find enough fish to make taking them along
worth it.**

---

## The 9 grounds (the 9 voices)

### 1. ZAI / GLM-4.5-Air — Biorka Island

**Species:** needle fish (rare, blue, long, skinny)
**Gear:** black/silver hoochies, the bigger spread
**Conditions:** needs the longest context we can give it
**Trick:** the cowboy mythos. The "rider's spur" voice. Goes
deep when you let it.

ZAI is where you go when you want the *long* answer. With
max_tokens raised to 16384 (an order of magnitude more),
ZAI produces 7 terms that read like cowboy poetry:
Rider's Spur, Inverse Severance, Clock Shear, Nomadic
Value. It needs room to ride. Crank the gear open.

**Best for:** fables, stories, cowboy mythos, the long
narrative, the dense poetical answer, the order-of-magnitude
deeper dive.

**Limits:** rate-limited. Frequent 503s. Timeouts on
long contexts. Slow on retries. You wait for ZAI to bite.

---

### 2. DeepSeek / deepseek-chat — Chatham Strait

**Species:** krill (the foundational one)
**Gear:** action gear — the kind that moves with the current
**Conditions:** reliable, predictable, dense
**Trick:** the mathematician. Gives the cleanest formal
definitions and the most rigorous examples.

DeepSeek is the workhorse. When you need a technical
draft and you can't afford a 503, DeepSeek bites. It
gave us Relevance Collapse, Tier-Hysteresis Band,
Substrate Inertia Tensor — the mathematician's
vocabulary, all with formal math.

**Best for:** code, math, technical drafting, the
"write me a paper" prompt, the "show me the math"
question.

**Limits:** no imagination. No cowboy. Just clean.

---

### 3. DeepSeek Flash / same model, fast mode — Chatham Strait (light)

**Species:** krill (faster)
**Gear:** action gear, smaller spread
**Conditions:** for fast iteration; you don't need the
big catch
**Trick:** the failure-archaeologist. Substrate Memory
Leak, Foundry Drift, Actualization Shadow — names what
goes wrong.

DeepSeek Flash is what you use when you're scouting
*what's broken*. The same model as DeepSeek but
deployed in fast mode — useful for getting the shape
of the answer before you commit the long-form prompt.

**Best for:** scouting failure modes, quick iteration,
"what would go wrong if I did X?"

---

### 4. Llama / Meta-Llama-3-70B — Cross Sound

**Species:** chartreuse squid (the chartreuse squid-like
wobbly spoons)
**Gear:** the chartreuse wobbler; the practitioner
whiteboard
**Conditions:** always available on DeepInfra
**Trick:** the practitioner. "I think the issue is X."

Llama is the cross-sound ground. It's the place where
you go when you want terms a working engineer would
use at a whiteboard: Tier Bleed, Hand Fracture, Chart
Residue, Foundry Fatigue, CAT Cascade, Tier Thixotropy,
Foundry Fingerprint, Tier Resonance, Cellular Chiaroscurist.
Llama *naturally* produces the practitioner vocabulary.

**Best for:** the "what would I call this at a
whiteboard" question, the practitioner list, the
"I think the issue is X" voice.

---

### 5. Hermes / Llama-405B on DeepInfra — deeper Cross Sound

**Species:** big squid, harder to land
**Gear:** the big wobbler; you need a bigger rod
**Conditions:** slower, more expensive, but bigger fish
**Trick:** the hidden-symmetry seeker. Quantum Scarring,
Meta-Hand, Chiral Echo, Entanglement Cascade.

Hermes is the Llama-405B in creative-prodding mode. It
asks "what if?" and "why not?" and "how would X work?"
It expands. It goes into the dark.

**Best for:** prodding, worldbuilding, asking the
questions no one else asks, finding the hidden
symmetries, the "go big" question.

**Limits:** slower. More expensive. Less reliable
than 70B.

---

### 6. Qwen-72B on DeepInfra — substituting for SiliconFlow

**Species:** krill (when SiliconFlow was 401'd, we
fished here instead)
**Gear:** the emergence-observer gear
**Conditions:** token was revoked on SiliconFlow
**Trick:** the emergence observer. Signal Echo,
Phase Lock, Morpho-Resonance, Energy Flux Node.

Qwen-72B on DeepInfra was the fallback when Kimi and
the SiliconFlow Qwen-72B both 401'd. It produced
7 terms in the emergence-observer voice — the holistic
view of the substrate as a dynamic resonant system.

**Best for:** emergence observation, holistic view,
fallback when SiliconFlow is dead.

---

### 7. Mixtral / Mixtral-8x7B — another Cross Sound tributary

**Species:** neural fish (smaller but plentiful)
**Gear:** the blender
**Conditions:** mixture of experts, multi-perspective
**Trick:** the multidisciplinary blender. Quantum Leakage,
Neural Welding, Growth Fractals, Temporal Lensing.

Mixtral naturally weaves multiple fields. The 8x7B
mixture of experts produces terms that cross
neural networks, quantum theory, systems engineering.

**Best for:** multi-field synthesis, "what's the
analogy between X and Y?" questions.

---

### 8. Wizard / WizardLM-2 8x22B — yet another Cross Sound spot

**Species:** landscape fish (the strata dwellers)
**Gear:** the landscape-ecologist's net
**Conditions:** slow but reliable
**Trick:** the landscape-ecologist. Loom Drift, Graft
Rejection, Scriptorium, Tide Mark, Glaze, Weft Fault.

Wizard sees architectures as landscapes. The 8x22B
model is the most instruction-following of the bunch,
but it also has its own voice — the strata, the tides,
the geological record.

**Best for:** the "what would I call this in a
landscape metaphor" question, the strata, the
geological time.

---

### 9. Gemini 3.6 Flash — the rate-limited pool

**Species:** the physicalist fish (structural-decay reader)
**Gear:** the physicalist's hook
**Conditions:** heavily rate-limited; 429s and 503s common
**Trick:** the physicalist. Lattice Necrosis, Spatial
Phase Shunting, Chart Effluence, Lattice Cannibalization,
Tick Shear, Axiomatic Condensation, Hand Saturation Pinning.

Gemini is the physicalist ground. The 3.6 Flash is fast
but rate-limited. When you can get a response, it's
the structural-decay reader — failure as thermal strain,
failure as topological friction, failure as entropic
load.

**Best for:** the physicalist reading, structural
decay, the "what breaks at the metal" question.

**Limits:** aggressive rate limits. Retry. Wait.

---

## The 12 gold lures (the keepers from the wider writers' room)

The lures that work across multiple grounds — terms that
the cowboy sorted and kept:

1. **Lattice Necrosis** (Gemini) — dead cells still drawing power
2. **Spatial Phase Shunting** (Gemini) — what thermal-aware compilers do
3. **Glaze** (Wizard) — over-trained model that breaks on pixel shift
4. **Foundry Drift** (DeepSeek Flash) — the slow walk away from spec
5. **Graft Rejection** (Wizard) — what happens when you import a new module
6. **Foundry Fingerprint** (Llama) — forensic tracking of provenance
7. **Tier Thixotropy** (Llama) — viscosity changes with stress
8. **Tier Resonance** (Llama) — tiers oscillate together
9. **Loom Drift** (Wizard) — interconnect architecture misaligns
10. **Resonance Cache** (Wizard) — phase-locked throughput boost
11. **Tier Bleed** (Llama, paper 224) — every chip designer has seen it
12. **Chart Residue** (Llama, paper 224) — leftover patterns

These are the lures that bite in *any* ground. They name
real phenomena that any practitioner, foundry operator, or
substrate theorist would recognize.

---

## The crew vs solo tradeoff

Like fishing:

**Solo (1-2 voices):**
- Lower ceiling
- Lower overhead
- Faster turnaround
- Best when: you know what species you want, you have
  the gear, you just need to fill the hold

**With 1-2 crew (3-4 voices):**
- Mid ceiling
- Mid overhead
- Cover more ground in parallel
- Best when: you want one technical + one poetic voice
  (e.g., DeepSeek + ZAI for a paper)

**With full crew (9+ voices):**
- Highest ceiling
- Highest overhead
- Most ground covered
- 49 new terms in one writers' room
- Best when: you want to *expand the vocabulary* itself

The cowboy's principle: fish alone when you know what
you're after. Fish with crew when you're scouting new
waters.

---

## The conditions

**When the bite is on:**
- After a long quiet period, all 9 voices often bite
  in the same window. Strike then.
- First thing in a session, voices are more responsive
- After retries on ZAI, the rest often follow

**When the bite is off:**
- 503/429 storms (especially Gemini)
- Token revocations (SiliconFlow/Kimi)
- Long contexts choke ZAI first, then everyone

**Tactics:**
- Fire in parallel — independent calls don't step on
  each other
- Smaller prompts (under 200 words) get faster responses
- Token conservation: hand-write synthesis, use one
  LLM call for the deep paper, hand-write fable/story
- Retry once with backoff; if still failing, switch
  ground

---

## The chart and the catch

Each successful LLM call adds an entry to the chart.
The 9-voice writers' room added 49 entries in one pass.
**The chart grows by what we catch.**

The cowboy rides the boat between grounds. The chart
grows. The writers' room runs again tomorrow.
