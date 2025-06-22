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

class Packet:
    def __init__(self, ptype: PacketType, src=None, dst=None, size=64, seq=0, ack=0):
        self.id, self.ptype = str(uuid.uuid4()), ptype
        self.src = getattr(src, 'name', src) # Handle both node objects and string names
        self.dst = getattr(dst, 'name', dst)
        self.size, self.seq, self.ack = size, seq, ack
        self.success, self.collision_count = True, 0
        self.color = {
            "SYN": "#5E81AC", "SYN_ACK": "#88C0D0", "ACK": "#A3BE8C", 
            "DATA": "#EBCB8B", "JAM": "#BF616A", "LIVENESS_TOKEN": "#B48EAD",
            "TSN_MSG": "#D08770", "IOT_DATA": "#A3BE8C"
        }.get(ptype.value, "#4C566A")

    def bits(self): return self.size * 8
    def to_dict(self):
        return {
            "time": getattr(self, 'start_time', None), "pkt_id": self.id, 
            "type": self.ptype.value, "src": self.src, "dst": self.dst, 
            "seq": self.seq, "ack": self.ack, "size": self.size, 
            "success": self.success, "collisions": self.collision_count,
            "color": self.color
        }
    def __repr__(self): return f"<{self.ptype.value} id={self.id[:4]} src={self.src}->dst={self.dst}>"

# -----------------------------------------------------------------------------
# Mock Implementations for External Modules
# -----------------------------------------------------------------------------

class MockDaedaelusFabric:
    def __init__(self, env):
        self.env = env

    def setup_processes(self):
        # The exchange of tokens represents the establishment of mutual knowledge, 
        # the "I Know That You Know That I Know" (IKTYKTIK) property.
        def link_formation(node1_name, node2_name):
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
        
        self.env.process(link_formation('A', 'B'))

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
            yield self.env.timeout(transmission_time - self.prop_delay)
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
            pass

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
            packet_to_send = Packet(PacketType.DATA, src=self)
            yield self.env.process(self.send_with_backoff(packet_to_send))
            
    def send_with_backoff(self, packet):
        attempts = 0
        while attempts < 16:
            if self.protocol_type == 'Slotted ALOHA':
                slot_size = 2 * self.ether.prop_delay
                yield self.env.timeout(slot_size - (self.env.now % slot_size))
            elif self.protocol_type == 'CSMA/CD (ALOHA)':
                while self.ether.is_busy():
                    yield self.env.timeout(self.ether.prop_delay / 10)

            self.active_tx_proc = self.env.event()
            yield self.env.process(self.ether.transmit(packet, self, self.all_nodes))
            result_packet = yield self.active_tx_proc
            
            if result_packet.success: return
            
            attempts += 1
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
    
    if "ALOHA" in protocol:
        ether = Ether(env, name="aloha_ether", bandwidth_bps=kwargs['bandwidth_bps'], contention=True)
        nodes = [AlohaNode(env, name=chr(ord('A') + i), ether=ether, all_nodes=[], arrival_rate=kwargs['arrival_rate'], protocol_type=protocol) for i in range(kwargs['num_nodes'])]
        for node in nodes: node.all_nodes = nodes
        
    elif "Ethernet" in protocol or "Handshake" in protocol:
        bw, num_nodes = kwargs.get('bandwidth_bps', 1e6), kwargs.get('num_nodes', 2)
        prop_delay = 5e-7
        
        if protocol == "Full-Duplex Ethernet" or "FD" in protocol:
            ether_ab = Ether(env, "ether_A->B", bandwidth_bps=bw, contention=False)
            ether_ba = Ether(env, "ether_B->A", bandwidth_bps=bw, contention=False)
            node_B = Node(env, 'B', ether_ba, [], is_sender=False, data_size=kwargs.get('data_size', 5120))
            node_A = Node(env, 'A', ether_ab, [], peer=node_B, is_sender=True, data_size=kwargs.get('data_size', 5120))
            node_B.peer, node_A.all_nodes, node_B.all_nodes = 'A', [node_A, node_B], [node_A, node_B]
        else: # Half-Duplex cases
            contention = "no contention" not in protocol
            ether = Ether(env, name="shared_ether", bandwidth_bps=bw, propagation_delay_s=prop_delay, contention=contention)
            all_nodes_list = [Node(env, chr(ord('A') + i), ether, [], is_sender=(i==0), data_size=kwargs.get('data_size', 5120 if "Ethernet" in protocol else 0)) for i in range(num_nodes)]
            for i, node in enumerate(all_nodes_list):
                node.all_nodes = all_nodes_list
                possible_peers = [p for p in all_nodes_list if p != node]
                if possible_peers: node.peer = random.choice(possible_peers)
    
    elif protocol == "Daedaelus Fabric": MockDaedaelusFabric(env).setup_processes()
    elif protocol == "Automotive TSN": MockAutomotiveTSN(env).setup_processes()
    elif protocol == "Active Building": MockActiveBuilding(env).setup_processes()
    
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
        self.proto = ttk.Combobox(lf, width=35, values=["TCP Handshake (HD, no contention)","TCP Handshake (HD, contention)","TCP Handshake (FD)","CSMA/CD (ALOHA)","Pure ALOHA","Slotted ALOHA","Half-Duplex Ethernet","Full-Duplex Ethernet","Daedaelus Fabric","Automotive TSN","Active Building"], state="readonly")
        self.proto.current(1); self.proto.grid(row=0, column=1, sticky=tk.W)
        self.proto.bind("<<ComboboxSelected>>", self.draw_network_layout)
        self.entries = {}
        labels_and_defaults = {"Pkt Size":"1024","Bandwidth":"1e6","Arrival λ":"0.1","Sim Time":"20","Priorities":"1,1,1","Num Nodes":"3","Export Logs?":"True"}
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

    def draw_network_layout(self, event=None):
        self.canvas.delete("all")
        proto = self.proto.get()
        self.nodes = []
        node_names = []

        if proto == "Daedaelus Fabric": node_names = ['A', 'B']
        elif proto == "Automotive TSN": node_names = ["CameraF", "ME", "US", "Lidar", "RC", "HU", "CU", "RS1", "S1"]
        elif proto == "Active Building": node_names = ["TempSensor", "Thermostat", "HVAC_Unit"]
        else: node_names = [chr(ord('A') + i) for i in range(self.get_sim_params()['num_nodes'])]
        
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

        if "Daedaelus Fabric" in proto:
            self.canvas.create_line(self.nodes[0]['x'], self.nodes[0]['y'], self.nodes[1]['x'], self.nodes[1]['y'], fill="#B48EAD", width=3)
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
        setup_and_run(simpy.Environment(), self.proto.get(), **sim_params)
        
        logs = [json.loads(line) for line in log_buffer.getvalue().strip().splitlines() if "{" in line]
        self.status.config(text=f"Simulation complete. Animating {len(logs)} events..."); self.root.update()
        if logs: self.animate_log(logs)
        else: self.status.config(text=f"Simulation for '{self.proto.get()}' complete. No animation events.")

    def stop_animation(self):
        # This method provides deterministic control over the animation loop, a key
        # feature for a responsive and reliable user interface.
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
            if not self.is_animating: return

            if event_idx >= len(events):
                self.is_animating = False
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                if self.get_sim_params()['do_export'] and Image:
                    self.export_btn.config(state="normal")
                self.status.config(text="Animation finished."); return
            
            event = events[event_idx]
            src = next((n for n in self.nodes if n['name'] == event.get("src")), None)
            
            delay_to_next_ms = 50
            if event_idx + 1 < len(events):
                delay_s = events[event_idx+1].get("time",0) - event.get("time",0)
                delay_to_next_ms = max(10, int(delay_s * time_scale))

            if src: self.animate_packet_movement(event, src, delay_to_next_ms)
            
            if Image: self.frames.append(self.capture_frame_as_image())
            self.root.after(delay_to_next_ms, lambda: _step(event_idx + 1))
        _step(0)

    def animate_packet_movement(self, event, src_node, duration_ms):
        dst_node = next((n for n in self.nodes if n['name'] == event.get("dst")), None)
        color = event.get('color', '#4C566A')
        if not event.get('success', True): color = '#BF616A'

        packet_size = 8
        pkt_obj = self.canvas.create_rectangle(0,0,0,0, fill=color, outline="#ECEFF4", tags="packet_anim")
        x_start, y_start = src_node['x'], src_node['y']
        
        steps, step_delay = 20, max(1, duration_ms // 20)
        is_bus = "Ethernet" in self.proto.get() or "ALOHA" in self.proto.get()
        y_bus = self.nodes[0]['y'] if self.nodes and is_bus else y_start

        def _move(step_num):
            if not self.is_animating:
                self.canvas.delete(pkt_obj)
                return

            if step_num > steps:
                self.canvas.delete(pkt_obj)
                if event.get('success') and event.get('type') != 'JAM_SIGNAL' and dst_node:
                     self.canvas.create_oval(dst_node['x']-4, dst_node['y']-4, dst_node['x']+4, dst_node['y']+4, fill=color, tags="packet_delivered", outline="")
                     self.root.after(200, lambda: self.canvas.delete("packet_delivered"))
                return

            prog = step_num / steps
            x_curr, y_curr = x_start, y_start
            
            if is_bus and dst_node:
                x_end, y_end = dst_node['x'], dst_node['y']
                if prog <= 0.2: y_curr = y_start - (y_start - y_bus) * (prog / 0.2)
                elif prog <= 0.8: x_curr, y_curr = x_start + (x_end - x_start) * ((prog - 0.2) / 0.6), y_bus
                else: x_curr, y_curr = x_end, y_bus + (y_end - y_bus) * ((prog - 0.8) / 0.2)
            elif dst_node:
                x_end, y_end = dst_node['x'], dst_node['y']
                x_curr, y_curr = x_start + (x_end - x_start) * prog, y_start + (y_end - y_start) * prog
            
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
    SimulationFramework(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    except tk.TclError:
        print("Tkinter window closed.")