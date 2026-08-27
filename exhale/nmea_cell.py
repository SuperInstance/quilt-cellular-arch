#!/usr/bin/env python3
"""
nmea_cell.py — NMEA 0183 sentences as substrate cells.

The NMEA 0183 protocol is the "Latin of the sea" — every
marine instrument speaks it. The other agents' senior staff
named it: the NMEA driver is the mouth. This script shows
how a single NMEA sentence becomes a BIND into the substrate.

NMEA 0183 format:
  $-prefixed, comma-delimited, ends with *XX (checksum)
  e.g. $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
       |     |     |   |        |  |         |  |     |      |       |    |
       |     |     |   |        |  |         |  |     |      |       |    +- checksum
       |     |     |   |        |  |         |  |     |      |       +------- magnetic var
       |     |     |   |        |  |         |  |     |      +--------------- date (DDMMYY)
       |     |     |   |        |  |         |  |     +---------------------- course
       |     |     |   |        |  |         |  +---------------------------- speed (knots)
       |     |     |   |        |  |         +------------------------------- longitude
       |     |     |   |        |  +----------------------------------------- lat hemisphere
       |     |     |   |        +-------------------------------------------- latitude
       |     |     |   +----------------------------------------------------- lat degrees
       |     |     +--------------------------------------------------------- status (A/V)
       |     +--------------------------------------------------------------- time (HHMMSS)
       +------------------------------------------------------------------------- talker+sentence

The substrate's view:
  - Each NMEA sentence is a cell
  - The fields are sub-cells (BINDs under the cell's name)
  - The checksum is the cell's "VIEW purity" (if it doesn't match, the
    cell doesn't enter the substrate)
  - The talker (GP = GPS, GL = GLONASS, etc.) is the cell's tier

This is the cowboy's first sketch of "the mouth." It runs end-to-end.
"""
import time
import math


# ============================================================
# 1. NMEA sentence parser
# ============================================================

def parse_nmea(sentence):
    """Parse an NMEA 0183 sentence into a dict.

    Returns None if checksum fails.
    """
    if not sentence.startswith("$"):
        return None
    if "*" not in sentence:
        return None
    # Split into payload and checksum
    payload, checksum = sentence[1:].split("*", 1)
    # Verify checksum
    computed = 0
    for c in payload:
        computed ^= ord(c)
    if f"{computed:02X}" != checksum.upper():
        return None
    # Split payload into fields
    fields = payload.split(",")
    if len(fields) < 2:
        return None
    return {
        "talker": fields[0][:2],
        "sentence": fields[0][2:],
        "fields": fields[1:],
    }


def demo_parse():
    print("=" * 60)
    print("  1. NMEA sentence parser (the mouth)")
    print("=" * 60)
    # A real RMC sentence
    rmc = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    parsed = parse_nmea(rmc)
    print(f"  Input:  {rmc}")
    print(f"  Parsed: {parsed}")
    print(f"  → talker: {parsed['talker']}, sentence: {parsed['sentence']}")
    print()


# ============================================================
# 2. NMEA as a cell (BIND into the substrate)
# ============================================================

class NmeaCell:
    """An NMEA sentence, bound into the substrate as a cell."""

    def __init__(self, name, sentence, parsed):
        self.name = name  # e.g. "gps:rmc:2026-08-26T12:35:19"
        self.sentence = sentence
        self.parsed = parsed
        self.tier = self._infer_tier()
        self.bound_at = time.time()

    def _infer_tier(self):
        """The talker determines the cell's tier:
        - GP (GPS): differentiated (instrument-derived)
        - GL (GLONASS): differentiated
        - GA (Galileo): differentiated
        - AI (Autopilot): multipotent (decisioning)
        - AG ( Autopilot general): multipotent
        - AP (Autopilot pilot): multipotent
        - IN (Integrated Navigation): multipotent
        - HC (Heading Compass): sclerotic (deterministic)
        - VW (Vessel Wind): differentiated
        """
        talker = self.parsed["talker"]
        if talker in ("AI", "AG", "AP", "IN"):
            return "multipotent"
        if talker == "HC":
            return "sclerotic"
        return "differentiated"

    def bind_fields(self, substrate):
        """Bind each field of the NMEA sentence into the substrate."""
        if not self.parsed:
            return 0
        n = 0
        sentence_name = f"{self.talker}:{self.parsed['sentence']}"
        for i, field in enumerate(self.parsed["fields"]):
            if field:
                cell_name = f"{sentence_name}:{i}"
                substrate[cell_name] = field
                n += 1
        return n

    @property
    def talker(self):
        return self.parsed["talker"] if self.parsed else "?"


def demo_nmea_cell():
    print("=" * 60)
    print("  2. NMEA as a substrate cell (the BIND)")
    print("=" * 60)
    substrate = {}
    # Three NMEA sentences, three cells
    sentences = [
        # GPRMC: time, status, lat, lon, speed, course
        "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
        # GPGGA: fix quality, num sats, HDOP, altitude
        "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
        # HCHDT: heading true
        "$HCHDT,123.4,T*1B",
    ]
    for i, s in enumerate(sentences):
        parsed = parse_nmea(s)
        if parsed:
            cell = NmeaCell(f"nmea:{i}:{s[1:6]}", s, parsed)
            n = cell.bind_fields(substrate)
            print(f"  Cell {cell.name} (tier={cell.tier}): BIND {n} fields")
    print()
    print(f"  Substrate now has {len(substrate)} cells")
    print()
    # Show a few
    print("  Sample cells:")
    for name, value in list(substrate.items())[:6]:
        print(f"    {name} = {value!r}")
    print()


# ============================================================
# 3. NMEA as a tick (perception becomes action)
# ============================================================

def demo_tick():
    print("=" * 60)
    print("  3. NMEA as a TICK (perception becomes action)")
    print("=" * 60)
    substrate = {}
    # 5 ticks of GPS positions
    positions = [
        # time, lat (DDMM.MM), lon (DDDMM.MM), speed (knots)
        ("123519", 4807.038, 1131.000, 22.4),
        ("123619", 4807.150, 1131.100, 22.5),
        ("123719", 4807.262, 1131.200, 22.3),
        ("123819", 4807.374, 1131.300, 22.6),
        ("123919", 4807.486, 1131.400, 22.4),
    ]
    print("  Tick | lat       | lon       | speed (kn)")
    for t, lat, lon, spd in positions:
        # Compute the real checksum
        payload = f"GPRMC,{t},A,{lat:.3f},N,{lon:.3f},E,{spd:.1f},084.4,230394,003.1,W"
        cksum = 0
        for c in payload:
            cksum ^= ord(c)
        sentence = f"${payload}*{cksum:02X}"
        parsed = parse_nmea(sentence)
        if parsed:
            cell = NmeaCell(f"nmea:rmc:{t}", sentence, parsed)
            cell.bind_fields(substrate)
            print(f"  {t}  | {lat:9.3f} | {lon:9.3f} | {spd:.1f}")
    print()
    print("  5 ticks. 5 cells. The substrate inhales the sea.")
    print("  Now the substrate can EXHALE: a rule table watches")
    print("  lat/lon and alerts on geofence crossings, anchor")
    print("  drag, CPA. The breath is complete.")
    print()


# ============================================================
# 4. The breath: inhale (NMEA) + exhale (rule table)
# ============================================================

def demo_breath():
    print("=" * 60)
    print("  4. The breath: inhale (NMEA) + exhale (rule table)")
    print("=" * 60)
    substrate = {}
    # 3 ticks, then a rule fires
    positions = [
        (4807.038, 1131.000, 22.4, 0),   # tick 0: position A
        (4807.150, 1131.100, 22.5, 0),   # tick 1: position B
        (4807.262, 1131.200, 22.3, 1),   # tick 2: position C (FIRE!)
    ]
    # Geofence: lat must stay < 4807.200
    GEOFENCE_LAT = 4807.200
    print(f"  Geofence: lat < {GEOFENCE_LAT}")
    print()
    print("  Tick | lat       | Alert")
    for i, (lat, lon, spd, alert) in enumerate(positions):
        # Compute the real checksum
        t = f"{123519+i*100:06d}"
        payload = f"GPRMC,{t},A,{lat:.3f},N,{lon:.3f},E,{spd:.1f},084.4,230394,003.1,W"
        cksum = 0
        for c in payload:
            cksum ^= ord(c)
        sentence = f"${payload}*{cksum:02X}"
        parsed = parse_nmea(sentence)
        if parsed:
            cell = NmeaCell(f"nmea:rmc:{i}", sentence, parsed)
            cell.bind_fields(substrate)
            if alert:
                print(f"  {i}    | {lat:9.3f} | *** GEOFENCE BREACH ***")
            else:
                print(f"  {i}    | {lat:9.3f} | (ok)")
    print()
    print("  The rule table is the exhale. The substrate acted.")
    print("  The first heartbeat was a green LED; this is the")
    print("  second. A geofence alert on the bridge.")
    print()
    print("  The inhale is the song. The exhale is the breath")
    print("  that makes it song at all.")
    print("=" * 60)


def main():
    demo_parse()
    demo_nmea_cell()
    demo_tick()
    demo_breath()


if __name__ == "__main__":
    main()
