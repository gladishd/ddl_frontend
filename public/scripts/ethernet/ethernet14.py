#
# DDL_Emulator: Ethernet Contention Simulation
#
# This simulation provides a computational model of the statistical arbitration
# mechanisms described in the seminal 1976 Metcalfe & Boggs paper, "Ethernet:
# Distributed Packet Switching for Local Computer Networks."
#
# The goal is to move beyond a purely statistical analysis and create an agentic
# model that visualizes the contention for the shared Ether. As requested, this
# means "modeling the controllers, and the packet retransmissions, not
# statistically, but computationally."
#

import sys
import random
import simpy
import math
import numpy as np
import matplotlib.pyplot as plt

class DaedalusConfig:
    """
    Configuration parameters for the Ether simulation. These values define the
    environment in which the distributed contention for the shared medium unfolds.
    """
    RANDOM_SEED = 33
    SIM_TIME = 100000  # Total simulation time in slots
    SLOT_TIME = 1      # The duration of a single contention slot
    NUM_STATIONS = 10  # The number of stations (Q) vying for the Ether
    
    # The rate at which new packets arrive at each station
    ARRIVAL_RATES = [0.001, 0.002, 0.003, 0.006, 0.012, 0.024]
    
    # "Coordination of access to the Ether for packet broadcasts is distributed
    # among the contending transmitting stations using controlled statistical arbitration."
    ARBITRATION_ALGORITHMS = ["pp", "op", "beb", "lb"]


class EtherArbiter(object):
    """
    Represents the shared communication medium, the passive Ether.
    This process arbitrates access to the Ether by advancing through discrete
    contention intervals and resolving transmission attempts from all stations.
    """
    def __init__(self, env, stations, arbitration_algorithm):
        self.env = env
        self.stations = stations
        self.arbitration_algorithm = arbitration_algorithm
        self.current_slot = 1

        # Statistics to measure the Ether's performance
        self.successful_acquisitions = 0
        self.interference_events = 0
        self.idle_slots = 0

        self.action = env.process(self.run())

    def run(self):
        """
        The main loop simulates the alternating periods of contention and transmission.
        "The first, called a transmission interval, is that during which the Ether
        has been acquired for a successful packet transmission. The second, called
        a contention interval, is that composed of the retransmission slots...
        during which stations attempt to acquire control of the Ether."
        """
        while True:
            yield self.env.timeout(DaedalusConfig.SLOT_TIME)

            # Identify all stations attempting to transmit in this exact slot
            active_stations = []
            for i in range(1, len(self.stations) + 1):
                if self.stations[i].next_transmission_slot == self.current_slot:
                    active_stations.append(i)

            # "When a slot contains only one attempted transmission, then the Ether has
            # been acquired... When a slot contains a collision... it will contain a
            # collision if more than one station attempts to transmit."
            if len(active_stations) > 1:
                # A collision has occurred.
                self.interference_events += 1
                self.handle_collision(active_stations)
            elif len(active_stations) == 1:
                # One station successfully acquires the Ether.
                self.successful_acquisitions += 1
                station_id = active_stations[0]
                
                # The station successfully transmits one packet.
                self.stations[station_id].packet_backlog -= 1
                self.stations[station_id].retransmission_attempts = 1 # Reset collision counter

                # If the station has more packets, it prepares for the next transmission.
                if self.stations[station_id].packet_backlog > 0:
                    self.stations[station_id].next_transmission_slot = self.current_slot + 1
            else:
                # The slot is idle; no station transmitted.
                self.idle_slots += 1

            self.current_slot += 1
            
    def handle_collision(self, active_stations):
        """
        Implements the "controlled statistical arbitration" used by stations to
        resolve interference and reschedule their transmissions.
        """
        # "A station recovers from a detected collision by abandoning the attempt and
        # retransmitting the packet after some dynamically chosen random time period."
        for station_id in active_stations:
            station = self.stations[station_id]
            
            if self.arbitration_algorithm == "pp":
                # p-persistent policy
                station.next_transmission_slot = self.current_slot + np.random.geometric(0.5)
            
            elif self.arbitration_algorithm == "op":
                # 1-persistent policy
                station.next_transmission_slot = self.current_slot + np.random.geometric(1.0 / DaedalusConfig.NUM_STATIONS)

            elif self.arbitration_algorithm == "lb":
                # Linear Backoff policy
                k = min(station.retransmission_attempts, 1024)
                backoff_slots = np.random.randint(0, k + 1)
                station.next_transmission_slot = self.current_slot + backoff_slots
                station.retransmission_attempts += 1
                
            elif self.arbitration_algorithm == "beb":
                # "Each time a transmission attempt ends in collision, the controller
                # delays for an interval of random length with a mean twice that of
                # the previous interval... This heuristic approximates an algorithm
                # we have called Binary Exponential Backoff."
                k = min(station.retransmission_attempts, 10) # Cap at 2^10
                backoff_slots = np.random.randint(0, 2**k)
                station.next_transmission_slot = self.current_slot + backoff_slots
                station.retransmission_attempts += 1


class ComputingStation:
    """
    Represents a single station connected to the Ether, capable of generating
    and transmitting packets.
    """
    def __init__(self, env, id, arrival_rate):
        self.env = env
        self.id = id
        self.arrival_rate = arrival_rate

        # State variables for packet handling and transmission scheduling
        self.packet_backlog = 0
        self.next_transmission_slot = 0
        self.retransmission_attempts = 1 # K, for backoff calculation

        self.action = env.process(self.run())

    def run(self):
        """
        Packet arrival process. New packets are generated according to a
        Poisson process defined by the arrival_rate.
        """
        while True:
            # Wait for a new packet to be generated
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            # If this is the first packet in the backlog, prepare for immediate transmission.
            if self.packet_backlog == 0:
                self.next_transmission_slot = math.ceil(self.env.now)
            
            self.packet_backlog += 1


def main():
    """
    Main function to configure and run the Ethernet simulation.
    It orchestrates the setup of the environment, stations, and arbiter,
    and collects performance metrics.
    """
    print("DDL_Emulator: Simulating the Metcalfe Shared Ether...")
    print("="*60)
    random.seed(DaedalusConfig.RANDOM_SEED)

    # Allow for command-line overrides of simulation parameters
    if len(sys.argv) > 1:
        DaedalusConfig.NUM_STATIONS = int(sys.argv[1])
        DaedalusConfig.ARBITRATION_ALGORITHMS = [sys.argv[2]]
        DaedalusConfig.ARRIVAL_RATES = [float(sys.argv[3])]
    
    achieved_throughputs = {}
    
    for algo in DaedalusConfig.ARBITRATION_ALGORITHMS:
        print(f"\nTesting Arbitration Algorithm: '{algo.upper()}'")
        throughputs = []
        offered_loads = []

        for rate in DaedalusConfig.ARRIVAL_RATES:
            env = simpy.Environment()
            
            # Create the dictionary of computing stations
            stations = {}
            for i in range(1, DaedalusConfig.NUM_STATIONS + 1):
                stations[i] = ComputingStation(env, i, rate)

            # Instantiate the Ether arbiter to manage the simulation
            arbiter = EtherArbiter(env, stations, algo)
            
            env.run(until=DaedalusConfig.SIM_TIME)

            # Calculate the overall efficiency of the Ether
            # "We now compute E, that fraction of time the Ether is
            # carrying good packets, the efficiency."
            total_slots = arbiter.current_slot - 1
            throughput = arbiter.successful_acquisitions / total_slots if total_slots > 0 else 0
            
            offered_load = DaedalusConfig.NUM_STATIONS * rate
            offered_loads.append(offered_load)
            throughputs.append(throughput)
            
            print(f"  Offered Load: {offered_load:<6.3f} | Achieved Throughput: {throughput:.4f}")
        
        achieved_throughputs[algo] = (offered_loads, throughputs)

    # Plotting the results
    print("\n" + "="*60)
    print("Generating performance plot...")
    
    plt.figure(figsize=(12, 8))
    for algo, (loads, tps) in achieved_throughputs.items():
        plt.plot(loads, tps, marker='o', linestyle='-', label=f'{algo.upper()} Policy')

    plt.xlabel("Offered Load (Total Arrival Rate λ * N)")
    plt.ylabel("Achieved Throughput (Fraction of Successful Slots)")
    plt.title("Ethernet Contention: Throughput vs. Offered Load")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.ylim(bottom=0)
    plt.show()


if __name__ == '__main__':
    main()