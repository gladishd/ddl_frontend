# python ethernet13.py 20 beb 0.05
# DDL_Emulator: Ethernet Contention Protocol Simulation
#
# This script provides a precise information-theoretic emulator for studying the behavior
# of Ethernet's foundational contention protocol, Carrier Sense Multiple Access with
# Collision Detection (CSMA/CD). It models the dynamics of multiple stations
# competing for access to a shared, passive communication medium—the "Ether."
#
# As described in the original Metcalfe & Boggs paper, "Coordination of access to
# the Ether for packet broadcasts is distributed among the contending transmitting
# stations using controlled statistical arbitration." This simulation explores the
# efficiency and throughput of that statistical model under various loads and
# with different retransmission policies.
#
# The goal is to understand the inherent limitations of a system where packet
# collisions are a normal part of operation. Such systems punt reliability up the
# protocol stack, creating what "Bandwidth Works in Practice, not in Theory"
# describes as a situation where "once the epistemic knowledge of an event is lost
# in the network, it is unrecoverable by either sender or receiver." This emulator
# allows us to quantify the performance degradation that arises from this model,
# creating a baseline against which the determinism of Open Atomic Ethernet can be
# measured.

import simpy
import random
import sys
import math

class SimulationParameters:
    """
    Global parameters for the simulation. These values define the
    environment for the contention analysis.
    """
    RANDOM_SEED = 33
    SIM_TIME = 50000  # Simulation time in slots. Should be large for stable results.
    SLOT_TIME = 1     # The fundamental time unit, representing the time to detect a collision.
    
    # --- Command-Line Arguments ---
    try:
        # The number of contending stations attempting to access the Ether.
        NUM_STATIONS = int(sys.argv[1])
        
        # The retransmission policy used by stations after a collision.
        # Policies: "pp" (p-persistent), "op" (optimal p-persistent),
        #           "beb" (binary exponential backoff), "lb" (linear backoff).
        RETRANSMISSION_POLICY = sys.argv[2]
        
        # The aggregate arrival rate (lambda) of new packets to the system.
        ARRIVAL_RATE = float(sys.argv[3])
    except (IndexError, ValueError):
        print("Usage: python ethernet_simulation.py <NUM_STATIONS> <POLICY> <ARRIVAL_RATE>")
        print("Example: python ethernet_simulation.py 20 beb 0.05")
        sys.exit(1)


class Ether(object):
    """
    Represents the shared communication medium, the passive Ether.

    This class orchestrates the simulation by observing the state of all
    stations at each time slot. It determines if a transmission results in a
    successful acquisition, a collision, or an idle slot, and it updates the
    stations' states accordingly. It has no central control; its role is to
    model the physical consequences of the distributed decisions made by each station.
    """
    def __init__(self, env, stations, policy, performance_monitor):
        self.env = env
        self.stations = stations
        self.policy = policy
        self.performance_monitor = performance_monitor
        self.action = env.process(self.run())

    def run(self):
        """
        The main simulation loop, advancing one time slot at a time.
        """
        while True:
            yield self.env.timeout(SimulationParameters.SLOT_TIME)
            self.performance_monitor.increment_total_slots()

            transmitting_stations = []

            # --- Carrier Sense and Deference ---
            # Stations check if they are ready to transmit in the current slot.
            # This models the "Carrier Sense" part of CSMA/CD, where stations
            # defer to other traffic. Here, the decision logic depends on the
            # chosen retransmission policy.
            
            # --- P-Persistent Policies ---
            if self.policy in ["pp", "op"]:
                retran_p = 0.5 if self.policy == "pp" else 1 / SimulationParameters.NUM_STATIONS
                for i, station in self.stations.items():
                    if station.has_packet():
                        if not station.is_retransmitting:
                            # New packet, transmits with p=1
                            transmitting_stations.append(i)
                        elif random.uniform(0, 1) < retran_p:
                            # Collided packet, retransmits with p < 1
                            transmitting_stations.append(i)
            
            # --- Backoff Policies (BEB and Linear) ---
            elif self.policy in ["beb", "lb"]:
                for i, station in self.stations.items():
                    if station.has_packet():
                        if station.retransmission_slot == 0:
                            transmitting_stations.append(i)
                        else:
                            # This station is in a backoff period.
                            station.retransmission_slot -= 1

            # --- Collision Detection and Resolution ---
            # The Ether now resolves the outcome of the slot based on how many
            # stations attempted to transmit.
            
            if len(transmitting_stations) == 1:
                # SUCCESS: Exactly one station transmitted. The Ether is acquired.
                station_id = transmitting_stations[0]
                self.stations[station_id].on_transmission_success()
                self.performance_monitor.increment_successful_slots()

            elif len(transmitting_stations) > 1:
                # COLLISION: Multiple stations transmitted, causing interference.
                # "Packets which overlap in time on the Ether are said to collide;
                # they interfere so as to be unrecognizable by a receiver."
                for station_id in transmitting_stations:
                    self.stations[station_id].on_transmission_collision(self.policy)


class Station(object):
    """
    Represents a single computing station connected to the Ether.

    Each station generates its own packets, creating bursty traffic, and
    contends for access to the shared medium using the distributed
    statistical arbitration defined by the chosen retransmission policy.
    """
    def __init__(self, env, station_id, arrival_rate):
        self.env = env
        self.id = station_id
        self.arrival_rate = arrival_rate
        
        # State variables for packet handling and contention
        self.packet_queue = []
        self.is_retransmitting = False
        self.retransmission_slot = 0
        self.collision_count = 0
        
        self.action = env.process(self.packet_generator())

    def has_packet(self):
        return len(self.packet_queue) > 0

    def packet_generator(self):
        """
        Generates new packets according to a Poisson process, representing
        the bursty nature of local network traffic.
        """
        packet_id = 0
        while True:
            # Wait for a random time determined by the exponential distribution.
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            
            packet_id += 1
            arrival_time = self.env.now
            packet = Packet(f"{self.id}-{packet_id}", arrival_time)
            self.packet_queue.append(packet)

    def on_transmission_success(self):
        """
        Called by the Ether when this station successfully acquires the medium.
        """
        self.packet_queue.pop(0)
        self.is_retransmitting = False
        self.collision_count = 0
        self.retransmission_slot = 0

    def on_transmission_collision(self, policy):
        """
        Called by the Ether when this station's transmission collides.
        The station must now enter a retransmission backoff state.
        """
        if policy in ["pp", "op"]:
            self.is_retransmitting = True
        elif policy == "beb":
            # Binary Exponential Backoff: The mean retransmission interval
            # doubles with each collision to adapt to network load.
            # "As the traffic load increases, more collisions are experienced,
            # a backlog of packets builds up in the stations, retransmission
            # intervals increase, and retransmission traffic backs off to
            # sustain channel efficiency." - Metcalfe & Boggs, 1976
            self.collision_count += 1
            k = min(self.collision_count, 10)
            backoff_limit = 2**k
            self.retransmission_slot = random.randint(0, backoff_limit - 1)
        elif policy == "lb":
            # Linear Backoff: A simpler backoff scheme.
            self.collision_count += 1
            k = min(self.collision_count, 1024)
            self.retransmission_slot = random.randint(0, k - 1)

class Packet:
    """
    A simple data structure representing a packet.
    In a real system, a packet carries the data payload. In this simulation,
    it is a token whose successful or unsuccessful transmission we track.
    """
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time

class PerformanceMonitor(object):
    """
    An object to collect and calculate simulation statistics.
    """
    def __init__(self):
        self.total_slots = 0
        self.successful_slots = 0

    def increment_total_slots(self):
        self.total_slots += 1

    def increment_successful_slots(self):
        self.successful_slots += 1

    def get_throughput(self):
        """
        Calculates the network throughput.
        Throughput is defined as the fraction of slots that carry successful
        transmissions. This is equivalent to the "Efficiency (E)" described
        in Metcalfe's 1976 paper.
        """
        if self.total_slots == 0:
            return 0.0
        return self.successful_slots / self.total_slots

def main():
    """
    Main function to set up and run the simulation.
    """
    print("--- Dædælus: Ethernet Contention Emulator ---")
    print(f"Simulating {SimulationParameters.NUM_STATIONS} stations with policy '{SimulationParameters.RETRANSMISSION_POLICY}' at arrival rate {SimulationParameters.ARRIVAL_RATE:.3f}")
    
    random.seed(SimulationParameters.RANDOM_SEED)
    env = simpy.Environment()
    
    performance_monitor = PerformanceMonitor()
    
    # Create the stations that will contend for the Ether
    stations = {
        i: Station(env, i, SimulationParameters.ARRIVAL_RATE)
        for i in range(1, SimulationParameters.NUM_STATIONS + 1)
    }
    
    # Create the Ether to manage the shared medium
    ether = Ether(env, stations, SimulationParameters.RETRANSMISSION_POLICY, performance_monitor)
    
    # Run the simulation
    env.run(until=SimulationParameters.SIM_TIME)
    
    # Print results
    throughput = performance_monitor.get_throughput()
    print("\n--- Simulation Complete ---")
    print(f"Policy: {SimulationParameters.RETRANSMISSION_POLICY}")
    print(f"Number of Stations: {SimulationParameters.NUM_STATIONS}")
    print(f"Arrival Rate (lambda): {SimulationParameters.ARRIVAL_RATE}")
    print(f"Total Slots Simulated: {performance_monitor.total_slots}")
    print(f"Successful Slots: {performance_monitor.successful_slots}")
    print(f"Throughput (Efficiency): {throughput:.4f}")

if __name__ == '__main__':
    main()
