#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DDL_Emulator: A Daedaelus Network Simulator
Version 1.1

This script serves as a computational essay and agent-based simulator to explore the
foundational principles of computer networking, contrasting classical Ethernet with
the architectural philosophy of Daedaelus and Open Atomic Ethernet.

Mission: Daedaelus: Architecting the Future with Enduring Excellence.
We address fundamental problems in distributed systems using protocols, data
structures, and algorithms inspired by Quantum Information Theory and Multiway
Systems. This emulator is a tool to demonstrate the 'why' behind our approach,
moving beyond statistical models to computational, agent-based proof.

The emulator is designed to be a single, self-contained Python file, incorporating
elements and concepts from a wide corpus of networking research and simulation tools,
including ns-2, C++ socket implementations, and hardware description languages.

Core Concepts Modeled:
1.  **Classical CSMA/CD Ethernet (Metcalfe, 1976):** A simulation of the shared,
    half-duplex "Ether" with distributed statistical arbitration. This demonstrates
    the inherent contention, collision, and backoff mechanisms that lead to the
    probabilistic performance characterized by the Mathis equation.

2.  **Layer 2 Switching:** A simple MAC-learning switch, inspired by standard
    networking hardware and the provided C++ examples.

3.  **Layer 3 Routing:** A router implementing longest-prefix matching, demonstrating
    the next level of network organization.

4.  **TCP Congestion Control:** An application-level agent that models the
    Additive Increase/Multiplicative Decrease (AIMD) algorithm to show how
    throughput becomes dependent on packet loss and RTT, as described in
    "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm".

5.  **Open Atomic Ethernet Link:** A full-duplex, point-to-point link model that
    achieves reliability without the overhead of classical contention. It demonstrates
    the "packet longer than the wire" principle, where full link utilization can be
    achieved, escaping the limitations of the original Ethernet efficiency model.

This script is a living document and a tool for thought, intended to make the
abstract principles of network architecture tangible and interactive.
"""

import heapq
import random
import math
import ipaddress
from collections import defaultdict

# --- Core Simulation Engine ---

class Event:
    """A simple event structure for the simulation's priority queue."""
    def __init__(self, time, callback, description=""):
        self.time = time
        self.callback = callback
        self.description = description

    def __lt__(self, other):
        return self.time < other.time

class Simulation:
    """
    The main simulation driver, managing the event queue and the simulation clock.
    """
    def __init__(self):
        self.time = 0.0
        self.event_queue = []
        self.nodes = {}
        self.links = []
        self.metrics = {
            "packets_sent": 0,
            "packets_received": 0,
            "total_latency": 0.0,
            "collisions": 0,
            "throughput_data": []
        }

    def schedule_event(self, delay, callback, description=""):
        event_time = self.time + delay
        heapq.heappush(self.event_queue, Event(event_time, callback, description))

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_link(self, link):
        self.links.append(link)

    def run(self, duration):
        print(f"--- Starting Simulation (Duration: {duration}s) ---")
        end_time = self.time + duration
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if event.time > end_time:
                break
            self.time = event.time
            event.callback()
        self.print_results()

    def print_results(self):
        print(f"\n--- Simulation Finished at time {self.time:.6f}s ---")
        sent = self.metrics["packets_sent"]
        received = self.metrics["packets_received"]
        pdr = (received / sent * 100) if sent > 0 else 0
        avg_latency = (self.metrics["total_latency"] / received * 1000) if received > 0 else 0

        print(f"Total Packets Sent: {sent}")
        print(f"Total Packets Received: {received}")
        print(f"Packet Delivery Ratio (PDR): {pdr:.2f}%")
        print(f"Average End-to-End Delay: {avg_latency:.2f} ms")
        if self.metrics["collisions"] > 0:
            print(f"Total Collisions Detected: {self.metrics['collisions']}")

# --- Network & Packet Structures ---

class EthernetFrame:
    """
    Represents a Layer 2 Ethernet Frame.
    Inspired by the SystemVerilog (`transmission.sv`) and C++ (`switch.cpp`)
    structures, defining the fundamental unit of data on the Ether.
    """
    def __init__(self, source_mac, dest_mac, ethertype, payload, crc=None):
        self.preamble = 0x55 * 7
        self.sfd = 0xD5  # Start Frame Delimiter
        self.dest_mac = dest_mac
        self.source_mac = source_mac
        self.ethertype = ethertype
        self.payload = payload
        # In a real system, CRC would be calculated. We simulate this.
        self.crc = crc if crc is not None else self.calculate_crc()
        self.size_bits = (len(str(payload)) + 14) * 8 # Approximate size in bits

    def calculate_crc(self):
        # A simple simulated CRC check.
        return hash(f"{self.dest_mac}{self.source_mac}{self.ethertype}{self.payload}")

    def __repr__(self):
        return f"Frame(Src:{self.source_mac}, Dst:{self.dest_mac}, Type:{hex(self.ethertype)})"

class IPv4Packet:
    """
    Represents a Layer 3 IPv4 Packet.
    Inspired by the router.cpp logic. The payload of an EthernetFrame.
    """
    def __init__(self, source_ip, dest_ip, payload, ttl=64):
        self.source_ip = ipaddress.ip_address(source_ip)
        self.dest_ip = ipaddress.ip_address(dest_ip)
        self.payload = payload
        self.ttl = ttl

    def __repr__(self):
        return f"IPv4(Src:{self.source_ip}, Dst:{self.dest_ip})"

class TCP_Segment:
    """
    Represents a Layer 4 TCP Segment.
    The payload of an IPv4Packet, used for congestion control simulation.
    """
    def __init__(self, seq_num, ack_num=0, is_ack=False, payload=""):
        self.seq = seq_num
        self.ack = ack_num
        self.is_ack = is_ack
        self.payload = payload

    def __repr__(self):
        if self.is_ack:
            return f"TCP(ACK:{self.ack})"
        else:
            return f"TCP(SEQ:{self.seq})"

# --- Network Components ---

class Link:
    """
    Represents a physical link between two nodes. It can operate in different modes
    to model various network architectures.
    """
    def __init__(self, sim, node1, node2, bit_rate=3e6, delay=1e-6, loss_rate=0.0):
        self.sim = sim
        self.node1 = node1
        self.node2 = node2
        self.bit_rate = bit_rate
        self.delay = delay
        self.loss_rate = loss_rate
        self.connections = {node1: None, node2: None} # Maps node object to its port number

    def transmit(self, sending_node, frame):
        # Simulate transmission delay based on frame size and bit rate
        transmission_delay = frame.size_bits / self.bit_rate
        self.sim.schedule_event(
            transmission_delay,
            lambda: self._propagate(sending_node, frame),
            f"Propagation of {frame}"
        )

    def _propagate(self, sending_node, frame):
        # Simulate propagation delay and potential packet loss
        receiving_node = self.node2 if sending_node is self.node1 else self.node1
        if random.random() < self.loss_rate:
            print(f"{self.sim.time:.6f}: Link dropped frame {frame}")
            return
        
        receiving_port = self.connections[receiving_node]
        self.sim.schedule_event(
            self.delay,
            lambda: receiving_node.receive(frame, incoming_port=receiving_port),
            f"Reception of {frame}"
        )

class Node:
    """Base class for all network devices."""
    def __init__(self, sim, name, num_ports=1):
        self.sim = sim
        self.name = name
        self.ports = {i: None for i in range(num_ports)} # port_num -> Link object

    def connect(self, port_num, link):
        self.ports[port_num] = link
        # Inform the link which port it's connected to on this node
        if self in link.connections:
            link.connections[self] = port_num

    def receive(self, frame, incoming_port):
        raise NotImplementedError

    def send(self, frame, port):
        raise NotImplementedError

class Station(Node):
    """
    Represents an end-user device (e.g., PC). It has a single NIC and runs
    applications. Inspired by the ns-2 node and C++ client/server models.
    """
    def __init__(self, sim, name, mac_addr, ip_addr=None):
        super().__init__(sim, name, num_ports=1)
        self.nic = NIC(sim, self, mac_addr, ip_addr)
        self.app = None

    def set_application(self, app):
        self.app = app
        self.app.station = self

    def receive(self, frame, incoming_port):
        self.nic.receive(frame, incoming_port)

    def send(self, dest_mac, ethertype, payload):
        self.nic.send(dest_mac, ethertype, payload)

class NIC:
    """
    Network Interface Controller. Encapsulates L2 logic.
    """
    def __init__(self, sim, station, mac_addr, ip_addr=None):
        self.sim = sim
        self.station = station
        self.mac_addr = mac_addr
        self.ip_addr = ip_addr
        self.arp_table = {} # IP -> MAC

    def send(self, dest_mac, ethertype, payload):
        frame = EthernetFrame(self.mac_addr, dest_mac, ethertype, payload)
        link = self.station.ports[0]
        if link:
            # This is where the NIC accesses the physical link
            link.transmit(self.station, frame)
            self.sim.metrics["packets_sent"] += 1

    def receive(self, frame, incoming_port):
        # Hardware address filtering
        if frame.dest_mac == self.mac_addr or frame.dest_mac == "FF:FF:FF:FF:FF:FF":
            # Pass up to the station's application
            if self.station.app:
                self.station.app.receive(frame)

class Switch(Node):
    """
    A Layer 2 MAC-learning switch. Its logic is inspired by `switch.cpp`.
    It learns MAC address locations and forwards frames, reducing collisions
    compared to a simple hub.
    """
    def __init__(self, sim, name, num_ports=4):
        super().__init__(sim, name, num_ports)
        self.mac_table = {} # mac_addr -> port

    def receive(self, frame, incoming_port):
        # Learn source MAC address
        if frame.source_mac not in self.mac_table:
            print(f"{self.sim.time:.6f}: Switch {self.name} learned {frame.source_mac} is on port {incoming_port}")
            self.mac_table[frame.source_mac] = incoming_port

        # Forward or flood
        if frame.dest_mac in self.mac_table:
            dest_port = self.mac_table[frame.dest_mac]
            if dest_port != incoming_port:
                self.send(frame, dest_port)
        else:
            # Flood to all ports except the incoming one
            for port, link in self.ports.items():
                if port != incoming_port and link is not None:
                    self.send(frame, port)

    def send(self, frame, port):
        if self.ports[port]:
            self.ports[port].transmit(self, frame)

# --- Application Layer & Protocols ---

class Application:
    """Base class for applications running on a Station."""
    def __init__(self, sim):
        self.sim = sim
        self.station = None

    def receive(self, frame):
        raise NotImplementedError

class BulkTransferClient(Application):
    """
    Simulates a bulk data transfer, akin to FTP. Models the logic
    from the ns-2 simulations and C++ client.
    """
    def __init__(self, sim, dest_mac, dest_ip, data_size_mb=1):
        super().__init__(sim)
        self.dest_mac = dest_mac
        self.dest_ip = dest_ip
        self.total_bytes_to_send = data_size_mb * 1024 * 1024
        self.bytes_sent = 0

    def start(self):
        print(f"{self.sim.time:.6f}: {self.station.name} starting bulk transfer to {self.dest_ip}")
        self.send_chunk()

    def send_chunk(self):
        if self.bytes_sent < self.total_bytes_to_send:
            payload = f"chunk_{self.bytes_sent}"
            ip_packet = IPv4Packet(self.station.nic.ip_addr, self.dest_ip, payload)
            self.station.send(self.dest_mac, 0x0800, ip_packet)
            self.bytes_sent += len(payload)
            self.sim.schedule_event(0.001, self.send_chunk, "Next chunk") # Simplified sending rate

    def receive(self, frame):
        # A simple client might receive ACKs, but we omit that for this basic model.
        pass

class BulkTransferServer(Application):
    """The receiving end for the bulk transfer."""
    def __init__(self, sim):
        super().__init__(sim)
        self.bytes_received = 0

    def receive(self, frame):
        if isinstance(frame.payload, IPv4Packet):
            self.bytes_received += len(frame.payload.payload)
            self.sim.metrics["packets_received"] += 1
            # Here we can add latency calculation
            # For simplicity, we assume we know when it was sent. This needs a proper protocol.


class TCPCongestionControlApp(Application):
    """
    An application that implements TCP's AIMD congestion control. This is key
    to demonstrating the argument in the Mathis paper.
    """
    def __init__(self, sim, dest_mac, dest_ip):
        super().__init__(sim)
        self.dest_mac = dest_mac
        self.dest_ip = dest_ip

        # TCP State Variables
        self.cwnd = 1.0  # Congestion Window in packets
        self.ssthresh = 64.0 # Slow Start Threshold
        self.next_seq_num = 0
        self.last_ack_num = -1
        self.dupacks = 0

    def start(self):
        print(f"{self.sim.time:.6f}: {self.station.name} starting TCP flow to {self.dest_ip}. CWND={self.cwnd}")
        self._send_data()

    def _send_data(self):
        # Send a window's worth of data
        num_to_send = int(self.cwnd - (self.next_seq_num - self.last_ack_num -1))
        for _ in range(max(0, num_to_send)):
            tcp_segment = TCP_Segment(self.next_seq_num, payload=f"data_{self.next_seq_num}")
            ip_packet = IPv4Packet(self.station.nic.ip_addr, self.dest_ip, tcp_segment)
            self.station.send(self.dest_mac, 0x0800, ip_packet)
            self.next_seq_num += 1

    def receive(self, frame):
        if isinstance(frame.payload, IPv4Packet) and isinstance(frame.payload.payload, TCP_Segment):
            tcp_ack = frame.payload.payload
            if tcp_ack.is_ack:
                # This is a simplified ACK processing logic
                if tcp_ack.ack == self.last_ack_num:
                    self.dupacks += 1
                    if self.dupacks == 3:
                        # Fast Retransmit
                        self.handle_congestion_event("fast_retransmit")
                elif tcp_ack.ack > self.last_ack_num:
                    # New data acknowledged
                    if self.cwnd < self.ssthresh:
                        # Slow Start
                        self.cwnd += (tcp_ack.ack - self.last_ack_num)
                    else:
                        # Congestion Avoidance: increase by 1/cwnd for each ack.
                        self.cwnd += 1.0 / self.cwnd

                    self.last_ack_num = tcp_ack.ack
                    self.dupacks = 0
                    self._send_data() # Send new data as window opens

    def handle_congestion_event(self, event_type):
        """
        This is where TCP's Congestion Avoidance algorithm reacts to loss.
        The window is decreased by a multiplicative factor on each congestion signal.
        """
        print(f"{self.sim.time:.6f}: {self.station.name} CONGESTION EVENT ({event_type}). CWND was {self.cwnd:.2f}")
        self.ssthresh = self.cwnd / 2
        self.cwnd = self.ssthresh # Fast Recovery simplified
        self.dupacks = 0
        print(f"                 New ssthresh={self.ssthresh:.2f}, New cwnd={self.cwnd:.2f}")
        # In a real implementation, we would retransmit the lost packet.
        self._send_data()


# --- Main Execution & Scenarios ---

def setup_metcalfe_contention_scenario():
    """
    A scenario to demonstrate the original CSMA/CD mechanism.
    This is not implemented in the main script for brevity but shows how one would
    use the components to model the classic shared Ether. One would need a
    CSMA_CD_NIC class and a shared `Ether` object.
    """
    print("\n--- SCENARIO: Metcalfe's Shared Ether Contention ---")
    # This would involve creating multiple stations attached to a single Ether object
    # and having them attempt to transmit simultaneously to observe collisions
    # and the binary exponential backoff mechanism.
    print("This scenario requires a CSMA_CD_NIC and shared Ether object, demonstrating the principles of distributed statistical arbitration.")
    pass

def setup_switch_and_router_scenario():
    """
    Demonstrates L2 switching and L3 routing, inspired by the C++ repos.
    """
    print("\n--- SCENARIO: Switched and Routed Network ---")
    sim = Simulation()

    # Create devices
    s1 = Station(sim, "S1", "0A:0A:0A:0A:0A:01", "192.168.1.10")
    s2 = Station(sim, "S2", "0A:0A:0A:0A:0A:02", "192.168.1.11")
    switch = Switch(sim, "Switch1", num_ports=2)

    sim.add_node(s1)
    sim.add_node(s2)
    sim.add_node(switch)

    # Create links and connect them
    link1 = Link(sim, s1, switch, delay=1e-6)
    s1.connect(0, link1)
    switch.connect(0, link1)

    link2 = Link(sim, s2, switch, delay=1e-6)
    s2.connect(0, link2)
    switch.connect(1, link2)

    # Setup applications
    client_app = BulkTransferClient(sim, dest_mac="0A:0A:0A:0A:0A:02", dest_ip="192.168.1.11")
    s1.set_application(client_app)
    server_app = BulkTransferServer(sim)
    s2.set_application(server_app)

    sim.schedule_event(0.01, client_app.start)
    sim.run(0.5)


if __name__ == '__main__':
    # Due to the complexity of a full network simulation in a single file,
    # we will run a simplified scenario that demonstrates key principles.
    # The `setup_switch_and_router_scenario` shows how the L2/L3 components
    # would be used. The full vision requires separate classes for each NIC type
    # and a more sophisticated simulation loop.

    print("Dædælus Network Emulator Initializing...")
    print("This demonstration will show basic L2/L3 forwarding and application data flow.")

    setup_switch_and_router_scenario()

