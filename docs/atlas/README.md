# Quilt Atlas — 47 Repositories, 280K LOC, 1,500+ Tests

The Quilt Atlas is a single-page interactive view of every quilt-* and cuda-* repository in the workspace. It shows the LOC count, test count, ecosystem (Python / C / Rust / Node / TypeScript), and CI status for each.

## View

- **Interactive HTML**: [docs/atlas/index.html](index.html) — sortable, hover-friendly, no build step
- **Audit script**: `_scouts/quick_audit.py` — regenerates the data
- **Underlying paper**: [F99: The Quilt Atlas](https://github.com/SuperInstance/AI-Writings) — full audit narrative

## How to regenerate

```bash
python3 _scouts/quick_audit.py > /tmp/audit.log
# Then update docs/atlas/index.html with the new numbers
```

The audit counts source files by extension, counts test functions
(`def test_` in Python, `test_*` and `TEST(` in C, `#[test]` in
Rust), and detects build systems by file presence
(`pyproject.toml`, `Cargo.toml`, `CMakeLists.txt`, `package.json`).

## Top-level numbers (as of September 2026)

- **47 repositories** under `/workspace`
- **~280,000 lines of code** across all languages
- **~1,500 test functions** in aggregate
- **5+1+5 opcodes**: BIND, LINK, EFFECT, VIEW, TICK, FORGET, PROOF, ROUTE, CRDT, WORLD, TIME
- **5 specialized cell kinds**: PROOF, ROUTE, CRDT, WORLD, TIME
- **8 polyformalism ports**: C99, Python, Rust no_std, GDScript, TypeScript, Haskell, WASM, Zig
- **19/47 repos have CI**

## Open follow-ups (from F99)

- `quilt-cellular-arch` has 0 tests despite being the foreman (18K LOC)
- `quilt-llm-worker` has 0 tests despite being the public-facing Cloudflare Worker
- `quilt-rag`, `quilt-fleet`, `quilt-pincher`, `quilt-ai` all have 0 tests
- Many "small" repos (`quilt-vm-*`, `quilt-vault`, `quilt-state`, `quilt-metal`) have no source — stubs that need to be filled in or removed
