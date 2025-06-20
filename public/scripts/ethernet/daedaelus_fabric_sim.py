#
# File: ddl_emulator/simulations/daedaelus_fabric_sim.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#
# (c) 2025 Dædælus Research. All rights reserved.
#

import heapq
import random
import json
import os
from collections import namedtuple, deque

# --- Message and State Definitions ---
# Modeled after the AitPacket.msg structure from the OMNeT++ example.
# This represents an Atomic Information Transfer (AIT) packet. The AIT protocol
# transfers tokens across a link atomically (all or nothing). This is a
# timestamp-free, event-only link protocol, with formal verification.
AitPacket = namedtuple('AitPacket', ['type', 'transaction_id', 'source_node', 'destination_node', 'payload', 'route'])

# Enum for packet types
AIT_REQUEST = 0
AIT_ACK = 1

class Simulation:
    """
    An event-driven simulation environment, replacing the OMNeT++ kernel.
    It manages a priority queue of events to process them in chronological order.
    """
    def __init__(self):
        self.current_time = 0
        self.event_queue = []

    def schedule_at(self, delay, event):
        heapq.heappush(self.event_queue, (self.current_time + delay, event))

    def run(self, until):
        while self.event_queue and self.current_time < until:
            time, event = heapq.heappop(self.event_queue)
            # A failure in a scheduled event should not stop the entire simulation
            try:
                # In an event-driven simulation, time advances to the moment of the next event.
                self.current_time = time
                event.handle()
            except Exception as e:
                print(f"[{self.current_time:.6f}s] SIMULATION ERROR: {e}\n")


class Cell:
    """
    Models a Cell, an autonomous unit of compute, storage, and packet processing.
    This class translates the logic from the Cell.ned, Cell.h, and Cell.cc files.
    """
    def __init__(self, simulation, node_id, fabric, state_dump_file=""):
        self.simulation = simulation
        self.node_id = node_id
        self.fabric = fabric
        # Adjacency list: port_id -> (neighbor_cell, link_delay, neighbor_port_id)
        self.ports = {}
        # State of each link: port_id -> {'busy': bool, 'timeout_event': SimEvent, 'transaction_id': int}
        self.link_states = {}

        # This JSON dump allows for a "precise information-theoretic emulator"
        # to enable competitive interactions for "Digital Twins".
        self.state_dump_file = state_dump_file
        self.state_dump = None
        self.first_dump = True
        if self.state_dump_file:
            os.makedirs(os.path.dirname(self.state_dump_file), exist_ok=True)
            self.state_dump = open(self.state_dump_file, "w")
            self.state_dump.write("{\"snapshots\": [\n")

    def connect(self, port_id, neighbor_cell, link_delay, neighbor_port_id):
        self.ports[port_id] = (neighbor_cell, link_delay, neighbor_port_id)
        timeout_event = self.SimulationEvent(self, msg_name="linkTimeout", context=port_id)
        self.link_states[port_id] = {'busy': False, 'timeout_event': timeout_event, 'transaction_id': -1}

    def handle_message(self, msg, arrival_port):
        if msg.type == AIT_REQUEST:
            self._handle_ait_request(msg, arrival_port)
        elif msg.type == AIT_ACK:
            self._handle_ait_ack(msg, arrival_port)

    def _handle_ait_request(self, pkt, arrival_port):
        # This implements the "I Know That You Know That I Know (IKTYKTIK)" property.
        # The cell receives a request and must acknowledge it to complete the atomic transfer.
        if pkt.destination_node == self.node_id:
            print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: Request for transaction {pkt.transaction_id} from {pkt.source_node} arrived. Sending ACK.")
            
            # Create the reverse route for the ACK
            reverse_route = list(reversed(pkt.route))

            ack = AitPacket(
                type=AIT_ACK, 
                transaction_id=pkt.transaction_id, 
                source_node=self.node_id, 
                destination_node=pkt.source_node, 
                payload="ACK", 
                route=reverse_route
            )
            self.send(ack, arrival_port)
        else:
            # This demonstrates Relative Address-Free Routing. The cell forwards
            # the packet along the pre-computed route provided by the GVM.
            self._forward_packet(pkt)
        
        self._dump_state()

    def _handle_ait_ack(self, pkt, arrival_port):
        # Receiving an ACK completes the "reversible subtransaction". The sender now knows the
        # receiver has the packet, achieving exactly-once semantics without timeouts.
        # This is the core of the Truncated Tail Latency protocol.
        if pkt.destination_node == self.node_id:
            # I am the original requester. The transaction is complete.
            port_to_clear = -1
            for port_id, state in self.link_states.items():
                if state['busy'] and state['transaction_id'] == pkt.transaction_id:
                    port_to_clear = port_id
                    break
            
            if port_to_clear != -1:
                print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: FINAL ACK for transaction {pkt.transaction_id} received. Transaction successful.")
                self.link_states[port_to_clear]['timeout_event'].cancel()
                self.link_states[port_to_clear]['busy'] = False
                self.link_states[port_to_clear]['transaction_id'] = -1
            else:
                print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: WARNING - Received stale/unexpected final ACK for transaction {pkt.transaction_id}.")
        else:
            # I am an intermediate node. I must forward the ACK back.
            # First, receiving this ACK means my forward-leg of the transaction was successful.
            # I can clear the timeout for the port on which I forwarded the request.
            port_to_clear = -1
            for port_id, state in self.link_states.items():
                if state['busy'] and state['transaction_id'] == pkt.transaction_id:
                    port_to_clear = port_id
                    break
            
            if port_to_clear != -1:
                print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: Clearing transaction {pkt.transaction_id} timeout on outgoing port {port_to_clear}.")
                self.link_states[port_to_clear]['timeout_event'].cancel()
                self.link_states[port_to_clear]['busy'] = False
                self.link_states[port_to_clear]['transaction_id'] = -1
            
            # Now, forward the ACK packet back along the reverse route.
            self._forward_packet(pkt)
        
        self._dump_state()

    def _forward_packet(self, pkt):
        if pkt.route:
            try:
                # Find my own index in the route to determine the next hop.
                my_index_in_route = pkt.route.index(self.node_id)
                if my_index_in_route + 1 < len(pkt.route):
                    next_hop_node_id = pkt.route[my_index_in_route + 1]
                    
                    out_port = -1
                    # Find the local port that connects to the next hop.
                    for port, (neighbor, _, _) in self.ports.items():
                        if neighbor.node_id == next_hop_node_id:
                            out_port = port
                            break
                    
                    if out_port != -1:
                        pkt_type_str = "Request" if pkt.type == AIT_REQUEST else "ACK"
                        print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: Forwarding {pkt_type_str} for {pkt.destination_node} towards next hop {next_hop_node_id} on port {out_port}.")
                        self.send(pkt, out_port)
                    else:
                        print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: ERROR - No physical port to next hop {next_hop_node_id}.")
                else:
                    print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: ERROR - I am the last hop in route, but packet is not for me.")
            except ValueError:
                print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: ERROR - My ID is not in the packet's route list: {pkt.route}.")
        else:
            print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: ERROR - No route information in packet.")

    def send(self, pkt, port_id):
        if self.link_states.get(port_id, {}).get('busy', True) and pkt.type == AIT_REQUEST:
            print(f"[{self.simulation.current_time:.6f}s] Node {self.node_id}: Port {port_id} is busy, cannot send request.")
            return

        neighbor_cell, link_delay, neighbor_port_id = self.ports[port_id]
        event = self.SimulationEvent(neighbor_cell, msg=pkt, arrival_port=neighbor_port_id)
        self.simulation.schedule_at(link_delay, event)

        if pkt.type == AIT_REQUEST:
            self.link_states[port_id]['busy'] = True
            self.link_states[port_id]['transaction_id'] = pkt.transaction_id
            self.link_states[port_id]['timeout_event'].schedule(2 * link_delay + 1e-6)
            self._dump_state()

    def _dump_state(self):
        if not self.state_dump:
            return
        if not self.first_dump:
            self.state_dump.write(",\n")
        self.first_dump = False
        state = {
            "time": self.simulation.current_time,
            "node_id": self.node_id,
            "ports": [
                {"port_id": i, "status": "busy" if self.link_states.get(i, {}).get('busy', False) else "idle"}
                for i in sorted(self.ports.keys())
            ]
        }
        self.state_dump.write(json.dumps(state, indent=4))
        self.state_dump.flush()

    def finish(self):
        if self.state_dump:
            self.state_dump.write("\n]}\n")
            self.state_dump.close()
        for port_id in self.link_states:
            if self.link_states[port_id]['timeout_event'].is_scheduled:
                self.link_states[port_id]['timeout_event'].cancel()

    class SimulationEvent:
        def __init__(self, target_cell, msg=None, msg_name=None, context=None, arrival_port=None):
            self.target_cell = target_cell
            self.msg = msg
            self.msg_name = msg_name
            self.arrival_port = arrival_port
            self.context = context
            self.is_cancelled = False
            self.is_scheduled = False

        def handle(self):
            self.is_scheduled = False
            if not self.is_cancelled:
                if self.msg_name == "linkTimeout":
                    port_index = self.context
                    print(f"[{self.target_cell.simulation.current_time:.6f}s] Node {self.target_cell.node_id}: Timeout on port {port_index}. Transaction failed.")
                    if port_index in self.target_cell.link_states:
                        self.target_cell.link_states[port_index]['busy'] = False
                        self.target_cell.link_states[port_index]['transaction_id'] = -1
                        self.target_cell._dump_state()
                else:
                    self.target_cell.handle_message(self.msg, self.arrival_port)

        def schedule(self, delay):
            self.is_cancelled = False
            self.is_scheduled = True
            self.target_cell.simulation.schedule_at(delay, self)

        def cancel(self):
            self.is_cancelled = True
            self.is_scheduled = False


class GVMController:
    """
    The Graph Virtual Machine (GVM) Controller orchestrates the network.
    It enables Transaction-Multiplexing, where instead of allowing flows to fight for
    bandwidth, it interleaves atomic request/reply transactions.
    """
    def __init__(self, simulation, fabric):
        self.simulation = simulation
        self.fabric = fabric
        self.transaction_id = 0

    def start(self):
        event = self.SimulationEvent(self, "scheduleTransaction")
        self.simulation.schedule_at(1e-6, event)

    def handle_message(self, msg_name):
        if msg_name == "scheduleTransaction":
            self._schedule_transaction()
            event = self.SimulationEvent(self, "scheduleTransaction")
            self.simulation.schedule_at(25e-6, event)

    def _schedule_transaction(self):
        num_cells = len(self.fabric.cells)
        if num_cells < 2: return

        source_id = random.randint(0, num_cells - 1)
        dest_id = random.randint(0, num_cells - 1)
        while dest_id == source_id:
            dest_id = random.randint(0, num_cells - 1)
        source_cell = self.fabric.cells[source_id]

        # The GVM computes a valid path through the fabric. This models the "Manage on a Tree"
        # aspect of the Daedaelus philosophy, where the route is determined before transmission.
        route = self.fabric.find_route(source_id, dest_id)

        if not route or len(route) < 2:
            print(f"[{self.simulation.current_time:.6f}s] GVM: No valid route found from {source_id} to {dest_id}. Aborting transaction.")
            return

        req_packet = AitPacket(
            type=AIT_REQUEST, transaction_id=self.transaction_id,
            source_node=source_id, destination_node=dest_id,
            payload=f"Transaction {self.transaction_id} data.", route=route
        )
        self.transaction_id += 1

        # The GVM selects an output port based on the first hop of the computed route.
        out_port = -1
        next_hop_id = route[1]
        for port, (neighbor, _, _) in source_cell.ports.items():
             if neighbor.node_id == next_hop_id and not source_cell.link_states[port]['busy']:
                out_port = port
                break

        if out_port != -1:
            print(f"[{self.simulation.current_time:.6f}s] GVM: Scheduling transaction from {source_id} to {dest_id}. Route: {route}. First hop via port {out_port}.")
            source_cell.send(req_packet, out_port)
        else:
            print(f"[{self.simulation.current_time:.6f}s] GVM: All ports on Node {source_id} towards next hop {next_hop_id} are busy. Deferring transaction.")

    class SimulationEvent:
        def __init__(self, target, msg_name):
            self.target = target
            self.msg_name = msg_name
        def handle(self):
            self.target.handle_message(self.msg_name)

class DaedaelusFabric:
    """
    This class translates the DaedaelusFabric.ned network definition. It constructs
    the N2N Lattice by creating and connecting a grid of Cells.
    """
    def __init__(self, simulation, num_rows=3, num_cols=3):
        self.cells = [Cell(simulation, i, self, f"results/cell{i}_state.json") for i in range(num_rows * num_cols)]
        self.num_rows = num_rows
        self.num_cols = num_cols

        ports_used = [0] * len(self.cells)
        for r in range(num_rows):
            for c in range(num_cols):
                cell_index = r * num_cols + c
                current_cell = self.cells[cell_index]
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < num_rows and 0 <= nc < num_cols:
                            neighbor_index = nr * num_cols + nc
                            if neighbor_index > cell_index:
                                neighbor_cell = self.cells[neighbor_index]
                                local_port_id = ports_used[cell_index]
                                neighbor_port_id = ports_used[neighbor_index]
                                current_cell.connect(local_port_id, neighbor_cell, 5e-9, neighbor_port_id)
                                neighbor_cell.connect(neighbor_port_id, current_cell, 5e-9, local_port_id)
                                ports_used[cell_index] += 1
                                ports_used[neighbor_index] += 1

    def find_route(self, start_node_id, end_node_id):
        queue = deque([[start_node_id]])
        visited = {start_node_id}
        while queue:
            path = queue.popleft()
            node_id = path[-1]
            if node_id == end_node_id:
                return path
            for port_id in sorted(self.cells[node_id].ports.keys()):
                neighbor, _, _ = self.cells[node_id].ports[port_id]
                if neighbor.node_id not in visited:
                    visited.add(neighbor.node_id)
                    new_path = list(path)
                    new_path.append(neighbor.node_id)
                    queue.append(new_path)
        return None

if __name__ == "__main__":
    sim = Simulation()
    fabric = DaedaelusFabric(sim, num_rows=3, num_cols=3)
    controller = GVMController(sim, fabric)

    print("--- Starting Daedaelus Fabric Simulation ---")
    print(f"Created a {fabric.num_rows}x{fabric.num_cols} N2N Lattice with {len(fabric.cells)} Cells.")
    print("GVM Controller will now schedule atomic transactions.")
    print("---------------------------------------------")

    controller.start()
    sim.run(until=1e-3)

    for cell in fabric.cells:
        cell.finish()

    print("\n-------------------------------------------")
    print("Simulation finished.")