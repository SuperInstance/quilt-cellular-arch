#!/usr/bin/env python3
"""
00_whoami.py — Identify the ProArt's compute substrate.

This is the first experiment the local agents should run.
It probes:
  - CPU (model, cores, frequency)
  - Memory (total, available)
  - dGPU (NVIDIA, via nvidia-smi)
  - iGPU (AMD, via /sys/class/drm)
  - NPU (Ryzen AI, via xdna-driver or lsmod)

Output: a JSON manifest of the ProArt's compute substrate.
The cowboy uses this to know what experiments can run where.
"""
import json
import subprocess
import os
import platform
from pathlib import Path

def run(cmd, default=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else default
    except Exception:
        return default

def probe_cpu():
    return {
        "model": run("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2", "unknown").strip(),
        "cores_physical": int(run("lscpu | grep 'Core(s) per socket' | awk '{print $NF}'", "0") or 0),
        "cores_logical": int(run("nproc", "0") or 0),
        "frequency_mhz": run("lscpu | grep 'CPU MHz' | awk '{print $NF}'", "?"),
        "flags": (run("cat /proc/cpuinfo | grep flags | head -1 | cut -d: -f2") or "").split()[:20],
    }

def probe_memory():
    meminfo = open("/proc/meminfo").read()
    def get(k):
        for line in meminfo.split("\n"):
            if line.startswith(k):
                return int(line.split()[1])  # kB
        return 0
    return {
        "total_kb": get("MemTotal"),
        "available_kb": get("MemAvailable"),
        "total_gb": round(get("MemTotal") / 1024 / 1024, 1),
        "available_gb": round(get("MemAvailable") / 1024 / 1024, 1),
    }

def probe_dgpu():
    """NVIDIA dGPU via nvidia-smi."""
    out = run("nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version,temperature.gpu,power.draw,clocks.gr,clocks.mem --format=csv,noheader,nounits", "")
    if not out:
        return {"present": False}
    parts = [p.strip() for p in out.split(",")]
    return {
        "present": True,
        "name": parts[0] if len(parts) > 0 else "?",
        "vram_total_mb": int(parts[1]) if len(parts) > 1 else 0,
        "vram_free_mb": int(parts[2]) if len(parts) > 2 else 0,
        "driver": parts[3] if len(parts) > 3 else "?",
        "temp_c": int(parts[4]) if len(parts) > 4 else 0,
        "power_w": float(parts[5]) if len(parts) > 5 else 0,
        "sm_clock_mhz": int(parts[6]) if len(parts) > 6 else 0,
        "mem_clock_mhz": int(parts[7]) if len(parts) > 7 else 0,
    }

def probe_igpu():
    """AMD iGPU via /sys/class/drm."""
    cards = []
    for d in Path("/sys/class/drm").iterdir():
        if d.name.startswith("card") and "-" not in d.name:
            vendor = (d / "device" / "vendor").read_text().strip() if (d / "device" / "vendor").exists() else "?"
            device = (d / "device" / "device").read_text().strip() if (d / "device" / "device").exists() else "?"
            cards.append({"card": d.name, "vendor": vendor, "device": device})
    return {
        "present": any(c["vendor"] == "0x1002" for c in cards),  # AMD
        "cards": cards,
    }

def probe_npu():
    """Ryzen AI NPU via lsmod or /dev/accel."""
    npu_present = Path("/dev/accel/accel0").exists() or "amdxdna" in (run("lsmod | grep xdna", "") or "")
    return {
        "present": npu_present,
        "module": (run("lsmod | grep xdna | awk '{print $1}'", "") or "").strip(),
    }

def probe_kernel():
    return {
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }

def main():
    print("=" * 60)
    print("  ProArt Whoami — the cowboy probes the harbor")
    print("=" * 60)
    manifest = {
        "kernel": probe_kernel(),
        "cpu": probe_cpu(),
        "memory": probe_memory(),
        "dgpu": probe_dgpu(),
        "igpu": probe_igpu(),
        "npu": probe_npu(),
    }
    print(json.dumps(manifest, indent=2))
    # Save to a file
    out = Path("/workspace/quilt-cellular-arch/proart/whoami.json")
    out.write_text(json.dumps(manifest, indent=2))
    print(f"\n  Saved to: {out}")
    print(f"\n  Verdict:")
    if manifest["dgpu"]["present"]:
        print(f"    dGPU: {manifest['dgpu']['name']} ({manifest['dgpu']['vram_total_mb']}MB VRAM)")
    if manifest["igpu"]["present"]:
        print(f"    iGPU: AMD present (Radeon 890M expected on Strix Halo)")
    if manifest["npu"]["present"]:
        print(f"    NPU: Ryzen AI XDNA 2 present")
    print(f"    CPU:  {manifest['cpu']['cores_logical']} threads")
    print(f"    RAM:  {manifest['memory']['total_gb']}GB")
    print()
    print("  The harbor is mapped. The cowboy knows the boats.")
    print("=" * 60)

if __name__ == "__main__":
    main()
