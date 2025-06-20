import sys
import simpy
import math
import numpy as np
import matplotlib.pyplot as plt
import random

# This simulation models the foundational principles of a shared broadcast
# communication system. Like the historical luminiferous ether, our simulated
# medium, the Ether, is a passive broadcast channel with no central control.
class G:
    RANDOM_SEED = 33
    SIM_TIME = 100000  # Simulation time should be sufficiently long for statistical convergence.
    SLOT_TIME = 1      # The fundamental unit of time, the slot, is the maximum time
                       # between starting a transmission and detecting a collision.
    N = 30             # The number of contending stations on the Ether.
    ARRIVAL_RATES = [0.001, 0.002, 0.003, 0.004, 0.006, 0.012, 0.018, 0.024, 0.027, 0.030]
    RETRANMISSION_POLICIES = ["pp", "op", "beb", "lb"]
    LONG_SLEEP_TIMER = 1000000000

# The Server_Process represents the shared communication facility, the Ether.
# It is a passive medium where coordination of access is distributed among
# the contending stations using controlled statistical arbitration.
class Server_Process(object):
    def __init__(self, env, dictionary_of_nodes, retran_policy, slot_stat):
        self.env = env
        self.dictionary_of_nodes = dictionary_of_nodes
        self.retran_policy = retran_policy
        self.slot_stat = slot_stat
        self.current_slot = 0
        self.action = env.process(self.run())

        self.collision = False
        self.nodes_transmitting = 0
        self.successful_Tx = 0

    def run(self):
        # The server process models the progression of time in discrete slots.
        # In each slot, it arbitrates access to the Ether based on the actions
        # of the distributed station controllers.
        while True:
            yield self.env.timeout(G.SLOT_TIME)

            # Determine the state of the Ether for the current slot: idle,
            # successful transmission, or collision.
            self.collision = False
            self.nodes_transmitting = 0

            # Each station's controller independently decides whether to transmit.
            for i in range(1, G.N + 1):
                if (self.dictionary_of_nodes[i].packets > 0) and (self.dictionary_of_nodes[i].scheduled_slot == self.current_slot):
                    self.nodes_transmitting += 1

            # Packets which overlap in time on the Ether are said to collide;
            # they interfere so as to be unrecognizable by a receiver.
            if self.nodes_transmitting > 1:
                self.collision = True

            if self.collision:
                # When a collision is detected, each participating station must back off.
                # The retransmission policy dictates how the new random retransmission
                # interval is chosen. This distributed algorithm is key to managing contention.

                if self.retran_policy == "pp": # p-persistent ALOHA
                    random_list = [1, 2]
                    distribution = [0.5, 0.5]
                    for i in range(1, G.N + 1):
                        node = self.dictionary_of_nodes[i]
                        if (node.packets > 0) and (node.scheduled_slot == self.current_slot):
                            if random.choices(random_list, distribution)[0] == 1:
                                node.scheduled_slot = self.current_slot + 1
                            node.attempts += 1
                        elif node.attempts > 0: # Node was waiting but another collision occurred
                            if random.choices(random_list, distribution)[0] == 1:
                                node.scheduled_slot = self.current_slot + 1
                            node.attempts += 1

                elif self.retran_policy == "op": # optimal p-persistent ALOHA
                    p = 1.0 / G.N
                    random_list = [1, 2]
                    distribution = [p, 1 - p]
                    for i in range(1, G.N + 1):
                        node = self.dictionary_of_nodes[i]
                        if (node.packets > 0) and (node.scheduled_slot == self.current_slot):
                            if random.choices(random_list, distribution)[0] == 1:
                                node.scheduled_slot = self.current_slot + 1
                            node.attempts += 1
                        elif node.attempts > 0:
                            if random.choices(random_list, distribution)[0] == 1:
                                node.scheduled_slot = self.current_slot + 1
                            node.attempts += 1

                elif self.retran_policy == "beb":
                    # This implements Binary Exponential Backoff. A station recovers from a
                    # detected collision by abandoning the attempt and retransmitting the
                    # packet after some dynamically chosen random time period.
                    for i in range(1, G.N + 1):
                        node = self.dictionary_of_nodes[i]
                        if (node.scheduled_slot == self.current_slot) and (node.packets > 0):
                            k = min(node.attempts, 10)
                            backoff_slots = random.randint(0, (2**k) - 1)
                            node.scheduled_slot = self.current_slot + 1 + backoff_slots
                            node.attempts += 1

                elif self.retran_policy == "lb": # Linear Backoff
                    for i in range(1, G.N + 1):
                        node = self.dictionary_of_nodes[i]
                        if (node.scheduled_slot == self.current_slot) and (node.packets > 0):
                            k = min(node.attempts, 1024)
                            backoff_slots = random.randint(0, k)
                            node.scheduled_slot = self.current_slot + 1 + backoff_slots
                            node.attempts += 1
            else: # No collision
                # If a slot contains only one attempted transmission, the Ether has been acquired.
                for i in range(1, G.N + 1):
                    node = self.dictionary_of_nodes[i]
                    if (node.packets > 0) and (node.scheduled_slot == self.current_slot):
                        self.successful_Tx += 1
                        node.packets -= 1
                        node.attempts = 0 # Reset attempts on successful transmission
                        # If the node has more packets, it will contend for the very next slot.
                        if (node.packets > 0):
                            node.scheduled_slot = self.current_slot + 1
                    # This logic for pp/op re-rolling on idle slots appears complex and may
                    # differ from standard interpretations. It's preserved from the original.
                    elif node.attempts > 0 and (self.retran_policy in ["op", "pp"]):
                        p = 0.5 if self.retran_policy == "pp" else 1.0 / G.N
                        if random.random() < p:
                            node.scheduled_slot = self.current_slot + 1
                        node.attempts += 1

            self.nodes_transmitting = 0
            self.current_slot += 1

# Each Node_Process represents a single computing station attempting to
# communicate on the shared Ether. It generates packets and interacts
# with its controller to schedule transmissions.
class Node_Process(object):
    def __init__(self, env, id, arrival_rate):
        self.env = env
        self.id = id
        self.arrival_rate = arrival_rate

        # State variables for the station's controller.
        self.attempts = 0         # Collision counter for the current packet.
        self.scheduled_slot = 0   # The slot this node is scheduled to attempt transmission in.
        self.packets = 0          # The number of packets in the node's output queue.

        self.action = env.process(self.run())

    def run(self):
        # This process models packet arrivals at the station, following a
        # Poisson process with the specified arrival rate.
        while True:
            # Time until the next packet arrival.
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            self.packets += 1
            # If the station was idle, the new packet can be transmitted immediately.
            # The controller schedules the attempt for the very next slot.
            if self.packets == 1:
                self.scheduled_slot = math.ceil(self.env.now)

# A simple data structure to represent a packet.
class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time

# A helper class for collecting statistics during the simulation.
class StatObject(object):
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)

def main():
    # This simulation computationally explores the performance of a local computer
    # network under various statistical arbitration schemes.
    random.seed(G.RANDOM_SEED)

    # Allow for command-line overrides of simulation parameters.
    if len(sys.argv) > 1:
        G.N = int(sys.argv[1])
        G.RETRANMISSION_POLICIES = [str(sys.argv[2])]
        G.ARRIVAL_RATES = [float(sys.argv[3])]

    # Iterate through each retransmission policy to compare performance.
    for retran_policy in G.RETRANMISSION_POLICIES:
        load_points = []
        throughput_points = []
        # Test each policy across a range of traffic loads.
        for arrival_rate in G.ARRIVAL_RATES:
            env = simpy.Environment()
            dictionary_of_nodes = {}

            # Instantiate N station processes.
            for i in range(1, G.N + 1):
                node = Node_Process(env, i, arrival_rate)
                dictionary_of_nodes[i] = node
            # Instantiate the single Ether (Server) process.
            server_process = Server_Process(env, dictionary_of_nodes, retran_policy, None)
            env.run(until=G.SIM_TIME)

            # Calculate the resulting throughput for this configuration.
            # Throughput is the rate of successful packet transmissions over the Ether.
            throughput = server_process.successful_Tx / G.SIM_TIME
            load = arrival_rate * G.N
            
            print(f"Policy: {retran_policy}, Load: {load:.3f}, Throughput: {throughput:.4f}")
            
            load_points.append(load)
            throughput_points.append(throughput)
        
        # Plot the performance curve for the policy.
        plt.plot(load_points, throughput_points, marker='o', linestyle='-', label=retran_policy)
    
    # Finalize and display the plot if not running in batch mode.
    if len(sys.argv) < 2:
        plt.legend()
        plt.title("Ethernet Contention: Throughput vs. Offered Load")
        plt.xlabel("Offered Load (λ * N)")
        plt.ylabel("Throughput (packets/slot)")
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    main()