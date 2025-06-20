import random
import enum
import collections

# --- Simulation Constants ---
# These parameters are based on the experimental Ethernet described
# in the 1976 Metcalfe & Boggs paper to provide a historically accurate model.
BIT_RATE = 3_000_000  # bits per second
CABLE_LENGTH = 1000  # meters
PROPAGATION_SPEED = 2.0 * 10**8  # meters per second, approx. 2/3 speed of light in vacuum

# The slot time is the critical unit for collision handling. It is the time
# to detect a collision after starting a transmission, which is at least
# twice the Ether's end-to-end propagation time.
SLOT_TIME = 2 * (CABLE_LENGTH / PROPAGATION_SPEED)

SIMULATION_TICKS = 200_000 # Total ticks for the simulation
TICK_DURATION = SLOT_TIME / 50 # Breaking slot time into smaller units for finer-grained simulation

# --- Daedalus/CoRE4INET Architectural Enhancements ---

class TrafficClass(enum.Enum):
    """
    Defines traffic classes, moving beyond Ethernet's single best-effort model.
    This aligns with the Daedalus principle of providing guaranteed service levels
    by distinguishing between different types of flows.
    """
    # Time-Triggered (TT) traffic operates on a strict, pre-defined schedule.
    # This traffic is paramount for deterministic, real-time operations and
    # reflects the highest level of reliability, similar to AS6802.
    TIME_TRIGGERED = 3
    # Rate-Constrained (RC) traffic, like AVB, is guaranteed a certain bandwidth
    # but does not have fixed time slots. It has priority over best-effort.
    RATE_CONSTRAINED = 2
    # Best-Effort (BE) is the classic Ethernet traffic, with no guarantees.
    BEST_EFFORT = 1

class State(enum.Enum):
    """
    Represents the state of a station's controller. A station moves between
    these states as it attempts to transmit a packet.
    """
    IDLE = 1
    # For scheduled traffic, the station must wait for its designated transmission window.
    AWAITING_SCHEDULE = 2
    SENSING_CARRIER = 3
    TRANSMITTING = 4
    JAMMING = 5
    BACKOFF = 6

class Packet:
    """
    A representation of a data packet, now including traffic class and stream identity.
    This allows the network to apply different policies based on the packet's role,
    a core concept in CoRE4INET and Daedalus.
    """
    def __init__(self, source_id, destination_id, payload_bits, creation_time, traffic_class=TrafficClass.BEST_EFFORT, stream_id=0):
        self.source_id = source_id
        self.destination_id = destination_id
        self.payload_bits = payload_bits
        self.creation_time = creation_time
        self.traffic_class = traffic_class
        self.stream_id = stream_id
        # The first 16 bits of all Ethernet packets contain its interface-
        # interpretable destination and source station addresses.
        self.total_bits = payload_bits + 16 # Simplified header

class Ether:
    """
    Represents the shared, passive broadcast medium. It has no central control
    and simply propagates signals, exposing interference if multiple stations
    transmit simultaneously.
    """
    def __init__(self):
        self.transmitting_stations = set()
        self.is_jammed = False

    def is_busy(self):
        # A station can sense the carrier of a passing packet. It can delay
        # sending one of its own until the detected packet passes safely.
        return len(self.transmitting_stations) > 0

    def has_collision(self):
        # Packets which overlap in time on the Ether are said to collide;
        # they interfere so as to be unrecognizable by a receiver.
        return len(self.transmitting_stations) > 1

    def add_transmitter(self, station):
        self.transmitting_stations.add(station)

    def remove_transmitter(self, station):
        self.transmitting_stations.discard(station)

class SRPTable:
    """
    A simplified model of a Stream Reservation Protocol (SRP) Table.
    In CoRE4INET, this is a complex module that manages bandwidth reservations.
    Here, it serves to register and look up stream characteristics, enabling the
    system to know the traffic class of a given data flow.
    """
    def __init__(self):
        self.streams = {} # stream_id -> TrafficClass

    def register_stream(self, stream_id, traffic_class):
        self.streams[stream_id] = traffic_class
        print(f"  [SRP] Stream {stream_id} registered as {traffic_class.name}")

    def get_traffic_class(self, stream_id):
        return self.streams.get(stream_id, TrafficClass.BEST_EFFORT)

class Scheduler:
    """
    A model of a global time-triggered scheduler, inspired by the schedulers in
    CoRE4INET's AS6802 implementation. It manages the transmission windows for
    Time-Triggered (TT) traffic. This provides the temporal determinism that
    contention-based systems lack.
    """
    def __init__(self, cycle_time_in_ticks):
        self.schedule = {} # stream_id -> (start_tick, end_tick)
        self.is_synchronized = False # The system must be synchronized to trust the schedule.
        self.cycle_time = cycle_time_in_ticks

    def add_tt_stream_to_schedule(self, stream_id, start_tick_in_cycle, duration_in_ticks):
        end_tick = start_tick_in_cycle + duration_in_ticks
        self.schedule[stream_id] = (start_tick_in_cycle, end_tick)
        print(f"  [Scheduler] TT Stream {stream_id} scheduled for ticks {start_tick_in_cycle}-{end_tick} in each cycle.")

    def is_window_open(self, stream_id, current_tick):
        if not self.is_synchronized or stream_id not in self.schedule:
            return False
        
        # The schedule repeats every cycle.
        tick_in_cycle = current_tick % self.cycle_time
        start, end = self.schedule[stream_id]
        return start <= tick_in_cycle < end

# --- Agent-Based Model ---

class Station:
    """
    An agentic model of a computing station, upgraded with CoRE4INET capabilities.
    It now manages multiple traffic classes and interacts with a global scheduler.
    """
    def __init__(self, station_id, ether, slot_time_in_ticks, srp_table, scheduler, jam_bits=32):
        self.id = station_id
        self.ether = ether
        self.srp_table = srp_table
        self.scheduler = scheduler
        
        # A station now maintains separate queues for each traffic class,
        # allowing for prioritized access to the Ether. This is a fundamental
        # departure from the single-queue, best-effort model of old.
        self.tx_queues = {
            TrafficClass.TIME_TRIGGERED: collections.deque(),
            TrafficClass.RATE_CONSTRAINED: collections.deque(),
            TrafficClass.BEST_EFFORT: collections.deque()
        }
        self.state = State.IDLE

        self.current_packet = None
        self.bits_sent = 0
        self.jam_bits_sent = 0
        
        self.collision_count = 0
        self.backoff_timer = 0

        self._slot_time_in_ticks = slot_time_in_ticks
        self._jam_duration_in_ticks = (jam_bits / BIT_RATE) / TICK_DURATION
        
        # Statistics
        self.packets_sent = 0
        self.total_collisions = 0

    def enqueue_packet(self, destination_id, payload_bits, creation_time, stream_id):
        # Packets are now classified upon creation, allowing the station to
        # handle them according to their required service guarantees.
        traffic_class = self.srp_table.get_traffic_class(stream_id)
        packet = Packet(self.id, destination_id, payload_bits, creation_time, traffic_class, stream_id)
        self.tx_queues[traffic_class].append(packet)

    def _select_packet_to_send(self):
        """
        Implements the priority-based transmission logic. This is the core of the
        shaping mechanism, ensuring TT traffic is sent on schedule, followed by
        RC, and finally BE.
        """
        # 1. Time-Triggered (TT) traffic has absolute priority, but only within its scheduled window.
        if self.tx_queues[TrafficClass.TIME_TRIGGERED]:
            packet = self.tx_queues[TrafficClass.TIME_TRIGGERED][0]
            if self.scheduler.is_window_open(packet.stream_id, current_tick):
                return self.tx_queues[TrafficClass.TIME_TRIGGERED].popleft()
            else:
                 # It's not this TT packet's time yet, it must wait.
                 # Fall through to check lower priority traffic.
                 pass

        # 2. Rate-Constrained (RC) traffic is next. It can be sent if no TT packet is ready.
        if self.tx_queues[TrafficClass.RATE_CONSTRAINED]:
            return self.tx_queues[TrafficClass.RATE_CONSTRAINED].popleft()

        # 3. Best-Effort (BE) traffic has the lowest priority.
        if self.tx_queues[TrafficClass.BEST_EFFORT]:
            return self.tx_queues[TrafficClass.BEST_EFFORT].popleft()
            
        return None

    def _start_next_transmission(self, current_time):
        self.current_packet = self._select_packet_to_send()
        if self.current_packet:
            if self.current_packet.traffic_class == TrafficClass.TIME_TRIGGERED:
                 # TT traffic does not sense the carrier; its transmission time is guaranteed by the schedule.
                 # It assumes the Ether is clear during its window.
                self._start_transmission_now()
            else:
                self.state = State.SENSING_CARRIER
        else:
            # If a TT packet was available but its window is not open, the station must wait.
            if self.tx_queues[TrafficClass.TIME_TRIGGERED]:
                self.state = State.AWAITING_SCHEDULE
            else:
                self.state = State.IDLE

    def _start_transmission_now(self):
        self.state = State.TRANSMITTING
        self.bits_sent = 0
        self.ether.add_transmitter(self)

    def _start_transmission(self):
        # This implements carrier sense and deference: a station will not start
        # transmitting while hearing carrier.
        if not self.ether.is_busy():
            self._start_transmission_now()
        # If busy, remain in SENSING state.

    def _handle_collision(self):
        # Interference detection is key. A station detecting a collision
        # knows its packet has been damaged and can retransmit immediately
        # after backoff, avoiding long timeouts.
        self.state = State.JAMMING
        self.jam_bits_sent = 0
        self.collision_count += 1
        self.total_collisions += 1
        self.ether.is_jammed = True # Signal to all stations on the Ether.
    
    def _start_jamming(self):
        # When a station determines that its transmission is experiencing
        # interference, it momentarily jams the Ether to insure that all other
        # participants in the collision will detect interference and be forced to abort.
        # This is the "collision consensus enforcement" mechanism.
        self.jam_bits_sent += 1
        if self.jam_bits_sent >= self._jam_duration_in_ticks:
            self.ether.remove_transmitter(self)
            self.ether.is_jammed = False # This station's jam signal is over
            self._calculate_and_enter_backoff()

    def _calculate_and_enter_backoff(self):
        # Ethernet controllers use random retransmission intervals. This heuristic
        # approximates Binary Exponential Backoff, adjusting the mean retransmission
        # interval based on collision history to maintain channel efficiency.
        k = min(self.collision_count, 10)
        max_backoff_slots = (2**k) - 1
        backoff_slots = random.randint(0, max_backoff_slots)
        self.backoff_timer = backoff_slots * self._slot_time_in_ticks
        self.state = State.BACKOFF
        
    def tick(self, current_time):
        if self.state == State.IDLE or self.state == State.AWAITING_SCHEDULE:
            self._start_next_transmission(current_time)

        elif self.state == State.SENSING_CARRIER:
            self._start_transmission()

        elif self.state == State.TRANSMITTING:
            # A station can detect interference in the first slot time. If no
            # collision is detected, the Ether has been acquired.
            if self.bits_sent < self._slot_time_in_ticks and self.ether.has_collision():
                # A collision in a TT window is a catastrophic schedule failure.
                if self.current_packet.traffic_class == TrafficClass.TIME_TRIGGERED:
                    print(f"!!! CRITICAL ERROR: Collision during scheduled TT transmission for Stream {self.current_packet.stream_id} !!!")
                self._handle_collision()
                return {"event": "collision", "packet": self.current_packet}

            self.bits_sent += BIT_RATE * TICK_DURATION
            if self.bits_sent >= self.current_packet.total_bits:
                # Successful transmission
                self.ether.remove_transmitter(self)
                self.state = State.IDLE
                self.collision_count = 0
                self.packets_sent += 1
                latency = current_time - self.current_packet.creation_time
                # This packet is delivered only with high probability.
                # Higher-level protocols must ensure reliable communication.
                return {"event": "success", "packet": self.current_packet, "latency": latency}

        elif self.state == State.JAMMING:
            self._start_jamming()
            
        elif self.state == State.BACKOFF:
            self.backoff_timer -= 1
            if self.backoff_timer <= 0:
                self.state = State.SENSING_CARRIER
        
        return None

def run_simulation(num_stations, traffic_mix):
    """
    Main simulation driver, now configured with a traffic mix to model
    a heterogeneous network environment.
    """
    print("--- Initializing Daedalus/CoRE4INET Ethernet Simulation ---")
    print(f"Slot Time: {SLOT_TIME*1e6:.2f} µs | Tick Duration: {TICK_DURATION*1e6:.2f} µs")

    slot_time_in_ticks = round(SLOT_TIME / TICK_DURATION)
    shared_ether = Ether()
    srp_table = SRPTable()
    # Schedule cycle time of 25ms
    scheduler = Scheduler(cycle_time_in_ticks=int(0.025 / TICK_DURATION))
    
    # --- Configuration Phase ---
    print("\n--- Configuring Streams and Schedule ---")
    # Register streams and schedule TT traffic before simulation starts.
    # This reflects the static configuration of real-time systems.
    stream_id_counter = 1
    for stream_config in traffic_mix.get("tt_streams", []):
        srp_table.register_stream(stream_id_counter, TrafficClass.TIME_TRIGGERED)
        scheduler.add_tt_stream_to_schedule(stream_id_counter, stream_config["start_tick"], stream_config["duration_ticks"])
        stream_id_counter += 1
        
    for _ in range(traffic_mix.get("num_rc_streams", 0)):
        srp_table.register_stream(stream_id_counter, TrafficClass.RATE_CONSTRAINED)
        stream_id_counter += 1
        
    # The rest are best-effort by default.

    stations = [Station(i, shared_ether, slot_time_in_ticks, srp_table, scheduler) for i in range(num_stations)]

    # Create initial traffic based on the mix
    total_packets_to_send = 0
    stream_id_iter = 1
    
    # Assign TT streams to specific stations
    for stream_config in traffic_mix.get("tt_streams", []):
        source_station_id = stream_config["source"]
        for _ in range(stream_config["packets"]):
            dest = random.choice([j for j in range(num_stations) if j != source_station_id])
            stations[source_station_id].enqueue_packet(dest, stream_config["payload"], 0, stream_id_iter)
            total_packets_to_send += 1
        stream_id_iter += 1

    # Assign RC and BE streams randomly
    all_stream_ids = list(srp_table.streams.keys())
    for i in range(num_stations):
        for _ in range(traffic_mix.get("packets_per_station_rc", 0)):
            rc_streams = [sid for sid, tc in srp_table.streams.items() if tc == TrafficClass.RATE_CONSTRAINED]
            if rc_streams:
                stations[i].enqueue_packet(random.randint(0, num_stations-1), 1500*8, 0, random.choice(rc_streams))
                total_packets_to_send += 1
        for _ in range(traffic_mix.get("packets_per_station_be", 0)):
             stations[i].enqueue_packet(random.randint(0, num_stations-1), 1024*8, 0, 999) # Stream 999 is unregistered -> BE
             total_packets_to_send +=1
             
    successful_transmissions = collections.defaultdict(list)
    
    print(f"\nStarting simulation for {SIMULATION_TICKS} ticks...")
    # The system must achieve synchronization for the schedule to be valid.
    scheduler.is_synchronized = True
    print("[System] Clock Synchronization Achieved. TT Schedule is now active.")

    for t in range(SIMULATION_TICKS):
        global current_tick
        current_tick = t
        current_time = t * TICK_DURATION

        random.shuffle(stations) # Randomize station processing order each tick
        for station in stations:
            result = station.tick(current_time)
            if result and result["event"] == "success":
                pkt = result["packet"]
                successful_transmissions[pkt.traffic_class].append(result)

        # Check for new collisions on the Ether
        if shared_ether.has_collision():
            for station in list(shared_ether.transmitting_stations):
                 # Only stations actively transmitting will detect the collision
                 if station.state == State.TRANSMITTING:
                    station._handle_collision()

        if sum(len(v) for v in successful_transmissions.values()) == total_packets_to_send:
            print(f"All packets transmitted successfully by tick {t}.")
            break

    print("\n--- Simulation Complete ---")
    
    # --- Performance Analysis ---
    total_collisions = sum(s.total_collisions for s in stations)
    total_sent = sum(len(v) for v in successful_transmissions.values())
    
    print(f"Total Ticks: {t+1} | Total Time: {current_time * 1000:.2f} ms")
    print(f"Successful Packets: {total_sent} / {total_packets_to_send}")
    print(f"Total Collisions Detected: {total_collisions}")

    if total_sent > 0:
        all_successful = [p for v in successful_transmissions.values() for p in v]
        total_bits_sent = sum(p['packet'].total_bits for p in all_successful)
        # Use the time of the last successful packet transmission for throughput calculation
        total_time_elapsed = max(p['packet'].creation_time + p['latency'] for p in all_successful)
        
        throughput_bps = total_bits_sent / total_time_elapsed if total_time_elapsed > 0 else 0
        print(f"\n--- Aggregate Performance ---")
        print(f"Total Bits Delivered: {total_bits_sent}")
        print(f"Effective Throughput: {throughput_bps / 1e6:.4f} Mbps")
        
        # The model's efficiency is the fraction of time the Ether is carrying good packets.
        # The remaining time is the contention interval.
        transmission_time = total_bits_sent / BIT_RATE
        efficiency = transmission_time / current_time if current_time > 0 else 0
        print(f"Ether Efficiency (Transmission Time / Total Time): {efficiency:.4f}")

        print("\n--- Per-Class Performance ---")
        for traffic_class in TrafficClass:
            if successful_transmissions[traffic_class]:
                class_transmissions = successful_transmissions[traffic_class]
                count = len(class_transmissions)
                avg_latency = (sum(p['latency'] for p in class_transmissions) / count) * 1000
                print(f"  {traffic_class.name}:")
                print(f"    Packets Sent: {count}")
                print(f"    Avg. Latency: {avg_latency:.4f} ms")
            else:
                print(f"  {traffic_class.name}: No packets sent.")


if __name__ == "__main__":
    # This simulation configuration models a network with a mix of traffic types,
    # including high-priority, scheduled TT streams and lower-priority traffic.
    # This reflects the kind of complex, heterogeneous environment where the
    # Daedalus architecture is designed to excel.
    
    traffic_profile = {
        "tt_streams": [
            {
                "source": 0, "stream_id": 1, "payload": 512*8, "packets": 5,
                "start_tick": 100, "duration_ticks": 200
            },
            {
                "source": 5, "stream_id": 2, "payload": 256*8, "packets": 5,
                "start_tick": 400, "duration_ticks": 100
            },
        ],
        "num_rc_streams": 3,
        "packets_per_station_rc": 3,
        "packets_per_station_be": 2,
    }

    run_simulation(num_stations=10, traffic_mix=traffic_profile)

