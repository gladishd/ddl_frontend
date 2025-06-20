#In conclusion, the simulation runs for a long time because it is accurately modeling an environment with high contention, frequent collisions, and long, random backoff delays. This is the inherent behavior of the 1976 Ethernet protocol. The long runtime is not an error in the code's logic but rather a successful demonstration of why Daedaelus advocates for a move away from contention-based, bandwidth-multiplexed systems toward a new architecture of "transaction-multiplexing" that avoids these inefficiencies altogether.
#
# DDL_Emulator: Optimized Ethernet Contention Simulation
#
# This script provides an agent-based computational model of the original 1976 Ethernet
# as described in the seminal paper by Metcalfe and Boggs. Its purpose is to serve as
# "Code as Proof," allowing for a direct and interactive exploration of the fundamental
# dynamics and limitations of a shared, passive communication medium.
#
# The Daedaelus philosophy posits that the industry's long-held assumptions about
# network congestion, which grew from this early model, are flawed. By computationally,
# not just statistically, modeling transmission intervals, contention, and collisions,
# we can highlight the root cause of inefficiency in bandwidth-multiplexed systems.
#
# OPTIMIZATION NOTES:
# This version has been optimized to run faster and use less space. The core changes
# reflect a key Daedaelus principle: eliminate unnecessary work. Instead of wastefully
# polling every station on every slot, we now maintain an 'active_stations' queue,
# focusing computation only where it is needed. Furthermore, a VERBOSE_LOGGING
# flag has been added to disable costly disk I/O during performance-critical runs.
#

import math
import random
import sys
from collections import deque

# --- Simulation Configuration ---

# Core parameters from Metcalfe's 1976 paper and our analysis.
# We model time in discrete 'slots'. A slot is the fundamental unit for contention.
# "Retransmission intervals are multiples of a slot, the maximum time between
# starting a transmission and detecting a collision, one end-to-end round trip delay." 
SLOT_TIME_US = 51.2  # Microseconds, based on a 1km Ether. (512 bits @ 10Mbps)

# "We limit in software the maximum length of our packets to be near 4000 bits..." 
PACKET_SIZE_BITS = 4096

# We use 3 Mbps as the channel capacity, as per the experimental Ethernet. 
BIT_RATE_BPS = 3_000_000

# Simulation setup
NUM_STATIONS = 10
FRAMES_PER_STATION = 5
MAX_COLLISIONS_PER_FRAME = 16 # A standard limit in Ethernet implementations

# --- OPTIMIZATION FLAG ---
# Set to False to disable fine-grained logging for maximum speed and minimal disk usage.
VERBOSE_LOGGING = False

class Packet:
    """A simple representation of an Ethernet packet or frame."""
    _next_id = 0
    def __init__(self, source_id, dest_id):
        # "Each packet has a source and a destination, both of which
        # are identified in the packet's header." 
        self.id = Packet._next_id
        self.source_id = source_id
        self.dest_id = dest_id
        self.payload = f"Frame {self.id} from {source_id} to {dest_id}"
        Packet._next_id += 1

    def __repr__(self):
        return f"Packet(id={self.id}, src={self.source_id}, dst={self.dest_id})"

class Ether:
    """
    Represents the shared, passive Ether. This class is the arbiter of the simulation.
    """
    def __init__(self):
        self.transmitting_stations = []
        self.busy_until_slot = 0

    def is_carrier_sensed(self, current_slot):
        # "Because a station can sense the carrier of a passing packet, it can delay
        # sending one of its own until the detected packet passes safely." 
        return current_slot < self.busy_until_slot

    def attempt_transmission(self, packet, station_id):
        self.transmitting_stations.append((packet, station_id))

    def resolve_slot(self, packet_duration_slots):
        """Resolves the state of the Ether for the current time slot."""
        if not self.transmitting_stations:
            return "EMPTY", None, []

        if len(self.transmitting_stations) > 1:
            # "Packets which overlap in time on the Ether are said to collide" 
            colliding_ids = [s_id for _, s_id in self.transmitting_stations]
            self.busy_until_slot += 1 # Jam signal lasts for one slot
            packet, _ = self.transmitting_stations.pop(0)
            self.transmitting_stations.clear()
            return "COLLISION", packet, colliding_ids

        if len(self.transmitting_stations) == 1:
            # "When a slot contains only one attempted transmission, then the Ether
            # has been acquired for the duration of a packet..." 
            packet, station_id = self.transmitting_stations.pop(0)
            self.busy_until_slot += packet_duration_slots
            return "SUCCESS", packet, [station_id]

        return "UNKNOWN", None, []

class Station:
    """Represents a single computing station. This is the 'agent' in our model."""
    def __init__(self, station_id, log_file_handle):
        self.id = station_id
        self.packet_queue = deque()
        self.collision_count = 0
        self.wait_until_slot = 0
        self.log_file = log_file_handle

    def log(self, message):
        if VERBOSE_LOGGING:
            self.log_file.write(f"[Station {self.id:02d} @ Slot {simulation_time:05d}] {message}\n")

    def add_packet_to_queue(self, destination_id):
        self.packet_queue.append(Packet(self.id, destination_id))

    def run(self, current_slot, ether):
        if not self.packet_queue or current_slot < self.wait_until_slot:
            return

        # "Transmissions initiated by a station defer to any which may already be in progress." 
        if ether.is_carrier_sensed(current_slot):
            self.log("Sensed carrier, deferring.")
            return

        ether.attempt_transmission(self.packet_queue[0], self.id)
        self.log(f"Attempting to transmit {self.packet_queue[0]}.")

    def on_success(self):
        sent_packet = self.packet_queue.popleft()
        self.log(f"Successfully transmitted {sent_packet}.")
        self.collision_count = 0
        return len(self.packet_queue) == 0 # Return True if now inactive

    def on_collision(self):
        self.collision_count += 1
        if self.collision_count > MAX_COLLISIONS_PER_FRAME:
            failed_packet = self.packet_queue.popleft()
            self.log(f"*** FAILED for {failed_packet} after {MAX_COLLISIONS_PER_FRAME} collisions. Dropping.")
            self.collision_count = 0
            return "DROPPED", len(self.packet_queue) == 0

        # "...the controller delays for an interval of random length...This heuristic
        # approximates an algorithm we have called Binary Exponential Backoff." 
        backoff_limit = 2**min(self.collision_count, 10)
        backoff_slots = random.randint(0, backoff_limit - 1)
        self.wait_until_slot = simulation_time + backoff_slots
        self.log(f"Collision for {self.packet_queue[0]}. Count: {self.collision_count}. Backing off for {backoff_slots} slots.")
        return "RETRY", False

class Simulation:
    """Manages the simulation, keeps time, and reports statistics."""
    def __init__(self, stations, total_packets):
        self.ether = Ether()
        self.stations = stations
        self.total_packets_initial = total_packets
        # OPTIMIZATION: Maintain a queue of only stations that have packets to send.
        self.active_stations = deque([s for s in stations if s.packet_queue])
        self.log_file = open("logs/simulation.log", "w")

        self.successful_transmissions = 0
        self.total_contention_slots = 0
        self.total_transmission_slots = 0
        self.total_collisions = 0
        self.dropped_packets = 0

        bits_per_slot = BIT_RATE_BPS * (SLOT_TIME_US / 1_000_000)
        self.packet_duration_slots = math.ceil(PACKET_SIZE_BITS / bits_per_slot)

    def log(self, message):
        if VERBOSE_LOGGING:
            self.log_file.write(f"[Simulation @ Slot {simulation_time:05d}] {message}\n")

    def run(self):
        global simulation_time
        simulation_time = 0
        self.log(f"--- Simulation Start ---")
        self.log(f"Config: {len(self.stations)} stations, {FRAMES_PER_STATION} frames each.")
        self.log(f"Packet size: {PACKET_SIZE_BITS} bits -> {self.packet_duration_slots} slots.")

        while (self.successful_transmissions + self.dropped_packets) < self.total_packets_initial:
            if not self.active_stations:
                self.log("*** LIVELOCK: No active stations but termination condition not met. Exiting.")
                break

            if not self.ether.is_carrier_sensed(simulation_time):
                self.log(f"Ether free. Active stations: {[s.id for s in self.active_stations]}. Contending...")
                # OPTIMIZATION: Iterate only over active stations.
                for station in list(self.active_stations):
                    station.run(simulation_time, self.ether)

                status, packet, ids = self.ether.resolve_slot(self.packet_duration_slots)

                if status == "SUCCESS":
                    self.successful_transmissions += 1
                    self.total_contention_slots += 1
                    self.total_transmission_slots += self.packet_duration_slots
                    station = self.stations[ids[0]]
                    is_inactive = station.on_success()
                    if is_inactive: self.active_stations.remove(station)
                    self.log(f"SUCCESS: Station {ids[0]} acquired Ether.")
                elif status == "COLLISION":
                    self.total_collisions += 1
                    self.total_contention_slots += 1
                    self.log(f"COLLISION between stations: {ids}. Jamming Ether.")
                    for station_id in ids:
                        station = self.stations[station_id]
                        if station in self.active_stations:
                            result, is_inactive = station.on_collision()
                            if result == "DROPPED": self.dropped_packets += 1
                            if is_inactive: self.active_stations.remove(station)
                elif status == "EMPTY":
                    self.total_contention_slots += 1
                    self.log(f"Ether idle. No transmissions.")

            simulation_time = self.ether.busy_until_slot if self.ether.is_carrier_sensed(simulation_time) else simulation_time + 1

        self.log(f"--- Simulation Complete at Slot {simulation_time} ---")
        self.report_stats()
        self.log_file.close()

    def report_stats(self):
        """Calculate and report performance metrics, including Metcalfe's Efficiency."""
        print("\n--- Simulation Results ---")
        print(f"Total Sim Time: {simulation_time} slots ({simulation_time * SLOT_TIME_US / 1000:.2f} ms)")
        print(f"Total Packets Goal: {self.total_packets_initial}")
        print(f"Successfully Transmitted: {self.successful_transmissions}")
        print(f"Packets Dropped: {self.dropped_packets}")
        print(f"Total Collisions: {self.total_collisions}")
        print("-" * 28)
        print(f"Total Transmission Slots: {self.total_transmission_slots}")
        print(f"Total Contention Slots:   {self.total_contention_slots}")

        try:
            # "We now compute E, that fraction of time the Ether is carrying good packets, the efficiency." 
            # E = (Transmission Time) / (Transmission Time + Contention Time)
            efficiency = self.total_transmission_slots / (self.total_transmission_slots + self.total_contention_slots)
            print(f"\nEthernet Efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")

            total_bits = self.successful_transmissions * PACKET_SIZE_BITS
            total_time_s = simulation_time * (SLOT_TIME_US / 1_000_000)
            throughput_bps = total_bits / total_time_s
            print(f"Total Throughput: {throughput_bps/1_000_000:.4f} Mbps")

        except ZeroDivisionError:
            print("No successful transmissions, efficiency calculation skipped.")
        print("-" * 28)


if __name__ == "__main__":
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # This context manager ensures files are closed even if the script crashes.
    with open("logs/simulation.log", "w") as sim_log:
        station_log_files = [open(f"logs/station{i}.log", "w") for i in range(NUM_STATIONS)]

        stations = [Station(i, station_log_files[i]) for i in range(NUM_STATIONS)]

        total_packets = 0
        for i in range(NUM_STATIONS):
            for _ in range(FRAMES_PER_STATION):
                destination = random.choice([k for k in range(NUM_STATIONS) if k != i])
                stations[i].add_packet_to_queue(destination)
                total_packets += 1

        sim = Simulation(stations, total_packets)
        sim.log_file = sim_log # Assign the file handle
        sim.run()

        for f in station_log_files:
            f.close()