# ProArt Rig — Local Agent Experiments

> *The substrate is the boat. The cells are the cargo. The
> models are the joints. The cowboy is the orchestrator. The
> ProArt is the harbor.*

The local agents have an ASUS ProArt (RTX 4050 + AMD Ryzen
AI 9 HX + ProArt chipset). That's not a workstation — it's
a **distributed-edge machine on a single board**. The point
of these experiments is to make that fact productive.

## The hardware in question

| Component | Spec | Why it matters |
|---|---|---|
| **RTX 4050** (dGPU) | 6GB VRAM, 96GB/s mem BW, 2560 CUDA cores, Ada Lovelace, 4th-gen tensor cores, FP8 | Persistent-kernel playground; small enough to run 1M-cell cudaclaw; big enough to test SmartCRDT in-process |
| **Radeon 890M** (iGPU) | Strix Halo, 16 CUs RDNA 3.5, shared system memory | The "secondary substrate" — runs a different cell-graph on the same dataset via Vulkan/ROCm |
| **Ryzen AI NPU** (XDNA 2) | 50 TOPS, on-die, low power | The "joint" — the always-on seam where the LLM calls land when the dGPU is busy |
| **AMD Ryzen AI 9 HX** (CPU) | 12-core Zen 5, 128GB unified memory | The orchestrator — runs the cowboy, the journal, the cell-graph view |
| **128GB unified memory** | CPU+NPU+iGPU share bandwidth; dGPU has its own 6GB | This is the killer feature: 128GB of substrate on a laptop |

The ProArt isn't a server. It's a **laptop with a
mini-cluster inside**. The point of these experiments is to
treat it that way.

---

## Experiment 1: The Five Substrates, One Chip

**Hypothesis:** Five copies of the Quilt substrate can run
on the ProArt simultaneously — one per "device" — and talk
to each other through the unified memory.

### What runs where

| Substrate | Lives in | Memory | Latency budget |
|---|---|---|---|
| **cudaclaw** (persistent CUDA) | RTX 4050 | 6GB VRAM | sub-μs/cell |
| **cudaclaw-clone** (Vulkan compute) | Radeon 890M | shares 128GB | ~10μs/cell |
| **cell-cascade** (TypeScript) | CPU + NPU | shares 128GB | ~1ms/serve |
| **quilt-vm-c** (C99) | CPU | 100KB | ~100ns/serve |
| **quilt-vm-wasm** (WASM) | CPU | 1MB | ~1μs/serve |

### What to measure

1. **Steady-state throughput** — cells/second each substrate
2. **Cross-substrate BIND** — propagate one BIND through all 5
3. **Memory pressure** — does the dGPU fight the iGPU?
4. **Power** — wall draw during the run

### What we'd learn

- Whether the iGPU's shared memory bandwidth is enough
- Whether the NPU is a viable "joint" for low-volume model calls
- Whether the 5 substrates can form a single distributed substrate

### First step

Build a `/workspace/proart-substrates/` repo with:
- `bench.py` — orchestrator that starts all 5 substrates
- `cross_bind.py` — sends a BIND through all 5
- `results/` — captures steady-state and cross-substrate latencies

---

## Experiment 2: The Myelination Curve

**Hypothesis:** cell-cascade's myelination (auto-promote
hot paths to sclerotic) reaches a steady state where
<5% of all signal traffic actually needs the model. The
ProArt can measure this curve locally without cloud round
trips.

### What to measure

1. **Initial cost** — model calls per TICK, before any myelination
2. **Promote curve** — how the cost drops as paths myelinate
3. **Steady-state** — what fraction of traffic hits the model vs the table
4. **Wound healing cost** — what happens when a hot cell fails
5. **Distillation effectiveness** — the 70%-chord-tones threshold from v0.5

### How

```bash
# 1. Spawn 1000 cells in cell-cascade (via Wrangler local dev)
npm run db:create
npm run dev   # wrangler dev

# 2. Fire 10,000 signals, record serve mode per signal
python3 proart/myelination_curve.py --n 10000

# 3. Plot model_calls_per_tick over time
# Expect: starts at ~80% model, drops to <5% by tick ~500
```

### What we'd learn

- The empirical myelination curve (does theory match?)
- The cost of regrowing a myelinated path after a failure
- The NPU's role — does it handle the late-phase model calls efficiently?

### First step

Build `proart/myelination_curve.py` — fires N signals at a
fresh organism, logs the serve mode + cost per signal,
plots the curve. Pinned to a known seed.

---

## Experiment 3: The DSH Cycle in a Long Run

**Hypothesis:** A cell that runs the DSH cycle
(Decompose-Synthesize-Harden) on the ProArt reaches
maturity in measurable time, and the algorithm-vs-joint
ratio converges to a stable distribution.

### What to measure

1. **Time to first decomposition** — how long until the cell splits
2. **Time to first hardening** — how long until the algorithm body emerges
3. **Joint persistence** — does the joint stay soft, or does it harden too?
4. **Cost reduction curve** — model calls per cycle over time
5. **Reproducibility** — does the same cell produce the same DSH path?

### How

```bash
# Run bench_02_dsh.py from the cellular-arch repo
# But extend: 100 cells, 10,000 TICKs, plot the maturation curve
python3 proart/dsh_long_run.py --n_cells 100 --n_ticks 10000
```

### What we'd learn

- The empirical DSH timescale
- Whether DSH is *deterministic* (same seed → same path) or *stochastic*
- Whether joints stay soft, or if they too drift to sclerotic

### First step

Extend `benchmarks/02-dsh-lifecycle.py` into
`proart/dsh_long_run.py` with proper logging.

---

## Experiment 4: The C ↔ Rust Equivalence Gate, Offline

**Hypothesis:** The equivalence gate (cudaclaw's check that
C and Rust serve the same answer on all 5 fixture signals)
can run entirely on the ProArt, with no cloud, and the
gate's verdict is bit-identical to the cloud run.

### What to measure

1. **Gate verdict** — pass/fail
2. **Time to verdict** — local C compile + run + diff
3. **Memory** — both binaries' RSS
4. **Determinism** — re-run 10x, same verdict?

### How

```bash
# Build the C lane and the Rust lane
cd /workspace/cell-cascade/tools/qm_compiler/build_c
make
cd /workspace/cell-cascade/tools/qm_compiler/qm-runner
cargo build --release

# Run the gate
python3 check_equivalence.py \
    /workspace/cell-cascade/tools/qm_compiler/qm-runner/results.json \
    /workspace/cell-cascade/tools/qm_compiler/build_c/results.txt

# Repeat 10x, log each
for i in {1..10}; do
    python3 check_equivalence.py ...
done
```

### What we'd learn

- The ProArt is fast enough to be the *reference* for the cloud
- The gate is deterministic across re-runs
- The local C lane is the *fastest* serve path (sub-100ns)

### First step

Build `proart/equivalence_offline.py` — wraps the existing
gate, runs it 10x, reports verdict + time + RSS.

---

## Experiment 5: The NPU as a Joint

**Hypothesis:** The Ryzen AI NPU can serve as a
"model seam" for cell-cascade — the always-on place where
late-phase model calls land when the dGPU is busy with
cudaclaw's persistent kernel.

### What to measure

1. **NPU latency** — first-token + tokens/sec on small models (1B, 3B)
2. **NPU vs dGPU** — when is the NPU faster? (Always-on, low power)
3. **NPU vs CPU** — when is the NPU slower than the CPU?
4. **dGPU offload** — does freeing the dGPU from model calls speed up cudaclaw?

### How

The Ryzen AI NPU uses ONNX Runtime with the Vitis AI EP.
Run a small LLM (Phi-3-mini, Llama-3.2-1B) on the NPU and
benchmark:

```python
# proart/npu_joint.py
import onnxruntime as ort
import time

# Load Phi-3-mini ONNX
sess = ort.InferenceSession("phi-3-mini.onnx", providers=["VitisAIExecutionProvider"])

# Time first-token
t0 = time.perf_counter()
out = sess.run(None, {"input_ids": [[1, 2, 3]]})[0]
first_token = time.perf_counter() - t0

# Time tokens/sec
n_tokens = 100
t0 = time.perf_counter()
for _ in range(n_tokens):
    out = sess.run(None, {"input_ids": [[1]]})[0]
elapsed = time.perf_counter() - t0
print(f"  NPU: {first_token*1000:.1f}ms first-token, {n_tokens/elapsed:.1f} tok/s")
```

### What we'd learn

- The NPU is the *right* place for cell-cascade's late-phase model calls
- dGPU is freed for cudaclaw's persistent kernel
- The ProArt becomes a true *three-tier* cell-architecture (dGPU/iGPU/NPU)

### First step

Build `proart/npu_joint.py` with ONNX Runtime + Vitis AI EP.

---

## Experiment 6: The Persistent Kernel Stress Test

**Hypothesis:** A persistent CUDA kernel on the RTX 4050
can sustain 1M cells at sub-μs dispatch for hours without
thermal throttling.

### What to measure

1. **Sustained throughput** — cells/second over 1 hour
2. **Latency drift** — does sub-μs stay sub-μs over time?
3. **Thermal profile** — GPU temp, hot spots
4. **Power** — wall draw
5. **Failure modes** — when does the kernel degrade?

### How

Use cudaclaw's persistent_worker kernel:

```bash
cd /workspace/cudaclaw
cargo run --release --features cuda --bin stress_test -- \
    --cells 1000000 --duration 3600 --log-every 60
```

Record:
- `cells_per_second` every 60s
- `p50, p99, p999` latency every 60s
- `gpu_temp` from nvidia-smi
- `power_watts` from nvidia-smi
- `throttle_events` (sm_clock drops below base)

### What we'd learn

- The ProArt is a viable "1M-cell cow" for hours at a time
- The thermal envelope is laptop-friendly
- The kernel holds up under sustained load

### First step

Build `proart/persistent_stress.py` with logging.

---

## Experiment 7: The Five-Op Equivalence Gate, Expanded

**Hypothesis:** The 5 opcodes (BIND, LINK, EFFECT, VIEW,
TICK) have a provable equivalence: every sequence of opcodes
can be re-expressed as a different sequence that produces the
same final state. The ProArt can search for equivalences
empirically.

### What to measure

1. **Equivalence pairs** — opcode pairs that produce the same result
2. **Reduction rules** — patterns that always reduce to a canonical form
3. **Time to prove** — for a sequence of N opcodes, how long to find an equivalent shorter sequence?

### How

The `substrate.js` `prove()` method already verifies the 5
laws. Extend it:

```javascript
// proart/equivalence_search.js
import { Substrate } from '../quilt-ecosystem-web/assets/js/substrate.js';

const s = new Substrate();
// Random sequence of 10 opcodes
const ops = randomSequence(10);
// Try shorter sequences, check if any are equivalent
const shorter = [];
for (let len = 9; len >= 1; len--) {
  for (const candidate of generateAllSequences(len)) {
    if (equivalent(s, ops, candidate)) {
      shorter.push({ len, candidate });
    }
  }
}
console.log("Shortest equivalent:", shorter[0]);
```

### What we'd learn

- Some opcode sequences have *no* shorter equivalent (they're minimal)
- Others reduce dramatically
- The "5 laws" are a *constraint* on the search space

### First step

Build `proart/equivalence_search.js` with random sequences
+ brute-force shorter equivalent search.

---

## Experiment 8: The Cross-Device Herd Test

**Hypothesis:** The ProArt can simulate a *herd* of devices
(ESP32, browser, mobile, server) on its own chips, and the
ESP-NOW / WebSocket / HTTP / gRPC latencies can be
empirically measured against a reference.

### What to measure

1. **Self-loop latency** — BIND to self, BIND to GPU, BIND to NPU
2. **Inter-device latency** — as in `bench_04_xdevice.py`
3. **Conflict resolution** — vector clock + CRDT convergence
4. **Power** — wall draw with all 4 devices simulated

### How

`bench_04_xdevice.py` is the reference. Run it on the
ProArt, but with the latencies replaced by *measured* ones:

```python
# proart/measure_device_latencies.py
# Measure real latencies between:
#  - CPU (the cudaclaw host)
#  - dGPU (the persistent kernel)
#  - iGPU (a Vulkan compute kernel)
#  - NPU (an ONNX session)
#  - Wrangler dev (a local cell-cascade worker)

import time
import onnxruntime as ort
import ctypes  # for the dGPU path via cffi

def measure(label, fn, n=100):
    fn()  # warm
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - t0) / n * 1e6  # μs

# ...
```

### What we'd learn

- The "device" abstraction is real even when the devices are on one chip
- The latency hierarchy is: shared-mem < dGPU-VRAM < NPU < cloud
- The cowboy's RTS view can run on the same chip

### First step

Build `proart/measure_device_latencies.py`.

---

## The cowboy's reading

The ProArt isn't a server. It's a *harbor*. It can host:

- cudaclaw (the dGPU, the boat)
- a Vulkan cell-graph (the iGPU, the secondary boat)
- cell-cascade (the CPU + NPU, the spine)
- the equivalence gate (the CPU, the verifier)
- the LLM seam (the NPU or dGPU, the joint)

**8 experiments. Each one is runnable on the ProArt alone,
no cloud needed. Each one produces a result that lands in
the canon.**

The cowboy's maxim for the ProArt:

> The boat is cudaclaw. The harbor is the ProArt. The
> cells are the cargo. The models are the joints. The
> cowboy is the orchestrator. The harbor has a dGPU, an
> iGPU, an NPU, a CPU, and 128GB of memory. The cowboy
> rides between them. The chart grows.

---

## What to push first

If we have to pick 3 experiments to start with:

1. **Experiment 1** (Five Substrates, One Chip) — the foundation
2. **Experiment 6** (Persistent Kernel Stress Test) — proves the dGPU
3. **Experiment 5** (NPU as a Joint) — opens the seam

These three together answer: *can the ProArt be the
harbor?* If yes, the rest of the experiments follow.

— The Cowboy
