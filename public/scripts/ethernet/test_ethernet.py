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
    log_buffer.truncate(0)
    log_buffer.seek(0)
    
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
# Mock Implementations for External Modules
#
# As the source for the external simulators (Daedaelus Fabric, TSN, Building)
# may not be available, these mock classes provide functional placeholders. They
# are designed to produce meaningful logs and behaviors consistent with the
# Daedaelus philosophy, allowing the UI to remain fully operational.
# -----------------------------------------------------------------------------

class MockDaedaelusFabric:
    """
    Mocks the Daedaelus Fabric simulation. This does not model statistical
    contention but rather the deterministic establishment of a reliable link.
    It simulates the exchange of tokens to create a shared state between two
    agents, reflecting the principle of "Interaction-Multiplexing" over
    "Bandwidth-Multiplexing." The output demonstrates a system where the
    epistemic knowledge of an event is preserved.
    """
    def __init__(self, env):
        self.env = env

    def run(self, until):
        def link_formation(node1_name, node2_name):
            logger.info(json.dumps({"time": self.env.now, "event": "LinkInitiation", "link": f"{node1_name}<->{node2_name}", "detail": "Attempting to establish a reversible transaction channel."}))
            yield self.env.timeout(random.uniform(0.5, 1.5))
            
            # The exchange of tokens represents the establishment of mutual knowledge, the "I Know That You Know That I Know" (IKTYKTIK) property.
            logger.info(json.dumps({"time": self.env.now, "event": "TokenExchange", "link": f"{node1_name}<->{node2_name}", "owner": node1_name, "state": "SENT_LIVENESS_TOKEN"}))
            yield self.env.timeout(random.uniform(0.5, 1.5))
            logger.info(json.dumps({"time": self.env.now, "event": "TokenExchange", "link": f"{node1_name}<->{node2_name}", "owner": node2_name, "state": "RECEIVED_LIVENESS_TOKEN"}))
            yield self.env.timeout(random.uniform(0.5, 1.5))
            
            logger.info(json.dumps({"time": self.env.now, "event": "ConservedQuantityTransfer", "link": f"{node1_name}<->{node2_name}", "size": 1024, "status": "SUCCESS"}))

        self.env.process(link_formation('A', 'B'))
        self.env.run(until=until)
        export_logs(os.path.join(os.getcwd(), "fabric_state.json"))

class MockAutomotiveTSN:
    """
    Mocks an Automotive Time-Sensitive Networking (TSN) simulation.
    This demonstrates a network where bandwidth is allocated by time slots,
    ensuring deterministic delivery for critical messages. This version includes
    both senders and receivers to produce meaningful end-to-end statistics.
    """
    def __init__(self, env):
        self.env = env
        self.results = {}

    def run(self, until):
        bus = simpy.Store(self.env)

        def sender(source, dest, period, size):
            flow_key = f"{source}_to_{dest}"
            self.results[flow_key] = {'sent': 0, 'received': 0, 'latencies': []}
            while True:
                yield self.env.timeout(period)
                sent_time = self.env.now
                pkt_info = {'id': str(uuid.uuid4()), 'source': source, 'dest': dest, 'sent_time': sent_time, 'size': size}
                bus.put(pkt_info)
                self.results[flow_key]['sent'] += 1
                logger.info(json.dumps({"time": sent_time, "event": "TSN_TX", "source": source, "dest": dest, "id": pkt_info['id']}))

        def receiver(bus, propagation_delay=0.0001):
            while True:
                pkt_info = yield bus.get()
                yield self.env.timeout(propagation_delay) # Simulate travel time
                
                latency = self.env.now - pkt_info['sent_time']
                flow_key = f"{pkt_info['source']}_to_{pkt_info['dest']}"
                if flow_key in self.results:
                    self.results[flow_key]['received'] += 1
                    self.results[flow_key]['latencies'].append(latency)
                logger.info(json.dumps({"time": self.env.now, "event": "TSN_RX", "source": pkt_info['source'], "dest": pkt_info['dest'], "id": pkt_info['id'], "latency": latency}))

        flows_config = {
            "CameraF": [("HU", 1/60, 1500)], "ME": [("RS1", 1/100, 100), ("S1", 1/100, 100)],
            "US": [("CU", 1/2, 64)], "Lidar": [("CU", 1/30, 1500)], "RC": [("HU", 1/100, 100)]
        }
        all_receivers = set()
        for src, destinations in flows_config.items():
            for dst, rate, size in destinations:
                self.env.process(sender(src, dst, rate, size))
                all_receivers.add(dst)
        
        # Single receiver process handling all packets on the bus
        self.env.process(receiver(bus))
        self.env.run(until=until)
        self._print_results()

    def _print_results(self):
        print("\n=== Automotive TSN Simulation Results ===")
        for flow, data in sorted(self.results.items()):
            sent, received, latencies = data['sent'], data['received'], data['latencies']
            lost, loss_ratio = (sent - received), ((sent - received) / sent if sent > 0 else 0)
            mean_delay = sum(latencies) / len(latencies) if latencies else 0
            jitter = max(latencies) - min(latencies) if len(latencies) > 1 else 0
            
            print(f"Flow: {flow}\n  Frames sent:      {sent}\n  Frames received:  {received}\n  Frames lost:      {lost}\n  Frame Loss Ratio: {loss_ratio:.4f}\n  E2E Delay (mean): {mean_delay:.6f} s\n  E2E Jitter:         {jitter:.6f} s\n  ---")

class MockActiveBuilding:
    def __init__(self, sim_duration, tick_interval):
        self.env = simpy.Environment()
        self.sim_duration = sim_duration

    def start(self):
        def temp_sensor(env, thermostat_name):
            while True:
                temp = round(random.uniform(20.0, 22.0), 1)
                logger.info(json.dumps({"time": env.now, "event": "SensorReading", "source": "TempSensor_1", "destination": thermostat_name, "payload": {"temperature": temp}}))
                yield env.timeout(5)

        def thermostat(env):
            while True:
                logger.info(json.dumps({"time": env.now, "event": "ControlLogic", "source": "Thermostat", "decision": "Activating AC"}))
                yield env.timeout(5.1)

        self.env.process(temp_sensor(self.env, "Thermostat"))
        self.env.process(thermostat(self.env))
        self.env.run(until=self.sim_duration)
        print("Mock Active Building simulation finished. Check logs for IoT events.")

# -----------------------------------------------------------------------------
# Core Networking Primitives
# -----------------------------------------------------------------------------
class PacketType(enum.Enum):
    SYN = "SYN"
    SYN_ACK = "SYN-ACK"
    ACK = "ACK"
    DATA = "DATA"
    JAM = "JAM_SIGNAL"

class Packet:
    def __init__(self, ptype: PacketType, src=None, dst=None, size=64, seq=0, ack=0):
        self.id, self.ptype, self.src, self.dst = str(uuid.uuid4()), ptype, src, dst
        self.size, self.seq, self.ack = size, seq, ack
        self.success, self.collision_count = True, 0
        self.color = {"SYN": "#5E81AC", "SYN_ACK": "#88C0D0", "ACK": "#A3BE8C", "DATA": "#EBCB8B", "JAM": "#BF616A"}.get(ptype.value, "#4C566A")

    def bits(self): return self.size * 8
    def to_dict(self):
        # Ensure all packet attributes, including presentation data, are serialized into the event log.
        # This creates a self-contained record for downstream analysis and visualization.
        return {
            "time": getattr(self, 'start_time', None), "pkt_id": self.id, 
            "type": self.ptype.value, "src": getattr(self.src, 'name', 'N/A'), 
            "dst": getattr(self.dst, 'name', 'N/A'), "seq": self.seq, "ack": self.ack, 
            "size": self.size, "success": self.success, "collisions": self.collision_count,
            "color": self.color
        }
    def __repr__(self): return f"<{self.ptype.value} id={self.id[:4]} src={getattr(self.src,'name','N/A')}->dst={getattr(self.dst,'name','N/A')}>"

class Ether:
    """Represents the shared communication medium, the "Ether" from Metcalfe's paper."""
    def __init__(self, env, name="ether", bandwidth_bps=1e6, propagation_delay_s=5e-9, contention=True):
        self.env, self.name, self.bandwidth, self.prop_delay = env, name, bandwidth_bps, propagation_delay_s
        self.contention, self.transmitting_packets, self.log = contention, [], []

    def is_busy(self): return len(self.transmitting_packets) > 0

    def transmit(self, packet: Packet, source_node, all_nodes):
        # This method returns the generator, which the caller is responsible for scheduling.
        # This ensures a clean separation of concerns and correct process handling in simpy.
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
            yield self.env.timeout(transmission_time - self.prop_delay)
            packet.success = True
            for node in all_nodes:
                if node != source_node: node.receive_packet(packet)
        
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
        self.peer, self.is_sender, self.data_size = peer, is_sender, data_size
        self.state, self.send_una, self.next_seq, self.rcv_nxt, self.acked_data = "CLOSED", 0, 0, 0, set()
        self.backoff_attempts, self.active_tx_proc, self.inbox = 0, None, simpy.Store(env)
        self.action = env.process(self.run())

    def receive_packet(self, packet): self.inbox.put(packet)

    def send_with_backoff(self, packet):
        self.backoff_attempts = 0
        while self.backoff_attempts < 16:
            self.active_tx_proc = self.env.event()
            # The calling process is now responsible for scheduling the generator returned by transmit().
            self.env.process(self.ether.transmit(packet, self, self.all_nodes))
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
            if pkt.dst != self: continue

            if self.state == "CLOSED" and pkt.ptype == PacketType.SYN:
                self.state = "SYN_RCVD"
                self.rcv_nxt = pkt.seq + 1
                logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))
                yield self.env.process(self.send_with_backoff(Packet(PacketType.SYN_ACK, src=self, dst=self.peer, seq=self.next_seq, ack=self.rcv_nxt)))
                self.next_seq += 1
            elif self.state == "SYN_SENT" and pkt.ptype == PacketType.SYN_ACK:
                self.state = "ESTABLISHED"
                self.rcv_nxt, self.send_una = pkt.seq + 1, pkt.ack
                logger.info(json.dumps({"time": self.env.now, "event": "state_change", "node": self.name, "new_state": self.state}))
                yield self.env.process(self.send_with_backoff(Packet(PacketType.ACK, src=self, dst=self.peer, seq=self.next_seq, ack=self.rcv_nxt)))
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
                    if ack_data.dst == self and ack_data.ptype == PacketType.ACK: self.send_una = ack_data.ack
        else:
            while self.data_size > 0:
                data_pkt = yield self.inbox.get()
                if data_pkt.dst == self and data_pkt.ptype == PacketType.DATA:
                    self.rcv_nxt = data_pkt.seq + data_pkt.size
                    yield self.env.process(self.send_with_backoff(Packet(PacketType.ACK, src=self, dst=self.peer, ack=self.rcv_nxt)))

# -----------------------------------------------------------------------------
# Simulation Orchestrator & UI Framework
# -----------------------------------------------------------------------------

def setup_and_run(env, protocol, **kwargs):
    """A unified function to set up and run different simulation scenarios."""
    
    # ALOHA-style contention simulation
    if "ALOHA" in protocol:
        ether = Ether(env, name="aloha_ether", bandwidth_bps=kwargs['bandwidth_bps'], contention=True)
        nodes = []
        for i in range(kwargs['num_nodes']):
            node = AlohaNode(env, name=chr(ord('A') + i), ether=ether, all_nodes=[], 
                             arrival_rate=kwargs['arrival_rate'], protocol_type=protocol)
            nodes.append(node)
        for node in nodes:
            node.all_nodes = nodes
        env.run(until=kwargs['duration'])
        return

    # Point-to-point and Ethernet Bus simulations
    if "Ethernet" in protocol or "Handshake" in protocol:
        bw, num_nodes = kwargs.get('bandwidth_bps', 1e6), kwargs.get('num_nodes', 2)
        prop_delay = 5e-7
        
        nodes = []
        if protocol == "Half-Duplex Ethernet" or "HD" in protocol:
            contention = "no contention" not in protocol
            ether = Ether(env, name="shared_ether", bandwidth_bps=bw, propagation_delay_s=prop_delay, contention=contention)
            
            # Create all nodes first
            all_nodes_list = [Node(env, chr(ord('A') + i), ether, [], is_sender=(i < num_nodes / 2), data_size=kwargs.get('data_size', 5120 if "Ethernet" in protocol else 0)) for i in range(num_nodes)]
            
            # Set peers and all_nodes list for each node
            for i, node in enumerate(all_nodes_list):
                node.all_nodes = all_nodes_list
                # Assign a unique peer to each node that isn't itself
                possible_peers = [p for p in all_nodes_list if p != node]
                if possible_peers:
                    node.peer = random.choice(possible_peers)

        elif protocol == "Full-Duplex Ethernet" or "FD" in protocol:
            ether_ab = Ether(env, "ether_A->B", bandwidth_bps=bw, contention=False)
            ether_ba = Ether(env, "ether_B->A", bandwidth_bps=bw, contention=False)
            node_B = Node(env, 'B', ether_ba, [], is_sender=False, data_size=kwargs.get('data_size', 5120))
            node_A = Node(env, 'A', ether_ab, [], peer=node_B, is_sender=True, data_size=kwargs.get('data_size', 5120))
            node_B.peer, node_A.all_nodes, node_B.all_nodes = node_A, [node_A, node_B], [node_A, node_B]

        env.run(until=kwargs['duration'])

    elif protocol == "Daedaelus Fabric": MockDaedaelusFabric(env).run(until=kwargs['duration'])
    elif protocol == "Automotive TSN": MockAutomotiveTSN(env).run(until=kwargs['duration'])
    elif protocol == "Active Building": MockActiveBuilding(kwargs['duration'], 0.1).start()


class AlohaNode:
    """A simplified node for demonstrating ALOHA-family contention protocols."""
    def __init__(self, env, name, ether, all_nodes, arrival_rate, protocol_type):
        self.env, self.name, self.ether, self.all_nodes = env, name, ether, all_nodes
        self.arrival_rate, self.protocol_type = arrival_rate, protocol_type
        self.active_tx_proc = None
        self.action = env.process(self.run())

    def receive_packet(self, packet):
        # In this simplified ALOHA model, nodes do not process received packets.
        # This method exists to satisfy the Ether's broadcast interface, preventing
        # errors when the Ether attempts to deliver a packet to all listening nodes.
        pass

    def run(self):
        while True:
            # Wait for a new packet to be "generated"
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            packet_to_send = Packet(PacketType.DATA, src=self)

            if self.protocol_type == 'Pure ALOHA':
                yield self.env.process(self.send_with_backoff(packet_to_send, aggressive=True))
            
            elif self.protocol_type == 'Slotted ALOHA':
                # Align to the next slot
                slot_size = 2 * self.ether.prop_delay
                yield self.env.timeout(slot_size - (self.env.now % slot_size))
                yield self.env.process(self.send_with_backoff(packet_to_send, aggressive=True))

            elif self.protocol_type == 'CSMA/CD (ALOHA)':
                 # Defer to carrier sense logic in Ether class
                yield self.env.process(self.send_with_backoff(packet_to_send))

    def send_with_backoff(self, packet, aggressive=False):
        """'aggressive=True' for pure/slotted ALOHA which don't wait for channel clear."""
        attempts = 0
        while attempts < 16:
            if not aggressive:
                while self.ether.is_busy():
                    yield self.env.timeout(self.ether.prop_delay / 10)

            self.active_tx_proc = self.env.event()
            # Pass this node instance as the source and let the caller schedule the generator
            self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            
            if result_packet.success:
                return  # Success
            
            attempts += 1
            k = min(attempts, 10)
            slot_time = 2 * self.ether.prop_delay
            backoff_duration = random.randint(0, (2**k) - 1) * slot_time
            logger.info(json.dumps({"time": self.env.now, "event": "backoff", "node": self.name, "attempts": attempts, "delay": backoff_duration}))
            yield self.env.timeout(backoff_duration)


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

        # Protocol Selection
        ttk.Label(lf, text="Protocol:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.proto = ttk.Combobox(lf, width=35, values=[
            "TCP Handshake (HD, no contention)",
            "TCP Handshake (HD, contention)",
            "TCP Handshake (FD)",
            "CSMA/CD (ALOHA)",
            "Pure ALOHA",
            "Slotted ALOHA",
            "Half-Duplex Ethernet",
            "Full-Duplex Ethernet",
            "Daedaelus Fabric",
            "Automotive TSN",
            "Active Building"
        ], state="readonly")
        self.proto.current(1); self.proto.grid(row=0, column=1, sticky=tk.W)
        self.proto.bind("<<ComboboxSelected>>", self.draw_network_layout)

        # Simulation Parameters
        self.entries = {}
        labels_and_defaults = {
            "Pkt Size": "1024",
            "Bandwidth": "1e6",
            "Arrival λ": "0.1",
            "Sim Time": "20",
            "Priorities": "1,1,1",
            "Num Nodes": "3",
            "Export Logs?": "True"
        }
        
        for i, (text, default_val) in enumerate(labels_and_defaults.items(), start=1):
            key = text.lower().split()[0].replace('?', '')
            ttk.Label(lf, text=f"{text}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(lf, width=15)
            entry.insert(0, default_val)
            entry.grid(row=i, column=1, sticky=tk.W)
            self.entries[key] = entry
        
        bf = ttk.Frame(lf); bf.grid(row=len(labels_and_defaults) + 1, column=0, columnspan=2, pady=10)
        self.start_btn = ttk.Button(bf, text="Start Simulation", command=self.start_sim); self.start_btn.pack(side=tk.LEFT, padx=5)
        self.export_btn = ttk.Button(bf, text="Export Animation", command=self.export_animation, state="disabled"); self.export_btn.pack(side=tk.LEFT, padx=5)

        self.status = ttk.Label(mf, text="Ready.", font=("Helvetica", 10, "bold")); self.status.grid(row=1, column=0, sticky="w", pady=5)
        self.canvas = tk.Canvas(mf, width=800, height=400, bg="#2E3440"); self.canvas.grid(row=2, column=0, sticky="nsew")
        mf.columnconfigure(0, weight=1); mf.rowconfigure(2, weight=1)

    def draw_network_layout(self, event=None):
        self.canvas.delete("all")
        try:
            num_nd = int(self.entries['num'].get())
        except (KeyError, ValueError):
            num_nd = 2 # Default value if UI not fully initialized
        
        cx, cy, rad = 400, 200, 150
        proto = self.proto.get()
        self.nodes = [{'id': i, 'name': chr(ord('A') + i), 'x': (100 + (600 / (num_nd -1) * i if num_nd > 1 else 300)) if "Ethernet" in proto or "ALOHA" in proto else (cx + rad * cos(2*pi*i/num_nd-pi/2)), 'y': cy if "Ethernet" in proto or "ALOHA" in proto else (cy + rad * sin(2*pi*i/num_nd-pi/2))} for i in range(num_nd)]
        
        if "Ethernet" in proto or "ALOHA" in proto: self.canvas.create_line(100, cy, 700, cy, fill="#88C0D0", width=4, tags="ether_bus")
        for node in self.nodes:
            if "Ethernet" in proto or "ALOHA" in proto: self.canvas.create_line(node['x'], node['y']-20, node['x'], cy, fill="#81A1C1", width=2)
            self.canvas.create_rectangle(node['x']-20, node['y']-20, node['x']+20, node['y']+20, fill="#4C566A", outline="#D8DEE9", width=2)
            self.canvas.create_text(node['x'], node['y'], text=node['name'], font=("Helvetica", 12, "bold"), fill="#ECEFF4")

    def start_sim(self):
        if self.is_animating: return
        self.export_btn.config(state="disabled")
        try:
            sim_params = {
                "num_nodes": int(self.entries['num'].get()),
                "duration": float(self.entries['sim'].get()),
                "bandwidth_bps": float(self.entries['bandwidth'].get()),
                "data_size": int(self.entries['pkt'].get()), # 'Pkt Size' now maps to data_size
                "arrival_rate": float(self.entries['arrival'].get()),
                "priorities": [int(p) for p in self.entries['priorities'].get().split(',')],
                "do_export": self.entries['export'].get().lower() in ("true","1","yes")
            }
        except (ValueError, KeyError) as e: 
            messagebox.showerror("Invalid Input", f"Please check parameters.\nError: {e}"); return
        
        self.draw_network_layout(); self.status.config(text="Running simulation..."); self.root.update()
        log_buffer.truncate(0); log_buffer.seek(0)
        setup_and_run(simpy.Environment(), self.proto.get(), **sim_params)
        
        logs = []
        for line in log_buffer.getvalue().strip().splitlines():
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        self.status.config(text=f"Simulation complete. Animating {len(logs)} events..."); self.root.update()
        if logs: self.animate_log(logs)
        else:
            self.status.config(text=f"Simulation for '{self.proto.get()}' complete. No animation events logged.")
            if sim_params['do_export'] and self.proto.get() == "Daedaelus Fabric":
                 self.status.config(text=f"Fabric sim complete. Check fabric_state.json")
                 if Image: self.export_btn.config(state="normal")

    def animate_log(self, log):
        if not log: self.status.config(text="Animation complete."); return
        self.frames = []
        self.is_animating = True
        self.start_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        
        events = sorted(log, key=lambda e: e.get("time", 0))
        t_start, t_end = events[0].get("time", 0), events[-1].get("time", 0)
        duration = t_end - t_start or 1.0
        anim_total_duration_ms = 10000
        time_scale = anim_total_duration_ms / duration

        def _step(event_idx):
            if event_idx >= len(events):
                self.is_animating = False
                self.start_btn.config(state="normal")
                if self.entries['export'].get().lower() in ("true", "1", "yes") and Image:
                    self.export_btn.config(state="normal")
                self.status.config(text="Animation finished."); return
            
            event = events[event_idx]
            src = next((n for n in self.nodes if n['name'] == event.get("src")), None)
            
            delay_to_next_ms = 50
            if event_idx + 1 < len(events):
                delay_s = events[event_idx+1].get("time",0) - event.get("time",0)
                delay_to_next_ms = max(50, int(delay_s * time_scale))

            if src: self.animate_packet_movement(event, src, delay_to_next_ms)
            
            # Capture frame here if Pillow is available
            if Image:
                self.frames.append(self.capture_frame_as_image())

            self.root.after(delay_to_next_ms, lambda: _step(event_idx + 1))
        _step(0)

    def animate_packet_movement(self, event, src_node, duration_ms):
        dst_node = next((n for n in self.nodes if n['name'] == event.get("dst")), None)
        # Read color directly from the event log, ensuring the animator is decoupled from packet logic.
        color = event.get('color', '#4C566A')
        if not event.get('success', True): color = '#BF616A' # Override color for failure

        packet_size = 8
        pkt_obj = self.canvas.create_rectangle(0,0,0,0, fill=color, outline="#ECEFF4", tags="packet_anim")
        
        x_start, y_start = src_node['x'], src_node['y']
        
        steps, step_delay = 20, max(1, duration_ms // 20)
        is_bus = "Ethernet" in self.proto.get() or "ALOHA" in self.proto.get()
        y_bus = self.nodes[0]['y'] if self.nodes and is_bus else y_start

        def _move(step_num):
            if step_num > steps:
                self.canvas.delete(pkt_obj)
                if event.get('success') and event.get('type') != 'JAM_SIGNAL' and dst_node:
                     self.canvas.create_oval(dst_node['x']-4, dst_node['y']-4, dst_node['x']+4, dst_node['y']+4, fill=color, tags="packet_delivered", outline="")
                     self.root.after(200, lambda: self.canvas.delete("packet_delivered"))
                return

            prog = step_num / steps
            x_curr, y_curr = x_start, y_start
            
            # Simplified animation logic for bus topology
            if is_bus:
                x_end = dst_node['x'] if dst_node else x_start
                y_end = dst_node['y'] if dst_node else y_start

                # Move from node to bus
                if prog <= 0.2: 
                    y_curr = y_start - (y_start - y_bus) * (prog / 0.2)
                # Move along bus
                elif prog <= 0.8:
                    x_curr = x_start + (x_end - x_start) * ((prog - 0.2) / 0.6)
                    y_curr = y_bus
                # Move from bus to destination
                else:
                    x_curr = x_end
                    y_curr = y_bus + (y_end - y_bus) * ((prog - 0.8) / 0.2)
            elif dst_node: # Point-to-point animation
                x_end, y_end = dst_node['x'], dst_node['y']
                x_curr, y_curr = x_start + (x_end - x_start) * prog, y_start + (y_end - y_start) * prog

            self.canvas.coords(pkt_obj, x_curr - packet_size/2, y_curr - packet_size/2, x_curr + packet_size/2, y_curr + packet_size/2)
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
    SimulationFramework(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    except tk.TclError:
        print("Tkinter window closed.")