# `webgpu_substrate.py` — WebGPU substrate sketch

WebGPU runs in the browser. The 5 opcodes map to GPU
primitives. This is a pseudo-code sketch (no wgpu-py
installed in the sandbox).

```python
# webgpu_substrate.py — WebGPU substrate sketch
# Browser-side JavaScript would be the production version.

class WebGPUSubstrate:
    """WebGPU substrate. The 5 opcodes are compute shaders."""

    def __init__(self, device, n_cells=10000):
        self.device = device
        self.n = n_cells
        # Cell state: 32 bytes per cell (8 bytes value, 8 bytes timestamp, 16 bytes metadata)
        self.cell_buffer = device.createBuffer(
            size=n_cells * 32,
            usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.COPY_SRC
        )
        # Graph adjacency (CSR sparse matrix)
        self.adjacency_buffer = device.createBuffer(
            size=n_cells * n_cells * 4,  # 32-bit weights
            usage=wgpu.BufferUsage.STORAGE
        )
        # Journal: ring buffer of events
        self.journal_buffer = device.createBuffer(
            size=10_000_000,  # 10MB
            usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC
        )

    # ---- BIND: parallel write to N cells ----
    def bind(self, indices, values):
        # Browser: writeBuffer() per index, or one big writeBuffer
        # GPU side: a tiny compute shader does parallel assignment
        bind_shader = """
        @compute @workgroup_size(64)
        fn bind_main(
            @builtin(global_invocation_id) gid : vec3<u32>,
            var<storage, read> indices : array<u32>,
            var<storage, read_write> cells : array<Cell>,
        ) {
            let i = gid.x;
            if (i >= arrayLength(&indices)) { return; }
            let idx = indices[i];
            cells[idx].value = bitcast<f64>(u64(0xBEEF));  // placeholder
        }
        """

    # ---- LINK: parallel edge construction ----
    def link(self, src_indices, dst_indices, weights):
        # CSR sparse matrix on GPU
        # Browser: build CSR on CPU, upload as one buffer
        pass

    # ---- EFFECT: parallel function application ----
    def effect(self, indices, func_shader):
        # Compute shader that applies func_shader to each cell
        # Browser: compute pass
        pass

    # ---- VIEW: parallel read from N cells ----
    def view(self, indices):
        # Browser: readBuffer() + map
        pass

    # ---- TICK: parallel time advance across the graph ----
    def tick(self, dt):
        # Compute barrier + new dispatch
        # Each cell's TICK updates its timestamp
        pass

# Frame loop:
#   1. Read pending BINDs, LINKs, EFFECTs from journal
#   2. Dispatch compute shaders in sequence
#   3. Compute barrier
#   4. Update timestamps (TICK)
#   5. Render UI from cell values (VIEW)
```

**Browser-side** (HTML+JS, the production version):

```html
<script>
async function initWebGPU() {
  const adapter = await navigator.gpu.requestAdapter();
  const device = await adapter.requestDevice();
  const substrate = new WebGPUSubstrate(device, 10000);
  // Load shaders, build pipeline, etc.
}
</script>
```

**The win:** WebGPU gives the substrate 10,000 cells at
60 FPS in the browser. The cowboy can run a 10K-cell
simulation in real time. The substrate becomes a
first-class citizen of the browser.

**Next step:** write the WGSL shaders (bind, link, effect,
view, tick) and the HTML harness. The pseudo-code above
is the spec; the WGSL is the implementation.
