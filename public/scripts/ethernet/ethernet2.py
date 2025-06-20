import random
import math

class Packet:
    """
    Represents a single, completely-addressed transmitter-synchronous bit sequence.
    As per the original design, each packet has a source and a destination, though
    in this simulation we are primarily concerned with the contention for the Ether itself.
    """
    def __init__(self, source_address, destination_address, payload_size, creation_time):
        self.source_address = source_address
        self.destination_address = destination_address
        # The number of time slots required to transmit this packet.
        self.transmission_slots = math.ceil(payload_size / SLOTS_PER_TRANSMISSION_UNIT)
        self.creation_time = creation_time

class Station:
    """
    Represents a computing station that contends for access to the shared Ether.
    Control is completely distributed among these stations.
    """
    def __init__(self, address, ether):
        self.address = address
        self.ether = ether
        self.packet_to_send = None
        self.collision_count = 0
        self.retransmission_delay = 0

    def create_packet(self, destination, payload_size, current_time):
        """Generates a new packet to be sent."""
        if not self.packet_to_send:
            self.packet_to_send = Packet(self.address, destination, payload_size, current_time)
            print(f"Time {current_time:4d}: Station {self.address} created a packet for {destination}.")

    def attempt_transmission(self, current_time):
        """
        Attempts to transmit a packet, adhering to the principles of deference
        and statistical arbitration.
        """
        if self.retransmission_delay > 0:
            self.retransmission_delay -= 1
            return

        if self.packet_to_send:
            # This implements carrier detection and deference.
            # A station can sense the carrier of a passing packet and delay
            # sending its own until the detected packet passes safely.
            # No station will start transmitting while hearing carrier.
            if self.ether.is_busy():
                # In a more complex model, this is where deference would be handled.
                # For our discrete time slot simulation, checking ether.is_busy() serves this purpose.
                return
            
            # If the Ether is silent, the station begins transmitting.
            self.ether.add_transmission(self, self.packet_to_send, current_time)

    def handle_successful_transmission(self, current_time):
        """Handles the completion of a successful packet transmission."""
        print(f"Time {current_time:4d}: Station {self.address} successfully transmitted packet.")
        self.packet_to_send = None
        self.collision_count = 0
        self.retransmission_delay = 0

    def handle_collision(self, current_time):
        """
        Handles a source-detected collision, which is the core of the distributed
        statistical arbitration mechanism.
        """
        # A station detecting a collision knows that its packet has been damaged.
        # It can be scheduled for retransmission immediately.
        self.collision_count += 1
        
        # This implements the Binary Exponential Backoff algorithm.
        # Each time a transmission attempt ends in collision, the controller
        # delays for an interval of random length with a mean twice that of
        # the previous interval. This backs off retransmission traffic to sustain channel efficiency.
        backoff_limit = (2 ** min(self.collision_count, 10)) - 1
        if backoff_limit > 0:
            self.retransmission_delay = random.randint(0, backoff_limit)

        print(f"Time {current_time:4d}: Station {self.address} detected collision {self.collision_count}. Backing off for {self.retransmission_delay} slots.")


class Ether:
    """
    Represents the shared communication facility, a passive broadcast medium with no central control.
    It is a logically passive medium for the propagation of digital signals.
    """
    def __init__(self, end_to_end_delay_slots):
        self.transmitting_stations = []
        self.current_packet = None
        self.current_transmitter = None
        self.transmission_countdown = 0
        # T is the time of a slot, the number of seconds it takes to detect a collision
        # after starting a transmission, i.e., one end-to-end round trip delay.
        self.end_to_end_delay_slots = end_to_end_delay_slots
        self.collision = False
        self.total_successful_transmissions = 0
        self.total_collisions = 0

    def is_busy(self):
        """Checks for the presence of carrier on the Ether."""
        return self.transmission_countdown > 0 or self.collision

    def add_transmission(self, station, packet, current_time):
        """A station attempts to acquire the Ether for transmission."""
        print(f"Time {current_time:4d}: Station {station.address} is attempting to transmit.")
        self.transmitting_stations.append((station, packet))

    def resolve_contention(self, current_time):
        """
        Resolves the contention interval for the current time slot. This models the
        statistical arbitration for acquiring the Ether.
        """
        if len(self.transmitting_stations) > 1:
            # This is a collision. Packets which overlap in time on the Ether interfere
            # so as to be unrecognizable by a receiver.
            self.collision = True
            self.total_collisions += 1
            print(f"Time {current_time:4d}: COLLISION DETECTED between {len(self.transmitting_stations)} stations.")
            
            # This implements Collision Consensus Enforcement.
            # When a station determines that its transmission is experiencing interference,
            # it momentarily jams the Ether to insure that all other participants in the
            # collision will detect interference and be forced to abort.
            for station, _ in self.transmitting_stations:
                station.handle_collision(current_time)
            
            # Interference periods on the Ether are limited. Colliding stations
            # detect interference and abort transmission within an Ether round trip time.
            self.transmission_countdown = self.end_to_end_delay_slots

        elif len(self.transmitting_stations) == 1:
            # One station has successfully acquired the Ether. The contention interval
            # ends, and a transmission interval begins.
            self.current_transmitter, self.current_packet = self.transmitting_stations[0]
            self.transmission_countdown = self.current_packet.transmission_slots
            print(f"Time {current_time:4d}: Station {self.current_transmitter.address} acquired the Ether. Transmission will take {self.transmission_countdown} slots.")

        self.transmitting_stations = []

    def tick(self, current_time):
        """Advances the state of the Ether by one time slot."""
        if self.transmission_countdown > 0:
            self.transmission_countdown -= 1
            if self.transmission_countdown == 0:
                if self.collision:
                    # The collision/jamming signal has cleared.
                    print(f"Time {current_time:4d}: Ether is now clear after collision.")
                    self.collision = False
                else:
                    # A successful transmission has completed.
                    self.current_transmitter.handle_successful_transmission(current_time)
                    self.total_successful_transmissions += 1
                    self.current_transmitter = None
                    self.current_packet = None

# --- Simulation Parameters ---
# These parameters can be tuned to explore the model's behavior.
NUMBER_OF_STATIONS = 10
SIMULATION_DURATION = 500  # in time slots
PACKET_PAYLOAD_SIZE = 4096 # in bits
PACKET_CREATION_PROBABILITY = 0.1 # Chance per slot for a station to create a packet
ETHER_BIT_RATE = 3_000_000 # 3 Mbps, as in the experimental Ethernet
ETHER_LENGTH_METERS = 1000 # 1 km
PROPAGATION_SPEED_MPS = 2e8 # Approx. speed of signal in coaxial cable (2/3 c)

# --- Derived Parameters ---
# The slot time must be at least one end-to-end round trip delay to ensure
# collision detection works correctly across the entire network.
ROUND_TRIP_TIME_SECONDS = (ETHER_LENGTH_METERS / PROPAGATION_SPEED_MPS) * 2
SLOT_TIME_SECONDS = ROUND_TRIP_TIME_SECONDS
BITS_PER_SLOT = ETHER_BIT_RATE * SLOT_TIME_SECONDS
END_TO_END_DELAY_SLOTS = 1 # By definition, the slot time covers one round trip.
SLOTS_PER_TRANSMISSION_UNIT = BITS_PER_SLOT

def run_simulation():
    """Main simulation loop."""
    print("--- Starting Agentic Simulation of Classic Half-Duplex Metcalfe Channel ---")
    print(f"Configuration: {NUMBER_OF_STATIONS} stations, {SIMULATION_DURATION} slots, {PACKET_PAYLOAD_SIZE}-bit packets.")
    print(f"Slot Time (Round-Trip Delay): {SLOT_TIME_SECONDS:.2e} seconds")
    print(f"Ether Bit Rate: {ETHER_BIT_RATE / 1e6} Mbps")
    print("-" * 70)

    ether = Ether(end_to_end_delay_slots=END_TO_END_DELAY_SLOTS)
    stations = [Station(address=i, ether=ether) for i in range(NUMBER_OF_STATIONS)]

    for t in range(SIMULATION_DURATION):
        # 1. New packets can be generated at stations that are not busy.
        for station in stations:
            if not station.packet_to_send and random.random() < PACKET_CREATION_PROBABILITY:
                destination = random.choice([s.address for s in stations if s.address != station.address])
                station.create_packet(destination, PACKET_PAYLOAD_SIZE, t)

        # 2. Stations with packets to send attempt to transmit.
        #    This is the beginning of the contention interval.
        if not ether.is_busy():
            for station in stations:
                station.attempt_transmission(t)

        # 3. The Ether resolves contention for the current slot.
        ether.resolve_contention(t)

        # 4. Time advances, and any ongoing transmission progresses.
        ether.tick(t)

    print("-" * 70)
    print("--- Simulation Complete ---")
    print(f"Total Successful Transmissions: {ether.total_successful_transmissions}")
    print(f"Total Collisions: {ether.total_collisions}")
    
    # This calculation of efficiency follows the simple model in the Metcalfe paper.
    # It is the ratio of time spent sending good packets to the total time.
    if ether.total_successful_transmissions > 0:
        time_transmitting_good_packets = ether.total_successful_transmissions * math.ceil(PACKET_PAYLOAD_SIZE / SLOTS_PER_TRANSMISSION_UNIT)
        efficiency = time_transmitting_good_packets / SIMULATION_DURATION
        print(f"Calculated Channel Efficiency: {efficiency:.2%}")
    else:
        print("No packets were successfully transmitted.")


if __name__ == "__main__":
    run_simulation()