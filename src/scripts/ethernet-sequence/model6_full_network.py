# Difference between Simulator and Emulators
# Integrate ALL Python files into one library! At the end all the code is going to be thrown away for Rust..
# Priority Queue based Simulation! More logs, preferably logs on each packet
# Look at Pipelining and Sliding for TCP where you're able to look at and send multiple data packets before acknowledging them..then you look at throughput congestion where you
# (have multiple links and switches)..start losing acknowledgments..NEXT STEP is *****Full Duplex over Multiple Links**** like Switches.****** Simulations and Visualizations that will be MOST USEFUL
# Tasks for Ethernet:
# 1. Want to have more specific models of what the Ethernet is sending and receiving, and how the model operates
# 2. Just do TCP don’t look at what applications need to send
# 3. Have a bidirectional flow, sending some data from A to B, all the data gets acknowledged
# 4. Distinguish between what kind of packet
# 5. Should be seeing what Metcalfe put in his paper; statistics is just a validation
# 6. Take what’s useful and put it into a clean notebook.nb
# 7. Want to show step by step the transmission of packets
# Logs for each packet; like the Wolfram Mathematica Cellular Automata, run something and reproduce all events. SPECIFICALLY for Reproducing the events in Wolfram Mathematica!
# Need to be able to reproduce all events via just the logs
# Mathematica can control how fast it's going through these logs in the visualization.
# Write the Python to run as fast as it can, and then analyze the output!
# Python logging package, will deal with the files, pretty simple to use (PyTransitions)!
# Packet Logs and Link Logs are the only thing missing!
# Don't need both simpy and numpy; optimization; make it work first..and then can make it fast later..
import simpy
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import time
import argparse
from enum import Enum
import math
import numpy as np  # Don't need both numpy and simpy
from matplotlib.animation import FuncAnimation
# I currently have Slotted and Pure Aloha and Half Duplex, need to have Full Duplex then it'll be more complete! I want to show more step by step the transmission of packets..
# Mathematica Visualization..don't show code show the output on the demo, don't show the code to them..their eyes will glaze over during the demo


class Protocol(Enum):
    PURE_ALOHA = 1
    SLOTTED_ALOHA = 2
    CSMA_CD = 3


class Packet:
    def __init__(self, id, src, dest, size, creation_time, protocol=None):
        self.id = id
        self.src = src
        self.dest = dest
        self.size = size
        self.creation_time = creation_time
        self.last_hop = src
        self.path = [src]
        self.dropped = False
        self.protocol = protocol
        self.transmission_count = 0

    def __repr__(self):
        return f"Packet({self.id} {self.src}→{self.dest})"


class Host:
    def __init__(self, env, id, mac, switch, packet_rate, packet_size, protocol=Protocol.PURE_ALOHA):
        self.env = env
        self.id = id
        self.mac = mac
        self.switch = switch
        self.packet_rate = packet_rate
        self.packet_size = packet_size
        self.protocol = protocol
        self.queue = deque()
        self.stats = {
            "sent": 0,
            "received": 0,
            "collisions": 0,
            "backoffs": 0
        }
        self.env.process(self.generate_traffic())

    def generate_traffic(self):
        packet_id = 0
        while True:
            dest = random.choice(
                [h for h in self.switch.network.hosts if h != self])
            packet = Packet(packet_id, self, dest,
                            self.packet_size, self.env.now, self.protocol)
            packet_id += 1

            if self.protocol == Protocol.SLOTTED_ALOHA:
                next_slot = math.ceil(self.env.now)
                yield self.env.timeout(next_slot - self.env.now)

            self.env.process(self.send_packet(packet))
            yield self.env.timeout(random.expovariate(self.packet_rate))

    def send_packet(self, packet):
        self.stats["sent"] += 1
        packet.transmission_count += 1

        if self.protocol in [Protocol.PURE_ALOHA, Protocol.SLOTTED_ALOHA]:
            yield self.env.process(self.switch.handle_aloha_packet(self, packet))
        else:
            yield self.env.process(self.switch.handle_csma_packet(self, packet))

    def receive_packet(self, packet):
        self.stats["received"] += 1
        packet.path.append(self)


class Switch:
    def __init__(self, env, id, mac, network, stp_enabled=True, ecmp_enabled=False):
        self.env = env
        self.id = id
        self.mac = mac
        self.network = network
        self.stp_enabled = stp_enabled
        self.ecmp_enabled = ecmp_enabled
        self.ports = {}
        self.mac_table = {}
        self.stp_state = {
            "root_bridge": self,
            "root_path_cost": 0,
            "ports": {}
        }
        self.buffer = defaultdict(deque)
        self.stats = {
            "forwarded": 0,
            "dropped": 0,
            "collisions": 0,
            "buffer_size": 0
        }
        self.env.process(self.process_buffer())

    def add_port(self, port_id, link):
        self.ports[port_id] = link
        self.stp_state["ports"][port_id] = {
            "state": "forwarding" if not self.stp_enabled else "blocking",
            "cost": 1
        }

    def handle_aloha_packet(self, host, packet):
        if random.random() < 0.3:
            host.stats["collisions"] += 1
            self.stats["collisions"] += 1
            backoff = random.randint(0, 2**min(packet.transmission_count, 10))
            host.stats["backoffs"] += 1
            yield self.env.timeout(backoff)
            if packet.transmission_count < 5:
                self.env.process(host.send_packet(packet))
            else:
                packet.dropped = True
                self.stats["dropped"] += 1
        else:
            self.receive_packet(host, packet)

    def handle_csma_packet(self, host, packet):
        if self.network.medium_busy():
            backoff = random.expovariate(1.0)
            host.stats["backoffs"] += 1
            yield self.env.timeout(backoff)
            self.env.process(host.send_packet(packet))
            return

        self.network.set_medium_busy(True)
        tx_time = packet.size / self.network.link_speed

        if random.random() < 0.2:
            host.stats["collisions"] += 1
            self.stats["collisions"] += 1
            self.network.set_medium_busy(False)
            yield self.env.timeout(0.01)
            backoff = random.randint(0, 2**min(packet.transmission_count, 10))
            host.stats["backoffs"] += 1
            yield self.env.timeout(backoff)
            if packet.transmission_count < 5:
                self.env.process(host.send_packet(packet))
            else:
                packet.dropped = True
                self.stats["dropped"] += 1
        else:
            yield self.env.timeout(tx_time)
            self.network.set_medium_busy(False)
            self.receive_packet(host, packet)

    def receive_packet(self, sender, packet):
        self.mac_table[sender.mac] = (sender, self.env.now)

        if packet.dest == self:
            packet.dest.host.receive_packet(packet)
        else:
            self.buffer[packet.dest].append(packet)
            self.stats["buffer_size"] = sum(len(q)
                                            for q in self.buffer.values())

    def process_buffer(self):
        while True:
            for dest, packets in list(self.buffer.items()):
                if packets:
                    packet = packets.popleft()
                    self.stats["buffer_size"] = sum(
                        len(q) for q in self.buffer.values())
                    if self.stats["buffer_size"] > 100:
                        packet.dropped = True
                        self.stats["dropped"] += 1
                        continue
                    path = self.network.find_path(self, packet.dest)
                    if path:
                        next_hop = path[0]
                        link = self.ports.get(next_hop)
                        if link:
                            if self.ecmp_enabled and len(path) > 1:
                                next_hop = random.choice(
                                    path[:min(3, len(path))])
                            tx_time = packet.size / self.network.link_speed
                            yield self.env.timeout(tx_time)
                            packet.last_hop = self
                            packet.path.append(next_hop)
                            self.stats["forwarded"] += 1
                            next_hop.receive_packet(self, packet)
                        else:
                            packet.dropped = True
                            self.stats["dropped"] += 1
                    else:
                        packet.dropped = True
                        self.stats["dropped"] += 1
            yield self.env.timeout(0.01)


class Network:
    def __init__(self, env, topology, link_speed=1e6, stp_enabled=True, ecmp_enabled=False):
        self.env = env
        self.topology = topology
        self.link_speed = link_speed
        self.stp_enabled = stp_enabled
        self.ecmp_enabled = ecmp_enabled
        self._medium_busy = False
        self.medium_busy_since = None
        self.switches = []
        self.hosts = []
        self.graph = nx.Graph()
        self.packets = []
        self.build_network()
        if stp_enabled:
            self.run_stp()

    def set_medium_busy(self, busy):
        self._medium_busy = busy
        if busy:
            self.medium_busy_since = self.env.now

    def medium_busy(self):
        return self._medium_busy

    def build_network(self):
        for i in range(self.topology["switches"]):
            mac = f"00:00:00:00:{i:02d}:01"
            switch = Switch(self.env, i, mac, self,
                            self.stp_enabled, self.ecmp_enabled)
            self.switches.append(switch)
            self.graph.add_node(f"S{i}", type="switch")
        for i in range(self.topology["hosts"]):
            mac = f"00:00:00:01:{i:02d}:01"
            switch = self.switches[i % len(self.switches)]
            host = Host(self.env, i, mac, switch,
                        packet_rate=0.5, packet_size=1500)
            self.hosts.append(host)
            self.graph.add_node(f"H{i}", type="host")
            self.graph.add_edge(f"S{switch.id}", f"H{i}")
        for i in range(len(self.switches)):
            for j in range(i + 1, len(self.switches)):
                if random.random() < 0.4:
                    self.graph.add_edge(f"S{i}", f"S{j}")

    def run_stp(self):
        for u, v in list(self.graph.edges):
            if self.graph[u][v].get('blocked', False):
                continue
            if random.random() < 0.2 and u.startswith('S') and v.startswith('S'):
                self.graph[u][v]['blocked'] = True

    def find_path(self, src, dest):
        try:
            src_node = f"S{src.id}" if isinstance(
                src, Switch) else f"H{src.id}"
            dest_node = f"S{dest.id}" if isinstance(
                dest, Switch) else f"H{dest.id}"
            all_paths = list(nx.all_shortest_paths(
                self.graph, src_node, dest_node))
            valid_paths = []
            for path in all_paths:
                valid = True
                for i in range(len(path)-1):
                    u, v = path[i], path[i+1]
                    if self.graph[u][v].get('blocked', False):
                        valid = False
                        break
                if valid:
                    valid_paths.append(path)
            if valid_paths:
                path = random.choice(valid_paths)
                node_objects = []
                for node in path[1:-1]:
                    if node.startswith('S'):
                        node_id = int(node[1:])
                        node_objects.append(self.switches[node_id])
                return node_objects
            return None
        except:
            return None


class Simulation:
    def __init__(self, duration=100, topology=None, protocol=Protocol.PURE_ALOHA,
                 stp_enabled=True, ecmp_enabled=False, animate=False):
        self.env = simpy.Environment()
        self.duration = duration
        self.topology = topology or {"switches": 4, "hosts": 8}
        self.protocol = protocol
        self.stp_enabled = stp_enabled
        self.ecmp_enabled = ecmp_enabled
        self.animate = animate
        self.network = Network(
            self.env, self.topology, stp_enabled=stp_enabled, ecmp_enabled=ecmp_enabled)

        for host in self.network.hosts:
            host.protocol = protocol

    def run(self):
        self.env.run(until=self.duration)
        return self.collect_stats()

    def collect_stats(self):
        stats = {"total_packets": 0, "delivered": 0, "dropped": 0,
                 "collisions": 0, "throughput": 0, "switch_stats": [], "host_stats": []}
        for host in self.network.hosts:
            host_stats = {"id": host.id, "sent": host.stats["sent"], "received": host.stats["received"],
                          "collisions": host.stats["collisions"], "backoffs": host.stats["backoffs"]}
            stats["host_stats"].append(host_stats)
            stats["total_packets"] += host.stats["sent"]
            stats["dropped"] += host.stats["sent"] - host.stats["received"]
            stats["collisions"] += host.stats["collisions"]
        for switch in self.network.switches:
            switch_stats = {"id": switch.id, "forwarded": switch.stats["forwarded"], "dropped": switch.stats[
                "dropped"], "collisions": switch.stats["collisions"], "buffer_size": switch.stats["buffer_size"]}
            stats["switch_stats"].append(switch_stats)
            stats["dropped"] += switch.stats["dropped"]
            stats["collisions"] += switch.stats["collisions"]
        stats["delivered"] = stats["total_packets"] - stats["dropped"]
        stats["throughput"] = stats["delivered"] / \
            self.duration if self.duration > 0 else 0
        return stats


def compare_aloha():
    # Compare Pure ALOHA vs Slotted ALOHA
    protocols = [Protocol.PURE_ALOHA, Protocol.SLOTTED_ALOHA]
    results = {}

    for protocol in protocols:
        sim = Simulation(
            duration=200,
            protocol=protocol,
            stp_enabled=False,
            ecmp_enabled=False
        )
        stats = sim.run()
        results[protocol.name] = {
            "throughput": stats["throughput"],
            "collision_rate": stats["collisions"] / stats["total_packets"] if stats["total_packets"] > 0 else 0,
            "delivery_ratio": stats["delivered"] / stats["total_packets"] if stats["total_packets"] > 0 else 0
        }

    # Plot comparison
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))

    # Throughput
    ax[0].bar([p.name for p in protocols], [
              results[p.name]["throughput"] for p in protocols])
    ax[0].set_title("Throughput (packets/sec)")
    ax[0].set_ylabel("Rate")

    # Collision Rate
    ax[1].bar([p.name for p in protocols], [
              results[p.name]["collision_rate"] for p in protocols])
    ax[1].set_title("Collision Rate")
    ax[1].set_ylabel("Ratio")

    # Delivery Ratio
    ax[2].bar([p.name for p in protocols], [
              results[p.name]["delivery_ratio"] for p in protocols])
    ax[2].set_title("Delivery Ratio")
    ax[2].set_ylabel("Ratio")

    plt.tight_layout()
    plt.savefig("aloha_comparison.png")
    plt.show()

    return results


def visualize_topology(network):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(network.graph)

    # Draw nodes
    switches = [node for node in network.graph.nodes if node.startswith('S')]
    hosts = [node for node in network.graph.nodes if node.startswith('H')]

    nx.draw_networkx_nodes(
        network.graph, pos, nodelist=switches, node_color='skyblue', node_size=500)
    nx.draw_networkx_nodes(network.graph, pos, nodelist=hosts,
                           node_color='lightgreen', node_size=300)

    # Draw edges
    active_edges = [(u, v) for u, v, data in network.graph.edges(
        data=True) if not data.get('blocked', False)]
    blocked_edges = [(u, v) for u, v, data in network.graph.edges(
        data=True) if data.get('blocked', False)]

    nx.draw_networkx_edges(network.graph, pos, edgelist=active_edges, width=2)
    nx.draw_networkx_edges(
        network.graph, pos, edgelist=blocked_edges, edge_color='r', style='dashed')

    # Labels
    labels = {node: node for node in network.graph.nodes}
    nx.draw_networkx_labels(network.graph, pos, labels, font_size=10)

    plt.title("Network Topology (Red = Blocked by STP)")
    plt.axis('off')
    plt.savefig("network_topology.png")
    plt.show()


def visualize_packet_spraying(network):
    # Show multiple paths between two switches
    if len(network.switches) < 2:
        return

    src = network.switches[0]
    dest = network.switches[-1]

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(network.graph)

    # Draw all nodes
    nx.draw(network.graph, pos, with_labels=True, node_color='lightblue')

    # Find and draw multiple paths
    paths = []
    for _ in range(3):  # Get up to 3 paths
        path = network.find_path(src, dest)
        if path and path not in paths:
            paths.append(path)

            # Convert path to node names
            node_path = [f"S{src.id}"] + \
                [f"S{s.id}" for s in path] + [f"S{dest.id}"]

            # Draw path
            path_edges = [(node_path[i], node_path[i+1])
                          for i in range(len(node_path)-1)]
            nx.draw_networkx_edges(network.graph, pos, edgelist=path_edges,
                                   edge_color=np.random.rand(3,), width=2)

    plt.title("ECMP Packet Spraying (Multiple Paths)")
    plt.savefig("packet_spraying.png")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Ethernet Network Simulator")
    parser.add_argument("--duration", type=int, default=100,
                        help="Simulation duration")
    parser.add_argument("--switches", type=int, default=4,
                        help="Number of switches")
    parser.add_argument("--hosts", type=int, default=8, help="Number of hosts")
    parser.add_argument("--protocol", choices=["pure_aloha", "slotted_aloha", "csma_cd"],
                        default="csma_cd", help="MAC protocol")
    parser.add_argument("--stp", action="store_true",
                        help="Enable Spanning Tree Protocol")
    parser.add_argument("--ecmp", action="store_true",
                        help="Enable ECMP Packet Spraying")
    parser.add_argument("--compare", action="store_true",
                        help="Compare ALOHA protocols")
    args = parser.parse_args()

    if args.compare:
        compare_aloha()
        return

    # Map protocol argument to enum
    protocol_map = {
        "pure_aloha": Protocol.PURE_ALOHA,
        "slotted_aloha": Protocol.SLOTTED_ALOHA,
        "csma_cd": Protocol.CSMA_CD
    }

    topology = {"switches": args.switches, "hosts": args.hosts}
    sim = Simulation(
        duration=args.duration,
        topology=topology,
        protocol=protocol_map[args.protocol],
        stp_enabled=args.stp,
        ecmp_enabled=args.ecmp
    )

    # Visualize topology before simulation
    visualize_topology(sim.network)

    # Run simulation
    start_time = time.time()
    stats = sim.run()
    elapsed = time.time() - start_time

    # Visualize packet spraying
    visualize_packet_spraying(sim.network)

    # Print results
    print("\n=== Simulation Results ===")
    print(
        f"Simulated time: {stats['total_packets']} packets in {elapsed:.2f} seconds")
    print(f"Throughput: {stats['throughput']:.2f} packets/sec")
    print(
        f"Delivery ratio: {stats['delivered']/stats['total_packets']:.2%}" if stats['total_packets'] > 0 else "N/A")
    print(
        f"Collision rate: {stats['collisions']/stats['total_packets']:.2%}" if stats['total_packets'] > 0 else "N/A")

    print("\nHost Statistics:")
    for host in stats["host_stats"]:
        print(f"Host {host['id']}: Sent: {host['sent']}, Received: {host['received']}, "
              f"Collisions: {host['collisions']}, Backoffs: {host['backoffs']}")

    print("\nSwitch Statistics:")
    for switch in stats["switch_stats"]:
        print(f"Switch {switch['id']}: Forwarded: {switch['forwarded']}, Dropped: {switch['dropped']}, "
              f"Collisions: {switch['collisions']}, Buffer: {switch['buffer_size']}")


if __name__ == "__main__":
    main()
