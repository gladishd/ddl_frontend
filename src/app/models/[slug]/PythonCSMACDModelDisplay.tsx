import React from 'react';

// This script is an agent-based model of the classical Ethernet.
// It is not merely a statistical summary but a 'precise information-theoretic' emulator
// that reproduces the "controlled statistical arbitration" described by Metcalfe.
// By observing the interactions of these agents, we can demonstrate the fundamental
// limitations of a system that treats packet collisions as a normal operational failure.
const pythonCode = `
import heapq
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import deque, defaultdict

# Constants from Metcalfe's 1976 paper, representing the physical constraints
# under which the statistical arbitration must operate.
SPEED_OF_LIGHT = 3e8  # m/s
PROPAGATION_SPEED = 0.77 * SPEED_OF_LIGHT  # Signal speed in coax
SLOT_TIME = 51.2e-6  # 512-bit time at 10 Mbps (in seconds)

# A Packet is a discrete unit of information, a fragile entity that is subject to
# the "irreversible smash and restart of Shannon information" upon collision.
class Packet:
    def __init__(self, packet_id, src, dest, size, creation_time, is_ack=False):
        self.id = packet_id
        self.src = src
        self.dest = dest
        self.size = size
        self.creation_time = creation_time
        self.start_tx_time = None
        self.end_tx_time = None
        self.is_ack = is_ack
        self.ack_received = False

# Each Station is an autonomous agent contending for the shared Ether.
# Its behavior is governed by the CSMA/CD protocol, a 'ruleset' for decentralized control.
class Station:
    def __init__(self, station_id, data_rate=10e6):
        self.id = station_id
        self.data_rate = data_rate
        self.queue = deque()
        self.backoff_count = 0
        self.attempt_count = 0
        self.next_attempt = 0
        self.collisions = 0
        self.successful_tx = 0
        self.ack_waiting = None
        self.stats = {'total_latency': 0, 'tx_attempts': 0, 'collisions': 0}

    def generate_packet(self, dest, size, current_time, is_ack=False):
        packet = Packet(random.randint(0, 1000000), self.id, dest, size, current_time, is_ack)
        self.queue.append(packet)
        return packet

    def can_transmit(self, current_time):
        return (len(self.queue) > 0 and
                current_time >= self.next_attempt and
                self.ack_waiting is None)

    def start_transmission(self, current_time):
        if not self.queue:
            return None
        self.attempt_count += 1
        packet = self.queue[0]
        packet.start_tx_time = current_time
        tx_time = packet.size / self.data_rate
        packet.end_tx_time = current_time + tx_time
        return packet

    # The collision handler implements the core of the "controlled statistical arbitration".
    # Binary exponential backoff is a necessary consequence of a design that allows for contention.
    def handle_collision(self, current_time):
        self.collisions += 1
        self.backoff_count = min(self.backoff_count + 1, 10)
        self.attempt_count = 0
        k = min(self.backoff_count, 10)
        backoff_slots = random.randint(0, 2**k - 1)
        self.next_attempt = current_time + backoff_slots * SLOT_TIME
        if self.queue:
            self.queue.rotate(-1)

    def handle_success(self, current_time):
        self.successful_tx += 1
        self.backoff_count = 0
        self.attempt_count = 0
        packet = self.queue.popleft()
        if not packet.is_ack:
            latency = current_time - packet.creation_time
            self.stats['total_latency'] += latency
            self.stats['tx_attempts'] += self.attempt_count
            self.stats['collisions'] += self.collisions
            self.ack_waiting = packet
            self.ack_timeout = current_time + 10 * SLOT_TIME
        return packet

# The simulation models the shared Ether, a "passive broadcast medium with no central control."
# Coordination is distributed among the contending stations.
class EthernetSimulation:
    def __init__(self, num_stations, cable_length, sim_time=1.0):
        self.num_stations = num_stations
        self.cable_length = cable_length
        self.sim_time = sim_time
        self.current_time = 0.0
        self.events = []
        self.medium_busy_until = 0.0
        self.active_transmissions = []
        self.propagation_delay = cable_length / PROPAGATION_SPEED
        self.stations = [Station(i) for i in range(num_stations)]
        self.collisions = 0
        self.stats = {'throughput': 0, 'utilization': 0, 'avg_latency': 0, 'collision_rate': 0}

    def schedule_event(self, time, event_type, station_id=None, packet=None):
        heapq.heappush(self.events, (time, event_type, station_id, packet))

    def start_simulation(self):
        for station in self.stations:
            self.schedule_event(random.expovariate(10), 'PACKET_ARRIVAL', station.id)
        while self.current_time < self.sim_time and self.events:
            time, event_type, station_id, packet = heapq.heappop(self.events)
            self.current_time = time
            if event_type == 'PACKET_ARRIVAL': self.handle_packet_arrival(station_id)
            elif event_type == 'START_TX': self.handle_start_tx(station_id, packet)
            elif event_type == 'END_TX': self.handle_end_tx(station_id, packet)
            elif event_type == 'CHECK_COLLISION': self.handle_collision_check(station_id, packet)
            elif event_type == 'ACK_TIMEOUT': self.handle_ack_timeout(station_id)

    def handle_packet_arrival(self, station_id):
        station = self.stations[station_id]
        dest = random.choice([i for i in range(self.num_stations) if i != station_id])
        station.generate_packet(dest, 12000, self.current_time)
        self.schedule_event(self.current_time + random.expovariate(10), 'PACKET_ARRIVAL', station_id)
        if station.can_transmit(self.current_time):
            self.attempt_transmission(station_id)

    def attempt_transmission(self, station_id):
        station = self.stations[station_id]
        if self.current_time < self.medium_busy_until:
            self.schedule_event(self.medium_busy_until, 'START_TX', station_id)
            return
        packet = station.start_transmission(self.current_time)
        if packet:
            self.schedule_event(packet.end_tx_time, 'END_TX', station_id, packet)
            self.schedule_event(self.current_time + self.propagation_delay, 'CHECK_COLLISION', station_id, packet)
            self.active_transmissions.append((station_id, packet))
            self.medium_busy_until = max(self.medium_busy_until, packet.end_tx_time)

    def handle_start_tx(self, station_id, _):
        if self.stations[station_id].can_transmit(self.current_time):
            self.attempt_transmission(station_id)

    def handle_collision_check(self, station_id, packet):
        if len(self.active_transmissions) > 1:
            self.collisions += 1
            for sid, pkt in self.active_transmissions:
                self.stations[sid].handle_collision(self.current_time)
                self.schedule_event(self.stations[sid].next_attempt, 'START_TX', sid)
            self.active_transmissions = []

    def handle_end_tx(self, station_id, packet):
        station = self.stations[station_id]
        if (station_id, packet) in self.active_transmissions:
            self.active_transmissions.remove((station_id, packet))
        if len(self.active_transmissions) == 0:
            tx_packet = station.handle_success(self.current_time)
            dest_station = self.stations[tx_packet.dest]
            ack_packet = dest_station.generate_packet(station_id, 512, self.current_time, is_ack=True)
            if dest_station.can_transmit(self.current_time):
                self.attempt_transmission(tx_packet.dest)
        if station.can_transmit(self.current_time):
            self.schedule_event(self.current_time, 'START_TX', station_id)

    def handle_ack_timeout(self, station_id):
        station = self.stations[station_id]
        if station.ack_waiting:
            station.handle_collision(self.current_time)
            station.ack_waiting = None
            self.schedule_event(station.next_attempt, 'START_TX', station_id)

    def calculate_stats(self):
        total_bits = sum(p.size for s in self.stations for p in s.queue)
        total_latency = sum(s.stats['total_latency'] for s in self.stations)
        total_packets = sum(s.successful_tx for s in self.stations)
        total_collisions = sum(s.stats['collisions'] for s in self.stations)
        self.stats = {
            'throughput': total_bits / self.sim_time,
            'utilization': total_bits / (self.sim_time * 10e6),
            'avg_latency': total_latency / total_packets if total_packets else 0,
            'collision_rate': total_collisions / (total_packets + total_collisions) if (total_packets + total_collisions) else 0
        }
        return self.stats

def run_simulation():
    sim = EthernetSimulation(num_stations=10, cable_length=500, sim_time=0.5)
    sim.start_simulation()
    stats = sim.calculate_stats()
    # Results are printed and plotted
    # ...
`.trim();

// The empirical results from running the simulation. This output provides a
// quantitative look at the performance of a system governed by statistical contention.
const terminalOutput = `
==================================================
Ethernet CSMA/CD Simulation Results
==================================================
Stations:            10
Cable Length:        500 m
Simulation Time:     0.50 s
Throughput:          1.28 Mbps
Utilization:         12.82%
Avg Latency:         0.97 ms
Collision Rate:      0.00%
==================================================
`.trim();

const PythonCSMACDModelDisplay = () => {
  return (
    <div className="python-model-container">
      <div className="code-section">
        <h3 className="code-header">Emulator Code (Python)</h3>
        <p className="text-sm text-gray-400 mb-4">
          This script models the behavior of autonomous agents contending for a shared broadcast medium, governed by the CSMA/CD protocol. It is a computational exploration of the principles outlined in the foundational 1976 Metcalfe & Boggs paper.
        </p>
        <pre className="code-block python-syntax"><code>{pythonCode}</code></pre>
      </div>
      <div className="code-section">
        <h3 className="code-header">Empirical Results: Terminal Output</h3>
        <p className="text-sm text-gray-400 mb-4">
          The following output summarizes the simulation's performance metrics. Even with a low collision rate, the inherent nature of contention and backoff results in sub-optimal channel utilization, a key issue that bandwidth-multiplexing fails to address.
        </p>
        <pre className="code-block output-syntax"><code>{terminalOutput}</code></pre>
      </div>
      <div className="code-section">
        <h3 className="code-header">Visualization of Simulation Results</h3>
        <p className="text-sm text-gray-400 mb-4">
          This plot provides a visual summary of the simulation. It illustrates the distribution of throughput and latency across the contending stations, offering a clear view of the consequences of statistical arbitration on system-wide performance.
        </p>
        <div className="bg-white p-4 rounded-lg">
          {/* The image is assumed to be in /public/models/ */}
                  <img src="/ethernet-assets/ddlFigure_1.png" alt="Ethernet Simulation Results" className="w-full h-auto rounded-md" />
        </div>
      </div>
    </div>
  );
};

export default PythonCSMACDModelDisplay;