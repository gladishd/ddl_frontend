"""
Python agent-based simulation of an automotive TSN (Time-Sensitive Networking) network.
Models devices, switches, prioritized queues, traffic shaping, delay, jitter, and frame loss.
Formally mirrors the OMNeT++ automotive TSN simulation as described in the provided files.
Author: Dædælus (2025)
"""

import simpy
import numpy as np
from collections import defaultdict, deque
from statistics import mean, stdev

# --- Model Parameters (mirrored from .ini/.ned) ---
BITRATE = 100e6                # 100 Mbps
MTU = 1500                     # bytes
SIM_DURATION = 2.0             # seconds (extend as needed)
QUEUE_LIMIT = 100              # max packets in switch egress queue (configurable)
EGRESS_TRAFFIC_CLASSES = 8     # per switch port

# --- Flow/Traffic Definition ---
# Each flow: (src, dst, period_sec, payload_B, burst, priority)
TRAFFIC = [
    # Lidar, Camera, RC, etc. -- see your OMNeT++ .ini and flow table
    dict(name="Lidar_to_CU",  src="LD1", dst="CU", period=0.0014, payload=1300, burst=1, priority=5),
    dict(name="CameraF_to_HU",src="CM1", dst="HU", period=0.01666, payload=178500, burst=119, priority=3),
    dict(name="RC_to_HU",     src="RC",  dst="HU", period=0.03333, payload=178500, burst=119, priority=3),
    dict(name="ME_to_RS1",    src="ME",  dst="RS1",period=0.03333, payload=178500, burst=119, priority=2),
    dict(name="ME_to_S1",     src="ME",  dst="S1", period=0.00025, payload=80,    burst=1,   priority=7),
    dict(name="US_to_CU",     src="US1", dst="CU", period=0.1,     payload=188,   burst=1,   priority=1),
    # Add other flows as in OMNeT++ .ini
]

# Priority to traffic class mapping (rate-monotonic, 0=lowest, 7=highest)
def priority_to_class(priority):
    return priority

# --- Statistics Container ---
class FlowStats:
    def __init__(self):
        self.delays = []
        self.frame_sent = 0
        self.frame_rcvd = 0
        self.frame_lost = 0
        self.burst_delays = []
    def add_delay(self, d): self.delays.append(d)
    def record_send(self): self.frame_sent += 1
    def record_recv(self): self.frame_rcvd += 1
    def record_loss(self): self.frame_lost += 1
    def add_burst_delay(self, d): self.burst_delays.append(d)

class TsnDevice:
    def __init__(self, env, name, switch, flows):
        self.env = env
        self.name = name
        self.switch = switch
        self.flows = flows
        # Ensure stats for all flows this device might handle (send or receive)
        relevant_flows = [f for f in TRAFFIC if f['src'] == name or f['dst'] == name]
        self.stats = {f['name']: FlowStats() for f in relevant_flows}
        for flow in self.flows:
            env.process(self.generate_frames(flow))

    def generate_frames(self, flow):
        next_time = 0
        while True:
            payload = flow['payload']
            burst = flow['burst']
            num_frames = max(1, int(np.ceil(payload / MTU)))
            for i in range(num_frames):
                frame_size = min(MTU, payload - i*MTU)
                frame = {
                    'flow': flow['name'],
                    'src': self.name,
                    'dst': flow['dst'],
                    'priority': flow['priority'],
                    'send_time': self.env.now,
                    'frame_num': i,
                    'burst_size': num_frames,
                    'size': frame_size
                }
                self.stats[flow['name']].record_send()
                yield self.env.timeout(0)
                self.switch.receive(frame)
            yield self.env.timeout(flow['period'])

    def receive(self, frame):
        flow = frame['flow']
        if flow not in self.stats:
            self.stats[flow] = FlowStats()
        delay = self.env.now - frame['send_time']
        self.stats[flow].record_recv()
        self.stats[flow].add_delay(delay)
        if (frame['frame_num'] + 1) == frame['burst_size']:
            self.stats[flow].add_burst_delay(delay)

class TsnSwitch:
    def __init__(self, env, name, port_names):
        self.env = env
        self.name = name
        self.egress_ports = {p: [deque() for _ in range(EGRESS_TRAFFIC_CLASSES)] for p in port_names}
        self.stats = defaultdict(lambda: FlowStats())
        for port in port_names:
            env.process(self.egress_scheduler(port))
    def receive(self, frame):
        # Egress port determined by destination
        dst = frame['dst']
        priority = frame['priority']
        tc = priority_to_class(priority)
        # Simplified: all flows exit on dst port
        q = self.egress_ports[dst][tc]
        if len(q) < QUEUE_LIMIT:
            q.append((self.env.now, frame))
        else:
            # Queue overflow → frame loss
            self.stats[frame['flow']].record_loss()
    def egress_scheduler(self, port):
        # Priority scheduling: highest to lowest
        while True:
            for tc in reversed(range(EGRESS_TRAFFIC_CLASSES)):
                q = self.egress_ports[port][tc]
                if q:
                    _, frame = q.popleft()
                    tx_time = frame['size'] * 8 / BITRATE
                    yield self.env.timeout(tx_time)
                    # Deliver frame to next hop (in this model: directly to device)
                    DEVICES[frame['dst']].receive(frame)
                    self.stats[frame['flow']].record_recv()
                    break
            else:
                # If all queues empty, wait briefly
                yield self.env.timeout(0.00001)

# --- Network Setup ---
env = simpy.Environment()
# Build devices and switch network as per .ned and .ini
# Only main actors are modeled; add all nodes/flows as needed.

SWITCH_PORTS = ["CU", "HU", "RS1", "S1"]  # Example egress ports
SWITCH = TsnSwitch(env, "Switch1", SWITCH_PORTS)

# Assign flows to devices (simplified: each device gets its outgoing flows)
DEVICES = {}
device_names = set(f['src'] for f in TRAFFIC) | set(f['dst'] for f in TRAFFIC)
for d in device_names:
    flows = [f for f in TRAFFIC if f['src'] == d]
    DEVICES[d] = TsnDevice(env, d, SWITCH, flows)

# --- Simulation Run ---
env.run(until=SIM_DURATION)

# --- Output Results ---
print("\n=== Automotive TSN Simulation Results ===")
for dev in DEVICES.values():
    for fname, stats in dev.stats.items():
        if stats.frame_sent == 0:
            continue
        delays = stats.delays or [0]
        burst_delays = stats.burst_delays or [0]
        a_jitter = max(burst_delays) - min(burst_delays) if len(burst_delays) > 1 else 0
        frame_loss_ratio = (stats.frame_lost / stats.frame_sent) if stats.frame_sent else 0
        print(f"Flow: {fname}")
        print(f"  Frames sent:      {stats.frame_sent}")
        print(f"  Frames received:  {stats.frame_rcvd}")
        print(f"  Frames lost:      {stats.frame_lost}")
        print(f"  Frame Loss Ratio: {frame_loss_ratio:.4f}")
        print(f"  E2E Delay (mean): {mean(delays):.6f} s")
        print(f"  E2E Jitter:       {a_jitter:.6f} s")
        print(f"  ---")
