# -*- coding: utf-8 -*-
"""
SEtSim: A Python-based Switched Ethernet Simulator

This script provides a comprehensive simulation of switched Ethernet protocols,
ported from the original SEtSim (rev 3.0) implemented in Matlab/Simulink.
It encapsulates the behavior of nodes, switches, and master controllers to model
network traffic and analyze message latency.

Copyright 2013-2024 Mohammad Ashjaei, Daedaelus Research
This code is an inspired translation and extension of the original work.
"""

import math
import pprint

# =============================================================================
# DÆDÆLUS PHILOSOPHICAL CONTEXT
#
# This simulator models a conventional switched Ethernet environment. It is a
# digital reenactment of the very architectural principles we, at Daedaelus,
# seek to transcend. The concepts you will see—centralized master nodes for
# scheduling, priority-based queuing, and complex, multi-window timing
# cycles—are all sophisticated workarounds for a fundamental problem: the
# lack of inherent reliability and determinism in the underlying packet
# transport mechanism.
#
# As stated in our foundational text, "Bandwidth Works in Practice, not in
# Theory," such systems treat the network as a best-effort, "lossy pipe,"
# pushing the burden of reliability and order onto higher-level protocols
# or, as seen here, a centralized scheduler. This results in complex,
# fragile, and ultimately non-deterministic systems.
#
# In contrast, the Daedaelus architecture, through its Graph Virtual Machine
# (GVM) and Neighbor-to-Neighbor (N2N) Lattice, embeds reliability directly
# into the link via 'reversible transactions'. We do not patch over ambiguity;
# we design it out of the system. This simulation, therefore, serves as a
# crucial point of contrast—a "Code as Proof" of the complexity we can
# eliminate when the network itself becomes a trustworthy, deterministic fabric.
# =============================================================================


# =============================================================================
# Helper Functions & Queue Management
#
# In the original SEtSim, queue management is handled by a series of
# separate .m files. Here, we consolidate this logic into a set of helper
# functions that operate on Python lists, which serve as our queues. The
# `insert_to_ascend` function is particularly important, as it embodies the
# core logic of priority queuing—a mechanism for arbitrating contention,
# which is a primary symptom of a non-deterministic network fabric.
# =============================================================================

def insert(queue, data):
    """Inserts data into a queue. Simplified from original to just append."""
    if data is not None:
        queue.append(data)
    return queue

def remove_msg(queue, msg_id):
    """Removes a specific message from a queue."""
    if msg_id in queue:
        queue.remove(msg_id)
    return queue

def get_head(queue):
    """Gets the first element of a queue, returning 0 if empty."""
    return queue[0] if queue else 0

def insert_to_ascend(queue, message_id, msg_structs):
    """
    Inserts a message ID into a queue, sorted by priority (ascending).
    Lower priority number means higher priority.
    This function is a direct translation of the priority queuing mechanism
    used to manage contention at the master and switch levels.
    """
    # Remove any placeholder zeros before sorting
    temp_list = [(msg_structs[qid].prio, qid) for qid in queue if qid != 0]
    
    # Add the new message
    if message_id in msg_structs:
        temp_list.append((msg_structs[message_id].prio, message_id))
    
    # Sort based on priority (the first element of the tuple)
    temp_list.sort(key=lambda x: x[0])
    
    # Reconstruct the queue with only message_ids
    return [item[1] for item in temp_list]


class Message:
    """
    Represents a data message, translating the Matlab 'message' struct.
    This object is a "token," carrying with it not just data, but the identity,
    priority, and routing information required to navigate a conventional
    switched network. In our Daedaelus system, much of this state would be
    an intrinsic property of the 'reversible transaction' on the link itself,
    not metadata to be interpreted by central schedulers.
    """
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.prio = kwargs.get('prio', 1)
        self.exec = kwargs.get('exec', 0.010) # Execution time in ms
        self.gType = kwargs.get('gType', 0) # 0: Local, 1: Global
        self.pType = kwargs.get('pType', 0) # 0: Periodic, 1: Aperiodic
        self.period = kwargs.get('period', 5) # Period in ECs
        self.deadline = kwargs.get('deadline', 5)
        self.dynPeriod = kwargs.get('dynPeriod', self.period if self.pType == 1 else 0)
        self.sourceMasterNumber = kwargs.get('sourceMasterNumber', 1)
        self.source = kwargs.get('source', 1)
        self.dest = kwargs.get('dest', 2)
        self.destMasterNumber = kwargs.get('destMasterNumber', 1)
        self.SwitchInRout = kwargs.get('SwitchInRout', [])
        self.SwitchPort = kwargs.get('SwitchPort', [])
        self.tickCount = kwargs.get('tickCount', self.period - 1)
        self.readyTime = kwargs.get('readyTime', 0)
        self.receiveTime = kwargs.get('receiveTime', 0)
        self.defNum = kwargs.get('defNum', 0) # Defragmentation number
        self.part = kwargs.get('part', 0)
        self.refMsgID = kwargs.get('refMsgID', self.id)
        self.cluster = kwargs.get('cluster', 0)
        self.ClParentMaster = kwargs.get('ClParentMaster', 0)
        self.offset = kwargs.get('offset', 0)

    def __repr__(self):
        return (f"Msg(id={self.id}, prio={self.prio}, src={self.source}, "
                f"dest={self.dest}, exec={self.exec:.4f})")

class Node:
    """Represents a slave node in the FTT-SE architecture."""
    def __init__(self, node_id, parent_master, segment_number, sw_port_number):
        self.id = node_id
        self.parentNumber = parent_master
        self.segmentNumber = segment_number
        self.swPortNumber = sw_port_number
        self.ap_req = []
        self.global_ap_req = []
        self.output_queue = []
        self.tm_rec = []
        self.asynch_tm_rec = []
        # State flags for state machine logic
        self.state1 = 0
        self.state2 = 0
        self.state3 = 0
        self.flagInput = 0


class Switch:
    """
    Represents an Ethernet switch.
    Its sole purpose is to route packets based on a pre-defined table,
    a stark contrast to the dynamic, address-free routing of an N2N Lattice.
    """
    def __init__(self, switch_id, port_count=16):
        self.id = switch_id
        self.port_nbr = port_count
        self.inBuffer = {p: [] for p in range(1, port_count + 1)}
        self.outBuffer = {p: [] for p in range(1, port_count + 1)}

class Master:
    """
    Represents a master node, the central controller for a segment or cluster.
    This is the "brain" of the conventional system, responsible for scheduling
    and bandwidth allocation. Its existence represents a single point of failure
    and a performance bottleneck—the very pattern the distributed control of the
    Daedaelus GVM is designed to avoid.
    """
    def __init__(self, master_id, EC, sim_config):
        self.id = master_id
        self.simTime = 0
        self.EC = EC
        self.nextHit = 0
        self.start_of_ec = 0
        self.state1 = 0
        self.state2 = 0
        self.tm_id = 0.5
        self.asynch_tm_id = 0.25
        self.tm_data = []
        self.asynch_tm_data = []
        self.tm_signal = []
        self.asynch_tm_signal = []
        self.local_sync_readyQ = []
        self.local_async_readyQ = []
        self.global_sync_readyQ = []
        self.global_async_readyQ = []
        self.outputMaster = []
        self.architect = sim_config['architect']
        self.bw_trackers = {}


class Simulator:
    """
    The main simulation engine, orchestrating the interactions between all
    network components over time.
    """
    def __init__(self, config):
        self.config = config
        self.time = 0.0
        self.sampleTime = config['sampleTime']
        self.messages = {}
        self.nodes = {}
        self.switches = {}
        self.masters = {}
        self.ready_time_buffer = {}
        self.receive_time_buffer = {}

        print("DÆDÆLUS-INSPIRED PYTHON SIMULATOR: INITIALIZING...")
        print(f"Simulating architecture: {config['architect_name']}")
        self._setup_network()
        self._declare_messages()
        self._defragment_messages()

    def _setup_network(self):
        """Initializes the network topology from the configuration."""
        print(f"Setting up {self.config['slave_number']} slaves, "
              f"{self.config['switch_number']} switches, "
              f"and {self.config['master_number']} masters.")

        for i in range(1, self.config['slave_number'] + 1):
            parent = 1
            seg = ((i - 1) // 3) + 1
            port = ((i - 1) % 3) + 7
            self.nodes[i] = Node(i, parent, seg, port)

        for i in range(1, self.config['switch_number'] + 1):
            self.switches[i] = Switch(i)

        for i in range(1, self.config['master_number'] + 1):
            self.masters[i] = Master(i, self.config['EC'], self.config)

    def _declare_messages(self):
        """Creates the initial set of messages to be transmitted."""
        msg_defs = [
            {'id': 1, 'prio': 1, 'exec': 0.010, 'gType': 1, 'pType': 0, 'period': 5, 'source': 4, 'dest': 7, 'sourceMasterNumber': 2, 'destMasterNumber': 3, 'SwitchInRout': [2, 1], 'SwitchPort': [2, 4]},
            {'id': 2, 'prio': 1, 'exec': 0.010, 'gType': 0, 'pType': 0, 'period': 5, 'source': 1, 'dest': 8, 'sourceMasterNumber': 1, 'destMasterNumber': 3, 'SwitchInRout': [1], 'SwitchPort': [4]},
            {'id': 3, 'prio': 1, 'exec': 0.010, 'gType': 0, 'pType': 1, 'period': 7, 'source': 2, 'dest': 1, 'sourceMasterNumber': 1, 'destMasterNumber': 1, 'SwitchInRout': [], 'SwitchPort': []},
            {'id': 4, 'prio': 2, 'exec': 0.015, 'gType': 1, 'pType': 0, 'period': 10, 'source': 5, 'dest': 9, 'sourceMasterNumber': 2, 'destMasterNumber': 3, 'SwitchInRout': [2, 1], 'SwitchPort': [3, 5]},
            {'id': 5, 'prio': 2, 'exec': 0.025, 'gType': 0, 'pType': 1, 'period': 12, 'source': 3, 'dest': 6, 'sourceMasterNumber': 1, 'destMasterNumber': 2, 'SwitchInRout': [1], 'SwitchPort': [2]}
        ]

        for m_def in msg_defs:
            msg = Message(**m_def)
            self.messages[msg.id] = msg
            # Use refMsgID for reporting buffers
            if msg.refMsgID not in self.ready_time_buffer:
                self.ready_time_buffer[msg.refMsgID] = []
                self.receive_time_buffer[msg.refMsgID] = []
        
        print(f"Declared {self.config['non_frag_msg']} initial message types.")

    def _defragment_messages(self):
        """
        Handles message defragmentation.
        This complexity arises from constraints on packet sizes in conventional
        networks. A Daedaelus link transaction would handle data more fluidly.
        """
        original_messages = list(self.messages.values())
        new_id_counter = len(self.messages) + 1
        
        for msg in original_messages:
            max_exec = 0.015
            if msg.exec > max_exec:
                msg.defNum = math.ceil(msg.exec / max_exec)
                part_exec = msg.exec / msg.defNum
                # Remove original message if it's going to be fragmented
                if msg.id in self.messages:
                    del self.messages[msg.id]
                
                for i in range(msg.defNum):
                    new_msg_def = msg.__dict__.copy()
                    new_msg_def['id'] = new_id_counter
                    new_msg_def['exec'] = part_exec
                    new_msg_def['part'] = i + 1
                    new_msg_def['refMsgID'] = msg.id
                    self.messages[new_id_counter] = Message(**new_msg_def)
                    new_id_counter += 1
        
        print(f"Message set size after defragmentation: {len(self.messages)} messages.")

    def run(self, simulation_time):
        """Main simulation loop."""
        print(f"\n--- Starting Simulation for {simulation_time:.4f} ms ---")
        while self.time <= simulation_time:
            self.update_masters()
            self.update_slaves()
            self.update_switches()
            self.time += self.sampleTime
        
        print("--- Simulation Finished ---")
        self.generate_report()

    def update_masters(self):
        """Simulates the logic of all master nodes for one time step."""
        for m_id, master in self.masters.items():
            if self.time >= master.nextHit:
                master.nextHit = self.time + master.EC
                master.start_of_ec = self.time
                master.state1 = 1
                master.outputMaster.append(master.tm_id)
            
            if master.state1 == 1 and self.time >= master.start_of_ec + self.config['tm_win']:
                master.state1 = 0
                master.state2 = 1
                for node in self.nodes.values():
                    if node.parentNumber == m_id:
                         for req_id in node.ap_req:
                             master.local_async_readyQ = insert_to_ascend(master.local_async_readyQ, req_id, self.messages)
                         node.ap_req = []

            if master.state2 == 1:
                for msg_id, msg in self.messages.items():
                    if msg.pType == 0 and msg.sourceMasterNumber == m_id:
                        msg.tickCount += 1
                        if msg.tickCount >= msg.period:
                            msg.tickCount = 0 - msg.offset
                            master.local_sync_readyQ = insert_to_ascend(master.local_sync_readyQ, msg_id, self.messages)
                            msg.readyTime = self.time + master.EC
                            self.ready_time_buffer[msg.refMsgID].append(msg.readyTime)

                master.tm_data.extend(master.local_sync_readyQ)
                master.tm_data.extend(master.local_async_readyQ)
                master.local_sync_readyQ, master.local_async_readyQ = [], []
                master.state2 = 0

            out_msg_id = get_head(master.outputMaster)
            if out_msg_id == master.tm_id:
                master.tm_signal = list(master.tm_data)
                master.tm_data = []

            if out_msg_id > 0:
                self.switches[master.id].inBuffer[1].append(out_msg_id)
                master.outputMaster.pop(0)

    def update_slaves(self):
        """Simulates the logic of all slave nodes."""
        for s_id, slave in self.nodes.items():
            master = self.masters.get(slave.segmentNumber)
            if not master: continue

            # Check for incoming signals from the switch
            in_port_q = self.switches[slave.segmentNumber].outBuffer[slave.swPortNumber]
            if get_head(in_port_q) == master.tm_id:
                slave.tm_rec = list(master.tm_signal)
                remove_msg(in_port_q, master.tm_id)
                slave.state1 = 1
            
            msg_id_in = get_head(in_port_q)
            if msg_id_in > 0:
                msg_in = self.messages.get(msg_id_in)
                if msg_in and msg_in.dest == s_id:
                    msg_in.receiveTime = self.time
                    self.receive_time_buffer[msg_in.refMsgID].append(self.time)
                    remove_msg(in_port_q, msg_id_in)

            if slave.state1 == 1:
                for msg_id, msg in self.messages.items():
                    if msg.source == s_id and msg.pType == 1:
                        msg.tickCount += 1
                        if msg.tickCount >= msg.dynPeriod:
                            msg.tickCount = 0 - msg.offset
                            slave.ap_req.append(msg_id)
                            msg.readyTime = self.time + self.config['EC']
                            self.ready_time_buffer[msg.refMsgID].append(msg.readyTime)
                slave.state1 = 0
                slave.state2 = 1

            if slave.state2 == 1:
                for msg_id in slave.tm_rec:
                    if self.messages[msg_id].source == s_id:
                        slave.output_queue.append(msg_id)
                slave.tm_rec = []
                slave.state2 = 0
                slave.state3 = 1
                
            out_msg_id = get_head(slave.output_queue)
            if out_msg_id > 0:
                self.switches[slave.segmentNumber].inBuffer[slave.swPortNumber].append(out_msg_id)
                slave.output_queue.pop(0)

    def update_switches(self):
        """Simulates the routing logic for all switches."""
        for sw_id, switch in self.switches.items():
            # Handle TM broadcast first (The crucial bug fix)
            tm_id = self.masters[sw_id].tm_id if sw_id in self.masters else 0.5
            if tm_id in switch.inBuffer.get(1, []):
                remove_msg(switch.inBuffer[1], tm_id)
                for port_out in range(2, switch.port_nbr + 1): # Broadcast to all other ports
                    switch.outBuffer[port_out].append(tm_id)
            
            # Handle data messages
            for port_in in range(1, switch.port_nbr + 1):
                if not switch.inBuffer[port_in]: continue
                
                # Process one message per input port per cycle
                msg_id = get_head(switch.inBuffer[port_in])
                if msg_id > 0 and msg_id != tm_id: # Ensure it's a data message
                    msg = self.messages.get(msg_id)
                    if not msg: continue

                    out_port = -1
                    if msg.destMasterNumber == sw_id:
                        if msg.dest in self.nodes:
                           out_port = self.nodes[msg.dest].swPortNumber
                    else:
                        try:
                            route_idx = msg.SwitchInRout.index(sw_id)
                            out_port = msg.SwitchPort[route_idx]
                        except (ValueError, IndexError):
                            pass

                    if out_port != -1:
                         switch.outBuffer[out_port].append(msg_id)
                    
                    remove_msg(switch.inBuffer[port_in], msg_id)
    
    def generate_report(self):
        """Calculates and prints the end-to-end delay for all messages."""
        print("\n--- Simulation Report ---")
        print(f"Total Original Messages: {self.config['non_frag_msg']}")
        print(f"EC Size: {self.config['EC'] * 10000:.0f} us")
        print("-" * 75)
        print("MsgID Prio Exec(us) Period(EC) Type G/L  Min(EC) Avg(EC) Max(EC) Received")
        print("-" * 75)

        for ref_id in range(1, self.config['non_frag_msg'] + 1):
            delays_ec = []
            if ref_id in self.receive_time_buffer and ref_id in self.ready_time_buffer:
                readies = self.ready_time_buffer[ref_id]
                receives = self.receive_time_buffer[ref_id]
                
                num_pairs = min(len(readies), len(receives))
                if num_pairs > 0:
                    delays = [(receives[i] - readies[i]) for i in range(num_pairs)]
                    delays_ec = [d / self.config['EC'] for d in delays]

            msg = next((m for m in self.messages.values() if m.refMsgID == ref_id and m.part == 0), None)
            if not msg:
                 msg = next((m for m in self.messages.values() if m.refMsgID == ref_id), None)
            
            if msg:
                 pType = "Per" if msg.pType == 0 else "Aper"
                 gType = "Glob" if msg.gType == 1 else "Loc"
                 if delays_ec:
                     print(f"{msg.refMsgID:<5d} {msg.prio:<4d} {msg.exec*10000:<7.0f} "
                           f"{msg.period:<9d} {pType:<4s} {gType:<4s} "
                           f"{min(delays_ec):<7.2f} {sum(delays_ec)/len(delays_ec):<7.2f} "
                           f"{max(delays_ec):<7.2f} {len(delays_ec):>8d}")
                 else:
                     print(f"{msg.refMsgID:<5d} {msg.prio:<4d} {msg.exec*10000:<7.0f} "
                           f"{msg.period:<9d} {pType:<4s} {gType:<4s} {'N/A':<7s} {'N/A':<7s} {'N/A':<7s} {0:>8d}")


if __name__ == '__main__':
    simulation_config = {
        'sampleTime': 0.005,
        'architect': 1,
        'architect_name': "Cluster-Based",
        'slave_number': 9,
        'switch_number': 3,
        'master_number': 3,
        'EC': 0.6,
        'tm_win': 0.02,
        'non_frag_msg': 5,
        'simulation_duration': 5.0
    }

    sim = Simulator(simulation_config)
    sim.run(simulation_config['simulation_duration'])

