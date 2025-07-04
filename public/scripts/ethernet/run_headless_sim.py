#
# Dædælus: run_headless_sim.py
#
# This script represents the decoupled, headless simulation engine of the Dædælus
# Network Protocol Emulator. It is architected for automated, non-interactive
# execution environments like Replit, taking its parameters from the command line
# rather than a graphical interface.
#
# The primary output of this script is a verifiable, structured JSON log file—a
# self-contained proof of the simulation's execution, embodying the Dædælus
# principle of creating enduring, analyzable artifacts.
#

#!/usr/bin/env python3
import json
import logging
import uuid
import io
import os
import random
import enum
import simpy
from datetime import datetime
import re
import argparse
import sys

# Optional imports are handled gracefully, ensuring the core simulation can
# run even if visualization or external modules are not present.
try:
    import daedaelus_fabric_sim as fabric_sim
    import ethernet24 as tsn_mod
    import ethernet25 as building_mod
except ImportError:
    # This is not an error, but a designed state for a headless environment.
    fabric_sim = None
    tsn_mod = None
    building_mod = None


# -----------------------------------------------------------------------------
# Dædælus Philosophy: Comprehensive Logging for Verifiable Proof
#
# The logging system is architected to be a primary artifact of the simulation.
# Every significant event, state change, and decision is captured as a structured
# JSON object. This creates a rich, analyzable dataset, allowing the behavior
# of the entire system—from low-level link contention to high-level protocol
# handshakes—to be rigorously inspected and visualized. This is not merely
# for debugging; it is the raw data for our "Code as Proof."
# -----------------------------------------------------------------------------
LOG_DIRECTORY = "logs"
log_buffer = io.StringIO()  # A temporary buffer for each simulation run.

# Configure the root logger to write to our buffer.
# We will control the file output manually after each simulation.
logger = logging.getLogger("net_sim")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(log_buffer)
    # The formatter ensures each log entry is a raw, self-contained JSON string.
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Capture logs from other libraries (like simpy if it used logging)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)


def _sanitize_protocol_name(protocol_name: str) -> str:
    """Converts a protocol name into a valid directory name."""
    s = protocol_name.lower()
    # Replace spaces and punctuation with underscores
    s = re.sub(r'[\s\(\),]+', '_', s)
    # Remove any remaining invalid characters
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = s.strip('_')
    return s


def export_logs_to_file(protocol_name: str):
    """
    Writes the entire logging buffer to a structured, protocol-specific JSON file.
    This function embodies the principle of producing verifiable artifacts from
    our simulations. Each log file is a self-contained proof of a single run.
    """
    # Create the main logs directory if it doesn't exist
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # Create the protocol-specific subdirectory
    protocol_dir = os.path.join(
        LOG_DIRECTORY, _sanitize_protocol_name(protocol_name))
    os.makedirs(protocol_dir, exist_ok=True)

    # Generate a unique, timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"log_{timestamp}.json"
    log_path = os.path.join(protocol_dir, log_filename)

    raw_content = log_buffer.getvalue()
    raw_lines = raw_content.strip().splitlines()
    records = []
    for line in raw_lines:
        try:
            # Dædælus: A robust parser that handles log prefixes.
            # We find the beginning of the JSON object ('{') and parse from there,
            # ignoring any timestamp or log-level prefixes that cause decoding errors.
            json_start_index = line.find('{')
            if json_start_index != -1:
                json_str = line[json_start_index:]
                records.append(json.loads(json_str))
        except json.JSONDecodeError:
            # This is a critical check for data integrity. If a log line is malformed,
            # it indicates a bug in the serialization of an event and must be noted.
            print(
                f"Warning: Skipping malformed log line during export: {line}", file=sys.stderr)

    try:
        with open(log_path, 'w') as f:
            json.dump(records, f, indent=2)

        # Log the export event itself to the console for user feedback.
        # This confirms the creation of the verifiable artifact.
        export_event_log = {
            "event": "export_logs_success",
            "protocol": protocol_name,
            "path": log_path,
            "records_exported": len(records)
        }
        print(json.dumps(export_event_log))
        return log_path
    except IOError as e:
        print(f"Error exporting logs to {log_path}: {e}", file=sys.stderr)
        return None

# -----------------------------------------------------------------------------
# Core Networking Primitives & Enums
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
    CREDIT = "CREDIT"


class Packet:
    def __init__(self, ptype: PacketType, src=None, dst=None, size=64, seq=0, ack=0, credit_val=0):
        self.id, self.ptype = str(uuid.uuid4()), ptype
        self.src = getattr(src, 'name', src)
        self.dst = getattr(dst, 'name', dst)
        self.size, self.seq, self.ack = size, seq, ack
        self.credit_val = credit_val
        self.success, self.collision_count = True, 0
        self.color = {
            "SYN": "#00BFFF", "SYN_ACK": "#00FFFF", "ACK": "#32CD32",
            "DATA": "#FFD700", "JAM": "#FF0000", "LIVENESS_TOKEN": "#FF00FF",
            "TSN_MSG": "#FFA500", "IOT_DATA": "#98FB98", "CREDIT": "#D8BFD8"
        }.get(ptype.value, "#FFFFFF")

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

    def __repr__(
        self): return f"<{self.ptype.value} id={self.id[:4]} src={self.src}->dst={self.dst}>"

# -----------------------------------------------------------------------------
# Protocol-Specific Class Definitions
# -----------------------------------------------------------------------------


class CongestedLink:
    def __init__(self, env, name, buffer_capacity=20, prop_delay=1e-6, bandwidth_bps=10e9):
        self.env = env
        self.name = name
        self.buffer = simpy.Store(env, capacity=buffer_capacity)
        self.prop_delay = prop_delay
        self.bandwidth = bandwidth_bps
        self.packets_dropped = 0
        self.receivers = {}
        self.total_bytes_transferred = 0
        logger.info(json.dumps({
            "time": self.env.now, "event": "component_init", "type": "CongestedLink", "name": self.name,
            "params": {"buffer_capacity": buffer_capacity, "prop_delay": prop_delay, "bandwidth_bps": bandwidth_bps}
        }))

    def put(self, packet):
        if len(self.buffer.items) < self.buffer.capacity:
            logger.info(json.dumps({
                "time": self.env.now, "event": "buffer_enq", "chan": self.name,
                "buffer_occupancy": len(self.buffer.items), **packet.to_dict()
            }))
            return self.buffer.put(packet)
        else:
            self.packets_dropped += 1
            packet.success = False
            logger.info(json.dumps({
                "time": self.env.now, "event": "pkt_drop", "chan": self.name,
                "reason": "buffer_full", "buffer_occupancy": len(self.buffer.items),
                **packet.to_dict()
            }))
            return self.env.timeout(0)

    def start_delivering(self):
        while True:
            packet = yield self.buffer.get()
            logger.info(json.dumps({
                "time": self.env.now, "event": "buffer_deq", "chan": self.name,
                "buffer_occupancy": len(self.buffer.items), **packet.to_dict()
            }))
            receiver_node = self.receivers.get(packet.dst)
            if receiver_node:
                self.env.process(self.deliver(packet, receiver_node))
            else:
                logger.info(json.dumps({"time": self.env.now, "event": "pkt_drop",
                            "chan": self.name, "reason": "no_receiver", **packet.to_dict()}))

    def deliver(self, packet, receiver_node):
        transmission_time = packet.bits() / self.bandwidth
        yield self.env.timeout(transmission_time)
        yield self.env.timeout(self.prop_delay)
        if packet.ptype == PacketType.DATA and packet.success:
            self.total_bytes_transferred += packet.size
        receiver_node.receive_packet(packet)


class TCPNode:
    def __init__(self, env, name, forward_link, reverse_link, peer=None, is_sender=False, data_size=1024*100):
        self.env, self.name, self.peer_name, self.is_sender, self.data_to_send = env, name, getattr(
            peer, 'name', peer), is_sender, data_size
        self.forward_link, self.reverse_link = forward_link, reverse_link
        self.state, self.next_seq, self.send_base, self.rcv_next = "CLOSED", 0, 0, 0
        self.mss, self.cwnd, self.ssthresh, self.rto, self.dupacks = 1024, 1.0, 64, 0.1, 0
        self.inbox = simpy.Store(env)
        self.action = env.process(self.run())
        logger.info(json.dumps({
            "time": self.env.now, "event": "component_init", "type": "TCPNode", "name": self.name,
            "params": {"peer": self.peer_name, "is_sender": is_sender, "data_size": data_size}
        }))

    def receive_packet(self, packet): self.inbox.put(packet)

    def handle_congestion_event(self, reason):
        old_cwnd, old_ssthresh = self.cwnd, self.ssthresh
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd, self.next_seq, self.dupacks = 1.0, self.send_base, 0
        logger.info(json.dumps({
            "time": self.env.now, "event": "congestion_event", "node": self.name, "reason": reason,
            "old_cwnd": round(old_cwnd, 2), "new_cwnd": round(self.cwnd, 2),
            "old_ssthresh": round(old_ssthresh, 2), "new_ssthresh": round(self.ssthresh, 2)
        }))

    def run(self):
        self.state = "ESTABLISHED"
        logger.info(json.dumps({"time": self.env.now, "event": "state_change",
                    "node": self.name, "old_state": "CLOSED", "new_state": self.state}))
        if self.is_sender:
            procs = [self.env.process(self.transmit_data()), self.env.process(
                self.receive_acks()), self.env.process(self.retransmit_timer())]
            yield simpy.AllOf(self.env, procs)
        else:
            yield self.env.process(self.receive_data())

    def retransmit_timer(self):
        try:
            while self.send_base < self.data_to_send:
                yield self.env.timeout(self.rto)
                if self.next_seq > self.send_base:
                    logger.info(json.dumps({"time": self.env.now, "event": "rto_fired",
                                "node": self.name, "send_base": self.send_base, "next_seq": self.next_seq}))
                    self.handle_congestion_event("timeout")
        except simpy.Interrupt:
            pass

    def transmit_data(self):
        while self.send_base < self.data_to_send:
            while self.next_seq < self.send_base + (self.cwnd * self.mss):
                if self.next_seq >= self.data_to_send:
                    break
                packet = Packet(PacketType.DATA, src=self.name,
                                dst=self.peer_name, size=self.mss, seq=self.next_seq)
                packet.start_time = self.env.now
                logger.info(json.dumps(
                    {"event": "start_tx", "node": self.name, **packet.to_dict(), "cwnd": round(self.cwnd, 2)}))
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
                        bytes_acked, self.send_base, self.dupacks, old_cwnd = ack_pkt.ack - \
                            self.send_base, ack_pkt.ack, 0, self.cwnd
                        pkts_acked = bytes_acked / self.mss
                        log_reason = "slow_start" if self.cwnd < self.ssthresh else "congestion_avoidance"
                        self.cwnd += (pkts_acked if self.cwnd <
                                      self.ssthresh else pkts_acked / self.cwnd)
                        logger.info(json.dumps({"time": self.env.now, "event": "cwnd_increase", "node": self.name,
                                    "reason": log_reason, "old_cwnd": round(old_cwnd, 2), "new_cwnd": round(self.cwnd, 2)}))
                    elif ack_pkt.ack == last_ack_seq:
                        self.dupacks += 1
                        if self.dupacks == 3:
                            self.handle_congestion_event("triple_dup_ack")
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
                        ack = Packet(PacketType.ACK, src=self.name,
                                     dst=data_pkt.src, ack=expected_seq)
                        ack.start_time = self.env.now
                        yield self.reverse_link.put(ack)
        except simpy.Interrupt:
            pass


class FibreChannelNode:
    def __init__(self, env, name, forward_link, reverse_link, peer=None, is_sender=False, initial_credits=10, data_size=1024*100):
        self.env, self.name, self.peer_name, self.is_sender = env, name, getattr(
            peer, 'name', peer), is_sender
        self.data_to_send, self.forward_link, self.reverse_link = data_size, forward_link, reverse_link
        self.credits, self.next_seq, self.send_base = initial_credits if is_sender else 0, 0, 0
        self.inbox = simpy.Store(env)
        self.action = env.process(self.run())
        logger.info(json.dumps({
            "time": self.env.now, "event": "component_init", "type": "FibreChannelNode", "name": self.name,
            "params": {"peer": self.peer_name, "is_sender": is_sender, "initial_credits": initial_credits, "data_size": data_size}
        }))

    def receive_packet(self, packet): self.inbox.put(packet)

    def run(self):
        if self.is_sender:
            procs = [self.env.process(self.transmit_data()), self.env.process(
                self.receive_credits())]
            yield simpy.AllOf(self.env, procs)
        else:
            yield self.env.process(self.receive_data_and_grant_credits())

    def transmit_data(self):
        while self.send_base < self.data_to_send:
            if self.credits > 0:
                self.credits -= 1
                packet = Packet(PacketType.DATA, src=self.name,
                                dst=self.peer_name, size=1024, seq=self.next_seq)
                packet.start_time = self.env.now
                logger.info(json.dumps(
                    {"event": "start_tx", "node": self.name, "credits_rem": self.credits, **packet.to_dict()}))
                yield self.forward_link.put(packet)
                self.next_seq += packet.size
            else:
                logger.info(json.dumps({"time": self.env.now, "event": "credit_stall",
                            "node": self.name, "reason": "no_credits_available"}))
                yield self.env.timeout(0.0001)

    def receive_credits(self):
        try:
            while True:
                credit_pkt = yield self.inbox.get()
                if credit_pkt.ptype == PacketType.CREDIT and credit_pkt.dst == self.name:
                    self.credits += credit_pkt.credit_val
                    logger.info(json.dumps({"time": self.env.now, "event": "credit_received", "node": self.name,
                                "credits_added": credit_pkt.credit_val, "new_total_credits": self.credits, **credit_pkt.to_dict()}))
                    self.send_base = credit_pkt.ack
        except simpy.Interrupt:
            pass

    def receive_data_and_grant_credits(self):
        while True:
            data_pkt = yield self.inbox.get()
            if data_pkt.ptype == PacketType.DATA and data_pkt.dst == self.name:
                yield self.env.timeout(0.00005)
                credit_packet = Packet(PacketType.CREDIT, src=self.name,
                                       dst=data_pkt.src, credit_val=1, ack=data_pkt.seq + data_pkt.size)
                credit_packet.start_time = self.env.now
                logger.info(json.dumps(
                    {"event": "grant_credit", "node": self.name, **credit_packet.to_dict()}))
                yield self.reverse_link.put(credit_packet)


class MockDaedaelusFabric:
    def __init__(self, env, num_nodes=2):
        self.env, self.num_nodes = env, num_nodes
        logger.info(json.dumps({"time": self.env.now, "event": "component_init",
                    "type": "DaedaelusFabric", "params": {"num_nodes": num_nodes}}))

    def setup_processes(self):
        def link_formation(node1_name, node2_name):
            p1 = Packet(PacketType.LIVENESS_TOKEN,
                        src=node1_name, dst=node2_name)
            p1.start_time = self.env.now
            logger.info(json.dumps(
                {"event": "start_tx", "protocol": "Daedaelus Fabric", "tx_type": "liveness_probe", **p1.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))
            p2 = Packet(PacketType.LIVENESS_TOKEN,
                        src=node2_name, dst=node1_name)
            p2.start_time = self.env.now
            logger.info(json.dumps(
                {"event": "start_tx", "protocol": "Daedaelus Fabric", "tx_type": "liveness_response", **p2.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))
            p3 = Packet(PacketType.ACK, src=node1_name, dst=node2_name)
            p3.start_time = self.env.now
            logger.info(json.dumps(
                {"event": "start_tx", "protocol": "Daedaelus Fabric", "tx_type": "liveness_confirm", **p3.to_dict()}))
            yield self.env.timeout(random.uniform(0.8, 1.2))
            logger.info(json.dumps({"time": self.env.now, "event": "link_established",
                        "protocol": "Daedaelus Fabric", "nodes": [node1_name, node2_name]}))
        node_names = [chr(ord('A') + i) for i in range(self.num_nodes)]
        if node_names:
            for i in range(self.num_nodes):
                self.env.process(link_formation(
                    node_names[i], node_names[(i + 1) % self.num_nodes]))


class MockAutomotiveTSN:
    def __init__(self, env):
        self.env = env
        logger.info(json.dumps(
            {"time": self.env.now, "event": "component_init", "type": "AutomotiveTSN"}))

    def setup_processes(self):
        bus = simpy.Store(self.env)

        def sender(source, dest, period, size):
            while True:
                yield self.env.timeout(period)
                p = Packet(PacketType.TSN_MSG, src=source, dst=dest, size=size)
                p.start_time = self.env.now
                bus.put(p)
                logger.info(json.dumps(
                    {"event": "start_tx", "protocol": "Automotive TSN", **p.to_dict()}))

        def receiver(bus, propagation_delay=0.0001):
            while True:
                p = yield bus.get()
                yield self.env.timeout(propagation_delay)
                p.success = True
                logger.info(json.dumps(
                    {"event": "end_tx", "protocol": "Automotive TSN", **p.to_dict()}))
        flows_config = {"CameraF": [("HU", 1/60, 1500)], "ME": [("RS1", 1/100, 100), ("S1", 1/100, 100)], "US": [
            ("CU", 1/2, 64)], "Lidar": [("CU", 1/30, 1500)], "RC": [("HU", 1/100, 100)]}
        for src, destinations in flows_config.items():
            for dst, rate, size in destinations:
                self.env.process(sender(src, dst, rate, size))
        self.env.process(receiver(bus))


class MockActiveBuilding:
    def __init__(self, env):
        self.env = env
        logger.info(json.dumps(
            {"time": self.env.now, "event": "component_init", "type": "ActiveBuilding"}))

    def setup_processes(self):
        def temp_sensor(thermostat_name):
            while True:
                p = Packet(PacketType.IOT_DATA, src="TempSensor",
                           dst=thermostat_name, size=8)
                p.start_time = self.env.now
                logger.info(json.dumps(
                    {"event": "start_tx", "protocol": "Active Building", **p.to_dict()}))
                yield self.env.timeout(5)

        def thermostat():
            while True:
                yield self.env.timeout(5.1)
                p = Packet(PacketType.IOT_DATA, src="Thermostat",
                           dst="HVAC_Unit", size=4)
                p.start_time = self.env.now
                logger.info(json.dumps(
                    {"event": "start_tx", "protocol": "Active Building", **p.to_dict()}))
        self.env.process(temp_sensor("Thermostat"))
        self.env.process(thermostat())


class Ether:
    def __init__(self, env, name="ether", bandwidth_bps=1e6, propagation_delay_s=5e-9, contention=True):
        self.env, self.name, self.bandwidth, self.prop_delay = env, name, bandwidth_bps, propagation_delay_s
        self.contention, self.transmitting_packets = contention, []
        logger.info(json.dumps({
            "time": self.env.now, "event": "component_init", "type": "Ether", "name": self.name,
            "params": {"bandwidth_bps": bandwidth_bps, "propagation_delay_s": propagation_delay_s, "contention": contention}
        }))

    def is_busy(self): return len(self.transmitting_packets) > 0

    def transmit(self, packet: Packet, source_node, all_nodes):
        transmission_time = packet.bits() / self.bandwidth
        packet.start_time = self.env.now
        if self.is_busy():
            logger.info(json.dumps(
                {"time": self.env.now, "event": "carrier_sense_defer", "chan": self.name, "node": source_node.name}))
            while self.is_busy():
                yield self.env.timeout(self.prop_delay / 10)
        self.transmitting_packets.append(packet)
        logger.info(json.dumps(
            {"time": self.env.now, "event": "start_tx", "chan": self.name, **packet.to_dict()}))
        yield self.env.timeout(self.prop_delay)
        if self.contention and len(self.transmitting_packets) > 1:
            packet.success = False
            logger.info(json.dumps({
                "time": self.env.now, "event": "collision_detected", "chan": self.name,
                "jamming_node": source_node.name, "colliding_packets": [p.id for p in self.transmitting_packets]
            }))
            yield self.env.timeout(self.prop_delay)
        else:
            yield self.env.timeout(max(0, transmission_time - self.prop_delay))
            packet.success = True
            for node in all_nodes:
                if node != source_node:
                    node.receive_packet(packet)
        if packet in self.transmitting_packets:
            self.transmitting_packets.remove(packet)
        packet.end_time = self.env.now
        logger.info(json.dumps({"time": self.env.now, "event": "end_tx", "chan": self.name,
                    **packet.to_dict(), "latency": packet.end_time - packet.start_time}))
        # In the original test_ethernet.py, this was inside an if-statement.
        # It has been moved out to ensure the sending process is always notified,
        # which is a more robust architectural pattern.
        if hasattr(source_node, 'active_tx_proc') and source_node.active_tx_proc and not source_node.active_tx_proc.triggered:
            source_node.active_tx_proc.succeed(packet)


class Node:
    def __init__(self, env, name, ether, all_nodes, peer=None, is_sender=False, data_size=5120):
        self.env, self.name, self.ether, self.all_nodes = env, name, ether, all_nodes
        self.peer, self.is_sender, self.data_size = getattr(
            peer, 'name', peer), is_sender, data_size
        self.state, self.send_una, self.next_seq, self.rcv_nxt = "CLOSED", 0, 0, 0
        self.backoff_attempts, self.active_tx_proc, self.inbox = 0, None, simpy.Store(
            env)
        self.action = env.process(self.run())
        logger.info(json.dumps({
            "time": self.env.now, "event": "component_init", "type": "Node", "name": self.name,
            "params": {"peer": self.peer, "is_sender": is_sender, "data_size": data_size}
        }))

    def receive_packet(self, packet): self.inbox.put(packet)

    def send_with_backoff(self, packet):
        self.backoff_attempts = 0
        while self.backoff_attempts < 16:
            self.active_tx_proc = self.env.event()
            # The transmit process is now owned by the Ether object, which is cleaner.
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            if result_packet.success:
                return result_packet

            self.backoff_attempts += 1
            k = min(self.backoff_attempts, 10)
            slot_time = 2 * self.ether.prop_delay
            backoff_duration = random.randint(0, (2**k) - 1) * slot_time
            logger.info(json.dumps({"time": self.env.now, "event": "backoff", "node": self.name,
                        "attempts": self.backoff_attempts, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)

        packet.success = False
        return packet

    def run(self):
        # Simplified TCP-like handshake
        if self.is_sender:
            self.state = "SYN_SENT"
            logger.info(json.dumps({"time": self.env.now, "event": "state_change",
                        "node": self.name, "old_state": "CLOSED", "new_state": self.state}))
            yield self.env.process(self.send_with_backoff(Packet(PacketType.SYN, src=self.name, dst=self.peer, seq=self.next_seq)))
            self.next_seq += 1

        while self.state != "ESTABLISHED":
            pkt = yield self.inbox.get()
            if pkt.dst != self.name:
                continue

            old_state = self.state
            if self.state == "CLOSED" and pkt.ptype == PacketType.SYN:
                self.state = "SYN_RCVD"
                self.rcv_nxt = pkt.seq + 1
                yield self.env.process(self.send_with_backoff(Packet(PacketType.SYN_ACK, src=self.name, dst=pkt.src, seq=self.next_seq, ack=self.rcv_nxt)))
                self.next_seq += 1
            elif self.state == "SYN_SENT" and pkt.ptype == PacketType.SYN_ACK:
                self.state = "ESTABLISHED"
                self.rcv_nxt, self.send_una = pkt.seq + 1, pkt.ack
                yield self.env.process(self.send_with_backoff(Packet(PacketType.ACK, src=self.name, dst=pkt.src, seq=self.next_seq, ack=self.rcv_nxt)))
            elif self.state == "SYN_RCVD" and pkt.ptype == PacketType.ACK and pkt.ack == self.next_seq:
                self.state = "ESTABLISHED"

            if old_state != self.state:
                logger.info(json.dumps({"time": self.env.now, "event": "state_change",
                            "node": self.name, "old_state": old_state, "new_state": self.state}))

        # Simplified data transfer
        if self.is_sender and self.data_size > 0:
            while self.send_una < self.data_size:
                data_pkt = Packet(PacketType.DATA, src=self.name,
                                  dst=self.peer, size=512, seq=self.next_seq)
                yield self.env.process(self.send_with_backoff(data_pkt))
                self.next_seq += data_pkt.size

                # Wait for the corresponding ACK
                ack_data = yield self.inbox.get()
                if ack_data.dst == self.name and ack_data.ptype == PacketType.ACK:
                    self.send_una = ack_data.ack
        else:  # Receiver
            while True:
                pkt = yield self.inbox.get()
                if pkt.dst == self.name and pkt.ptype == PacketType.DATA:
                    self.rcv_nxt = pkt.seq + pkt.size
                    ack_pkt = Packet(PacketType.ACK, src=self.name,
                                     dst=pkt.src, ack=self.rcv_nxt)
                    yield self.env.process(self.send_with_backoff(ack_pkt))


class MetcalfeNode:
    def __init__(self, env, name, ether, all_nodes, peer=None, is_sender=False):
        self.env, self.name, self.ether, self.all_nodes, self.is_sender, self.peer = env, name, ether, all_nodes, is_sender, peer
        self.inbox, self.active_tx_proc = simpy.Store(env), None
        self.action = env.process(self.run())
        logger.info(json.dumps({"time": self.env.now, "event": "component_init", "type": "MetcalfeNode",
                    "name": self.name, "params": {"peer": getattr(peer, 'name', peer), "is_sender": is_sender}}))

    def receive_packet(self, packet): self.inbox.put(packet)

    def run(self):
        if self.is_sender:
            while True:
                yield self.env.timeout(random.expovariate(0.5))
                self.env.process(self.send_packet(
                    Packet(PacketType.DATA, src=self.name, dst=self.peer)))
        else:  # Receiver
            while True:
                received_packet = yield self.inbox.get()
                if received_packet.ptype == PacketType.DATA and received_packet.dst == self.name:
                    self.env.process(self.send_packet(
                        Packet(PacketType.ACK, src=self.name, dst=received_packet.src)))

    def send_packet(self, packet):
        packet.collision_count = 0
        while packet.collision_count < 16:
            if self.ether.is_busy():
                while self.ether.is_busy():
                    yield self.env.timeout(self.ether.prop_delay / 10)

            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc

            if result_packet.success:
                return

            packet.collision_count += 1
            k = min(packet.collision_count, 10)
            backoff_duration = random.randint(
                0, (2**k) - 1) * (2 * self.ether.prop_delay)
            logger.info(json.dumps({"time": self.env.now, "event": "backoff", "node": self.name,
                        "reason": "collision", "attempts": packet.collision_count, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)

        logger.info(json.dumps({"time": self.env.now, "event": "tx_abort",
                    "node": self.name, "reason": "max_retries_exceeded", "pkt_id": packet.id}))


class AlohaNode:
    def __init__(self, env, name, ether, all_nodes, arrival_rate, protocol_type):
        self.env, self.name, self.ether, self.all_nodes, self.arrival_rate, self.protocol_type = env, name, ether, all_nodes, arrival_rate, protocol_type
        self.active_tx_proc = None
        self.action = env.process(self.run())
        logger.info(json.dumps({"time": self.env.now, "event": "component_init", "type": "AlohaNode",
                    "name": self.name, "params": {"arrival_rate": arrival_rate, "protocol": protocol_type}}))

    def receive_packet(self, packet): pass

    def run(self):
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            yield self.env.process(self.send_with_backoff(Packet(PacketType.DATA, src=self.name, dst=random.choice([n.name for n in self.all_nodes if n.name != self.name]))))

    def send_with_backoff(self, packet):
        attempts = 0
        while attempts < 16:
            if self.protocol_type == 'Slotted ALOHA':
                slot_size = (packet.bits() / self.ether.bandwidth) + \
                    self.ether.prop_delay
                yield self.env.timeout(slot_size - (self.env.now % slot_size))
            elif self.protocol_type == 'CSMA/CD (ALOHA)':
                if self.ether.is_busy():
                    while self.ether.is_busy():
                        yield self.env.timeout(self.ether.prop_delay / 10)

            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc

            if result_packet.success:
                return

            attempts += 1
            packet.collision_count = attempts
            k = min(attempts, 10)
            backoff_duration = random.randint(
                0, (2**k) - 1) * (2 * self.ether.prop_delay)
            logger.info(json.dumps({"time": self.env.now, "event": "backoff",
                        "node": self.name, "attempts": attempts, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)


# -----------------------------------------------------------------------------
# Simulation Orchestration Logic
# -----------------------------------------------------------------------------
def setup_and_run(env, protocol, **kwargs):
    """A unified function to set up and run different simulation scenarios."""
    logger.info(json.dumps(
        {"time": env.now, "event": "simulation_start", "protocol": protocol, "params": kwargs}))
    nodes = []
    if protocol == "Fibre Channel (STRETCH)":
        bw, prop_delay, buffer_size, num_pairs = kwargs.get(
            'bandwidth_bps', 10e9), 5e-6, 20, kwargs['num_nodes'] // 2
        forward_fabric = CongestedLink(
            env, "FC_Forward_Fabric", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        reverse_fabric = CongestedLink(
            env, "FC_Reverse_Fabric", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        nodes_map = {f'S{i}': FibreChannelNode(env, f'S{i}', forward_fabric, reverse_fabric, is_sender=True, initial_credits=kwargs.get(
            'data_size', 512*1024)//1024) for i in range(num_pairs)}
        nodes_map.update({f'R{i}': FibreChannelNode(
            env, f'R{i}', reverse_fabric, forward_fabric) for i in range(num_pairs)})
        for i in range(num_pairs):
            sender, receiver = nodes_map[f'S{i}'], nodes_map[f'R{i}']
            sender.peer_name, receiver.peer_name = receiver.name, sender.name
            forward_fabric.receivers[receiver.name], reverse_fabric.receivers[sender.name] = receiver, sender
        env.process(forward_fabric.start_delivering())
        env.process(reverse_fabric.start_delivering())
        nodes = list(nodes_map.values())
    elif protocol == "Metcalfe Full-Duplex":
        bw, prop_delay, buffer_size, num_pairs = kwargs.get(
            'bandwidth_bps', 10e9), 5e-6, 20, kwargs['num_nodes'] // 2
        forward_link = CongestedLink(
            env, "ForwardChannel", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        reverse_link = CongestedLink(
            env, "ReverseChannel", buffer_capacity=buffer_size, prop_delay=prop_delay, bandwidth_bps=bw)
        nodes_map = {f'S{i}': TCPNode(env, f'S{i}', forward_link, reverse_link, is_sender=True, data_size=kwargs.get(
            'data_size', 512*1024)) for i in range(num_pairs)}
        nodes_map.update({f'R{i}': TCPNode(
            env, f'R{i}', reverse_link, forward_link) for i in range(num_pairs)})
        for i in range(num_pairs):
            sender, receiver = nodes_map[f'S{i}'], nodes_map[f'R{i}']
            sender.peer_name, receiver.peer_name = receiver.name, sender.name
            forward_link.receivers[receiver.name], reverse_link.receivers[sender.name] = receiver, sender
        env.process(forward_link.start_delivering())
        env.process(reverse_link.start_delivering())
        nodes = list(nodes_map.values())
    elif "ALOHA" in protocol:
        ether = Ether(env, name="aloha_ether",
                      bandwidth_bps=kwargs['bandwidth_bps'], contention=True)
        nodes = [AlohaNode(env, name=chr(ord('A') + i), ether=ether, all_nodes=[],
                           arrival_rate=kwargs['arrival_rate'], protocol_type=protocol) for i in range(kwargs['num_nodes'])]
        for node in nodes:
            node.all_nodes = nodes
    elif protocol == "Metcalfe Half-Duplex":
        ether = Ether(env, name="metcalfe_ether",
                      bandwidth_bps=kwargs['bandwidth_bps'], propagation_delay_s=5e-7, contention=True)
        for i in range(kwargs['num_nodes'] // 2):
            sender = MetcalfeNode(
                env, f'S{i}', ether, [], peer=f'R{i}', is_sender=True)
            receiver = MetcalfeNode(
                env, f'R{i}', ether, [], peer=f'S{i}', is_sender=False)
            nodes.extend([sender, receiver])
        for node in nodes:
            node.all_nodes = nodes
    elif "Ethernet" in protocol or "Handshake" in protocol:
        bw, num_nodes, prop_delay = kwargs.get(
            'bandwidth_bps', 1e6), kwargs.get('num_nodes', 2), 5e-7
        if protocol == "Full-Duplex Ethernet" or "FD" in protocol:
            node_B = Node(env, 'B', Ether(env, "ether_B->A", bandwidth_bps=bw, contention=False),
                          [], is_sender=False, data_size=kwargs.get('data_size', 5120))
            node_A = Node(env, 'A', Ether(env, "ether_A->B", bandwidth_bps=bw, contention=False),
                          [], peer='B', is_sender=True, data_size=kwargs.get('data_size', 5120))
            nodes = [node_A, node_B]
            node_A.all_nodes = nodes
            node_B.all_nodes = nodes
        else:
            ether = Ether(env, name="shared_ether", bandwidth_bps=bw,
                          propagation_delay_s=prop_delay, contention="no contention" not in protocol)
            nodes = [Node(env, chr(ord('A') + i), ether, [], is_sender=(i == 0), data_size=kwargs.get(
                'data_size', 5120 if "Ethernet" in protocol else 0)) for i in range(num_nodes)]
            for i, node in enumerate(nodes):
                node.all_nodes = nodes
                if (p_list := [p for p in nodes if p != node]):
                    node.peer = random.choice(p_list).name
    elif protocol == "Daedaelus Fabric":
        MockDaedaelusFabric(
            env, num_nodes=kwargs['num_nodes']).setup_processes()
    elif protocol == "Automotive TSN":
        MockAutomotiveTSN(env).setup_processes()
    elif protocol == "Active Building":
        MockActiveBuilding(env).setup_processes()

    env.run(until=kwargs['duration'])
    logger.info(json.dumps(
        {"time": env.now, "event": "simulation_end", "protocol": protocol}))

# -----------------------------------------------------------------------------
# Headless Execution Main Entry Point
# -----------------------------------------------------------------------------


def main():
    """
    This main function serves as the entry point for headless execution.
    It uses argparse to parse command-line arguments, replacing the need for
    the tkinter GUI from the original script. This is the core adaptation
    that makes the simulation engine deployable on Replit.
    """
    parser = argparse.ArgumentParser(
        description="Dædælus Headless Network Simulator")
    parser.add_argument('--protocol', type=str, required=True,
                        help='The simulation protocol to run.')
    parser.add_argument('--num_nodes', type=int, default=8,
                        help='Number of nodes in the simulation.')
    parser.add_argument('--duration', type=float, default=5.0,
                        help='Duration of the simulation in virtual seconds.')
    parser.add_argument('--bandwidth_bps', type=float,
                        default=10e9, help='Link bandwidth in bits per second.')
    parser.add_argument('--data_size', type=int, default=1024,
                        help='Packet size for data transfers.')
    parser.add_argument('--arrival_rate', type=float,
                        default=0.1, help='Arrival rate for ALOHA protocols.')

    args = parser.parse_args()
    sim_params = vars(args)

    # This is the architectural fix. We extract the 'protocol' argument for explicit
    # passing and remove it from the dictionary that will be unpacked into kwargs.
    # This resolves the TypeError by ensuring a clean, unambiguous function call.
    protocol_to_run = sim_params.pop('protocol')

    print(
        f"INFO: Starting Dædælus simulation. Protocol: '{protocol_to_run}'. Parameters: {sim_params}")

    env = simpy.Environment()
    setup_and_run(env, protocol_to_run, **sim_params)

    log_path = export_logs_to_file(protocol_to_run)
    if log_path:
        print(
            f"INFO: Simulation complete. Verifiable log artifact saved to: {log_path}")
    else:
        print("ERROR: Simulation complete, but log export failed.", file=sys.stderr)


if __name__ == "__main__":
    main()
