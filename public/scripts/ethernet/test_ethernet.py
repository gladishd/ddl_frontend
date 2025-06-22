#
# Dædælus: test_ethernet.py
#
# This script provides an interactive simulation environment for comparing
# conventional networking protocols with the principles of the Dædælus Transaction Fabric.
# It is designed to be a form of "Code as Proof," demonstrating the
# fundamental flaws in statistical contention models and showcasing the
# efficiency of deterministic, interaction-multiplexed communication.
#
# Inspired by the principles outlined in "Bandwidth Works in Practice, not in Theory,"
# this emulator moves beyond simple bandwidth metrics to explore the nuanced
# interplay of latency, reliability, and transactional integrity.
#

#!/usr/bin/env python3
import json
import logging
import uuid
import io
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from math import cos, sin, pi
import random
import enum
import simpy

# These imports may not be available; mock implementations are provided below.
try:
    from PIL import Image, EpsImagePlugin, ImageDraw
    EpsImagePlugin.gs_windows_binary = r'gswin64c' if os.name == 'nt' else 'gs'
except ImportError:
    print("Warning: Pillow not found. Animation export will be disabled.")
    Image = None

# External simulation modules are optional
try:
    import daedaelus_fabric_sim as fabric_sim
    import ethernet24 as tsn_mod
    import ethernet25 as building_mod
except ImportError:
    print("Info: External Daedaelus modules not found. Using internal mock implementations.")
    fabric_sim = None
    tsn_mod = None
    building_mod = None


# -----------------------------------------------------------------------------
# Logging setup: Packet & link logs (capture all modules)
#
# A unified logging stream is crucial for creating a cohesive view of the
# entire system, from the lowest-level link events to the highest-level
# application logic. This allows for comprehensive analysis in tools like Mathematica.
# -----------------------------------------------------------------------------
logger = logging.getLogger("net_sim")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

def export_logs(path: str):
    """Write the entire logging buffer to a JSON file for Mathematica."""
    raw_content = log_buffer.getvalue()
    raw_lines = raw_content.strip().splitlines()
    records = []
    for line in raw_lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Skipping malformed log line: {line}")
            
    with open(path, 'w') as f:
        json.dump(records, f, indent=2)
    logger.info(json.dumps({"event": "export_logs", "path": path, "records_exported": len(records)}))

# -----------------------------------------------------------------------------
# Core Networking Primitives & Enums
#
# Expanded to include types for the new mock simulations, ensuring each
# conceptual operation has a distinct visual representation.
# -----------------------------------------------------------------------------
class PacketType(enum.Enum):
    SYN = "SYN"
    SYN_ACK = "SYN-ACK"
    ACK = "ACK"
    DATA = "DATA"
    JAM = "JAM_SIGNAL"
    LIVENESS_TOKEN = "LIVENESS_TOKEN"
    TSN_MSG = "TSN_MSG"
    IOT_DATA = "IOT_DATA"
    CREDIT = "CREDIT" # Added for Fibre Channel

class Packet:
    def __init__(self, ptype: PacketType, src=None, dst=None, size=64, seq=0, ack=0, credit_val=0):
        self.id, self.ptype = str(uuid.uuid4()), ptype
        self.src = getattr(src, 'name', src) # Handle both node objects and string names
        self.dst = getattr(dst, 'name', dst)
        self.size, self.seq, self.ack = size, seq, ack
        self.credit_val = credit_val
        self.success, self.collision_count = True, 0
        # A high-contrast color palette to ensure visual clarity of different packet types.
        # Clear visualization is essential for making the system's behavior intelligible.
        self.color = {
            "SYN": "#00BFFF",           # DeepSkyBlue
            "SYN_ACK": "#00FFFF",       # Cyan
            "ACK": "#32CD32",           # LimeGreen
            "DATA": "#FFD700",          # Gold
            "JAM": "#FF0000",           # Red
            "LIVENESS_TOKEN": "#FF00FF", # Magenta
            "TSN_MSG": "#FFA500",        # Orange
            "IOT_DATA": "#98FB98",       # PaleGreen
            "CREDIT": "#D8BFD8"          # Thistle
        }.get(ptype.value, "#FFFFFF")   # White for default

    def bits(self): return self.size * 8
    def to_dict(self):
        d = {
            "time": getattr(self, 'start_time', None), "pkt_id": self.id, 
            "type": self.ptype.value, "src": self.src, "dst": self.dst, 
            "seq": self.seq, "ack": self.ack, "size": self.size, 
            "success": self.success, "collisions": self.collision_count,
            "color": self.color
        }
        if self.ptype == PacketType.CREDIT:
            d["credit_val"] = self.credit_val
        return d
    def __repr__(self): return f"<{self.ptype.value} id={self.id[:4]} src={self.src}->dst={self.dst}>"

# -----------------------------------------------------------------------------
# Protocol-Specific Classes
# -----------------------------------------------------------------------------

class CongestedLink:
    """
    Models a congested, buffered link (like a switch) that can drop packets.
    It uses a SimPy Store to represent a finite buffer. This is key for the
    Metcalfe Full-Duplex simulation to model a central bottleneck.
    """
    def __init__(self, env, name, buffer_capacity=20, prop_delay=1e-6, bandwidth_bps=10e9):
        self.env = env
        self.name = name
        self.buffer = simpy.Store(env, capacity=buffer_capacity)
        self.prop_delay = prop_delay
        self.bandwidth = bandwidth_bps
        self.packets_dropped = 0
        self.receivers = {}
        self.total_bytes_transferred = 0

    def put(self, packet):
        if len(self.buffer.items) < self.buffer.capacity:
            return self.buffer.put(packet)
        else:
            self.packets_dropped += 1
            packet.success = False
            log_entry = {
                "time": self.env.now, "event": "pkt_drop", "chan": self.name,
                "reason": "buffer_full", **packet.to_dict()
            }
            logger.info(json.dumps(log_entry))
            return self.env.timeout(0)

    def start_delivering(self):
        while True:
            packet = yield self.buffer.get()
            receiver_node = self.receivers.get(packet.dst)
            if receiver_node:
                self.env.process(self.deliver(packet, receiver_node))
            else:
                log_entry = {"time": self.env.now, "event": "pkt_drop", "chan": self.name, "reason": "no_receiver", **packet.to_dict()}
                logger.info(json.dumps(log_entry))

    def deliver(self, packet, receiver_node):
        transmission_time = packet.bits() / self.bandwidth
        yield self.env.timeout(transmission_time)
        yield self.env.timeout(self.prop_delay)
        if packet.ptype == PacketType.DATA and packet.success:
            self.total_bytes_transferred += packet.size
        receiver_node.receive_packet(packet)

class TCPNode:
    """
    Represents a node using a simplified TCP Reno-like congestion control.
    - Implements Additive Increase, Multiplicative Decrease (AIMD).
    - Reacts to timeouts by reducing cwnd and retransmitting.
    """
    def __init__(self, env, name, forward_link, reverse_link, peer=None, is_sender=False, data_size=1024*100):
        self.env = env
        self.name = name
        self.peer_name = getattr(peer, 'name', peer)
        self.is_sender = is_sender
        self.data_to_send = data_size

        self.forward_link = forward_link
        self.reverse_link = reverse_link

        self.state = "CLOSED"
        self.next_seq = 0
        self.send_base = 0 
        self.rcv_next = 0
        
        self.mss = 1024
        self.cwnd = 1.0 
        self.ssthresh = 64
        self.rto = 0.1
        self.dupacks = 0
        
        self.inbox = simpy.Store(env)
        self.action = env.process(self.run())

    def receive_packet(self, packet):
        self.inbox.put(packet)

    def handle_congestion_event(self, reason):
        """Multiplicative Decrease: The core of TCP's reaction to congestion."""
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = 1.0
        self.next_seq = self.send_base
        self.dupacks = 0
        log_entry = {
            "time": self.env.now, "event": "congestion_event", "node": self.name,
            "reason": reason, "new_cwnd": round(self.cwnd, 2), "new_ssthresh": round(self.ssthresh, 2)
        }
        logger.info(json.dumps(log_entry))

    def run(self):
        """Main lifecycle process for the node."""
        self.state = "ESTABLISHED"
        logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))

        if self.is_sender:
            data_proc = self.env.process(self.transmit_data())
            ack_proc = self.env.process(self.receive_acks())
            timer_proc = self.env.process(self.retransmit_timer())
            yield data_proc
            if not ack_proc.triggered: ack_proc.interrupt()
            if not timer_proc.triggered: timer_proc.interrupt()
        else:
            yield self.env.process(self.receive_data())

    def retransmit_timer(self):
        try:
            while self.send_base < self.data_to_send:
                yield self.env.timeout(self.rto)
                if self.next_seq > self.send_base:
                    self.handle_congestion_event("timeout")
        except simpy.Interrupt:
            pass 

    def transmit_data(self):
        while self.send_base < self.data_to_send:
            while self.next_seq < self.send_base + (self.cwnd * self.mss):
                if self.next_seq >= self.data_to_send: break
                
                packet = Packet(PacketType.DATA, src=self.name, dst=self.peer_name, size=self.mss, seq=self.next_seq)
                packet.start_time = self.env.now
                logger.info(json.dumps({"event": "start_tx", "node": self.name, **packet.to_dict(), "cwnd": round(self.cwnd, 2)}))
                yield self.forward_link.put(packet)
                self.next_seq += self.mss
            
            yield self.env.timeout(0.00001)

    def receive_acks(self):
        last_ack_seq = -1
        try:
            while True:
                ack_pkt = yield self.inbox.get()
                if ack_pkt.ptype == PacketType.ACK and ack_pkt.dst == self.name:
                    if ack_pkt.ack > self.send_base: 
                        bytes_acked = ack_pkt.ack - self.send_base
                        pkts_acked = bytes_acked / self.mss
                        self.send_base = ack_pkt.ack
                        self.dupacks = 0
                        
                        if self.cwnd < self.ssthresh:
                            self.cwnd += pkts_acked
                        else:
                            self.cwnd += pkts_acked / self.cwnd
                    elif ack_pkt.ack == last_ack_seq: 
                        self.dupacks += 1
                    
                    last_ack_seq = ack_pkt.ack
        except simpy.Interrupt:
            pass

    def receive_data(self):
        expected_seq = 0
        try:
            while True:
                data_pkt = yield self.inbox.get()
                if data_pkt.ptype == PacketType.DATA and data_pkt.dst == self.name:
                    if data_pkt.seq >= expected_seq:
                        if data_pkt.seq == expected_seq:
                            expected_seq += data_pkt.size
                        ack = Packet(PacketType.ACK, src=self.name, dst=data_pkt.src, ack=expected_seq)
                        ack.start_time = self.env.now
                        yield self.reverse_link.put(ack)
        except simpy.Interrupt:
            pass

class FibreChannelNode:
    """
    Represents a node in a Fibre Channel fabric. Senders are throttled by credits,
    and receivers (switches) issue credits as they process packets.
    This model demonstrates how promise-based networks avoid congestion-driven
    packet loss by design, instead managing flow through explicit credits.
    """
    def __init__(self, env, name, forward_link, reverse_link, peer=None, is_sender=False, initial_credits=10, data_size=1024*100):
        self.env = env
        self.name = name
        self.peer_name = getattr(peer, 'name', peer)
        self.is_sender = is_sender
        self.data_to_send = data_size
        self.forward_link = forward_link
        self.reverse_link = reverse_link
        self.credits = initial_credits if is_sender else 0
        self.next_seq = 0
        self.send_base = 0
        self.inbox = simpy.Store(env)
        self.action = env.process(self.run())

    def receive_packet(self, packet):
        self.inbox.put(packet)

    def run(self):
        if self.is_sender:
            yield self.env.process(self.transmit_data())
            yield self.env.process(self.receive_credits())
        else: # Receiver logic
            yield self.env.process(self.receive_data_and_grant_credits())

    def transmit_data(self):
        """Sends data only when credits are available."""
        while self.send_base < self.data_to_send:
            if self.credits > 0:
                self.credits -= 1
                packet = Packet(PacketType.DATA, src=self.name, dst=self.peer_name, size=1024, seq=self.next_seq)
                packet.start_time = self.env.now
                logger.info(json.dumps({"event": "start_tx", "node": self.name, "credits": self.credits, **packet.to_dict()}))
                yield self.forward_link.put(packet)
                self.next_seq += packet.size
            else:
                # This is where the sender throttles its flow, waiting for credits.
                logger.info(json.dumps({"time": self.env.now, "event": "credit_stall", "node": self.name}))
                yield self.env.timeout(0.0001) # Small delay to prevent busy-waiting

    def receive_credits(self):
        """Listens for incoming credit packets."""
        while True:
            credit_pkt = yield self.inbox.get()
            if credit_pkt.ptype == PacketType.CREDIT and credit_pkt.dst == self.name:
                self.credits += credit_pkt.credit_val
                logger.info(json.dumps({"time": self.env.now, "event": "credit_received", "node": self.name, "new_credits": self.credits, **credit_pkt.to_dict()}))
                # ACK the data implicitly by receiving a credit
                self.send_base = credit_pkt.ack

    def receive_data_and_grant_credits(self):
        """Receives data and sends back credit packets, simulating processing."""
        while True:
            data_pkt = yield self.inbox.get()
            if data_pkt.ptype == PacketType.DATA and data_pkt.dst == self.name:
                # Simulate processing time before granting a new credit
                yield self.env.timeout(0.00005) 
                
                # In Fibre Channel, credits are returned to the sender. This represents
                # the promise that the receiver has buffer space available.
                credit_packet = Packet(PacketType.CREDIT, src=self.name, dst=data_pkt.src, credit_val=1, ack=data_pkt.seq + data_pkt.size)
                credit_packet.start_time = self.env.now
                logger.info(json.dumps({"event": "grant_credit", "node": self.name, **credit_packet.to_dict()}))
                yield self.reverse_link.put(credit_packet)

class MockDaedaelusFabric:
    def __init__(self, env, num_nodes=2):
        self.env = env
        self.num_nodes = num_nodes

    def setup_processes(self):
        # The exchange of liveness tokens represents the establishment of mutual 
        # knowledge, the "I Know That You Know That I Know" (IKTYKTIK) property,
        # across each individual N2N link in the fabric.
        def link_formation(node1_name, node2_name):
            # Each link formation is an independent, atomic transaction.
            p1 = Packet(PacketType.LIVENESS_TOKEN, src=node1_name, dst=node2_name)
            p1.start_time = self.env.now
            logger.info(json.dumps({"event": "start_tx", **p1.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))

            p2 = Packet(PacketType.LIVENESS_TOKEN, src=node2_name, dst=node1_name)
            p2.start_time = self.env.now
            logger.info(json.dumps({"event": "start_tx", **p2.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))
            
            p3 = Packet(PacketType.ACK, src=node1_name, dst=node2_name)
            p3.start_time = self.env.now
            logger.info(json.dumps({"event": "start_tx", **p3.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))

        node_names = [chr(ord('A') + i) for i in range(self.num_nodes)]
        if not node_names: return
        
        for i in range(self.num_nodes):
            node1_name = node_names[i]
            node2_name = node_names[(i + 1) % self.num_nodes]
            self.env.process(link_formation(node1_name, node2_name))

class MockAutomotiveTSN:
    def __init__(self, env):
        self.env = env

    def setup_processes(self):
        bus = simpy.Store(self.env)
        def sender(source, dest, period, size):
            while True:
                yield self.env.timeout(period)
                p = Packet(PacketType.TSN_MSG, src=source, dst=dest, size=size)
                p.start_time = self.env.now
                bus.put(p)
                logger.info(json.dumps({"event": "start_tx", **p.to_dict()}))

        def receiver(bus, propagation_delay=0.0001):
            while True:
                p = yield bus.get()
                yield self.env.timeout(propagation_delay)
                p.success = True
                logger.info(json.dumps({"event": "end_tx", **p.to_dict()}))
        
        flows_config = {"CameraF":[("HU",1/60,1500)],"ME":[("RS1",1/100,100),("S1",1/100,100)],"US":[("CU",1/2,64)],"Lidar":[("CU",1/30,1500)],"RC":[("HU",1/100,100)]}
        for src, destinations in flows_config.items():
            for dst, rate, size in destinations:
                self.env.process(sender(src, dst, rate, size))
        self.env.process(receiver(bus))

class MockActiveBuilding:
    def __init__(self, env):
        self.env = env

    def setup_processes(self):
        def temp_sensor(thermostat_name):
            while True:
                p = Packet(PacketType.IOT_DATA, src="TempSensor", dst=thermostat_name, size=8)
                p.start_time = self.env.now
                logger.info(json.dumps({"event": "start_tx", **p.to_dict()}))
                yield self.env.timeout(5)

        def thermostat():
            while True:
                yield self.env.timeout(5.1)
                p = Packet(PacketType.IOT_DATA, src="Thermostat", dst="HVAC_Unit", size=4)
                p.start_time = self.env.now
                logger.info(json.dumps({"event": "start_tx", **p.to_dict()}))

        self.env.process(temp_sensor("Thermostat"))
        self.env.process(thermostat())

class Ether:
    """Represents the shared communication medium, the "Ether" from Metcalfe's paper."""
    def __init__(self, env, name="ether", bandwidth_bps=1e6, propagation_delay_s=5e-9, contention=True):
        self.env, self.name, self.bandwidth, self.prop_delay = env, name, bandwidth_bps, propagation_delay_s
        self.contention, self.transmitting_packets, self.log = contention, [], []

    def is_busy(self): return len(self.transmitting_packets) > 0

    def transmit(self, packet: Packet, source_node, all_nodes):
        return self._csma_cd_transmit(packet, source_node, all_nodes)

    def _csma_cd_transmit(self, packet: Packet, source_node, all_nodes):
        transmission_time = packet.bits() / self.bandwidth
        packet.start_time = self.env.now
        
        while self.is_busy():
            yield self.env.timeout(self.prop_delay / 10)
        
        self.transmitting_packets.append(packet)
        log_entry = {"time": self.env.now, "event": "start_tx", "chan": self.name, **packet.to_dict()}
        logger.info(json.dumps(log_entry)); self.log.append(log_entry)

        yield self.env.timeout(self.prop_delay)

        if self.contention and len(self.transmitting_packets) > 1:
            packet.success = False
            jam_packet = Packet(PacketType.JAM, src=source_node)
            logger.info(json.dumps({"time": self.env.now, "event": "jam_signal", "chan": self.name, **jam_packet.to_dict()}))
            yield self.env.timeout(self.prop_delay)
        else:
            # In the Daedalus model, with short, neighbor-to-neighbor links, it's common
            # for a packet to be "longer than the wire." This means the transmission
            # time can be less than the propagation delay. This logic correctly handles
            # that case by ensuring the timeout is never negative. This is the foundation
            # of our argument for why "reliability is almost free," as an acknowledgment can
            # be processed and returned before the sender has even finished transmitting.
            yield self.env.timeout(max(0, transmission_time - self.prop_delay))
            packet.success = True
            for node in all_nodes:
                if node != source_node: node.receive_packet(packet)
        
        if packet in self.transmitting_packets:
            self.transmitting_packets.remove(packet)
        packet.end_time = self.env.now
        end_log = {"time": self.env.now, "event": "end_tx", "chan": self.name, **packet.to_dict(), "latency": packet.end_time - packet.start_time}
        logger.info(json.dumps(end_log)); self.log.append(end_log)
        
        if hasattr(source_node, 'active_tx_proc') and source_node.active_tx_proc and not source_node.active_tx_proc.triggered:
            source_node.active_tx_proc.succeed(packet)

class Node:
    """Represents a station or a "Cell Agent," containing logic for TCP handshake and CSMA/CD."""
    def __init__(self, env, name, ether, all_nodes, peer=None, is_sender=False, data_size=5120):
        self.env, self.name, self.ether, self.all_nodes = env, name, ether, all_nodes
        self.peer = getattr(peer, 'name', peer)
        self.is_sender, self.data_size = is_sender, data_size
        self.state, self.send_una, self.next_seq, self.rcv_nxt, self.acked_data = "CLOSED", 0, 0, 0, set()
        self.backoff_attempts, self.active_tx_proc, self.inbox = 0, None, simpy.Store(env)
        self.action = env.process(self.run())

    def receive_packet(self, packet): self.inbox.put(packet)

    def send_with_backoff(self, packet):
        self.backoff_attempts = 0
        while self.backoff_attempts < 16:
            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            if result_packet.success: return result_packet
            
            self.backoff_attempts += 1
            k = min(self.backoff_attempts, 10)
            slot_time = 2 * self.ether.prop_delay
            backoff_duration = random.randint(0, (2**k) - 1) * slot_time
            logger.info(json.dumps({"time": self.env.now, "event": "backoff", "node": self.name, "attempts": self.backoff_attempts, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)
        packet.success = False
        return packet

    def run(self):
        if self.is_sender:
            self.state = "SYN_SENT"
            logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))
            yield self.env.process(self.send_with_backoff(Packet(PacketType.SYN, src=self, dst=self.peer, seq=self.next_seq)))
            self.next_seq += 1

        while self.state != "ESTABLISHED":
            pkt = yield self.inbox.get()
            if pkt.dst != self.name: continue

            if self.state == "CLOSED" and pkt.ptype == PacketType.SYN:
                self.state = "SYN_RCVD"
                self.rcv_nxt = pkt.seq + 1
                logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))
                yield self.env.process(self.send_with_backoff(Packet(PacketType.SYN_ACK, src=self, dst=pkt.src, seq=self.next_seq, ack=self.rcv_nxt)))
                self.next_seq += 1
            elif self.state == "SYN_SENT" and pkt.ptype == PacketType.SYN_ACK:
                self.state = "ESTABLISHED"
                self.rcv_nxt, self.send_una = pkt.seq + 1, pkt.ack
                logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))
                yield self.env.process(self.send_with_backoff(Packet(PacketType.ACK, src=self, dst=pkt.src, seq=self.next_seq, ack=self.rcv_nxt)))
            elif self.state == "SYN_RCVD" and pkt.ptype == PacketType.ACK and pkt.ack == self.next_seq:
                self.state = "ESTABLISHED"
                logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))

        if self.is_sender and self.data_size > 0:
            while self.send_una < self.data_size:
                data_pkt = Packet(PacketType.DATA, src=self, dst=self.peer, size=512, seq=self.next_seq)
                yield self.env.process(self.send_with_backoff(data_pkt))
                self.next_seq += data_pkt.size
                while self.send_una < self.next_seq:
                    ack_data = yield self.inbox.get()
                    if ack_data.dst == self.name and ack_data.ptype == PacketType.ACK: self.send_una = ack_data.ack
        else:
            while True:
                pkt = yield self.inbox.get()
                if pkt.dst == self.name and pkt.ptype == PacketType.DATA:
                    self.rcv_nxt = pkt.seq + pkt.size
                    ack_pkt = Packet(PacketType.ACK, src=self, dst=pkt.src, ack=self.rcv_nxt)
                    yield self.env.process(self.send_with_backoff(ack_pkt))

class MetcalfeNode:
    """A station operating on the classic Metcalfe half-duplex channel, implementing CSMA/CD."""
    def __init__(self, env, name, ether, all_nodes, peer=None, is_sender=False):
        self.env, self.name, self.ether, self.all_nodes = env, name, ether, all_nodes
        self.is_sender = is_sender
        self.peer = peer
        self.inbox = simpy.Store(env)
        self.active_tx_proc = None
        self.action = env.process(self.run())

    def receive_packet(self, packet):
        self.inbox.put(packet)

    def run(self):
        if self.is_sender:
            while True:
                yield self.env.timeout(random.expovariate(0.5))
                packet_to_send = Packet(PacketType.DATA, src=self, dst=self.peer)
                self.env.process(self.send_packet(packet_to_send))
        else:
            while True:
                received_packet = yield self.inbox.get()
                if received_packet.ptype == PacketType.DATA and received_packet.dst == self.name:
                    ack_packet = Packet(PacketType.ACK, src=self, dst=received_packet.src)
                    self.env.process(self.send_packet(ack_packet))

    def send_packet(self, packet):
        packet.collision_count = 0
        while packet.collision_count < 16:
            while self.ether.is_busy():
                yield self.env.timeout(self.ether.prop_delay / 10)
            
            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            
            if result_packet.success:
                return
            
            packet.collision_count += 1
            k = min(packet.collision_count, 10)
            slot_time = 2 * self.ether.prop_delay
            backoff_duration = random.randint(0, (2**k) - 1) * slot_time
            
            log_entry = {
                "time": self.env.now, "event": "backoff", "node": self.name, 
                "attempts": packet.collision_count, "delay": backoff_duration
            }
            logger.info(json.dumps(log_entry))
            yield self.env.timeout(backoff_duration)
            
        logger.info(json.dumps({"time": self.env.now, "event": "tx_abort", "node": self.name, "pkt_id": packet.id}))


class AlohaNode:
    """A simplified node for demonstrating ALOHA-family contention protocols."""
    def __init__(self, env, name, ether, all_nodes, arrival_rate, protocol_type):
        self.env, self.name, self.ether, self.all_nodes = env, name, ether, all_nodes
        self.arrival_rate, self.protocol_type = arrival_rate, protocol_type
        self.active_tx_proc = None
        self.action = env.process(self.run())

    def receive_packet(self, packet):
        pass

    def run(self):
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            packet_to_send = Packet(PacketType.DATA, src=self, dst=random.choice([n.name for n in self.all_nodes if n.name != self.name]))
            yield self.env.process(self.send_with_backoff(packet_to_send))
            
    def send_with_backoff(self, packet):
        attempts = 0
        while attempts < 16:
            if self.protocol_type == 'Slotted ALOHA':
                transmission_time = packet.bits() / self.ether.bandwidth
                slot_size = transmission_time + self.ether.prop_delay
                yield self.env.timeout(slot_size - (self.env.now % slot_size))
            elif self.protocol_type == 'CSMA/CD (ALOHA)':
                while self.ether.is_busy():
                    yield self.env.timeout(self.ether.prop_delay / 10)

            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            
            if result_packet.success: return
            
            attempts += 1
            packet.collision_count = attempts
            k = min(attempts, 10)
            slot_time = 2 * self.ether.prop_delay
            backoff_duration = random.randint(0, (2**k) - 1) * slot_time
            logger.info(json.dumps({"time": self.env.now, "event": "backoff", "node": self.name, "attempts": attempts, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)

# -----------------------------------------------------------------------------
# Simulation Orchestrator & UI Framework
# -----------------------------------------------------------------------------

def setup_and_run(env, protocol, **kwargs):
    """A unified function to set up and run different simulation scenarios."""
    
    nodes = []
    if protocol == "Fibre Channel (STRETCH)":
        bw = kwargs.get('bandwidth_bps', 10e9) 
        prop_delay = 5e-6 
        buffer_size = 20 
        num_pairs = kwargs['num_nodes'] // 2
        
        # In this model, the "CongestedLink" represents the Fibre Channel switch fabric.
        forward_fabric = CongestedLink(env, "FC_Forward_Fabric", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        reverse_fabric = CongestedLink(env, "FC_Reverse_Fabric", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        
        nodes_map = {}
        for i in range(num_pairs):
            sender = FibreChannelNode(env, f'S{i}', forward_fabric, reverse_fabric, is_sender=True, initial_credits=kwargs.get('data_size', 512*1024)//1024)
            receiver = FibreChannelNode(env, f'R{i}', reverse_fabric, forward_fabric)
            nodes_map[sender.name] = sender
            nodes_map[receiver.name] = receiver

        for i in range(num_pairs):
            sender_name, receiver_name = f'S{i}', f'R{i}'
            sender, receiver = nodes_map[sender_name], nodes_map[receiver_name]
            sender.peer_name = receiver_name
            receiver.peer_name = sender_name
            forward_fabric.receivers[receiver_name] = receiver
            reverse_fabric.receivers[sender_name] = sender
            
        env.process(forward_fabric.start_delivering())
        env.process(reverse_fabric.start_delivering())
        
        nodes = list(nodes_map.values())

    elif protocol == "Metcalfe Full-Duplex":
        bw = kwargs.get('bandwidth_bps', 10e9) 
        prop_delay = 5e-6 
        buffer_size = 20 
        num_pairs = kwargs['num_nodes'] // 2

        forward_link = CongestedLink(env, "ForwardChannel", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        reverse_link = CongestedLink(env, "ReverseChannel", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        
        nodes_map = {}
        for i in range(num_pairs):
            sender = TCPNode(env, f'S{i}', forward_link, reverse_link)
            receiver = TCPNode(env, f'R{i}', reverse_link, forward_link)
            nodes_map[sender.name] = sender
            nodes_map[receiver.name] = receiver

        for i in range(num_pairs):
            sender_name, receiver_name = f'S{i}', f'R{i}'
            sender, receiver = nodes_map[sender_name], nodes_map[receiver_name]
            sender.is_sender = True
            sender.peer_name = receiver_name
            sender.data_to_send = kwargs.get('data_size', 512*1024)
            receiver.peer_name = sender_name
            forward_link.receivers[receiver_name] = receiver
            reverse_link.receivers[sender_name] = sender
            
        env.process(forward_link.start_delivering())
        env.process(reverse_link.start_delivering())
        
        nodes = list(nodes_map.values())

    elif "ALOHA" in protocol:
        ether = Ether(env, name="aloha_ether", bandwidth_bps=kwargs['bandwidth_bps'], contention=True)
        nodes = [AlohaNode(env, name=chr(ord('A') + i), ether=ether, all_nodes=[], arrival_rate=kwargs['arrival_rate'], protocol_type=protocol) for i in range(kwargs['num_nodes'])]
        for node in nodes: node.all_nodes = nodes

    elif protocol == "Metcalfe Half-Duplex":
        ether = Ether(env, name="metcalfe_ether", bandwidth_bps=kwargs['bandwidth_bps'], propagation_delay_s=5e-7, contention=True)
        num_pairs = kwargs['num_nodes'] // 2
        for i in range(num_pairs):
            sender_name = f'S{i}'
            receiver_name = f'R{i}'
            sender = MetcalfeNode(env, sender_name, ether, [], peer=receiver_name, is_sender=True)
            receiver = MetcalfeNode(env, receiver_name, ether, [], peer=sender_name, is_sender=False)
            nodes.extend([sender, receiver])
        for node in nodes: node.all_nodes = nodes
    
    elif "Ethernet" in protocol or "Handshake" in protocol:
        bw, num_nodes = kwargs.get('bandwidth_bps', 1e6), kwargs.get('num_nodes', 2)
        prop_delay = 5e-7
        
        if protocol == "Full-Duplex Ethernet" or "FD" in protocol:
            ether_ab = Ether(env, "ether_A->B", bandwidth_bps=bw, contention=False)
            ether_ba = Ether(env, "ether_B->A", bandwidth_bps=bw, contention=False)
            node_B = Node(env, 'B', ether_ba, [], is_sender=False, data_size=kwargs.get('data_size', 5120))
            node_A = Node(env, 'A', ether_ab, [], peer='B', is_sender=True, data_size=kwargs.get('data_size', 5120))
            nodes = [node_A, node_B]
            node_A.all_nodes = nodes
            node_B.all_nodes = nodes
        else:
            contention = "no contention" not in protocol
            ether = Ether(env, name="shared_ether", bandwidth_bps=bw, propagation_delay_s=prop_delay, contention=contention)
            nodes = [Node(env, chr(ord('A') + i), ether, [], is_sender=(i==0), data_size=kwargs.get('data_size', 5120 if "Ethernet" in protocol else 0)) for i in range(num_nodes)]
            for i, node in enumerate(nodes):
                node.all_nodes = nodes
                possible_peers = [p for p in nodes if p != node]
                if possible_peers: node.peer = random.choice(possible_peers).name
    
    elif protocol == "Daedaelus Fabric":
        fabric = MockDaedaelusFabric(env, num_nodes=kwargs['num_nodes'])
        fabric.setup_processes()
    elif protocol == "Automotive TSN": 
        MockAutomotiveTSN(env).setup_processes()
    elif protocol == "Active Building": 
        MockActiveBuilding(env).setup_processes()
    
    if hasattr(env, 'root_tk'):
        env.root_tk.sim_nodes = nodes

    env.run(until=kwargs['duration'])


class SimulationFramework:
    def __init__(self, root):
        self.root, self.frames, self.nodes, self.is_animating = root, [], [], False
        self.root.title("Dædælus - Network Protocol Emulator")
        self.setup_ui()
        self.draw_network_layout()

    def setup_ui(self):
        mf = ttk.Frame(self.root, padding="10"); mf.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1); self.root.rowconfigure(0, weight=1)
        lf = ttk.LabelFrame(mf, text="Controls", padding="10"); lf.grid(row=0, column=0, sticky="w")
        ttk.Label(lf, text="Protocol:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        protocol_list = ["Fibre Channel (STRETCH)", "Metcalfe Full-Duplex", "Metcalfe Half-Duplex","TCP Handshake (HD, no contention)","TCP Handshake (HD, contention)","TCP Handshake (FD)","CSMA/CD (ALOHA)","Pure ALOHA","Slotted ALOHA","Half-Duplex Ethernet","Full-Duplex Ethernet","Daedaelus Fabric","Automotive TSN","Active Building"]
        self.proto = ttk.Combobox(lf, width=35, values=protocol_list, state="readonly")
        
        self.proto.current(0); self.proto.grid(row=0, column=1, sticky=tk.W)
        self.proto.bind("<<ComboboxSelected>>", self.draw_network_layout)
        self.entries = {}
        labels_and_defaults = {"Pkt Size":"1024","Bandwidth":"10e9","Arrival λ":"0.1","Sim Time":"5","Priorities":"1,1,1","Num Nodes":"8","Export Logs?":"True"}
        for i, (text, default_val) in enumerate(labels_and_defaults.items(), start=1):
            key = text.lower().split()[0].replace('?', '')
            ttk.Label(lf, text=f"{text}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(lf, width=15); entry.insert(0, default_val); entry.grid(row=i, column=1, sticky=tk.W)
            self.entries[key] = entry
        bf = ttk.Frame(lf); bf.grid(row=len(labels_and_defaults) + 1, column=0, columnspan=2, pady=10)
        self.start_btn = ttk.Button(bf, text="Start Simulation", command=self.start_sim); self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(bf, text="Stop Animation", command=self.stop_animation, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.export_btn = ttk.Button(bf, text="Export Animation", command=self.export_animation, state="disabled"); self.export_btn.pack(side=tk.LEFT, padx=5)
        self.status = ttk.Label(mf, text="Ready.", font=("Helvetica", 10, "bold")); self.status.grid(row=1, column=0, sticky="w", pady=5)
        self.canvas = tk.Canvas(mf, width=800, height=400, bg="#2E3440"); self.canvas.grid(row=2, column=0, sticky="nsew")
        mf.columnconfigure(0, weight=1); mf.rowconfigure(2, weight=1)

    def get_sim_params(self):
        return {
            "num_nodes": int(self.entries['num'].get()),
            "duration": float(self.entries['sim'].get()),
            "bandwidth_bps": float(self.entries['bandwidth'].get()),
            "data_size": int(self.entries['pkt'].get()),
            "arrival_rate": float(self.entries['arrival'].get()),
            "priorities": [int(p) for p in self.entries['priorities'].get().split(',')],
            "do_export": self.entries['export'].get().lower() in ("true","1","yes")
        }

    def draw_metcalfe_channel_layout(self):
        self.canvas.delete("all")
        self.nodes = []
        try:
            num_nodes_total = self.get_sim_params()['num_nodes']
        except (ValueError, KeyError):
            num_nodes_total = 24
            
        nodes_per_quadrant = max(1, num_nodes_total // 4)
        y_pos = {'tx_fwd': 100, 'rx_fwd': 150, 'tx_rev': 250, 'rx_rev': 300}
        quadrants = {
            'tx_fwd': {'y': y_pos['tx_fwd'], 'x_start': 50, 'x_end': 350, 'flow': 'right', 'labels': ("INFO SRC", "TRANSMITTER")},
            'rx_fwd': {'y': y_pos['rx_fwd'], 'x_start': 450, 'x_end': 750, 'flow': 'right', 'labels': ("RECEIVER", "DESTINATION")},
            'tx_rev': {'y': y_pos['tx_rev'], 'x_start': 750, 'x_end': 450, 'flow': 'left', 'labels': ("DESTINATION", "RECEIVER")},
            'rx_rev': {'y': y_pos['rx_rev'], 'x_start': 350, 'x_end': 50, 'flow': 'left', 'labels': ("TRANSMITTER", "INFO SRC")},
        }

        for quad_name, props in quadrants.items():
            for i in range(nodes_per_quadrant):
                prog = i / (nodes_per_quadrant - 1) if nodes_per_quadrant > 1 else 0.5
                x = props['x_start'] + (props['x_end'] - props['x_start']) * prog
                label = ""
                if i == 0: label = props['labels'][0]
                elif i == nodes_per_quadrant - 1: label = props['labels'][1]
                self.nodes.append({'name': f"{quad_name}_{i}", 'label': label, 'x': x, 'y': props['y'], 'quad': quad_name})

        for quad_name, props in quadrants.items():
            quad_nodes = sorted([n for n in self.nodes if n['quad'] == quad_name], key=lambda n: n['x'])
            if props['flow'] == 'left': quad_nodes.reverse()
            for i in range(len(quad_nodes) - 1):
                n1, n2 = quad_nodes[i], quad_nodes[i+1]
                self.canvas.create_line(n1['x'], n1['y'], n2['x'], n2['y'], arrow=tk.LAST, fill="#D8DEE9", width=1.5)

        for node in self.nodes:
                self.canvas.create_rectangle(node['x']-20, node['y']-10, node['x']+20, node['y']+10, fill="#434C5E", outline="#D8DEE9")
                if node['label']: self.canvas.create_text(node['x'], node['y'] + 20, text=node['label'], font=("Helvetica", 8, "italic"), fill="#ECEFF4")

        hub_x, hub_y, hub_gap = 400, 200, 10
        hub_tx_y, hub_rx_y = hub_y - hub_gap, hub_y + hub_gap
        self.canvas.create_rectangle(hub_x - 10, hub_tx_y - 5, hub_x + 10, hub_tx_y + 5, fill="#4C566A", outline="#D8DEE9")
        self.canvas.create_rectangle(hub_x - 10, hub_rx_y - 5, hub_x + 10, hub_rx_y + 5, fill="#4C566A", outline="#D8DEE9")
        self.canvas.create_line(hub_x, hub_tx_y, hub_x, hub_rx_y, fill="#D8DEE9", width=4)
        self.canvas.create_text(hub_x, hub_y + 35, text="ETHERNET", fill="#ECEFF4", font=("Helvetica", 9))
        self.canvas.create_line(quadrants['tx_fwd']['x_end'], quadrants['tx_fwd']['y'], hub_x, hub_tx_y, arrow=tk.LAST, fill="#BF616A")
        self.canvas.create_line(hub_x, hub_tx_y, quadrants['rx_fwd']['x_start'], quadrants['rx_fwd']['y'], arrow=tk.LAST, fill="#BF616A")
        self.canvas.create_line(quadrants['tx_rev']['x_end'], quadrants['tx_rev']['y'], hub_x, hub_rx_y, arrow=tk.LAST, fill="#A3BE8C")
        self.canvas.create_line(hub_x, hub_rx_y, quadrants['rx_rev']['x_start'], quadrants['rx_rev']['y'], arrow=tk.LAST, fill="#A3BE8C")
    
    def draw_full_duplex_layout(self, channel_text="Bandwidth-Multiplexed\nChannel"):
        """Draws the layout for full-duplex, centrally switched simulations."""
        self.canvas.delete("all")
        self.nodes = []
        try:
            num_pairs = self.get_sim_params()['num_nodes'] // 2
        except (ValueError, KeyError):
            num_pairs = 4

        y_step = 70
        canvas_height = self.canvas.winfo_height() or 400
        start_y = (canvas_height - (num_pairs - 1) * y_step) / 2
        left_x, right_x, channel_x = 150, 650, 400

        for i in range(num_pairs):
            y_pos = start_y + i * y_step
            s_name, r_name = f'S{i}', f'R{i}'
            self.nodes.append({'name': s_name, 'x': left_x, 'y': y_pos})
            self.nodes.append({'name': r_name, 'x': right_x, 'y': y_pos})
            self.canvas.create_rectangle(left_x-20, y_pos-15, left_x+20, y_pos+15, fill="#5E81AC", outline="#ECEFF4")
            self.canvas.create_text(left_x, y_pos, text=s_name, fill="#ECEFF4")
            self.canvas.create_rectangle(right_x-20, y_pos-15, right_x+20, y_pos+15, fill="#A3BE8C", outline="#ECEFF4")
            self.canvas.create_text(right_x, y_pos, text=r_name, fill="#2E3440")

        channel_height = (num_pairs) * y_step
        self.canvas.create_rectangle(channel_x-50, start_y-30, channel_x+50, start_y-30+channel_height, fill="#434C5E", outline="#D8DEE9")
        self.canvas.create_text(channel_x, start_y+(channel_height/2)-30, text=channel_text, fill="#ECEFF4", justify=tk.CENTER)
        
        for node in self.nodes:
            if node['name'].startswith('S'):
                self.canvas.create_line(node['x']+20, node['y'], channel_x-50, node['y'], arrow=tk.LAST, fill="#D8DEE9")
            else: # is a Receiver
                self.canvas.create_line(channel_x+50, node['y'], node['x']-20, node['y'], arrow=tk.LAST, fill="#D8DEE9")

    def draw_network_layout(self, event=None):
        proto = self.proto.get()
        if proto == "Metcalfe Half-Duplex":
            self.draw_metcalfe_channel_layout()
            return
        elif proto == "Metcalfe Full-Duplex":
            self.draw_full_duplex_layout()
            return
        elif proto == "Fibre Channel (STRETCH)":
            self.draw_full_duplex_layout(channel_text="Fibre Channel\nSwitch")
            return

        self.canvas.delete("all")
        self.nodes = []
        node_names = []
        
        try:
            num_nodes_param = self.get_sim_params()['num_nodes']
        except (ValueError, KeyError):
            num_nodes_param = 2

        if proto == "Daedaelus Fabric": node_names = [chr(ord('A') + i) for i in range(num_nodes_param)]
        elif proto == "Automotive TSN": node_names = ["CameraF", "ME", "US", "Lidar", "RC", "HU", "CU", "RS1", "S1"]
        elif proto == "Active Building": node_names = ["TempSensor", "Thermostat", "HVAC_Unit"]
        else: node_names = [chr(ord('A') + i) for i in range(num_nodes_param)]
        
        num_nd = len(node_names)
        is_bus = "Ethernet" in proto or "ALOHA" in proto
        cx, cy, rad = 400, 200, 150
        
        for i, name in enumerate(node_names):
            if is_bus:
                x, y = (100 + (600 / (num_nd - 1) * i if num_nd > 1 else 300)), cy
            else:
                angle = 2 * pi * i / num_nd - pi / 2
                x, y = cx + rad * cos(angle), cy + rad * sin(angle)
            self.nodes.append({'id': i, 'name': name, 'x': x, 'y': y})

        if "Daedaelus Fabric" in proto and len(self.nodes) > 1:
            for i in range(len(self.nodes)):
                node1 = self.nodes[i]
                node2 = self.nodes[(i + 1) % len(self.nodes)]
                self.canvas.create_line(node1['x'], node1['y'], node2['x'], node2['y'], fill="#B48EAD", width=3, tags="fabric_link")
        elif is_bus: self.canvas.create_line(100, cy, 700, cy, fill="#88C0D0", width=4, tags="ether_bus")
        
        for node in self.nodes:
            if is_bus: self.canvas.create_line(node['x'], node['y']-20, node['x'], cy, fill="#81A1C1", width=2)
            self.canvas.create_rectangle(node['x']-20, node['y']-20, node['x']+20, node['y']+20, fill="#4C566A", outline="#D8DEE9", width=2)
            self.canvas.create_text(node['x'], node['y'], text=node['name'], font=("Helvetica", 12, "bold"), fill="#ECEFF4")

    def start_sim(self):
        if self.is_animating: return
        self.stop_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        try:
            sim_params = self.get_sim_params()
        except (ValueError, KeyError) as e: 
            messagebox.showerror("Invalid Input", f"Please check parameters.\nError: {e}"); return
        
        self.draw_network_layout(); self.status.config(text="Running simulation..."); self.root.update()
        log_buffer.truncate(0); log_buffer.seek(0)
        
        env = simpy.Environment()
        env.root_tk = self 
        setup_and_run(env, self.proto.get(), **sim_params)
        
        logs = [json.loads(line) for line in log_buffer.getvalue().strip().splitlines() if "{" in line]
        self.status.config(text=f"Simulation complete. Animating {len(logs)} events..."); self.root.update()
        if logs: self.animate_log(logs)
        else: self.status.config(text=f"Simulation for '{self.proto.get()}' complete. No animation events.")

    def stop_animation(self):
        if not self.is_animating: return
        self.is_animating = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.config(text="Animation stopped by user.")
        self.canvas.delete("packet_anim")
        self.canvas.delete("packet_delivered")

    def animate_log(self, log):
        if not log: self.status.config(text="Animation complete."); return
        self.frames = []
        self.is_animating = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.export_btn.config(state="disabled")
        
        events = sorted(log, key=lambda e: e.get("time", 0))
        t_start, t_end = events[0].get("time", 0), events[-1].get("time", 0)
        duration = t_end - t_start or 1.0
        anim_total_duration_ms = 10000
        time_scale = anim_total_duration_ms / duration

        def _step(event_idx):
            if not self.is_animating or event_idx >= len(events):
                self.is_animating = False
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                if self.get_sim_params()['do_export'] and Image:
                    self.export_btn.config(state="normal")
                self.status.config(text="Animation finished."); return
            
            event = events[event_idx]
            
            src_node = next((n for n in self.nodes if n['name'] == event.get("src")), None)
            dst_node = next((n for n in self.nodes if n['name'] == event.get("dst")), None)

            delay_to_next_ms = 50
            if event_idx + 1 < len(events):
                delay_s = events[event_idx+1].get("time",0) - event.get("time",0)
                delay_to_next_ms = max(10, int(delay_s * time_scale))

            self.animate_packet_movement(event, src_node, dst_node, delay_to_next_ms)
            if Image: self.frames.append(self.capture_frame_as_image())
            self.root.after(delay_to_next_ms, lambda: _step(event_idx + 1))
        _step(0)

    def animate_packet_movement(self, event, src_node, dst_node, duration_ms):
        proto = self.proto.get()
        color = event.get('color', '#4C566A')
        if not event.get('success', True): color = '#BF616A'
        
        packet_size = 12
        pkt_obj = self.canvas.create_rectangle(0,0,0,0, fill=color, outline="#ECEFF4", tags="packet_anim")
        
        steps, step_delay = 20, max(1, duration_ms // 20)
        is_bus = "Ethernet" in proto or "ALOHA" in proto
        is_metcalfe_hd = proto == "Metcalfe Half-Duplex"
        is_full_duplex = proto in ["Metcalfe Full-Duplex", "Fibre Channel (STRETCH)"]

        def _move(step_num):
            if not self.is_animating or step_num > steps:
                self.canvas.delete(pkt_obj)
                if step_num > steps and event.get('success') and event.get('type') != 'JAM_SIGNAL' and dst_node:
                    if not (is_metcalfe_hd or is_full_duplex):
                        self.canvas.create_oval(dst_node['x']-4, dst_node['y']-4, dst_node['x']+4, dst_node['y']+4, fill=color, tags="packet_delivered", outline="")
                        self.root.after(200, lambda: self.canvas.delete("packet_delivered"))
                return

            prog = step_num / steps
            x_curr, y_curr = (src_node['x'], src_node['y']) if src_node else (0,0)
            
            if is_full_duplex and src_node and dst_node:
                channel_x = 400
                is_reverse = event.get('type') in ['ACK', 'CREDIT']
                
                # Senders are on the left, Receivers on the right.
                if src_node['x'] < channel_x: # Forward path S->R
                    if prog <= 0.5: # Animate from Sender to Channel
                        p = prog * 2
                        x_curr = src_node['x'] + (channel_x - 50 - src_node['x']) * p
                        y_curr = src_node['y']
                    else: # Animate from Channel to Receiver
                        p = (prog - 0.5) * 2
                        x_curr = (channel_x + 50) + (dst_node['x'] - (channel_x + 50)) * p
                        y_curr = dst_node['y']
                else: # Reverse path R->S
                    if prog <= 0.5: # Animate from Receiver to Channel
                        p = prog * 2
                        x_curr = src_node['x'] + (channel_x + 50 - src_node['x']) * p
                        y_curr = src_node['y']
                    else: # Animate from Channel to Sender
                        p = (prog - 0.5) * 2
                        x_curr = (channel_x - 50) + (dst_node['x'] - (channel_x - 50)) * p
                        y_curr = dst_node['y']

            elif is_metcalfe_hd:
                hub_x, hub_y = 400, 200
                is_ack = "ACK" in event.get('type', "")

                tx_path_start = next((n for n in self.nodes if (is_ack and n['quad']=='tx_rev' and n['label']=='DESTINATION') or (not is_ack and n['quad']=='tx_fwd' and n['label']=='INFO SRC')), None)
                rx_path_end = next((n for n in self.nodes if (is_ack and n['quad']=='rx_rev' and n['label']=='INFO SRC') or (not is_ack and n['quad']=='rx_fwd' and n['label']=='DESTINATION')), None)
                
                if not tx_path_start or not rx_path_end: 
                    self.canvas.delete(pkt_obj); return

                x_start, y_start = tx_path_start['x'], tx_path_start['y']
                x_mid, y_mid = hub_x, hub_y - (10 if not is_ack else -10)
                x_end, y_end = rx_path_end['x'], rx_path_end['y']

                if prog <= 0.5:
                    p = prog * 2
                    x_curr = x_start + (x_mid - x_start) * p
                    y_curr = y_start + (y_mid - y_start) * p
                else:
                    p = (prog - 0.5) * 2
                    x_curr = x_mid + (x_end - x_mid) * p
                    y_curr = y_mid + (y_end - y_mid) * p
            
            elif is_bus and src_node and dst_node:
                y_bus = src_node['y']
                x_start, y_start = src_node['x'], src_node['y']
                x_end, y_end = dst_node['x'], dst_node['y']
                
                if prog <= 0.2:
                    x_curr = x_start
                    y_curr = y_start - (y_start - y_bus) * (prog / 0.2)
                elif prog <= 0.8:
                    x_curr = x_start + (x_end - x_start) * ((prog - 0.2) / 0.6)
                    y_curr = y_bus
                else:
                    x_curr = x_end
                    y_curr = y_bus + (y_end - y_bus) * ((prog - 0.8) / 0.2)

            elif src_node and dst_node:
                x_start, y_start = src_node['x'], src_node['y']
                x_end, y_end = dst_node['x'], dst_node['y']
                x_curr, y_curr = x_start + (x_end - x_start) * prog, y_start + (y_end - y_start) * prog
            
            else: 
                self.canvas.delete(pkt_obj)
                return
            
            self.canvas.coords(pkt_obj, x_curr-packet_size/2, y_curr-packet_size/2, x_curr+packet_size/2, y_curr+packet_size/2)
            self.root.after(step_delay, lambda: _move(step_num + 1))
        _move(0)

    def capture_frame_as_image(self):
        ps = self.canvas.postscript(colormode='color')
        return Image.open(io.BytesIO(ps.encode('utf-8')))

    def export_animation(self):
        if not Image: messagebox.showerror("Error", "Pillow library not installed."); return
        if not self.frames: messagebox.showinfo("Export", "No animation frames to save."); return
        path = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF Animation', '*.gif')])
        if path:
            self.frames[0].save(path, save_all=True, append_images=self.frames[1:], optimize=False, duration=100, loop=0)
            messagebox.showinfo("Export", f"Animation exported to {path}")

def main():
    root = tk.Tk()
    root.sim_nodes = []
    SimulationFramework(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    except tk.TclError:
        print("Tkinter window closed.")