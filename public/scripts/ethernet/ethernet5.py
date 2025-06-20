#!/usr/bin/env python3
import simpy
import random
import collections
import math

# --- Simulation Parameters ---
SIM_DURATION = 15.0   # Total simulation time in seconds
NUM_NODES    = 16     # Must be a perfect square for grid topology
NUM_FLOWS    = 10     # Total number of TCP flows to simulate
PACKET_RATE  = 100    # Packets per second for the CBR application
PACKET_SIZE  = 960    # Size of data packets in bytes
HEADER_SIZE  = 40     # Size of the TCP/IP header in bytes
LINK_BANDWIDTH = 2e6  # Link bandwidth in bits per second (2 Mb)
LINK_LATENCY   = 0.010# Link propagation delay in seconds (10 ms)
QUEUE_LIMIT    = 10   # Queue limit in packets

class Packet:
    def __init__(self, time, flow_id, packet_id, source, dest,
                 size=PACKET_SIZE, ptype="TCP"):
        self.time      = time
        self.flow_id   = flow_id
        self.packet_id = packet_id
        self.source    = source
        self.dest      = dest
        self.size      = size
        self.ptype     = ptype  # 'TCP' or 'ACK'
        self.acked     = False

class StatsCollector:
    def __init__(self):
        self.sent_packets     = 0
        self.received_packets = 0
        self.dropped_packets  = 0
        self.total_received_bytes = 0
        self.total_delay      = 0.0
        self.start_time       = float('inf')
        self.end_time         = 0.0
        self.packet_send_times    = {}
        self.packet_receive_times = {}

    def log_sent(self, time, packet):
        self.sent_packets += 1
        self.packet_send_times[packet.packet_id] = time
        self.start_time = min(self.start_time, time)

    def log_received(self, time, packet):
        pid = packet.packet_id
        if pid in self.packet_send_times:
            self.received_packets += 1
            self.total_received_bytes += packet.size
            delay = time - self.packet_send_times[pid]
            self.total_delay += delay
            self.end_time = max(self.end_time, time)
            del self.packet_send_times[pid]

    def log_dropped(self, time, packet):
        self.dropped_packets += 1

    def calculate_metrics(self):
        sim_time = self.end_time - self.start_time
        if sim_time <= 0:
            return {}
        throughput_bps = (self.total_received_bytes * 8) / sim_time
        avg_delay     = (self.total_delay / self.received_packets
                         if self.received_packets > 0 else 0)
        delivery_ratio = (self.received_packets / self.sent_packets * 100
                          if self.sent_packets > 0 else 0)
        drop_ratio     = (self.dropped_packets / self.sent_packets * 100
                          if self.sent_packets > 0 else 0)
        return {
            "Throughput (bps)": throughput_bps,
            "Average Delay (s)": avg_delay,
            "Sent Packets": self.sent_packets,
            "Received Packets": self.received_packets,
            "Dropped Packets": self.dropped_packets,
            "Packet Delivery Ratio (%)": delivery_ratio,
            "Packet Drop Ratio (%)": drop_ratio,
            "Total Simulation Time (s)": sim_time
        }

class Node:
    def __init__(self, env, id, stats):
        self.env   = env
        self.id    = id
        self.name  = f"Node-{id}"
        self.stats = stats
        self.queue = simpy.Store(env, capacity=QUEUE_LIMIT)
        self.routing_table = {}  # dest_id -> (next_hop_node, link)
        self.agents = {}         # flow_id -> TCPAgent
        self.env.process(self.run())

    def add_link(self, next_hop, link):
        self.routing_table[next_hop.id] = (next_hop, link)

    def add_agent(self, agent):
        self.agents[agent.flow_id] = agent

    def run(self):
        while True:
            packet = yield self.queue.get()
            dest_id = packet.dest.id

            if dest_id == self.id:
                if packet.ptype == "ACK":
                    if packet.flow_id in self.agents:
                        self.agents[packet.flow_id].receive_ack(packet)
                else:
                    self.stats.log_received(self.env.now, packet)
                    ack = Packet(self.env.now,
                                 packet.flow_id,
                                 packet.packet_id,
                                 self,
                                 packet.source,
                                 size=HEADER_SIZE,
                                 ptype="ACK")
                    self.put(ack)
            else:
                # grid‐routing
                num_cols    = int(math.sqrt(NUM_NODES))
                current_col = self.id % num_cols
                dest_col    = dest_id % num_cols
                current_row = self.id // num_cols
                dest_row    = dest_id // num_cols

                next_hop_id = -1
                if dest_col > current_col:
                    next_hop_id = self.id + 1
                elif dest_col < current_col:
                    next_hop_id = self.id - 1
                elif dest_row > current_row:
                    next_hop_id = self.id + num_cols
                elif dest_row < current_row:
                    next_hop_id = self.id - num_cols

                if (next_hop_id != -1 and
                    next_hop_id in self.routing_table):
                    nh, link = self.routing_table[next_hop_id]
                    self.env.process(link.transmit(packet))
                else:
                    self.stats.log_dropped(self.env.now, packet)

    def put(self, packet):
        if len(self.queue.items) < self.queue.capacity:
            return self.queue.put(packet)
        else:
            self.stats.log_dropped(self.env.now, packet)

class Link:
    def __init__(self, env, node1, node2):
        self.env   = env
        self.node1 = node1
        self.node2 = node2

    def transmit(self, packet):
        transmission_delay = (packet.size * 8) / LINK_BANDWIDTH
        yield self.env.timeout(transmission_delay)
        yield self.env.timeout(LINK_LATENCY)
        packet.dest.put(packet)

class TCPAgent:
    def __init__(self, env, node, flow_id, dest_node, stats):
        self.env      = env
        self.node     = node
        self.flow_id  = flow_id
        self.dest     = dest_node
        self.stats    = stats
        self.cwnd     = 1.0
        self.ssthresh = 32.0
        self.last_ack = -1
        self.dupacks  = 0
        self.next_packet_id = 0
        self.outstanding_packets = {}  # pid -> send_time
        self.rtx_timer_proc = None
        self.rto = 1.0  # Retransmission timeout (sec)

        self.node.add_agent(self)
        self.env.process(self.run_cbr())

    def run_cbr(self):
        interval = 1.0 / PACKET_RATE
        while True:
            yield self.env.timeout(interval)
            self.send_much()

    def send_packet(self, is_retransmit=False, packet_id_to_send=None):
        pid = packet_id_to_send if is_retransmit else self.next_packet_id
        if pid is None:
            return

        pkt = Packet(self.env.now,
                     self.flow_id,
                     pid,
                     self.node,
                     self.dest)
        if not is_retransmit:
            self.next_packet_id += 1

        self.stats.log_sent(self.env.now, pkt)
        self.outstanding_packets[pid] = self.env.now
        self.node.put(pkt)

        # reset retransmission timer, but never interrupt ourselves
        if self.rtx_timer_proc:
            try:
                self.rtx_timer_proc.interrupt()
            except RuntimeError:
                pass
        self.rtx_timer_proc = self.env.process(self.timeout_process())

    def receive_ack(self, ack_packet):
        ack_id = ack_packet.packet_id
        if ack_id in self.outstanding_packets:
            if self.rtx_timer_proc:
                try:
                    self.rtx_timer_proc.interrupt()
                except RuntimeError:
                    pass

            # update RTT estimate
            rtt = self.env.now - self.outstanding_packets[ack_id]
            self.rto = 0.9 * self.rto + 0.1 * rtt

            # cumulative ACK: remove all ≤ ack_id
            for pid in list(self.outstanding_packets):
                if pid <= ack_id:
                    del self.outstanding_packets[pid]

            if ack_id > self.last_ack:
                self.last_ack = ack_id
                self.dupacks  = 0
                # AIMD
                if self.cwnd < self.ssthresh:
                    self.cwnd += 1.0
                else:
                    self.cwnd += 1.0 / self.cwnd
                self.send_much()
            elif ack_id == self.last_ack:
                self.dupacks += 1
                if self.dupacks == 3:
                    self.handle_duplicate_ack()

    def handle_duplicate_ack(self):
        self.ssthresh = max(self.cwnd / 2.0, 2.0)
        self.cwnd     = self.ssthresh + 3.0
        lost_pid = self.last_ack + 1
        if lost_pid in self.outstanding_packets:
            self.send_packet(is_retransmit=True,
                             packet_id_to_send=lost_pid)

    def timeout_process(self):
        try:
            yield self.env.timeout(self.rto)
            # timeout event
            self.ssthresh = max(self.cwnd / 2.0, 2.0)
            self.cwnd     = 1.0
            self.dupacks  = 0
            self.rto *= 2.0
            lost_pid = self.last_ack + 1
            self.send_packet(is_retransmit=True,
                             packet_id_to_send=lost_pid)
        except simpy.Interrupt:
            # timer reset by ACK or retransmit
            pass

    def send_much(self):
        while len(self.outstanding_packets) < int(self.cwnd):
            if self.next_packet_id < self.last_ack + int(self.cwnd) + 1:
                self.send_packet()
            else:
                break

class Simulation:
    def __init__(self):
        self.env   = simpy.Environment()
        self.stats = StatsCollector()
        self.nodes = []

    def setup_wired_grid(self):
        num_cols = int(math.sqrt(NUM_NODES))
        if num_cols * num_cols != NUM_NODES:
            raise ValueError("NUM_NODES must be a perfect square")
        print(f"Building a {num_cols}×{num_cols} wired grid...")
        for i in range(NUM_NODES):
            self.nodes.append(Node(self.env, i, self.stats))

        for i in range(NUM_NODES):
            row, col = divmod(i, num_cols)
            # horizontal
            if col < num_cols-1:
                right = i + 1
                link = Link(self.env, self.nodes[i], self.nodes[right])
                self.nodes[i].add_link(self.nodes[right], link)
                self.nodes[right].add_link(self.nodes[i], link)
            # vertical
            if row < num_cols-1:
                down = i + num_cols
                link = Link(self.env, self.nodes[i], self.nodes[down])
                self.nodes[i].add_link(self.nodes[down], link)
                self.nodes[down].add_link(self.nodes[i], link)

        print(f"Deploying {NUM_FLOWS} random TCP flows...")
        for fid in range(NUM_FLOWS):
            src, dst = random.sample(self.nodes, 2)
            TCPAgent(self.env, src, fid, dst, self.stats)

    def run(self):
        print(f"Running simulation for {SIM_DURATION} seconds...")
        self.setup_wired_grid()
        self.env.run(until=SIM_DURATION)
        print("\n--- Simulation Complete ---")
        for k,v in self.stats.calculate_metrics().items():
            print(f"{k:<28}: {v:.2f}")

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
