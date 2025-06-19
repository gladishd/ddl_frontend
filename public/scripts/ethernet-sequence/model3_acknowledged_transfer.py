#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Based Ethernet + TCP Simulation
-------------------------------------
Simulates a single TCP connection over a shared Ethernet medium (CSMA/CD)
between two endpoints (A ↔ B), showing packet-level events step by step.

Features:
  1. Full TCP three-way handshake (SYN, SYN-ACK, ACK).
  2. Data transfer: A sends DATA segments, B ACKs each one.
  3. Distinct packet types: SYN, SYN-ACK, ACK, DATA.
  4. Underlying Ethernet channel with collision detection and jamming.
  5. Detailed event logging for visualization.

Usage:
  python comprehensive.py --mss 1000 --data 10000 --slot 1 --simtime 1000
"""

import simpy # This is why it takes so long
import enum
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt

# ----- Packet definitions -----
class PacketType(enum.Enum):
    SYN     = "SYN"
    SYN_ACK = "SYN-ACK"
    ACK     = "ACK"
    DATA    = "DATA"

class Packet:
    def __init__(self, ptype, seq=0, ack=0, src=None, dst=None, size=0):
        self.ptype = ptype
        self.seq   = seq
        self.ack   = ack
        self.src   = src
        self.dst   = dst
        self.size  = size  # payload bytes
        self.success = True  # will be set on transmission completion

    def __repr__(self):
        if self.ptype == PacketType.DATA:
            return f"{self.ptype.value}[{self.seq}]→{self.dst}"
        else:
            return f"{self.ptype.value}[{self.seq}/{self.ack}]"

# ----- Ethernet channel -----
class Channel:
    def __init__(self, env, slot_time):
        self.env = env
        self.slot_time = slot_time
        self.current = []
        self.collided = False
        self.log = []  # (time, 'start'/'end', packet)

    def transmit(self, packet, duration):
        """Begin sending packet; detect collision if >1 active."""
        self.current.append(packet)
        if len(self.current) > 1:
            self.collided = True
        self.log.append((self.env.now, 'start', packet))
        return self.env.process(self._finish(packet, duration))

    def _finish(self, packet, duration):
        yield self.env.timeout(duration)
        self.current.remove(packet)
        packet.success = not self.collided
        self.log.append((self.env.now, 'end', packet))
        if not self.current:
            self.collided = False

# ----- TCP endpoint -----
class TCPEndpoint:
    def __init__(self, env, name, channel, peer, mss, data_size, slot_time):
        self.env = env
        self.name = name
        self.channel = channel
        self.peer = peer          # reference to other endpoint
        self.mss = mss
        self.data_size = data_size
        self.slot_time = slot_time

        self.next_seq = 0
        self.sent = {}
        self.acked = set()
        env.process(self.run())

    def send_packet(self, pkt):
        pkt.src = self.name
        pkt.dst = self.peer.name
        # normalize duration: assume FRAME_TIME proportional to payload/MSS
        duration = max(1, pkt.size // self.mss) * self.slot_time
        return self.channel.transmit(pkt, duration)

    def receive(self, pkt):
        """Called by deliverer when a packet finishes successfully."""
        # only handle if success
        if not pkt.success or pkt.dst != self.name:
            return
        if pkt.ptype == PacketType.SYN:
            synack = Packet(PacketType.SYN_ACK, seq=0, ack=1)
            yield self.send_packet(synack)
        elif pkt.ptype == PacketType.SYN_ACK:
            ack = Packet(PacketType.ACK, seq=1, ack=1)
            yield self.send_packet(ack)
        elif pkt.ptype == PacketType.DATA:
            ack = Packet(PacketType.ACK, seq=0, ack=pkt.seq + pkt.size)
            yield self.send_packet(ack)
        elif pkt.ptype == PacketType.ACK:
            self.acked.add(pkt.ack)

    def run(self):
        # Initiator A does handshake
        if self.name == 'A':
            syn = Packet(PacketType.SYN, seq=0, ack=0)
            yield self.send_packet(syn)

        # Wait handshake completion
        while True:
            # A waits for ACK seq=1 to itself
            if self.name=='A' and 1 in self.acked:
                break
            # B waits for SYN to itself
            if self.name=='B' and any(evt for _,evt,p in self.channel.log if evt=='start' and p.ptype==PacketType.SYN and p.dst=='B'):
                break
            yield self.env.timeout(self.slot_time/10)

        # Data transfer from A to B
        if self.name == 'A':
            while self.next_seq < self.data_size:
                pkt = Packet(PacketType.DATA, seq=self.next_seq, size=self.mss)
                self.sent[self.next_seq] = pkt
                yield self.send_packet(pkt)
                # wait for corresponding ACK
                while (self.next_seq + self.mss) not in self.acked:
                    yield self.env.timeout(self.slot_time)
                self.next_seq += self.mss

# ----- Simulation & Delivery -----
def simulate(mss, data_size, slot_time, sim_time):
    env = simpy.Environment()
    channel = Channel(env, slot_time)
    A = TCPEndpoint(env, 'A', channel, None, mss, data_size, slot_time)
    B = TCPEndpoint(env, 'B', channel, A, mss, data_size, slot_time)
    A.peer = B

    # deliver completed packets to endpoints
    def deliver():
        last_idx = 0
        while True:
            # check new log entries
            for entry in channel.log[last_idx:]:
                t, ev, pkt = entry
                if ev == 'end':
                    # schedule reception handling
                    env.process(A.receive(pkt))
                    env.process(B.receive(pkt))
                last_idx += 1
            yield env.timeout(slot_time/10)

    env.process(deliver())
    env.run(until=sim_time)
    return channel.log

# ----- Visualization -----
def visualize(log, slot_time):
    # build intervals
    starts = {}
    intervals = []
    for t, ev, pkt in log:
        if ev == 'start':
            starts[pkt] = t
        else:
            s = starts.pop(pkt, None)
            if s is not None:
                intervals.append((pkt, s, t-s, pkt.success))

    fig, ax = plt.subplots(figsize=(12,6))
    y_map = {'A→B':1, 'B→A':2}
    for pkt, s, d, ok in intervals:
        direction = f"{pkt.src}→{pkt.dst}"
        ax.broken_barh([(s, d)], (y_map[direction]-0.4, 0.8),
                       facecolors=('green' if ok else 'red'))
        ax.text(s + d/2, y_map[direction], repr(pkt),
                ha='center', va='center', color='white', fontsize=8)

    ax.set_yticks([1, 2])
    ax.set_yticklabels(['A→B', 'B→A'])
    ax.set_xlabel("Time")
    ax.set_title("TCP over Ethernet Packet Timeline\n(green=success, red=collision)")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

# ----- Main -----
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mss",      type=int,   default=1000)
    parser.add_argument("--data",     type=int,   default=10000)
    parser.add_argument("--slot",     type=float, default=1)
    parser.add_argument("--simtime",  type=float, default=1000)
    args = parser.parse_args()

    log = simulate(args.mss, args.data, args.slot, args.simtime)
    visualize(log, args.slot)

if __name__ == "__main__":
    main()
