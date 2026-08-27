"""api_pulse.py — quick test of all voices, mark which are working."""
import sys
import time
sys.path.insert(0, '/workspace/_scouts')
from multi_api_v2 import call_voice, VOICES

print("=" * 60)
print("API PULSE — quick test of all 19 voices")
print("=" * 60)
print()

PROMPT = "Reply in 5 words or less: what is the Quilt?"

working = []
failing = []
reasoning = []

for vname in VOICES.keys():
    try:
        n, out = call_voice(vname, PROMPT, max_tokens=200)
        if out and not out.startswith('[') and not out.startswith('('):
            preview = out.replace('\n', ' ').strip()[:80]
            print(f"  [✓] {vname:10s}: {preview}")
            working.append(vname)
        else:
            print(f"  [✗] {vname:10s}: {out[:60] if out else '(empty)'}")
            failing.append(vname)
    except Exception as e:
        print(f"  [!] {vname:10s}: err {e}")
        failing.append(vname)
    time.sleep(0.5)

print()
print("─" * 60)
print(f"  Working: {len(working)}/{len(VOICES)}")
print(f"  Failing: {len(failing)}/{len(VOICES)}")
if working:
    print(f"  Working voices: {', '.join(working)}")
if failing:
    print(f"  Failing voices: {', '.join(failing)}")
print()

# Save to a file for tracking
with open('/workspace/_scouts/api_pulse.log', 'w') as f:
    f.write(f"API Pulse — {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Working: {len(working)}/{len(VOICES)}\n")
    f.write(f"Failing: {failing}\n")
    f.write(f"Working: {working}\n")
print("Saved to /workspace/_scouts/api_pulse.log")
