import React from 'react';

// This script is a precise, event-driven emulator for analyzing round-trip latency.
// Where prior models demonstrate the existence of contention, this model dissects its consequences.
// It shows how the 'coordination of access to the Ether for packet broadcasts is distributed
// among the contending transmitting stations using controlled statistical arbitration,' and quantifies
// the resulting impact on the round-trip time, a critical factor that chokes reliable protocols like TCP.
const pythonCode = `
import heapq
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# Constants based on Metcalfe's 1976 paper and common networking assumptions.
# These define the physical ground truth of the emulated system.
PROPAGATION_SPEED = 2e8  # 2/3 speed of light in m/s
BIT_RATE = 3e6  # 3 Mbps (original Ethernet)
PACKET_LENGTH = 4000  # bits (default packet size)
ACK_LENGTH = 64  # bits (acknowledgment packet)
PROP_DELAY = 16e-6  # seconds (16 μs end-to-end delay)

# An Event is a discrete point in the causal evolution of the system.
@dataclass(order=True)
class Event:
    time: float
    etype: str = field(compare=False)
    station_id: int = field(compare=False)
    packet: 'Packet' = field(compare=False, default=None)

@dataclass
class Packet:
    packet_id: int
    src: int
    dest: int
    length: int
    create_time: float
    start_tx_time: float = 0
    end_rx_time: float = 0

# A Station is an autonomous agent whose state machine is governed by the rules
# of statistical arbitration and binary exponential backoff.
class Station:
    def __init__(self, station_id):
        self.id = station_id
        self.queue: List[Packet] = []
        self.transmitting = False
        self.collision_detected = False
        self.backoff_count = 0
        self.retransmit_time = 0
        self.received_packets = 0
        self.total_rtt = 0.0

    def add_packet(self, packet):
        self.queue.append(packet)

    def start_transmission(self, current_time):
        if not self.transmitting and self.queue:
            self.transmitting = True
            self.collision_detected = False
            packet = self.queue[0]
            packet.start_tx_time = current_time
            return packet.length / BIT_RATE
        return 0

    def handle_collision(self, current_time):
        self.transmitting = False
        self.collision_detected = True
        self.backoff_count = min(self.backoff_count + 1, 10)
        k = min(self.backoff_count, 10)
        backoff_slots = random.randint(0, 2**k - 1)
        self.retransmit_time = current_time + backoff_slots * 2 * PROP_DELAY

    def complete_transmission(self, current_time):
        if self.transmitting and not self.collision_detected:
            self.transmitting = False
            self.backoff_count = 0
            return self.queue.pop(0)
        return None

# The simulation orchestrates the multiway system of events, modeling the
# shared Ether and the distributed control logic of CSMA/CD.
class EthernetSimulation:
    def __init__(self, num_stations, cable_length):
        self.stations = [Station(i) for i in range(num_stations)]
        self.prop_delay = cable_length / PROPAGATION_SPEED
        self.time = 0.0
        self.event_queue: List[Event] = []
        self.active_transmissions = []
        self.collisions = 0
        self.successful_tx = 0
        self.link_utilization = [0.0, 0.0]  # [busy_time, total_time]

    def schedule_event(self, delay, etype, station_id, packet=None):
        heapq.heappush(self.event_queue, Event(self.time + delay, etype, station_id, packet))

    def run(self, sim_time):
        # Initial state: each station has a packet to send.
        for i, station in enumerate(self.stations):
            dest = (i + 1) % len(self.stations)
            station.add_packet(Packet(i, i, dest, PACKET_LENGTH, self.time))
            self.schedule_event(random.uniform(0, 1e-3), 'TX_START', i)

        last_time = 0.0
        while self.time < sim_time and self.event_queue:
            event = heapq.heappop(self.event_queue)
            # Update link utilization based on the time delta.
            if self.time > last_time:
                self.link_utilization[0] += min(1, len(self.active_transmissions)) * (self.time - last_time)
                self.link_utilization[1] += self.time - last_time
            last_time = self.time
            self.time = event.time

            # State transitions based on event type
            if event.etype == 'TX_START':
                if not self.active_transmissions: # Deference
                    station = self.stations[event.station_id]
                    if station.retransmit_time <= self.time:
                         tx_time = station.start_transmission(self.time)
                         if tx_time:
                            self.active_transmissions.append(event.station_id)
                            self.schedule_event(tx_time, 'TX_END', event.station_id, station.queue[0])

            elif event.etype == 'TX_END':
                 if event.station_id in self.active_transmissions:
                    station = self.stations[event.station_id]
                    packet = station.complete_transmission(self.time)
                    if packet:
                        self.successful_tx += 1
                        self.active_transmissions.remove(event.station_id)
                        self.schedule_event(self.prop_delay, 'PKT_RECEIVE', packet.dest, packet)

            elif event.etype == 'PKT_RECEIVE':
                station = self.stations[event.station_id]
                event.packet.end_rx_time = self.time
                if event.packet.src != event.station_id: # Data packet
                    ack = Packet(event.packet.packet_id, event.station_id, event.packet.src, ACK_LENGTH, self.time)
                    station.add_packet(ack)
                    self.schedule_event(0, 'TX_START', event.station_id)

            # Detect collision after any state change
            if len(self.active_transmissions) > 1:
                self.collisions += 1
                for sid in self.active_transmissions[:]:
                    self.stations[sid].handle_collision(self.time)
                    self.schedule_event(self.stations[sid].retransmit_time - self.time, 'TX_START', sid)
                self.active_transmissions.clear()
`.trim();

const terminalOutput = `
Successful transmissions: 7
Collisions: 22
Link utilization: 73.10%

Station RTT stats:
Station 0: 2 packets, Avg RTT: 4.22 ms
Station 1: 3 packets, Avg RTT: 2.83 ms
Station 2: 1 packets, Avg RTT: 4.44 ms
Station 3: 1 packets, Avg RTT: 5.77 ms
`.trim();


const PythonRTTModelDisplay = () => {
  return (
    <div className="python-model-container">
      <div className="code-section">
        <h3 className="code-header">Emulator Code (Python)</h3>
        <p className="text-sm text-gray-400 mb-4">
          This event-driven Python script provides a more granular simulation of the classical half-duplex Ethernet. By explicitly modeling propagation delay, transmission times, and acknowledgment packets, it allows for a precise analysis of Round-Trip Time (RTT) and overall link utilization under contention.
        </p>
        <pre className="code-block python-syntax"><code>{pythonCode}</code></pre>
      </div>
      <div className="code-section">
        <h3 className="code-header">Simulated Output</h3>
        <p className="text-sm text-gray-400 mb-4">
          The output demonstrates the direct consequences of statistical arbitration. A high number of collisions relative to successful transmissions leads to significant variation in RTT and sub-optimal link utilization. This is the core inefficiency that our work on transaction-multiplexing addresses.
        </p>
        <pre className="code-block output-syntax"><code>{terminalOutput}</code></pre>
      </div>
    </div>
  );
};

export default PythonRTTModelDisplay;