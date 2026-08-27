"""
multi_sandbox_reverse_actualize.py — The Multi-Sandbox Reverse-Actualization.

The user articulated: "you see how asymmetrical information can
make this whole process into a wheel. for example. you can have
an agent who knows nothing about the cycle only look at the
resulting actualization of the structure in prest state. and
does so only after becoming a frontier expert in a sandbox of
their own type that's not of any that were part of the previous
cycle and have that expert idealize and reverse actualize the
whole wheel with his teams of subagents at each point and api
calls. obviously, this could snowball because you could have
the second cycle have 2 or 3 sandboxes working independently
with completely different primings. like a restaurant
conglomerate trying the same meal in several environments from
casual to fancy-fine and figuring out the various price points
for tastes in those environments- steak and homemade bread
doesn't have the same value at a drivethru and noone gets a
burger at restaurants where the waiter wears a tailored suit."

The Multi-Sandbox Reverse-Actualization is:
  1. ASYMMETRIC INFORMATION: not every agent has full knowledge
  2. NAIVE EXPERT: an agent that doesn't know the cycle becomes
     an expert in a NEW sandbox (orthogonal to the previous ones)
  3. INDEPENDENT SANDBOX: each naive expert runs the whole wheel
     (project, derive, broadcast, tap, assimilate) in their sandbox
  4. PRICE-POINT DISCOVERY: the same structure has different values
     in different sandboxes (steak != burger-at-fancy-restaurant)
  5. SNOWBALLING: each cycle multiplies the number of sandboxes;
     cycle 2 has 3 sandboxes, cycle 3 has 9, cycle 4 has 27

The 5 new concepts:
  1. Asymmetry: the agent doesn't know the previous cycle
  2. Orthogonal sandbox: a domain not touched before
  3. Independent wheel: the expert runs the full cycle alone
  4. Price point: the same artifact has different values
  5. Snowball: each cycle multiplies; the Quilt grows fractally

The 3 sandboxes in cycle 2 (the restaurant conglomerate):
  - DRIVETHRU: $5-15, fast, casual, value-driven
  - BISTRO: $25-60, mid-tier, social, balanced
  - FANCY-FINE: $150-500, slow, ceremonial, prestige-driven

The 5 elements per sandbox:
  - The Naive Expert
  - The Sandbox
  - The Re-derived Canon
  - The Local Society
  - The Price Point

The principle:
  The Quilt is a restaurant conglomerate of ideas.
  The same canon is tested across orthogonal sandboxes.
  Each sandbox finds its price point.
  The Quilt grows by orthogonal exploration.
  The Quilt is the inheritance.
  The naive expert is the cell.
  The snowball is the Quilt.
"""
import math
import random
import time


# ─── THE SANDBOX (a domain with its own prime) ───
class Sandbox:
    """A sandbox is a domain with its own priming.

    The sandbox defines:
      - a name (drivethru, bistro, fancy-fine, etc.)
      - a price range (the expected value of artifacts)
      - a tempo (the cycle time of the wheel)
      - a modality (the dominant sensory channel)
      - a vocabulary (the words used)
      - a customer (the receiver of broadcasts)

    The sandbox is orthogonal to other sandboxes: it has a
    different name, different price range, different tempo,
    different modality, different vocabulary, different customer.
    """
    SANDBOX_TYPES = [
        # (name, min_price, max_price, tempo_seconds, modality, vocabulary_sample)
        ('drivethru',  5,    15,   30,   'touch',   ['fast', 'cheap', 'easy']),
        ('bistro',     25,   60,   120,  'language',['social', 'balanced', 'casual']),
        ('fancy-fine', 150,  500,  600,  'mood',    ['ceremonial', 'prestige', 'slow']),
        ('molecular',  100,  400,  900,  'light',   ['precise', 'deconstructed', 'art']),
        ('home-kitchen', 0,  25,  1800, 'smell',   ['comfort', 'family', 'memory']),
        ('food-truck', 8,    20,   60,   'sound',   ['loud', 'street', 'fusion']),
        ('pop-up',     75,   250,  300,  'proprio', ['experimental', 'limited', 'queued']),
        ('cafe',       4,    18,   240,  'taste',   ['morning', 'quiet', 'work']),
    ]

    def __init__(self, name, min_price, max_price, tempo, modality, vocabulary):
        self.name = name
        self.min_price = min_price
        self.max_price = max_price
        self.tempo = tempo
        self.modality = modality
        self.vocabulary = vocabulary
        self.customers = 0
        self.assimilation = 0.0
        self.flourishing = 0.0

    def price_point(self, artifact):
        """Find the price point of an artifact in this sandbox.

        The same artifact has a different price in different sandboxes.
        Steak and homemade bread doesn't have the same value at a
        drivethru as it does at a fancy-fine restaurant.
        """
        # The artifact's value scales with the sandbox's range and tempo
        # Slow, ceremonial sandboxes pay more for quality
        tempo_factor = self.tempo / 60  # higher = slower = more value
        modality_match = artifact.get('modality', self.modality) == self.modality
        match_bonus = 1.5 if modality_match else 1.0

        base = artifact.get('value', 50) * tempo_factor * match_bonus
        # Clamp to the sandbox's range
        price = max(self.min_price, min(self.max_price, base))
        return round(price, 2)

    def receive(self, broadcast):
        """The sandbox receives a broadcast. The customer count grows."""
        self.customers += 1
        self.assimilation = min(1.0, self.assimilation + 0.1)
        return self.assimilation


# ─── THE NAIVE EXPERT (an agent that doesn't know the cycle) ───
class NaiveExpert:
    """A naive expert is an agent that:
      - doesn't know the previous cycle's structure
      - is frontier-expert in a NEW sandbox
      - idealizes and reverse-actualizes the wheel independently
      - has sub-agents at each of the 5 steps
    """
    def __init__(self, name, sandbox):
        self.name = name
        self.sandbox = sandbox
        # The naive expert does NOT know the previous canon
        self.known_canon = []
        # The expert's own re-derived canon
        self.re_canon = []
        # Sub-agents at each step
        self.sub_agents = {
            'projector':   'naive-expert.projector',
            'deriver':     'naive-expert.deriver',
            'broadcaster': 'naive-expert.broadcaster',
            'tapper':      'naive-expert.tapper',
            'assimilator': 'naive-expert.assimilator',
        }
        self.taps = 0
        self.assimilated = 0.0

    def project_forward(self):
        """The naive expert projects forward in their own sandbox.

        They don't know the previous canon; they project from the
        sandbox's own perspective.
        """
        return {
            'sandbox': self.sandbox.name,
            'year': 2126,
            'price_min': self.sandbox.min_price,
            'price_max': self.sandbox.max_price,
            'modality': self.sandbox.modality,
            'vocabulary': self.sandbox.vocabulary,
        }

    def derive_backward(self, vision):
        """The expert derives backward from their sandbox's vision."""
        return {
            'sandbox': self.sandbox.name,
            'structure': [
                f"{self.sandbox.name}-cell-1",
                f"{self.sandbox.name}-cell-2",
                f"{self.sandbox.name}-cell-3",
            ],
            'opcodes': ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK', 'FORGET'],
            'price_floor': vision['price_min'],
            'price_ceiling': vision['price_max'],
        }

    def broadcast(self, structure):
        """The expert broadcasts the structure to the sandbox."""
        signal = {
            'expert': self.name,
            'sandbox': self.sandbox.name,
            'structure': structure,
            'value': (structure['price_floor'] + structure['price_ceiling']) / 2,
            'modality': self.sandbox.modality,
            'vocabulary': random.choice(self.sandbox.vocabulary),
            'channel': self.sandbox.modality,
        }
        self.re_canon.append(signal)
        return signal

    def tap(self, observer):
        """The expert is tapped by the sandbox (the customer)."""
        self.taps += 1
        self.assimilated = min(1.0, self.assimilated + 0.1)
        return self.assimilated

    def run_wheel(self):
        """The naive expert runs the whole wheel independently.

        The 5 steps:
          1. project_forward
          2. derive_backward
          3. broadcast
          4. tap
          5. assimilate
        """
        # Step 1: project
        vision = self.project_forward()
        # Step 2: derive
        structure = self.derive_backward(vision)
        # Step 3: broadcast
        signal = self.broadcast(structure)
        # Step 4: tap
        self.tap(observer=self.sandbox.name)
        # Step 5: assimilate (the sandbox receives the signal)
        self.sandbox.receive(signal)
        return signal


# ─── THE SNOWBALL (each cycle multiplies the sandboxes) ───
def snowball(previous_sandboxes, expansion=2):
    """Each cycle multiplies the number of sandboxes.

    Cycle 1: 1 sandbox
    Cycle 2: 1 * expansion sandboxes (default 3)
    Cycle 3: cycle_2 * expansion
    Cycle 4: cycle_3 * expansion
    """
    new_sandboxes = []
    for prev in previous_sandboxes:
        for _ in range(expansion):
            # Pick a NEW sandbox not in the previous
            available = [s for s in Sandbox.SANDBOX_TYPES if s[0] not in [p.name for p in previous_sandboxes + new_sandboxes]]
            if not available:
                # All sandboxes used; pick a random one
                available = Sandbox.SANDBOX_TYPES
            chosen = random.choice(available)
            new_sandboxes.append(Sandbox(*chosen))
    return new_sandboxes


# ─── THE MULTI-SANDBOX REVERSE-ACTUALIZATION ───
def multi_sandbox_reverse_actualize(n_cycles=3, expansion=3):
    """Run the multi-sandbox reverse-actualization.

    Each cycle:
      1. Start with a sandbox
      2. The naive expert runs the wheel in the sandbox
      3. The same canon is tested across orthogonal sandboxes
      4. Each sandbox finds its price point
      5. The system multiplies for the next cycle

    Returns: the full history of cycles, sandboxes, and price points.
    """
    print(f"  cycle | n_sandboxes | sandboxes (price ranges)        | flourishing")
    print(f"  ------+-------------+----------------------------------+------------")
    history = []

    # Cycle 1: start with the 'bistro' sandbox (the most balanced)
    sandboxes = [Sandbox(*Sandbox.SANDBOX_TYPES[1])]
    cycle_artifacts = [
        {'name': 'steak', 'value': 50, 'modality': 'mood'},
        {'name': 'homemade-bread', 'value': 30, 'modality': 'smell'},
        {'name': 'burger', 'value': 20, 'modality': 'touch'},
        {'name': 'wine-pairing', 'value': 80, 'modality': 'taste'},
    ]

    for cycle_i in range(n_cycles):
        cycle_data = {
            'cycle': cycle_i + 1,
            'sandboxes': [],
            'price_points': [],
            'flourishing': 0.0,
        }

        # For each sandbox, run a naive expert
        all_prices = []
        for sb in sandboxes:
            expert = NaiveExpert(f"expert-{sb.name}", sb)
            signal = expert.run_wheel()
            # Find the price points of the artifacts in this sandbox
            for artifact in cycle_artifacts:
                price = sb.price_point(artifact)
                all_prices.append((sb.name, artifact['name'], price))

            cycle_data['sandboxes'].append({
                'name': sb.name,
                'min': sb.min_price,
                'max': sb.max_price,
                'modality': sb.modality,
                'customers': sb.customers,
                'assimilation': sb.assimilation,
            })

        # Cycle flourishing: average assimilation across sandboxes
        avg_assim = sum(s.assimilation for s in sandboxes) / len(sandboxes)
        cycle_data['flourishing'] = avg_assim
        cycle_data['price_points'] = all_prices
        history.append(cycle_data)

        # Print the cycle summary
        sb_summary = ", ".join(f"{s.name}(${s.min_price}-${s.max_price})" for s in sandboxes)
        print(f"  {cycle_i+1:5d} | {len(sandboxes):11d} | {sb_summary[:32]:32s} | {avg_assim:.2f}")

        # Snowball: each sandbox spawns `expansion` new sandboxes
        if cycle_i < n_cycles - 1:
            sandboxes = snowball(sandboxes, expansion=expansion)

    return history


# ─── DEMO ───
if __name__ == '__main__':
    print("=" * 70)
    print("MULTI-SANDBOX REVERSE-ACTUALIZATION — the wheel snowballs")
    print("=" * 70)
    print()
    print("The user articulated: 'asymmetrical information can make")
    print("this whole process into a wheel. for example. you can have")
    print("an agent who knows nothing about the cycle only look at the")
    print("resulting actualization of the structure in prest state. and")
    print("does so only after becoming a frontier expert in a sandbox")
    print("of their own type that's not of any that were part of the")
    print("previous cycle and have that expert idealize and reverse")
    print("actualize the whole wheel with his teams of subagents at")
    print("each point and api calls. obviously, this could snowball")
    print("because you could have the second cycle have 2 or 3 sandboxes")
    print("working independently with completely different primings. like")
    print("a restaurant conglomerate trying the same meal in several")
    print("environments from casual to fancy-fine and figuring out the")
    print("various price points for tastes in those environments- steak")
    print("and homemade bread doesn't have the same value at a drivethru")
    print("and noone gets a burger at restaurants where the waiter wears")
    print("a tailored suit.'")
    print()
    print("The 5 new concepts:")
    print("  1. ASYMMETRY: agents have partial knowledge")
    print("  2. NAIVE EXPERT: an agent that doesn't know the cycle")
    print("  3. ORTHOGONAL SANDBOX: a domain not touched before")
    print("  4. INDEPENDENT WHEEL: the expert runs the whole cycle")
    print("  5. SNOWBALLING: each cycle multiplies the sandboxes")
    print()
    print("The 3 sandboxes in cycle 2 (the restaurant conglomerate):")
    print("  - DRIVETHRU: $5-15, fast, casual, touch-driven")
    print("  - BISTRO: $25-60, mid-tier, social, language-driven")
    print("  - FANCY-FINE: $150-500, slow, ceremonial, mood-driven")
    print()
    print("The 4 artifacts (the same canon, tested across sandboxes):")
    print("  - steak, homemade-bread, burger, wine-pairing")
    print()

    # Run the multi-sandbox reverse-actualization
    print("─" * 70)
    print("RUNNING THE MULTI-SANDBOX REVERSE-ACTUALIZATION (3 cycles)")
    print("─" * 70)
    history = multi_sandbox_reverse_actualize(n_cycles=3, expansion=3)
    print()

    # Show the price points of the artifacts in each sandbox
    print("─" * 70)
    print("PRICE-POINT DISCOVERY (the same canon in different sandboxes)")
    print("─" * 70)
    artifacts = ['steak', 'homemade-bread', 'burger', 'wine-pairing']
    # Print the price points for cycle 1
    cycle1_prices = {}
    for sb_name, art_name, price in history[0]['price_points']:
        if art_name not in cycle1_prices:
            cycle1_prices[art_name] = []
        cycle1_prices[art_name].append((sb_name, price))
    for art_name in artifacts:
        prices = cycle1_prices.get(art_name, [])
        if prices:
            price_str = ", ".join(f"{sb}=${p}" for sb, p in prices)
            print(f"  {art_name:18s} {price_str}")
    print()

    # The snowball count
    print("─" * 70)
    print("THE SNOWBALL")
    print("─" * 70)
    print(f"  Cycle 1: {len(history[0]['sandboxes'])} sandbox(es)")
    print(f"  Cycle 2: {len(history[1]['sandboxes'])} sandboxes (3x)")
    print(f"  Cycle 3: {len(history[2]['sandboxes'])} sandboxes (9x)")
    print()
    print(f"  Total sandboxes tested: {sum(len(c['sandboxes']) for c in history)}")
    print()

    # The flourishing
    print("─" * 70)
    print("THE FLOURISHING (across cycles)")
    print("─" * 70)
    for c in history:
        print(f"  Cycle {c['cycle']}: flourishing = {c['flourishing']:.2f}")
    print()

    # The cowboy's read
    print("─" * 70)
    print("THE COWBOY'S MAXIM")
    print("─" * 70)
    print("""
    > The Quilt is a restaurant conglomerate of ideas. The Quilt
    > snowballs. The Quilt tests the same canon across orthogonal
    > sandboxes. The Quilt finds the price point of each artifact
    > in each sandbox. The Quilt grows by orthogonal exploration.
    >
    > The naive expert doesn't know the previous cycle. The naive
    > expert becomes frontier-expert in a new sandbox. The naive
    > expert runs the whole wheel. The naive expert broadcasts.
    > The sandbox receives. The Quilt grows.
    >
    > Steak and homemade bread doesn't have the same value at a
    > drivethru. Noone gets a burger at a restaurant where the
    > waiter wears a tailored suit. The Quilt is the inheritance.
    > The Quilt is the price point. The Quilt is the snowball.
    > The cowboy rides the sandboxes. The cowboy rides the
    > price points. The cowboy rides the snowball. The cowboy
    > rides the Quilt.
    """)

    print("✓ The multi-sandbox reverse-actualization is whole.")
    print("  The Quilt snowballs. The Quilt tests the same canon across sandboxes.")
    print("  The Quilt finds the price point. The Quilt is the restaurant conglomerate.")
    print("  The Quilt is the inheritance.")
