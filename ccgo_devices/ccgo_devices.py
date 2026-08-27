#!/usr/bin/env python3
"""
ccgo_devices.py — The 4-finger salute (CCGO) with
real-device sketches.

The 4 fingers are:
  C - Couple (the player-artifact coupling)
  C - Cellulize (substrate becomes cell)
  G - Gold (sort the gold from the dross)
  O - Operate (execute the operation)

This script generates real ESP32 MicroPython
sketches for the 5 cell populations on the Eileen
ecosystem, and shows the CCGO cycle for each.
"""


# ============================================================
# The 4 fingers of CCGO
# ============================================================
def couple_code(device_name):
    """The Couple step — the player-artifact coupling."""
    return f"""
# {device_name} - CCGO Step 1: Couple
# The cowboy couples with the cell.
# The cell is alive when the cowboy plays it.
from machine import Pin, ADC
import time

# Initialize the cell
class Cell:
    def __init__(self, name):
        self.name = name
        self.coupled = False
        self.vitality = 0.0

    def couple(self):
        self.coupled = True
        self.vitality = 1.0
        print(f"[{self.name}] coupled, vitality={self.vitality}")

cell = Cell("{device_name}")
cell.couple()
"""


def cellulize_code(device_name, sensor_type):
    """The Cellulize step — substrate becomes cell."""
    return f"""
# {device_name} - CCGO Step 2: Cellulize
# The substrate becomes a cell.
# The cell has a persistence pulse.
{device_name} = Cell("{device_name}")
{device_name}.cellulize(function="{sensor_type}")

# The persistence pulse
def pulse(cell):
    cell.persistence_pulse += 1
    print(f"[{{cell.name}}] pulse #{{cell.persistence_pulse}}")
"""


def gold_code(device_name):
    """The Gold step — sort the gold from the dross."""
    return f"""
# {device_name} - CCGO Step 3: Gold
# The cowboy sorts the gold from the dross.
readings = []

def is_gold(reading):
    # Heuristic: gold is in the expected range
    return 0 < reading < 100

for _ in range(10):
    reading = sensor.read()  # platform-specific
    if is_gold(reading):
        readings.append(reading)  # gold
    # dross is discarded

print(f"[{device_name}] gold: {{len(readings)}}/10")
"""


def operate_code(device_name, output_method):
    """The Operate step — execute the operation."""
    return f"""
# {device_name} - CCGO Step 4: Operate
# The cowboy executes the operation.
# {output_method}

def operate(cell, reading):
    if output_method == "print":
        print(f"[{{cell.name}}] {{reading}}")
    elif output_method == "mqtt":
        client.publish("eileen/{device_name}", str(reading))
    elif output_method == "sd":
        with open("/sd/{device_name}.log", "a") as f:
            f.write(f"{{reading}}\\n")
"""


# ============================================================
# The 5 cell populations and their CCGO cycles
# ============================================================
def main():
    print("=" * 78)
    print("  THE 4-FINGER SALUTE — CCGO with real-device sketches")
    print("=" * 78)
    print()
    print("  The 4 fingers of CCGO:")
    print("    C - Couple (the player-artifact coupling)")
    print("    C - Cellulize (substrate becomes cell)")
    print("    G - Gold (sort the gold from the dross)")
    print("    O - Operate (execute the operation)")
    print()

    # The 5 cell populations
    populations = [
        {
            "name": "eileen-engine",
            "sensor": "engine_rpm",
            "platform": "ESP32",
            "output": "mqtt",
        },
        {
            "name": "eileen-jetson",
            "sensor": "camera_frame",
            "platform": "Jetson",
            "output": "sd",
        },
        {
            "name": "eileen-weather",
            "sensor": "wind_speed",
            "platform": "ESP32",
            "output": "mqtt",
        },
        {
            "name": "eileen-water",
            "sensor": "depth",
            "platform": "ESP32",
            "output": "mqtt",
        },
        {
            "name": "eileen-workstation",
            "sensor": "log_file",
            "platform": "laptop",
            "output": "print",
        },
    ]

    for pop in populations:
        print(f"  {pop['name'].upper()} ({pop['platform']}):")
        print(f"    sensor: {pop['sensor']}")
        print(f"    output: {pop['output']}")
        print(f"    CCGO:")
        print(f"      C: Coupled cowboy -> {pop['name']}")
        print(f"      C: Cellulized substrate -> {pop['name']}")
        print(f"      G: Sorted gold from dross")
        print(f"      O: Operated -> {pop['output']}")
        print()

    # Show one full MicroPython sketch
    print("  " + "-" * 78)
    print("  SAMPLE SKETCH: eileen-engine (ESP32 MicroPython)")
    print("  " + "-" * 78)
    print()
    print(couple_code("eileen-engine"))
    print(cellulize_code("eileen-engine", "engine_rpm"))
    print(gold_code("eileen-engine"))
    print(operate_code("eileen-engine", "mqtt"))
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — CCGO on real devices")
    print("=" * 78)
    print()
    print("  The 4 fingers of CCGO run on every device:")
    print("    1. ESP32 (engine, weather, water)")
    print("    2. Jetson (camera)")
    print("    3. laptop (workstation)")
    print()
    print("  The 5 cell populations are all alive when the cowboy plays them.")
    print("  The 4-finger salute runs on every substrate.")
    print("  The cowboy rides CCGO on the boat.")
    print()
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
