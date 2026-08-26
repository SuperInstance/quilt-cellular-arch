#!/usr/bin/env python3
"""Quick SIMD benchmark."""
import numpy as np
import time

def bench(name, fn, n=100):
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    ms = (time.perf_counter() - t0) / n * 1000
    print(f"  {name:30s}: {ms:.4f} ms")
    return ms

N = 10000
values = np.zeros(N, dtype=np.float64)
si = np.random.randint(0, N, 100)
sv = np.random.random(100)
gi = np.random.randint(0, N, 1000)

print("=== BIND (100 writes) ===")
def sb():
    for i, idx in enumerate(si):
        values[idx] = sv[i]
def vb():
    values[si] = sv
s = bench("scalar BIND", sb)
v = bench("NumPy BIND", vb)
print(f"  Speedup: {s/v:.1f}x")

print("\n=== VIEW (1000 reads) ===")
def sv():
    out = np.zeros(1000)
    for i, idx in enumerate(gi):
        out[i] = values[idx]
    return out
def vv():
    return values[gi]
s = bench("scalar VIEW", sv)
v = bench("NumPy VIEW", vv)
print(f"  Speedup: {s/v:.1f}x")

print("\n=== EFFECT (transform N cells) ===")
def se():
    out = np.zeros(N)
    for i in range(N):
        out[i] = values[i] * 2 + 1
    return out
def ve():
    return values * 2 + 1
s = bench("scalar EFFECT", se)
v = bench("NumPy EFFECT", ve)
print(f"  Speedup: {s/v:.1f}x")

print("\n=== TICK (modulo N cells) ===")
def st():
    for i in range(1000):
        values[i] = (values[i] + 1) % 1.0
def vt():
    np.add(values, 1, out=values)
    np.mod(values, 1, out=values)
s = bench("scalar TICK (1k)", st)
v = bench("NumPy TICK (10k)", vt)
print(f"  NumPy is 10x larger: per-cell speedup: {s/v*10:.1f}x")

print("\n=== LINK (graph scatter) ===")
src = np.random.randint(0, 1000, 1000)
dst = np.random.randint(0, 1000, 1000)
def sl():
    adj = np.zeros((1000, 1000))
    for i in range(1000):
        adj[src[i], dst[i]] = 1.0
    return adj
def vl():
    adj = np.zeros((1000, 1000))
    np.add.at(adj, (src, dst), 1.0)
    return adj
s = bench("scalar LINK", sl)
v = bench("NumPy LINK", vl)
print(f"  Speedup: {s/v:.1f}x")
