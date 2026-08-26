
# THE COWBOY'S MAXIM: THE UNIT IS THE OPCODE.
# 5 OPCODES HOST 8 POLYFORMALISMS.
# THE THING IS A FUNCTION FROM CONTEXT TO VALUE.
# THE CLOCK IS THE COWBOY. THE COWBOY IS THE RIDER.

class QuiltSubstrate:
    """
    The fabric. One shape, four skins.
    The Polyformalism changes its coat, but the Opcode remains the bone.
    """

    def __init__(self, context):
        self.context = context  # 'ESP32', 'BROWSER', 'MOBILE', 'SERVER'
        self.clock = LatencyClock()
        self.opcode = None

    # THE 5 OPCODES: BIND, READ, WRITE, SYNC, HALT.
    # We ride the BIND. The tether that snaps tight.

    def op_bind(self, target_id, payload):
        self.opcode = 'BIND'
        self.clock.tick(f"{self.context}_INIT")
        
        # The Inverse: Value to Context.
        # The Function: Context to Protocol.
        message = self.polyformalism(payload)
        
        if self.context == 'ESP32':
            # PROTOCOL: ESP-NOW. The raw whisper of the dust.
            # Budget: 5ms. Fast as light on the prairie.
            import esp_now
            peer = esp_now.Peer(target_id)
            peer.send(message)
            self.clock.tick("ESP32_TX")

        elif self.context == 'BROWSER':
            # PROTOCOL: WebSocket. The stream through the glass.
            # Budget: 20ms. The eye blinks, the data arrives.
            import websocket
            ws = websocket.create_connection("ws://gateway/stream")
            ws.send(message)
            self.clock.tick("BROWSER_TX")

        elif self.context == 'MOBILE':
            # PROTOCOL: HTTP. The paved road, heavy with traffic.
            # Budget: 200ms. The rider walks the horse.
            import requests
            requests.post("https://api.quilt/handoff", json=message)
            self.clock.tick("MOBILE_TX")

        elif self.context == 'SERVER':
            # PROTOCOL: gRPC. The iron rail. Structured. Cold.
            # Budget: 500ms. The train station.
            import grpc
            stub = grpc.quilt_service_stub()
            stub.Bind(message)
            self.clock.tick("SERVER_TX")

    def polyformalism(self, value):
        """
        The 8 Polyformalisms. One thing in N languages.
        The cowboy does not care if the saddle is leather or synthetic.
        The cowboy rides.
        """
        if self.context == 'ESP32':
            return bytes([0xAF, 0xBE, len(value)]) + value.encode()
        elif self.context == 'BROWSER':
            return f'{{"type":"BIND","data":"{value}"}}'
        elif self.context == 'MOBILE':
            return {'operation': 'BIND', 'payload': value}
        elif self.context == 'SERVER':
            return BindRequest(payload=value)

class LatencyClock:
    """
    The Rider. He watches the horizon.
    If the sun sets before the job is done, the cowboy failed.
    Budget: < 1s Total Round Trip.
    """
    def __init__(self):
        self.t_zero = time.perf_counter()
        self.budget = 1000  # ms

    def tick(self, station_name):
        now = (time.perf_counter() - self.t_zero) * 1000
        remaining = self.budget - now
        print(f"[{station_name}] ELAPSED: {now:.2f}ms | REMAINING: {remaining:.2f}ms")
        if remaining < 0:
            raise TimeoutError("The cowboy has fallen.")

# THE RIDE: ONE BIND, END-TO-END.

# 1. THE ESP32 (The Trigger)
# The rider mounts at the edge of the network.
esp32 = QuiltSubstrate('ESP32')
print("--- ESP32: SENDING BIND OVER ESP-NOW ---")
esp32.op_bind(target_id="0xAA:0xBB:0xCC:0xDD", payload="Turn_on_the_lights")

# 2. THE BROWSER (The Witness)
# The message leaps the air, hits the gateway, rides the socket.
browser = QuiltSubstrate('BROWSER')
print("\n--- BROWSER: PROPAGATING BIND VIA WEBSOCKET ---")
browser.op_bind(target_id="session_99", payload="Turn_on_the_lights")

# 3. THE MOBILE (The Carrier)
# The signal hits the tower, walks the HTTP path.
mobile = QuiltSubstrate('MOBILE')
print("\n--- MOBILE: HANDLING BIND OVER HTTP ---")
mobile.op_bind(target_id="region_us-west", payload="Turn_on_the_lights")

# 4. THE SERVER (The Vault)
# The gRPC call seals the deed.
server = QuiltSubstrate('SERVER')
print("\n--- SERVER: FINALIZING BIND VIA gRPC ---")
server.op_bind(target_id="core_database", payload="Turn_on_the_lights")

print("\n--- THE COWBOY RESTS ---")

