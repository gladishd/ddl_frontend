#!/usr/bin/env python3
"""
ethernetsimulation.py

A corrected and more accurate simulation of Ethernet CSMA/CD contention.
This version fixes logical errors in the original script that caused infinite loops
and models host behavior more accurately.

Key improvements:
 - Stateful hosts that manage their own frame queues and collision backoffs.
 - A medium that correctly orchestrates transmission attempts, collision detection,
   and successful transmissions.
 - Correct implementation of binary exponential backoff, which was a source of
   the original infinite loop.
 - Clearer separation of concerns between Host and Medium classes.

Usage:
  python ethernetsimulation.py [--bitrate BITRATE] [--hosts N] [--frames M] [--simtime T]
"""
import random
import heapq
import sys
from dataclasses import dataclass

def parse_args():
    """Parses command-line arguments for the simulation."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Ethernet CSMA/CD contention simulation')
    parser.add_argument('--bitrate', type=float, default=10e6,
                        help='Medium bit rate in bits per second')
    parser.add_argument('--hosts', type=int, default=5,
                        help='Number of competing hosts')
    parser.add_argument('--frames', type=int, default=10,
                        help='Number of frames per host to send')
    parser.add_argument('--simtime', type=float, default=1.0,
                        help='Simulation duration in seconds')
    return parser.parse_args()

@dataclass
class Frame:
    """
    Represents a data frame. It's a simple data carrier and does not hold state
    like collision counts, as that state belongs to the host's transmission attempt.
    """
    src: int
    size_bits: float
    id: int

class Medium:
    """
    Manages the shared communication medium. It is responsible for scheduling
    events and tracking the medium's state (free or busy). It is the central
    clock and event coordinator for the simulation.
    """
    def __init__(self, bit_rate):
        self.bit_rate = bit_rate
        self.events = []
        self.current_time = 0.0
        # This set tracks which hosts are currently trying to transmit in the
        # collision vulnerability window.
        self.transmitting_hosts = set()
        # A reference to all host objects is kept to call their methods.
        self.hosts = {}

    def add_host(self, host):
        """Adds a host to the medium's knowledge."""
        self.hosts[host.id] = host

    def schedule(self, delay, callback, *args):
        """Schedules a future event. `delay` is in seconds."""
        event_time = self.current_time + delay
        # id(callback) is used as a tie-breaker for events at the same time in the heap.
        heapq.heappush(self.events, (event_time, id(callback), callback, args))

    def run(self, until):
        """Runs the simulation event loop until the specified time."""
        while self.events:
            time, _, callback, args = heapq.heappop(self.events)
            # Ensure simulation does not run past the specified end time.
            if time > until:
                break
            self.current_time = time
            callback(*args)

    def attempt_transmit(self, host):
        """
        A host calls this to attempt to transmit a frame. This is the entry
        point for the CSMA/CD logic on the medium.
        """
        # CSMA (Carrier Sense Multiple Access): If the medium is busy, the host must defer.
        if self.transmitting_hosts:
            host.on_medium_busy()
            return

        # The medium is free. The host starts transmitting.
        # It enters a vulnerability window where a collision can occur.
        self.transmitting_hosts.add(host)
        
        # A collision can only be detected for certain after one propagation delay.
        # We schedule an event to resolve the state of the medium after this delay.
        propagation_delay = 512.0 / (2 * self.bit_rate) # Simplified one-way delay
        self.schedule(propagation_delay, self._resolve_transmission, host)

    def _resolve_transmission(self, initial_host):
        """
        This is called after a propagation delay to determine if a collision
        occurred or if the transmission was successful.
        """
        # If the host that initiated this check was forced to back off by a
        # collision it detected, it would no longer be in the transmitting set.
        if initial_host not in self.transmitting_hosts:
            return

        # CD (Collision Detection): Check if more than one host is transmitting.
        if len(self.transmitting_hosts) > 1:
            # A collision occurred. Notify all hosts that were transmitting.
            colliding_hosts = list(self.transmitting_hosts)
            print(f"{self.current_time:.6f}s: Collision detected among hosts {[h.id for h in colliding_hosts]}")
            for host in colliding_hosts:
                host.on_collision()
            self.transmitting_hosts.clear()
        else:
            # Success! The host has acquired the medium.
            # Schedule the completion of this successful transmission.
            tx_time = initial_host.current_frame.size_bits / self.bit_rate
            self.schedule(tx_time, self._finish_transmission, initial_host)

    def _finish_transmission(self, host):
        """
        Called when a frame has been successfully transmitted without collision.
        """
        # This function is only called for successful transmissions.
        print(f"{self.current_time:.6f}s: Host {host.id} finished sending frame {host.current_frame.id}")
        
        # The host is now done transmitting this frame.
        if host in self.transmitting_hosts:
             self.transmitting_hosts.remove(host)
        
        # Notify the host of its success.
        host.on_success()

class Host:
    """
    Represents a host on the network. Each host now manages its own frame queue,
    and handles its own retransmissions after collisions using binary exponential backoff.
    This is a key change to fix the original code's state management flaws.
    """
    def __init__(self, host_id, medium, num_frames):
        self.id = host_id
        self.medium = medium
        self.frames_to_send_queue = [Frame(self.id, size_bits=1500*8, id=i) for i in range(num_frames)]
        self.current_frame = None
        self.collision_count = 0

    def start(self, initial_delay):
        """Prepares the first frame and schedules its first transmission attempt."""
        if self.frames_to_send_queue:
            self.current_frame = self.frames_to_send_queue.pop(0)
            self.medium.schedule(initial_delay, self._attempt_to_send)

    def on_success(self):
        """Callback from the Medium after a successful transmission."""
        print(f"  -> Host {self.id} acknowledged success for frame {self.current_frame.id}")
        self.collision_count = 0
        self.current_frame = None
        # If there are more frames, prepare the next one and attempt to send it.
        if self.frames_to_send_queue:
            self.current_frame = self.frames_to_send_queue.pop(0)
            # Attempt to send the next frame after a small "processing" delay.
            self.medium.schedule(1e-6, self._attempt_to_send)

    def on_collision(self):
        """
        Callback from the Medium when a collision occurs. This is the BEB algorithm.
        This fixes the bug where backoff was based on frame ID instead of collision count.
        """
        self.collision_count += 1
        # The backoff exponent `k` is capped at 10.
        k = min(self.collision_count, 10)
        slot_time = 512.0 / self.medium.bit_rate # Standard Ethernet slot time
        
        # Choose a random number of slots to wait.
        backoff_slots = random.randint(0, 2**k - 1)
        backoff_delay = backoff_slots * slot_time
        
        # Reschedule the transmission attempt for the *same* frame.
        self.medium.schedule(backoff_delay, self._attempt_to_send)

    def on_medium_busy(self):
        """Callback from the Medium if the host senses a busy channel."""
        # Defer: try again after a very short time to emulate persistent sensing.
        defer_delay = 512.0 / (10 * self.medium.bit_rate) # A fraction of a slot time
        self.medium.schedule(defer_delay, self._attempt_to_send)

    def _attempt_to_send(self):
        """Wrapper to call the medium's transmit logic."""
        if self.current_frame:
            self.medium.attempt_transmit(self)

def main():
    """Sets up and runs the simulation."""
    args = parse_args()
    medium = Medium(bit_rate=args.bitrate)
    
    hosts = [Host(i, medium, args.frames) for i in range(args.hosts)]
    for host in hosts:
        medium.add_host(host)
        # Schedule each host to start at a random time to avoid a guaranteed
        # collision at time t=0.
        host.start(initial_delay=random.uniform(0, 0.005))

    print(f"Simulating {args.hosts} hosts, {args.frames} frames each, "
          f"bitrate={args.bitrate/1e6:.1f}Mbps for {args.simtime}s")
    
    medium.run(until=args.simtime)
    
    print("\n--- Simulation complete ---")
    for host in hosts:
        frames_sent = args.frames - len(host.frames_to_send_queue)
        if host.current_frame: # Account for the frame that was being processed
             frames_sent -=1
        print(f"Host {host.id} successfully sent {frames_sent}/{args.frames} frames.")


if __name__ == '__main__':
    main()
