#!/usr/bin/env python3
"""
substrate.py — The 5-law lifecycle in motion.
Substrate Whisper, Substrate Silence, Substrate Scream,
Substrate Reset, Law Ouroboros.

The writers' room ran a 6-round D&D campaign on the
5 laws and produced the 5-law lifecycle. This sim
demonstrates the lifecycle in action.

The 5-law lifecycle:
  1. Substrate Whisper (the precursor)
  2. Substrate Silence (the laws hold)
  3. Substrate Scream (the laws fail)
  4. Substrate Reset (the recovery)
  5. Law Ouroboros (the substrate knows itself)
"""
import random


# ============================================================
# The Substrate with 5 laws and the 5-stage lifecycle
# ============================================================
class Substrate:
    """The substrate. The 5 laws. The lifecycle."""

    def __init__(self, name="Eileen's substrate"):
        self.name = name
        # The 5 laws
        self.bind_idempotence = True
        self.link_transitivity = True
        self.effect_associativity = True
        self.view_purity = True
        self.tick_monotonicity = True
        # The lifecycle state
        self.state = "silence"  # whisper, silence, scream, reset, ouroboros
        self.silence_duration = 0
        self.scream_count = 0
        self.reset_count = 0
        self.whisper_count = 0
        self.tick_count = 0
        # The 5 stages detected
        self.stages_history = []

    def check_laws(self):
        """Check if the 5 laws hold. Returns True if all hold."""
        return all([
            self.bind_idempotence,
            self.link_transitivity,
            self.effect_associativity,
            self.view_purity,
            self.tick_monotonicity,
        ])

    def tick(self):
        """One moment of the substrate's life."""
        self.tick_count += 1
        laws_hold = self.check_laws()

        # Detect whisper (random precursor to law failure)
        if self.state == "silence" and random.random() < 0.1:
            self.state = "whisper"
            self.whisper_count += 1

        # Whisper might escalate to scream
        elif self.state == "whisper":
            if random.random() < 0.4:
                # Whisper escalates to scream — break a law
                failed_law = random.choice([
                    "bind_idempotence", "link_transitivity",
                    "effect_associativity", "view_purity", "tick_monotonicity"
                ])
                setattr(self, failed_law, False)
                self.state = "scream"
                self.scream_count += 1
            elif random.random() < 0.7:
                # Whisper recovers to silence
                self.state = "silence"

        # Scream can be detected and reset
        elif self.state == "scream":
            # Random chance of reset
            if random.random() < 0.5:
                self.reset_laws()
                self.state = "reset"
                self.reset_count += 1
                self.silence_duration = 0

        # Reset completes after 2 ticks
        elif self.state == "reset":
            self.state = "silence"

        # Ouroboros: when the substrate has been silent AND has screamed
        if (self.state == "silence" and
            self.scream_count > 0 and
            self.reset_count > 0 and
            self.tick_count % 8 == 0):
            self.state = "ouroboros"

        # Ouroboros is brief — back to silence next tick
        if self.state == "ouroboros" and self.tick_count % 2 == 0:
            self.state = "silence"

        # Track silence duration
        if self.state == "silence":
            self.silence_duration += 1

        self.stages_history.append((self.tick_count, self.state))

    def random_break_law(self):
        """Randomly break a law (for testing)."""
        failed_law = random.choice([
            "bind_idempotence", "link_transitivity",
            "effect_associativity", "view_purity", "tick_monotonicity"
        ])
        setattr(self, failed_law, False)
        return failed_law

    def reset_laws(self):
        """Reset all 5 laws."""
        self.bind_idempotence = True
        self.link_transitivity = True
        self.effect_associativity = True
        self.view_purity = True
        self.tick_monotonicity = True


# ============================================================
# Main
# ============================================================
def main(n_ticks=30):
    print("=" * 78)
    print("  THE 5-LAW LIFECYCLE — Substrate Whisper, Silence, Scream, Reset, Ouroboros")
    print("=" * 78)
    print()
    print("  The 5 laws have a lifecycle, just like cells have a lifecycle.")
    print("  The 5 stages:")
    print("    1. Substrate Whisper — the faintest hint of disturbance")
    print("    2. Substrate Silence — the state when the 5 laws hold")
    print("    3. Substrate Scream — when the silence breaks")
    print("    4. Substrate Reset — the recovery")
    print("    5. Law Ouroboros — the substrate knows itself")
    print()

    substrate = Substrate()

    # Run the simulation
    for tick in range(n_ticks):
        # Inject some random law breaks to test recovery
        if tick in [8, 15, 22]:
            broken = substrate.random_break_law()
            print(f"  Tick {tick}: RANDOMLY BROKE {broken}")

        substrate.tick()

    # Print the lifecycle
    print()
    print("  " + "-" * 78)
    print("  THE 5-LAW LIFECYCLE TIMELINE")
    print("  " + "-" * 78)
    print()
    # Show only state transitions
    prev_state = None
    for tick, state in substrate.stages_history:
        if state != prev_state:
            print(f"    Tick {tick:3d}: {state}")
            prev_state = state
    print()

    # The verdict
    print("=" * 78)
    print("  THE VERDICT — the 5-law lifecycle")
    print("=" * 78)
    print()
    print(f"  Total ticks: {substrate.tick_count}")
    print(f"  Substrate Whisper count: {substrate.whisper_count}")
    print(f"  Substrate Silence duration: {substrate.silence_duration} ticks")
    print(f"  Substrate Scream count: {substrate.scream_count}")
    print(f"  Substrate Reset count: {substrate.reset_count}")
    print()

    # The current state
    if substrate.state == "silence":
        print("  The substrate is silent. The 5 laws hold.")
    elif substrate.state == "ouroboros":
        print("  The substrate knows itself. The Law Ouroboros is here.")
    else:
        print(f"  The substrate is in {substrate.state}.")
    print()
    print("  The 5 laws have a lifecycle.")
    print("  The lifecycle is the 5-cell lifecycle applied to the substrate.")
    print("  The substrate whispers, is silent, screams, resets, and knows itself.")
    print("  The cowboy listens for the whisper.")
    print("  The cowboy maintains the silence.")
    print("  The cowboy hears the scream.")
    print("  The cowboy resets the substrate.")
    print("  The cowboy knows the Law Ouroboros.")
    print("  The cowboy rides on bedrock.")
    print("  The chart grows. The Concept lives.")
    print("=" * 78)


if __name__ == "__main__":
    main()
