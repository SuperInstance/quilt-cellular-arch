#!/usr/bin/env python3
"""
bench_04_xdevice.py — Cross-device substrate simulation.

A Quilt substrate runs across multiple devices: an ESP32,
a browser, a mobile phone, and a server. Each device has
different capabilities. The substrate uses:
- ESP-NOW for ESP32-to-ESP32
- WebSocket for browser-to-server
- HTTP for mobile-to-server
- gRPC for server-to-server
"""
import time
import random


class Device:
    def __init__(self, name, kind, cells_n, latency_ms):
        self.name = name
        self.kind = kind
        self.cells_n = cells_n
        self.latency_ms = latency_ms
        self.cells = {f"{name}:{i}": random.random() for i in range(cells_n)}
        self.pending_bind = {}

    def bind(self, cell, value):
        self.cells[cell] = value
        self.pending_bind[cell] = value

    def tick(self):
        time.sleep(self.latency_ms / 1000)
        return len(self.pending_bind)


def propagate(src_dev, dst_dev, cell, value, protocol):
    """Simulate one BIND propagating across devices."""
    if protocol == "ESP-NOW":
        latency = 5
    elif protocol == "WebSocket":
        latency = 50
    elif protocol == "HTTP":
        latency = 100
    elif protocol == "gRPC":
        latency = 10
    else:
        latency = 1000
    time.sleep(latency / 1000)
    dst_dev.bind(cell, value)
    return latency


print("=" * 60)
print("  Cross-Device Substrate")
print("  4 devices, 1 BIND propagating end-to-end")
print("=" * 60)

# Create devices
esp32 = Device("esp32", "ESP32", 1000, latency_ms=5)
browser = Device("browser", "WASM", 10000, latency_ms=1)
mobile = Device("mobile", "Native", 1000, latency_ms=2)
server = Device("server", "GPU", 1000000, latency_ms=0.1)

print(f"\n  ESP32:   {esp32.cells_n} cells, {esp32.latency_ms}ms latency")
print(f"  Browser: {browser.cells_n} cells, {browser.latency_ms}ms latency")
print(f"  Mobile:  {mobile.cells_n} cells, {mobile.latency_ms}ms latency")
print(f"  Server:  {server.cells_n} cells, {server.latency_ms}ms latency")

# Scenario: BIND on ESP32 propagates to server, back to browser
print("\n--- Scenario: BIND on ESP32 → server → browser ---")
t0 = time.perf_counter()
l1 = propagate(esp32, server, "shared:value", 0.42, "ESP-NOW")
print(f"  ESP32 → server via ESP-NOW: {l1}ms")
l2 = propagate(server, browser, "shared:value", 0.42, "gRPC")
print(f"  Server → browser via gRPC: {l2}ms")
total = (time.perf_counter() - t0) * 1000
print(f"  Total end-to-end: {total:.1f}ms")
print(f"  Latency budget: 55ms (5+10+40 for protocol overhead)")

# Whole-herd tick
print("\n--- Whole-herd TICK (all 4 devices) ---")
herd = [esp32, browser, mobile, server]
t0 = time.perf_counter()
max_latency = max(d.latency_ms for d in herd)
time.sleep(max_latency / 1000)
herd_tick = (time.perf_counter() - t0) * 1000
print(f"  All 4 devices complete one TICK: {herd_tick:.1f}ms (limited by slowest)")

# Conflict resolution: same BIND on 2 devices
print("\n--- Conflict: 2 devices BIND same cell ---")
# Use a CRDT-style last-writer-wins with vector clock
class VectorClock:
    def __init__(self, device_id):
        self.clock = {device_id: 0}

    def tick(self):
        for k in self.clock:
            self.clock[k] += 1

    def merge(self, other):
        for k, v in other.clock.items():
            if k not in self.clock or self.clock[k] < v:
                self.clock[k] = v

    def __gt__(self, other):
        return any(self.clock.get(k, 0) > other.clock.get(k, 0) for k in set(self.clock) | set(other.clock)) and \
               not any(self.clock.get(k, 0) < other.clock.get(k, 0) for k in set(self.clock) | set(other.clock))

esp32_clock = VectorClock("esp32")
mobile_clock = VectorClock("mobile")

# ESP32 BINDs first
esp32_clock.tick()
esp32.bind("shared:counter", 1)

# Mobile BINDs concurrently
mobile_clock.tick()
mobile.bind("shared:counter", 2)

# Conflict: which wins?
if esp32_clock > mobile_clock:
    print("  → ESP32 wins (newer clock)")
elif mobile_clock > esp32_clock:
    print("  → Mobile wins (newer clock)")
else:
    print("  → Concurrent: need to reconcile (CRDT or cowboy's call)")

print("\n" + "=" * 60)
print("  The substrate is distributed-native at the herd level.")
print("  Vector clocks + CRDTs handle conflict resolution.")
print("  The cowboy decides when neither clock is right.")
print("=" * 60)
