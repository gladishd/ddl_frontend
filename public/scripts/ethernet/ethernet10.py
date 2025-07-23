# python ethernet10.py
# -*- coding: utf-8 -*-

#
# DDL_Emulator.stp_simulator (ethernet10.py)
#
# Copyright (c) 2021-2023 Maen Artimy
# Copyright (c) 2025 Dædælus
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the MIT License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# MIT License for more details.
#

"""
This script provides an emulation of the Spanning Tree Protocol (STP). In the Dædælus
philosophy, we recognize that before robust, higher-level computational strata can be built,
the physical groundplane must be tamed and made deterministic. Today's datacenter architects
build their infrastructures using two kinds of boxes: switches and servers. This results in
very high operational costs and nothing close to five-nines reliability.

STP is a classic example of a distributed algorithm that imposes order on a potentially
chaotic physical topology. It prunes a meshed network graph into a loop-free logical tree.
This aligns with the Dædælus principle to "Manage on a Tree, Compute on a Graph." By
establishing a single, unambiguous path between any two nodes, STP prevents the broadcast
storms and MAC table corruption that arise from loops, which are a source of the
"insidious non-determinism" that plagues conventional networks.

This emulator models the BPDU exchange process, where each node, using only a Local
Observer View (LOV), contributes to the global consensus of the tree structure. This process
of distributed consensus is fundamental to building the "Transaction Fabric" envisioned by
Dædælus, where the network itself enforces reliability rather than leaving it as an
afterthought for the application to clean up.
"""

import logging
import sys
import argparse
import io
import os

try:
    import networkx as nx
    from netaddr import EUI
    import pydot
except ImportError as e:
    print(f"Error: Missing dependency. Please install required libraries: pip install networkx netaddr pydot")
    print(f"({e})")
    sys.exit(1)


class BPDU(object):
    """
    Represents a Bridge Protocol Data Unit (BPDU).
    This is the fundamental message exchanged between Graph Virtual Machines (GVMs)
    to establish a distributed consensus on the network's logical tree topology.
    The "best" BPDU is chosen through a deterministic comparison, ensuring that all
    nodes eventually agree on a single Root Bridge and the loop-free paths to it.
    """
    def __init__(self, root_id, cost, bridge_id, port_id):
        self.root = root_id
        self.cost = cost
        self.id = bridge_id
        self.port = port_id

    def get_best(self, other_bpdu):
        """
        Determines the superior BPDU between self and another.
        The selection criteria—(root_id, cost, bridge_id, port_id)—form a strict
        lexicographical ordering. This provides a deterministic "ruleset" that enables
        the distributed system to converge to a single, stable state without ambiguity,
        avoiding the race conditions that lead to network failure.
        """
        if not other_bpdu:
            return self

        # The comparison is a tuple-wise evaluation to find the superior BPDU.
        # A lower value is superior, establishing a clear hierarchy.
        if (self.root, self.cost, self.id, self.port) <= (other_bpdu.root, other_bpdu.cost, other_bpdu.id, other_bpdu.port):
            return self
        else:
            return other_bpdu

    def __str__(self):
        return f"[{hex(self.root)}, {self.cost}, {hex(self.id)}, {self.port}]"


class Port(object):
    """
    Represents a port on a Graph Virtual Machine (GVM), acting as an interface
    to a physical link in the N2N Lattice. Each port functions as a local observer,
    exchanging BPDUs to build a coherent view of the network topology.
    """

    ROLE_ROOT = "Root Port"
    ROLE_UNDESIGNATED = "Undesignated"
    ROLE_DESIGNATED = "Designated"

    STATUS_FORWARDING = "Forwarding"
    STATUS_BLOCKED = "Blocked"

    # Mapping port roles to their forwarding status.
    # In the Dædælus model, a port is either forwarding data to maintain the
    # logical tree or blocked to prevent loops. This binary state eliminates
    # the ambiguity that leads to packet duplication and reordering.
    ROLE_STATUS_MAP = {
        ROLE_ROOT: STATUS_FORWARDING,
        ROLE_DESIGNATED: STATUS_FORWARDING,
        ROLE_UNDESIGNATED: STATUS_BLOCKED
    }

    def __init__(self, num, cost):
        self.num = num
        self.cost = cost
        self.remote_port = None
        self.reset_stp_state()

    def reset_stp_state(self):
        """
        Initializes the port's Spanning Tree state. At boot, a port has
        no knowledge of the wider network until it begins receiving BPDUs.
        """
        self.best_bpdu = None
        self.role = Port.ROLE_UNDESIGNATED
        self.status = Port.STATUS_BLOCKED
        self.cost_to_root = None

    def connect_to(self, remote_port):
        """Establishes a bidirectional connection to a remote port."""
        self.remote_port = remote_port

    def send_bpdu(self, bpdu):
        """
        Transmits a BPDU to the connected port. This action is the primary
        mechanism for sharing local knowledge across the N2N Lattice.
        """
        self.best_bpdu = self.best_bpdu.get_best(bpdu) if self.best_bpdu else bpdu
        self.remote_port.receive_bpdu(bpdu)

    def receive_bpdu(self, bpdu):
        """
        Receives a BPDU from a remote port and updates its own view of the
        best known network configuration.
        """
        self.best_bpdu = self.best_bpdu.get_best(bpdu) if self.best_bpdu else bpdu

    def assign_role(self, role):
        """
        Assigns a role to the port based on the STP algorithm's outcome.
        This assignment determines whether the port will become part of the
        active, loop-free data path.
        """
        self.role = role
        self.status = self.ROLE_STATUS_MAP[role]


class GraphVirtualMachine(object):
    """
    Represents a network switch, conceptualized in the Dædælus framework as a
    Graph Virtual Machine (GVM). The GVM's role is to "build and tear down
    'named' graph relationships." In the context of STP, it collaborates with
    other GVMs to prune the physical graph into a stable, logical tree,
    ensuring a reliable foundation for data transport.
    """

    def __init__(self, label, id):
        self.label = label
        self.id = id
        self.ports = []
        self.best_bpdu = None
        self.is_root = False

    def boot(self):
        """
        Initializes the GVM. Upon booting, each GVM assumes it is the center of
        its own universe—the root of its own tree. This decentralized starting
        point is fundamental to the distributed consensus algorithm.
        """
        self.best_bpdu = BPDU(self.id, 0, self.id, 0)
        self.is_root = True

        for p in self.ports:
            p.reset_stp_state()

        logging.debug(f"GVM {hex(self.id)} boots, assuming it is the Root.")

    def process_bpdu_exchange(self):
        """
        Executes one step of the Spanning Tree algorithm. The GVM evaluates all
        BPDUs received from its neighbors, updates its own view of the optimal
        network topology, and broadcasts this view back out. This iterative
        exchange of local information is what allows the entire lattice to
        converge on a single, global, loop-free tree.
        """
        # A GVM's understanding of the network is built from the BPDUs received on its ports.
        # It calculates a potential new BPDU for each port based on received information.
        potential_bpdu_candidates = [BPDU(p.best_bpdu.root, p.best_bpdu.cost + p.cost,
                                          self.id, p.num) for p in self.ports if p.best_bpdu]

        # From all potential paths, the GVM determines the single best path to the root.
        current_best_bpdu = BPDU(self.id, 0, self.id, 0)
        root_port_num = None
        for b in potential_bpdu_candidates:
            if b.get_best(current_best_bpdu) == b:
                current_best_bpdu = b
                root_port_num = b.port
        logging.debug(
            f"GVM {hex(self.id)} believes best path is via BPDU {current_best_bpdu} on port {root_port_num}.")

        # The GVM determines if it is the root of the converged tree.
        self.is_root = current_best_bpdu.root == self.id

        if self.is_root:
            logging.debug(f"GVM {hex(self.id)} has concluded it is the Root Bridge.")
            # As the root, all its ports are designated and actively forwarding.
            for p in self.ports:
                bpdu_to_send = BPDU(self.id, 0, self.id, p.num)
                p.send_bpdu(bpdu_to_send)
                p.assign_role(Port.ROLE_DESIGNATED)
                logging.debug(
                    f"GVM {hex(self.id)} (Root) sends BPDU {bpdu_to_send} via port {p.num}.")
        else:
            # As a non-root bridge, it must decide the role for each port.
            for p in self.ports:
                # If this GVM offers a better path than the neighbor on this port, it becomes Designated.
                if p.best_bpdu and current_best_bpdu.get_best(p.best_bpdu) == current_best_bpdu:
                    p.send_bpdu(current_best_bpdu)
                    p.assign_role(Port.ROLE_DESIGNATED)
                    p.cost_to_root = None
                    logging.debug(
                        f"GVM {hex(self.id)} sends BPDU {current_best_bpdu} via port {p.num}.")
                # If this port is the best path to the root, it becomes the Root Port.
                elif p.num == root_port_num:
                    p.cost_to_root = current_best_bpdu.cost
                    p.assign_role(Port.ROLE_ROOT)
                # Otherwise, the port is blocked to prevent a loop.
                else:
                    p.cost_to_root = None
                    p.assign_role(Port.ROLE_UNDESIGNATED)

    def generate_report(self):
        """
        Reports the final converged state of the GVM and its ports. This shows
        the result of the distributed computation: a stable, logical tree topology.
        """
        root_status = "This GVM is the Root." if self.is_root else ""
        print(f"GVM: {self.label}:")
        print(f"ID: {hex(self.id)}. {root_status}")

        row_format = "{:<8} {:<15} {:<15} {:<8} {:<15}"
        print("-" * 65)
        print(row_format.format('Port', 'Role', 'Status', 'Cost', 'Cost-to-Root'))
        print("-" * 65)
        for p in sorted(self.ports, key=lambda x: x.num):
            cost_to_root_str = p.cost_to_root if p.cost_to_root is not None else '-'
            print(row_format.format(
                p.num, p.role, p.status, p.cost, cost_to_root_str))
        print()


class N2N_Lattice(object):
    """
    Represents the physical network, a "Neighbor-to-Neighbor" (N2N) lattice of
    interconnected GVMs. This class is responsible for parsing a static network
    description and constructing the corresponding dynamic object model that the
    emulator can operate on. This represents the "groundplane" upon which logical
    and virtual trees are built.
    """

    # Per IEEE 802.1D standard, port costs are derived from link speed.
    # This provides a simple metric for finding the "cheapest" path, which
    # generally corresponds to the highest bandwidth path.
    PORT_COST_MAP = {
        10: 100,      # 10 Mbps
        100: 19,      # 100 Mbps
        1000: 4,      # 1 Gbps
        10000: 2      # 10 Gbps
    }

    def __init__(self):
        self.gvms = {}

    def get_gvm(self, label, id):
        """Retrieves or creates a GVM instance."""
        if id in self.gvms:
            return self.gvms[id]
        gvm = GraphVirtualMachine(label, id)
        self.gvms[id] = gvm
        return gvm

    def get_all_gvms(self):
        """Returns all GVMs in the lattice."""
        return self.gvms.values()

    def connect_nodes(self, gvm1, port1_num, gvm2, port2_num, speed):
        """Creates a bidirectional link between two ports on two GVMs."""
        cost = self.PORT_COST_MAP.get(speed, 19) # Default to 100 Mbps cost
        port1 = Port(port1_num, cost)
        port2 = Port(port2_num, cost)
        port1.connect_to(port2)
        port2.connect_to(port1)
        gvm1.ports.append(port1)
        gvm2.ports.append(port2)


def build_lattice_from_dot(dot_data):
    """
    Parses a DOT string or file path describing the physical network topology
    and constructs an N2N_Lattice object. This function translates a static
    graph definition into a live, emulated structure.
    """
    try:
        if os.path.exists(dot_data):
            graph = nx.drawing.nx_pydot.read_dot(dot_data)
        else:
            pydot_graph = pydot.graph_from_dot_data(dot_data)[0]
            graph = nx.drawing.nx_pydot.from_pydot(pydot_graph)
    except Exception as e:
        print(f"Error: Failed to parse DOT data. Ensure 'pydot' is installed and the data is valid.")
        print(f"({e})")
        sys.exit(1)

    lattice = N2N_Lattice()
    node_map = {}

    # Create GVMs from node definitions in the DOT file.
    for node_label, attributes in graph.nodes.data():
        # JUDICIOUS MODIFICATION: This check ensures we only instantiate GVMs for the
        # primary switch nodes defined in the DOT file. It filters out the ephemeral
        # node objects (e.g., "SW1:1") that the parsing library creates for port
        # endpoints, thus correcting the "ghost GVM" bug.
        if ':' in node_label:
            continue

        # This is the corrected section. Parsing attributes from pydot can include
        # quotes, which must be stripped before converting to a number.
        mac = attributes.get('mac', '00:00:00:00:00:00').strip('\'"')
        priority_str = attributes.get('priority', '32768').strip('\'"')
        priority = int(priority_str)
        
        # The Bridge ID is a concatenation of a 16-bit priority and a 48-bit MAC address.
        bridge_id = priority * (2**48) + int(EUI(mac))
        node_map[node_label] = bridge_id
        lattice.get_gvm(node_label, bridge_id)

    # Create links from edge definitions.
    for source, dest, attributes in graph.edges.data():
        source_label, source_port_str = source.split(':')
        dest_label, dest_port_str = dest.split(':')
        source_port = int(source_port_str)
        dest_port = int(dest_port_str)

        gvm1 = lattice.get_gvm(source_label, node_map[source_label])
        gvm2 = lattice.get_gvm(dest_label, node_map[dest_label])
        speed = int(attributes.get('speed', '100').strip('\'"'))
        lattice.connect_nodes(gvm1, source_port, gvm2, dest_port, speed)

    return lattice


# Default simulation parameters
DEFAULT_STEPS = 5
LOG_FILE_NAME = 'daedalus_stp_emulator.log'
# To make the emulator self-contained and easily demonstrable, we define a default
# N2N Lattice topology that will be used if no input file is provided.
# This topology includes a loop, which allows the Spanning Tree Protocol
# to demonstrate its primary function of creating a loop-free logical tree.
DEFAULT_DOT_TOPOLOGY = """
graph testnet {
    node [mac="00:00:00:00:01:01"];
    SW1 [priority="4096"];
    node [mac="00:00:00:00:01:02"];
    SW2 [priority="8192"];
    node [mac="00:00:00:00:01:03"];
    SW3;

    SW1:1 -- SW2:1 [speed="1000"];
    SW2:2 -- SW3:1 [speed="100"];
    SW3:2 -- SW1:2 [speed="1000"];
}
"""

def main():
    """
    Main execution function. Parses arguments, sets up logging, builds the
    network, runs the simulation, and reports the results.
    """
    parser = argparse.ArgumentParser(
        description="A Dædælus-inspired emulator for the Spanning Tree Protocol."
    )
    parser.add_argument("-i", "--infile", required=False, default=None, help="Input DOT file describing the network topology. Runs a default demo if not provided.")
    parser.add_argument("-s", "--steps", type=int, default=DEFAULT_STEPS, help=f"Number of simulation steps. Default: {DEFAULT_STEPS}.")
    parser.add_argument("-l", "--loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="Set the logging level (outputs to log file).")
    args = parser.parse_args()

    # Configure logging
    if args.loglevel:
        log_level = getattr(logging, args.loglevel.upper())
        logging.basicConfig(filename=LOG_FILE_NAME, filemode='w', level=log_level,
                            format='%(levelname)s:%(name)s:%(message)s')
    else:
        logging.basicConfig(filename=LOG_FILE_NAME, filemode='w', level=logging.INFO,
                            format='%(levelname)s:%(name)s:%(message)s')
    
    if args.infile:
        logging.info(f"Reading network definition from: {args.infile}")
        dot_data = args.infile
    else:
        logging.info("No input file provided. Using default built-in topology.")
        dot_data = DEFAULT_DOT_TOPOLOGY

    # Build the N2N Lattice from the specified DOT file or default string.
    lattice = build_lattice_from_dot(dot_data)

    logging.info("Simulation starting: All GVMs are booting.")
    # Boot all GVMs, initializing their STP state.
    for gvm in lattice.get_all_gvms():
        gvm.boot()

    # The core simulation loop. The network will iterate until it reaches a
    # stable, converged state. The number of steps should be at least the
    # diameter of the network to ensure convergence.
    logging.info(f"Running STP convergence for {args.steps} steps.")
    for i in range(args.steps):
        logging.debug(f"Entering Simulation Step: {i}")
        for gvm in lattice.get_all_gvms():
            gvm.process_bpdu_exchange()

    logging.info("Simulation completed. The logical tree has converged.")
    print("\n--- Spanning Tree Protocol Emulation Report ---")

    # Print the final report for each GVM.
    for gvm in sorted(lattice.get_all_gvms(), key=lambda x: x.label):
        gvm.generate_report()


if __name__ == "__main__":
    main()