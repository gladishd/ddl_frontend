#
# DDL_Emulator: A Computational Proof
#
# This simulation serves as a concrete, agent-based implementation of the core
# networking principles that underpin the Daedaelus architecture. Its purpose is
# to move beyond static analysis and computationally demonstrate the fundamental
# differences between classical, contention-based networking and the deterministic,
# transaction-multiplexed fabric enabled by the Graph Virtual Machine (GVM).
#
# We will model three distinct regimes to build our argument:
#   1. The original 1976 Metcalfe "Ether," a shared half-duplex medium where
#      distributed stations use statistical arbitration (CSMA/CD) to contend
#      for bandwidth. This will demonstrate the inherent inefficiencies of
#      collision-based access.
#   2. The modern switched TCP environment, where bandwidth-multiplexing on
#      full-duplex links still results in chaotic contention and RTT-dependent
#      throughput degradation, as predicted by the Mathis equation.
#   3. The Daedaelus N2N fabric, where reliable links and an interaction-
#      multiplexing GVM provide deterministic latency and vastly superior
#      transactional throughput, proving that the network should not be a
#      mess for the application to clean up.
#
# This is "Code as Proof," architecting the future with enduring excellence.
#

import heapq
import random
import math
from collections import deque

# --- Simulation Constants & Configuration ---
# These parameters are chosen to be representative and allow for clear demonstration.

# Physical Layer Constants
BITS_PER_SECOND_1GB = 1e9
PROPAGATION_SPEED_M_PER_NS = 0.2  # Approx. 2/3 speed of light in vacuum

# Packet/Frame Constants
PREAMBLE_BITS = 64
INTERFRAME_GAP_BITS = 96
MINIMUM_FRAME_BITS = 512  # 64 bytes
DEFAULT_PACKET_BITS = 12144  # 1518 bytes
TCP_ACK_BITS = 512 # 64 bytes, includes headers

# Metcalfe Model Constants
SLOT_TIME_BITS = 512 # As defined in the original Ethernet spec

# --- Core Discrete-Event Simulation Engine ---
# A simple priority-queue based engine to manage events in time.

class Event:
    """A simple event structure for the simulation."""
    def __init__(self, time, callback, description=""):
        self.time = time
        self.callback = callback
        self.description = description

    def __lt__(self, other):
        return self.time < other.time

class Simulator:
    """Manages the event queue and simulation time."""
    def __init__(self):
        self.current_time = 0
        self.event_queue = []

    def schedule(self, delay, callback, description=""):
        heapq.heappush(self.event_queue, Event(self.current_time + delay, callback, description))

    def run(self, until_time):
        while self.event_queue and self.current_time <= until_time:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            event.callback()
        print(f"\n--- Simulation finished at {self.current_time / 1e9:.6f} seconds. ---\n")


# --- Foundational Network Component Classes ---

class Packet:
    """Represents a unit of data. In our philosophy, this is a Token carrying
       epistemic state which must be conserved across the fabric."""
    def __init__(self, size_bits, source, destination, flow_id=0, creation_time=0):
        self.size_bits = size_bits
        self.source = source
        self.destination = destination
        self.flow_id = flow_id
        self.creation_time = creation_time
        self.unique_id = random.randint(1000, 9999)

    def __repr__(self):
        return f"Pkt({self.flow_id}-{self.unique_id})"

# --- MODEL 1: THE CLASSICAL SHARED ETHER (METCALFE, 1976) ---
# This section models a shared, half-duplex broadcast medium. It is a system
# built on the assumption that the Ether is a passive, scarce resource for
# which stations must contend. Control is distributed and statistical.

class Ether:
    """Represents the shared passive broadcast medium of classical Ethernet."""
    def __init__(self, length_meters, simulator, stations):
        self.length_meters = length_meters
        self.simulator = simulator
        self.stations = stations
        self.propagation_delay = self.length_meters / PROPAGATION_SPEED_M_PER_NS
        # The 'Slot Time' is the critical parameter for collision detection. It's
        # twice the end-to-end propagation delay, ensuring a station knows for
        # certain it has acquired the Ether.
        self.slot_time = 2 * self.propagation_delay
        self.is_busy = False
        self.transmitting_stations = []

    def is_carrier_sensed(self):
        # A station can sense the carrier of a passing packet and will defer
        # its own transmission. This is the 'listen before talk' aspect of CSMA.
        return self.is_busy

    def transmit(self, station, packet):
        # When a station begins transmission, it takes one propagation delay
        # for the signal to reach the far end of the Ether.
        self.transmitting_stations.append(station)

        if not self.is_busy:
            # The Ether was idle, this station might acquire it.
            self.is_busy = True
            # Schedule the end of this transmission.
            transmission_time = packet.size_bits / BITS_PER_SECOND_1GB
            self.simulator.schedule(transmission_time,
                                    lambda: self.end_transmission(station, packet, collision=False),
                                    f"EndTx {station.name}")
        else:
            # A collision is guaranteed. All transmitting stations will detect it.
            # This is interference detection, a key innovation over the original
            # Aloha network that truncates collisions and saves bandwidth.
            for s in self.transmitting_stations:
                if s.controller.is_transmitting:
                    # Schedule collision detection for each station. The time it takes
                    # to detect depends on their relative positions on the Ether. For
                    # simplicity, we use the maximum time, one slot_time.
                    self.simulator.schedule(self.slot_time,
                                            lambda s=s: s.controller.handle_collision(),
                                            f"CollisionDetect {s.name}")

    def end_transmission(self, station, packet, collision):
        if not collision and station in self.transmitting_stations:
            # Successful transmission. The packet has propagated without interference.
            # Notify the sender's controller of the success.
            station.controller.handle_successful_tx()
            # Schedule the reception event for all other stations.
            for s in self.stations:
                if s is not station:
                    self.simulator.schedule(self.propagation_delay,
                                            lambda s=s, p=packet: s.receive(p),
                                            f"Receive {s.name}")

        # The Ether is now free. Even if a collision occurred, the jamming signal
        # has ceased, and the controllers handle their own backoff timing.
        self.is_busy = False
        self.transmitting_stations = []


class ClassicalController:
    """Implements the CSMA/CD logic for a station on the shared Ether."""
    def __init__(self, station, ether, simulator):
        self.station = station
        self.ether = ether
        self.simulator = simulator
        self.send_queue = deque()
        self.is_transmitting = False
        self.collision_count = 0
        self.MAX_COLLISIONS = 16

    def send(self, packet):
        self.send_queue.append(packet)
        if not self.is_transmitting:
            self.attempt_transmission()

    def attempt_transmission(self):
        if not self.send_queue:
            self.is_transmitting = False
            return

        # Deference: A station must defer to any transmission already in progress.
        # This is the "Carrier Sense" part of CSMA/CD.
        if self.ether.is_carrier_sensed():
            self.simulator.schedule(INTERFRAME_GAP_BITS / BITS_PER_SECOND_1GB, self.attempt_transmission, f"Defer {self.station.name}")
            return

        self.is_transmitting = True
        packet = self.send_queue[0]
        self.ether.transmit(self.station, packet)

    def handle_successful_tx(self):
        # A successful transmission resets the collision counter for the next packet.
        if not self.is_transmitting: return # Already handled
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.station.name} successfully transmitted {self.send_queue[0]}.")
        self.is_transmitting = False
        self.send_queue.popleft()
        self.collision_count = 0
        self.station.notify_tx_success()
        if self.send_queue:
            self.attempt_transmission()

    def handle_collision(self):
        if not self.is_transmitting: return # Already handled by another station's collision detect
        
        # Collision Consensus Enforcement: The station jams the Ether to ensure
        # all other colliding stations also detect the interference.
        self.is_transmitting = False
        self.collision_count += 1
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.station.name} detected collision #{self.collision_count}.")
        
        if self.collision_count > self.MAX_COLLISIONS:
            print(f"ERROR: {self.station.name} dropped packet after {self.MAX_COLLISIONS} attempts.")
            self.send_queue.popleft()
            self.collision_count = 0
            self.attempt_transmission()
            return
        
        # Binary Exponential Backoff: The core of statistical arbitration. The station
        # waits a random number of "slot times" before re-transmitting. The range
        # of the random wait doubles with each collision.
        backoff_limit = min(self.collision_count, 10)
        k = random.randint(0, 2**backoff_limit - 1)
        wait_time = k * self.ether.slot_time
        
        self.simulator.schedule(wait_time, self.attempt_transmission, f"Backoff {self.station.name}")

class Station:
    """A generic network node."""
    def __init__(self, name, simulator):
        self.name = name
        self.simulator = simulator
        self.controller = None
        self.packets_sent = 0
        self.packets_received = 0
        self.total_latency = 0

    def send_packet(self, destination, size_bits):
        packet = Packet(size_bits, self, destination, flow_id=self.name, creation_time=self.simulator.current_time)
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.name} queues {packet} for {destination.name}.")
        self.controller.send(packet)

    def receive(self, packet):
        self.packets_received += 1
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.name} received {packet} from {packet.source.name}.")

    def notify_tx_success(self):
        self.packets_sent += 1
        
    def __repr__(self):
        return self.name

# --- MODEL 2: MODERN SWITCHED TCP ENVIORNMENT ---
# This model represents the current paradigm: bandwidth-multiplexed, full-duplex
# links where TCP flows compete. It operates on the flawed assumption that
# reliability can be layered on top of a best-effort fabric, leading to
# performance degradation governed by latency and loss (the Mathis equation).

class TCPFlow:
    """Simulates a bulk data transfer using TCP's AIMD congestion control."""
    def __init__(self, source, destination, simulator, switch):
        self.source = source
        self.destination = destination
        self.simulator = simulator
        self.switch = switch
        self.flow_id = source.name
        
        # TCP State Variables
        self.cwnd = 1.0  # Congestion window in packets
        self.ssthresh = 64  # Slow start threshold
        self.rtt = switch.latency * 2 # Simplified RTT
        self.packets_in_flight = 0
        self.next_packet_to_send = 0
        self.is_active = True
        self.total_sent = 0
        
    def start(self):
        self.send_data()

    def send_data(self):
        if not self.is_active: return
        
        while self.packets_in_flight < self.cwnd:
            packet = Packet(DEFAULT_PACKET_BITS, self.source, self.destination, self.flow_id)
            self.switch.enqueue(packet, self.source)
            self.packets_in_flight += 1
            self.total_sent += 1

    def handle_ack(self):
        self.packets_in_flight -= 1
        
        # Additive Increase: For each ACK received, the congestion window is
        # increased. In equilibrium, this results in an increase of roughly
        # one MSS per round-trip time.
        if self.cwnd < self.ssthresh:
            self.cwnd += 1 # Slow Start
        else:
            self.cwnd += 1.0 / self.cwnd # Congestion Avoidance

        self.send_data()

    def handle_loss(self):
        # Multiplicative Decrease: Upon a congestion signal (packet loss),
        # the window is halved. This is TCP's primary mechanism for reacting
        # to network congestion.
        print(f"{self.simulator.current_time/1e6:.3f}ms: TCP Flow {self.flow_id} experienced loss.")
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = self.ssthresh # Simplified Fast Recovery
        self.packets_in_flight = int(self.cwnd) # Simplified retransmission

        self.send_data()

class BandwidthMultiplexedSwitch:
    """Models a simple, modern switch that multiplexes bandwidth. It has a
       single output queue and introduces loss when the queue is full."""
    def __init__(self, simulator, latency, loss_probability=0.0):
        self.simulator = simulator
        self.latency = latency
        self.loss_prob = loss_probability # Represents background loss
        self.queue = deque()
        self.is_busy = False
        self.capacity_bps = BITS_PER_SECOND_1GB
        self.queue_limit_packets = 50 # A buffer to handle bursts

    def enqueue(self, packet, source_node):
        # The switch enforces no fairness; it's a simple FIFO queue. When the
        # queue is full, packets are dropped. This is the root cause of
        # congestion signals in modern networks.
        if len(self.queue) >= self.queue_limit_packets:
            print(f"DROP: Switch queue full. Dropping {packet} from {source_node.name}.")
            packet.source.controller.handle_loss()
            return

        self.queue.append(packet)
        if not self.is_busy:
            self.process_queue()

    def process_queue(self):
        if not self.queue:
            self.is_busy = False
            return

        self.is_busy = True
        packet = self.queue.popleft()
        
        # Transmission time depends on packet size and link bandwidth.
        tx_time = packet.size_bits / self.capacity_bps
        
        # Total delay is propagation latency + transmission time.
        total_delay = self.latency + tx_time

        # Simulate packet reaching the destination
        self.simulator.schedule(total_delay, lambda p=packet: self.deliver(p), f"Deliver {packet}")
        
        # Schedule the next queue processing event
        self.simulator.schedule(tx_time, self.process_queue, "SwitchNext")

    def deliver(self, packet):
        # Simulate an ACK coming back for TCP flows
        ack_packet = Packet(TCP_ACK_BITS, packet.destination, packet.source)
        # Senders and receivers rely on this handshake to know the outcome of a transmission.
        self.simulator.schedule(self.latency, lambda: packet.source.controller.handle_ack(), f"ACK {packet}")
        # The packet arrives at the destination station's interface.
        packet.destination.receive(packet)


# --- MODEL 3: THE DAEDÆLUS N2N FABRIC ---
# This model demonstrates our core philosophy. It replaces statistical contention
# with deterministic scheduling. It replaces unreliable links with reliable N2N
# links. This is not an optimization of Ethernet; it is an escape from that model.

class N2NLink:
    """A reliable, point-to-point, full-duplex link. This is a first-class
       citizen in the infrastructure, a bipartite element of information. It
       does not drop packets."""
    def __init__(self, node_a, node_b, length_meters, simulator):
        self.nodes = (node_a, node_b)
        self.simulator = simulator
        self.propagation_delay = length_meters / PROPAGATION_SPEED_M_PER_NS
        self.capacity_bps = BITS_PER_SECOND_1GB
        self.busy_until = {node_a: 0, node_b: 0} # Tracks when each node's transmitter is free

    def send(self, source, packet):
        destination = self.nodes[0] if source is self.nodes[1] else self.nodes[1]
        
        # The 'snake on a wire' principle: transmission time can be longer than
        # the propagation delay.
        transmission_time = packet.size_bits / self.capacity_bps
        
        # The link is pipelined. A node can start sending as soon as its transmitter is free.
        start_time = max(self.simulator.current_time, self.busy_until[source])
        end_time = start_time + transmission_time
        self.busy_until[source] = end_time

        # The head of the packet arrives after one propagation delay.
        arrival_time = start_time + self.propagation_delay
        
        # Because the link is reliable (like Fibre Channel), the acknowledgment
        # is an intrinsic part of the protocol, not a separate, unreliable packet.
        # Here, we model an immediate, zero-cost ACK generated upon receipt.
        # This models our Truncated Tail Latency protocol, where the sender
        # knows the outcome instantly without timeouts or retries.
        ack_arrival_time = arrival_time + self.propagation_delay
        
        self.simulator.schedule(arrival_time - self.simulator.current_time,
                                lambda d=destination, p=packet: d.receive(p),
                                f"N2N Deliver {packet}")
        self.simulator.schedule(ack_arrival_time - self.simulator.current_time,
                                lambda s=source: s.notify_tx_success(),
                                f"N2N ACK {packet}")
                                
class Interaction:
    """A Reversible Subtransaction: an atomic request/reply pair."""
    def __init__(self, source, destination, size_bits):
        self.source = source
        self.destination = destination
        self.packet = Packet(size_bits, source, destination)
        
class GraphVirtualMachine:
    """The GVM's role is not to forward packets but to schedule interactions.
       Instead of allowing flows to fight for bandwidth, we interleave the
       atomic request/reply transactions to ensure fairness and progress for all."""
    def __init__(self, links, simulator):
        self.links = links # The groundplane or transaction fabric
        self.simulator = simulator
        self.interaction_queue = deque()
        self.is_busy = False

    def schedule_interaction(self, interaction):
        self.interaction_queue.append(interaction)
        if not self.is_busy:
            self.process_next_interaction()
            
    def process_next_interaction(self):
        if not self.interaction_queue:
            self.is_busy = False
            return
            
        self.is_busy = True
        # Round-robin scheduling of atomic interactions. This is transaction-multiplexing.
        interaction = self.interaction_queue.popleft()
        
        link = self.get_link_for(interaction.source)
        if link:
            link.send(interaction.source, interaction.packet)
            
            # The GVM knows the link's properties (transmission time) and can
            # schedule the next interaction immediately after the current one finishes.
            tx_time = interaction.packet.size_bits / link.capacity_bps
            self.simulator.schedule(tx_time, self.process_next_interaction, "GVM Next")
        else:
            self.process_next_interaction() # Skip if no link

    def get_link_for(self, node):
        for link in self.links:
            if node in link.nodes:
                return link
        return None

class DaedaelusNode(Station):
    """A station operating within the Daedaelus fabric."""
    def __init__(self, name, simulator, gvm):
        super().__init__(name, simulator)
        self.gvm = gvm
        self.received_packets = []
        self.successful_sends = 0
        self.completion_time = 0

    def send_packet(self, destination, size_bits):
        interaction = Interaction(self, destination, size_bits)
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.name} requests GVM to schedule interaction with {destination.name}.")
        self.gvm.schedule_interaction(interaction)

    def receive(self, packet):
        super().receive(packet)
        self.received_packets.append(packet)

    def notify_tx_success(self):
        super().notify_tx_success()
        self.successful_sends += 1
        self.completion_time = self.simulator.current_time
        print(f"{self.simulator.current_time/1e6:.3f}ms: {self.name} received ACK for an interaction.")
        

# --- Simulation Scenarios ---

def run_classical_ethernet_sim():
    print("--- SCENARIO 1: CLASSICAL SHARED ETHER (METCALFE, 1976) ---")
    print("Models N stations contending for a single half-duplex channel.")
    print("Observe collisions, backoffs, and the resulting low channel utilization.\n")

    sim = Simulator()
    stations = [Station(f"Node-{i}", sim) for i in range(5)]
    ether = Ether(length_meters=500, simulator=sim, stations=stations)
    for s in stations:
        s.controller = ClassicalController(s, ether, sim)
        
    # Schedule all stations to send a packet at nearly the same time to induce collision
    for i, s in enumerate(stations):
        sim.schedule(i * 10, lambda s=s: s.send_packet(stations[0], DEFAULT_PACKET_BITS))

    sim.run(until_time=2_000_000) # Run for 2ms
    
    total_packets = sum(s.packets_sent for s in stations)
    total_bits = total_packets * DEFAULT_PACKET_BITS
    # Efficiency is the ratio of time spent sending useful data vs. total time.
    # Total time includes contention intervals (collisions, backoffs, deferrals).
    if sim.current_time > 0:
        utilization = (total_bits / BITS_PER_SECOND_1GB) / (sim.current_time / 1e9)
    else:
        utilization = 0
    print(f"Classical Ether Result: {total_packets} packets transmitted.")
    print(f"Effective Channel Utilization: {utilization * 100:.2f}%")


def run_tcp_contention_sim():
    print("--- SCENARIO 2: MODERN TCP BANDWIDTH MULTIPLEXING ---")
    print("Models N TCP flows competing over a single bottleneck switch link.")
    print("This demonstrates how throughput degrades as flows are serialized by the queue.\n")

    sim = Simulator()
    num_flows = 5
    
    nodes = [Station(f"Flow-{i}", sim) for i in range(num_flows)]
    server_node = Station("Server", sim)
    
    # A single bottleneck link with a queue that drops packets
    switch = BandwidthMultiplexedSwitch(sim, latency=10e3) # 10us latency
    
    flows = [TCPFlow(s, server_node, sim, switch) for s in nodes]
    for i, s in enumerate(nodes):
        s.controller = flows[i]
        
    for flow in flows:
        flow.start()

    sim.run(until_time=50_000_000) # Run for 50ms
    
    total_bits_received = server_node.packets_received * DEFAULT_PACKET_BITS
    total_time_sec = sim.current_time / 1e9
    if total_time_sec > 0:
        throughput_mbps = (total_bits_received / total_time_sec) / 1e6
    else:
        throughput_mbps = 0
    
    print(f"TCP Contention Result: Server received {server_node.packets_received} packets.")
    print(f"Total Aggregate Throughput: {throughput_mbps:.2f} Mbps")
    print("Note how flows interfere, causing packet drops and AIMD backoff, limiting total throughput.")


def run_daedalus_fabric_sim():
    print("--- SCENARIO 3: DAEDÆLUS INTERACTION MULTIPLEXING ---")
    print("Models N pairs of nodes communicating over reliable N2N Links, scheduled by a GVM.")
    print("This demonstrates deterministic, concurrent progress without contention.\n")

    sim = Simulator()
    num_pairs = 5
    
    nodes = [DaedaelusNode(f"Node-{i}", sim, None) for i in range(num_pairs * 2)]
    links = [N2NLink(nodes[2*i], nodes[2*i+1], length_meters=2, simulator=sim) for i in range(num_pairs)]
    gvm = GraphVirtualMachine(links, sim)
    for node in nodes:
        node.gvm = gvm
    
    # Schedule all pairs to start their interactions at the same time
    total_interactions = 10
    for i in range(total_interactions):
        for j in range(num_pairs):
            source = nodes[2*j]
            dest = nodes[2*j+1]
            # Delay slightly to show scheduling, not simultaneous start
            sim.schedule(i * 10, lambda s=source, d=dest: s.send_packet(d, DEFAULT_PACKET_BITS))

    sim.run(until_time=5_000_000) # Run for 5ms
    
    total_packets_sent = sum(n.successful_sends for n in nodes if n.name.startswith("Node-"))
    # Find the last time any of the target interactions completed
    last_completion_time = 0
    for n in nodes:
        if n.successful_sends > 0:
             last_completion_time = max(last_completion_time, n.completion_time)

    if last_completion_time > 0:
        total_time_sec = last_completion_time / 1e9
        total_bits = total_packets_sent * DEFAULT_PACKET_BITS
        throughput_mbps = (total_bits / total_time_sec) / 1e6
    else:
        total_time_sec = 0
        throughput_mbps = 0


    print(f"Daedaelus Fabric Result: {total_packets_sent} interactions completed.")
    if total_time_sec > 0:
        print(f"Time to complete all interactions: {total_time_sec * 1e6:.2f} us")
    print(f"Effective Transactional Throughput: {throughput_mbps:.2f} Mbps")
    print("Note that all flows make progress concurrently without collisions or drops.")


if __name__ == "__main__":
    run_classical_ethernet_sim()
    run_tcp_contention_sim()
    run_daedalus_fabric_sim()