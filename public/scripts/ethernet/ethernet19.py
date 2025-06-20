import random
import heapq
import time
import matplotlib.pyplot as plt

# --- Dædælus Philosophy Integration ---
# This simulation models the classic half-duplex, shared-medium Ethernet described by
# Metcalfe & Boggs in 1976. The original code's performance issues stemmed from an
# inadequate contention resolution mechanism, which we will enhance.
# By implementing a proper Binary Exponential Backoff, we not only make the simulation
# run faster but also more accurately model the statistical arbitration that governed
# early Ethernets. This process highlights a core Daedaelus tenet: understanding
# foundational models is crucial to demonstrating their limitations and building
# superior, more deterministic systems.
#
# "As more stations begin to transmit, the rate of packet interference increases.
# Ethernet controllers in each station are built to adjust the mean retransmission
# interval in proportion to the frequency of collisions; sharing of the Ether among
# competing station-station transmissions is thereby kept near the optimum."
# -- Metcalfe & Boggs, "Ethernet: Distributed Packet Switching for Local Computer Networks", 1976.

# --- Constants ---
LINK_BPS = 100e6          # 100 Mbps, a representative link speed.
ACK_BITS = 64 * 8         # Size of an ACK/NACK packet in bits.

# The "slot time" is the fundamental unit of retransmission. It's the time to detect
# a collision, which is at least twice the end-to-end propagation delay of the Ether.
# This ensures a station knows its transmission collided before the packet finishes.
PROPAGATION_DELAY = 5e-6  # Approx. 5 µs for 1km of cable.
SLOT_TIME = 2 * PROPAGATION_DELAY

# --- Data Structures ---
class Packet:
    """A variable length digital data packet broadcast onto the Ether."""
    __slots__ = ('dest', 'src', 'type_of_data', 'data', 'is_corrupted')
    def __init__(self, dest, src, type_of_data, data, is_corrupted=False):
        self.dest = dest
        self.src = src
        self.type_of_data = type_of_data
        self.data = data
        self.is_corrupted = is_corrupted

class Event:
    """An entry in the simulation's priority queue, representing a future action."""
    __slots__ = ('time', 'src_mac', 'dest_mac', 'payload', 'duration', 'type')
    def __init__(self, time, src_mac, dest_mac, payload, duration, event_type):
        self.time = time
        self.src_mac = src_mac
        self.dest_mac = dest_mac
        self.payload = payload
        self.duration = duration
        self.type = event_type

    def __lt__(self, other):
        return self.time < other.time

# --- Simulation Components ---
class TransmissionLine:
    """
    Models the passive Ether, a shared broadcast medium. It holds references
    to all connected stations and tracks basic transmission statistics.
    """
    def __init__(self, error_rate):
        self.error_rate = error_rate
        self.time_to_free = 0.0
        self.pcs = {}
        self.stats = {'msgs': 0, 'acks': 0, 'nacks': 0, 'collisions': 0}

    def register(self, pc):
        """Connects a PC to the transmission line."""
        self.pcs[pc.mac] = pc

    def send(self, packet):
        """
        Simulates broadcasting a packet onto the Ether. The packet is heard by all
        stations, but only the destination processes it.
        """
        # "Packets may be lost due to ... impulse noise on the Ether"
        # We simulate this as a random corruption event.
        if packet.type_of_data == 'MESSAGE' and random.random() < self.error_rate:
            packet.is_corrupted = True
        return self.pcs[packet.dest].receive(packet)

class PC:
    """
    Represents a single computing station. In this revised model, it now tracks its own
    collision history to implement the backoff algorithm correctly.
    """
    __slots__ = ('mac', 'line', 'waiting_for_ack', 'last_pkt', 'collision_count')
    def __init__(self, mac, line):
        self.mac = mac
        self.line = line
        self.waiting_for_ack = False  # Implements a stop-and-wait protocol per station
        self.last_pkt = None
        # Each controller maintains a collision count to dynamically adjust its backoff window.
        self.collision_count = 0
        line.register(self)

    def send(self, dest, type_of_data, payload):
        """Creates and sends a packet, entering a waiting state for MESSAGEs."""
        pkt = Packet(dest, self.mac, type_of_data, payload)
        if type_of_data == 'MESSAGE':
            self.waiting_for_ack = True
            self.last_pkt = pkt
        
        # A successful transmission resets the collision counter for the next attempt.
        self.collision_count = 0
        return self.line.send(pkt)

    def receive(self, pkt):
        """Processes an incoming packet and generates the appropriate response."""
        if pkt.type_of_data == 'MESSAGE':
            self.line.stats['msgs'] += 1
            # "The EFTP uses 5 packet types: data, ack, abort, end, and endreply."
            # We model a simplified version with MESSAGE and ARQ (ack/nack).
            ack = 'ACK' if not pkt.is_corrupted else 'NACK'
            return (self.mac, pkt.src, 'ARQ', ack)

        # Handle an ARQ (Automatic Repeat Request) response
        elif pkt.type_of_data == 'ARQ' and self.last_pkt:
            if pkt.data == 'ACK':
                self.waiting_for_ack = False
                self.last_pkt = None
                self.line.stats['acks'] += 1
                return None
            elif pkt.data == 'NACK':
                # This is the critical deadlock fix. Upon receiving a NACK, the station's
                # wait is over. It is now free to attempt retransmission.
                self.waiting_for_ack = False
                self.line.stats['nacks'] += 1
                # The receiver has indicated the packet was corrupt; the sender must retransmit.
                return (self.mac, self.last_pkt.dest, 'MESSAGE', self.last_pkt.data)
        return None

class Simulator:
    """The main simulation engine, managing the event queue and global clock."""
    MAX_COLLISIONS = 10 # Caps the backoff to prevent excessively long waits, per the 802.3 standard.

    def __init__(self, n, err, msgs):
        self.line = TransmissionLine(err/100)
        self.pcs = [PC(f'PC{i}', self.line) for i in range(n)]
        self.events = []
        self.time = 0.0
        self.msgs_to_send = msgs
        self.initial_msgs_scheduled = 0

    def schedule(self, evt):
        heapq.heappush(self.events, evt)

    def init(self):
        """Schedules the initial message transmission attempts."""
        # Create all messages up front to simulate a loaded network.
        for _ in range(self.msgs_to_send):
            src_pc = random.choice(self.pcs)
            dest_pc = random.choice(self.pcs)
            while dest_pc is src_pc: dest_pc = random.choice(self.pcs)

            # Packet sizes are variable, as in the original Ethernet specification.
            size_in_bits = random.randint(64*8, 1518*8)
            duration = size_in_bits / LINK_BPS
            
            # Stagger initial events slightly to prevent a perfect collision at t=0
            t0 = self.time + random.random() * 1e-4
            self.schedule(Event(t0, src_pc.mac, dest_pc.mac, size_in_bits, duration, 'MESSAGE'))
            self.initial_msgs_scheduled += 1

    def run(self):
        """
        Executes the simulation loop, processing events in chronological order.
        This loop now correctly models carrier sense and binary exponential backoff.
        """
        successful_acks = 0
        # The simulation ends once all initial messages have been successfully acknowledged.
        while successful_acks < self.msgs_to_send and self.events:
            evt = heapq.heappop(self.events)
            self.time = evt.time
            pc = self.line.pcs.get(evt.src_mac)
            if not pc: continue

            # --- Carrier Sense and Contention Detection ---
            # A station must defer if the Ether is busy OR if it's already waiting for an ACK.
            # This check models a station sensing the carrier before transmitting.
            is_line_busy = self.line.time_to_free > self.time
            is_pc_waiting = pc.waiting_for_ack and evt.type == 'MESSAGE'

            if is_line_busy or is_pc_waiting:
                self.line.stats['collisions'] += 1
                pc.collision_count += 1
                
                # --- Binary Exponential Backoff Algorithm ---
                # "Each time a transmission attempt ends in collision, the controller delays for an
                # interval of random length with a mean twice that of the previous interval."
                # This is the crucial fix for the simulation's performance.
                k = min(pc.collision_count, self.MAX_COLLISIONS)
                backoff_slots = random.randint(0, (2**k) - 1)
                backoff_time = backoff_slots * SLOT_TIME
                
                # The station must wait until the line is free *plus* its random backoff time.
                new_time = max(self.time, self.line.time_to_free) + backoff_time
                self.schedule(Event(new_time, evt.src_mac, evt.dest_mac, evt.payload, evt.duration, evt.type))
                continue

            # --- Successful Ether Acquisition and Transmission ---
            self.line.time_to_free = self.time + evt.duration
            resp = pc.send(evt.dest_mac, evt.type, evt.payload)

            if resp:
                src, dst, typ, pay = resp
                if typ == 'ARQ':
                    if pay == 'ACK':
                        successful_acks += 1 # Count successful deliveries to determine when to stop.
                    bits = ACK_BITS
                else: # It's a retransmitted MESSAGE
                    bits = pay
                
                dur = bits / LINK_BPS
                # The response is scheduled to be sent after the current transmission completes.
                self.schedule(Event(self.line.time_to_free + PROPAGATION_DELAY, src, dst, pay, dur, typ))

        stats = self.line.stats
        return stats['acks'], stats['collisions'], self.initial_msgs_scheduled

# --- Main Execution ---
def main():
    start_time = time.time()
    devs = [2, 4, 8, 16, 32] # Added a larger station count for more rigorous testing
    errs = [0, 1, 5, 10]    # Adjusted error rates for more granularity
    msgs = 100
    
    print("Simulating Metcalfe's Shared Ether with Correct Backoff and Deadlock Prevention...")
    print("-" * 75)
    print(f"{'Stations':>10} | {'Error %':>10} | {'Delivered':>12} | {'Collisions':>12} | {'Time (s)':>10}")
    print("-" * 75)

    for n in devs:
        for e in errs:
            loop_start_time = time.time()
            sim = Simulator(n, e, msgs)
            sim.init()
            delivered, collisions, sent = sim.run()
            loop_time = time.time() - loop_start_time
            print(f"{n:>10} | {e:>10} | {delivered:>12} | {collisions:>12} | {loop_time:>10.2f}")

    print("-" * 75)
    print(f"\nTotal Elapsed Time: {time.time() - start_time:.2f}s")

if __name__ == '__main__':
    main()