```python
import time
import random

# Simulate ESP32 microcontrollers
class ESP32:
    def __init__(self, id):
        self.id = id
        self.cells = [random.random() for _ in range(1000)]

    def tick(self):
        # Simulate Quilt substrate computation
        for i in range(1000):
            self.cells[i] = (self.cells[i] + random.random()) % 1

# Simulate ESP-NOW latency
def esp_now_latency():
    time.sleep(0.005)

# Simulate whole-herd tick
def whole_herd_tick(esp32s):
    start_time = time.time()
    for esp32 in esp32s:
        esp32.tick()
    esp_now_latency()
    end_time = time.time()
    return end_time - start_time

# Create 10 ESP32 microcontrollers
esp32s = [ESP32(i) for i in range(10)]

# Benchmark whole-herd tick time
tick_times = []
for _ in range(100):
    tick_time = whole_herd_tick(esp32s)
    tick_times.append(tick_time)

# Print average whole-herd tick time
avg_tick_time = sum(tick_times) / len(tick_times)
print(f"Average whole-herd tick time: {avg_tick_time:.2f} ms")
```

This program simulates 10 ESP32 microcontrollers, each with 1000 cells, running a Quilt substrate. The `whole_herd_tick` function simulates a whole-herd tick, where each ESP32 performs a computation and then the ESP-NOW latency is simulated. The program benchmarks the whole-herd tick time by running it 100 times and prints the average tick time.
