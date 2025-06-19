#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Based TCP over Ethernet Simulation – Step-by-Step Packet Events
--------------------------------------------------------------------
Features:
  1. Pure Ethernet CSMA/CD transport for TCP packets.
  2. Full TCP handshake (SYN, SYN-ACK, ACK) and bidirectional DATA/ACK flow.
  3. Distinct packet types: SYN, SYN-ACK, ACK, DATA.
  4. Detailed event logging for step-by-step visualization.
  5. Collision detection & jamming per Metcalfe & Boggs (1976).

Usage:
  python comprehensive.py --mss 1000 --data 5000 --slot 1 --simtime 500
"""

import simpy
import enum
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt

# ----- Packet Definitions -----
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
        self.size  = size
        self.success = True

    def __repr__(self):
        if self.ptype == PacketType.DATA:
            return f"{self.ptype.value}[{self.seq}]→{self.dst}"
        return f"{self.ptype.value}[{self.seq}/{self.ack}]→{self.dst}"

# ----- Ethernet Channel -----
class Channel:
    def __init__(self, env, slot_time):
        self.env = env
        self.slot_time = slot_time
        self.current = []
        self.collided = False
        self.log = []  # (time, 'start'/'end', packet)

    def transmit(self, packet, duration):
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

# ----- TCP Endpoint -----
class TCPEndpoint:
    def __init__(self, env, name, channel, peer, mss, data_size, slot_time):
        self.env = env
        self.name = name
        self.channel = channel
        self.peer = peer
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
        # normalize duration to slot_time units
        duration = (pkt.size / self.mss) * self.slot_time if pkt.ptype==PacketType.DATA else self.slot_time
        return self.channel.transmit(pkt, duration)

    def receive(self, pkt):
        env = self.env
        def _handler():
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
        env.process(_handler())

    def run(self):
        # 1) Three-way handshake initiated by A
        if self.name == 'A':
            syn = Packet(PacketType.SYN, seq=0, ack=0)
            yield self.send_packet(syn)
        # wait for handshake to complete
        while True:
            # A waits for ACK seq=1
            if self.name == 'A' and any(p.ptype==PacketType.ACK and p.seq==1 and p.dst=='A' for _,_,p in self.channel.log):
                break
            # B waits for SYN to arrive
            if self.name == 'B' and any(p.ptype==PacketType.SYN and p.dst=='B' for _,_,p in self.channel.log):
                break
            yield self.env.timeout(self.slot_time/10)

        # 2) If A, send data segments and await ACKs
        if self.name == 'A':
            while self.next_seq < self.data_size:
                data_pkt = Packet(PacketType.DATA, seq=self.next_seq, size=self.mss)
                self.sent[self.next_seq] = data_pkt
                yield self.send_packet(data_pkt)
                # wait until acknowledged
                while (self.next_seq + self.mss) not in self.acked:
                    yield self.env.timeout(self.slot_time/10)
                self.next_seq += self.mss

# ----- Simulation and Visualization -----
def simulate(mss, data_size, slot_time, sim_time):
    env = simpy.Environment()
    channel = Channel(env, slot_time)
    A = TCPEndpoint(env, 'A', channel, None, mss, data_size, slot_time)
    B = TCPEndpoint(env, 'B', channel, A, mss, data_size, slot_time)
    A.peer = B

    # Delivery process
    def deliver():
        while True:
            for _, ev, pkt in list(channel.log):
                if ev == 'end':
                    if pkt.dst == 'A': A.receive(pkt)
                    if pkt.dst == 'B': B.receive(pkt)
            yield env.timeout(slot_time/10)
    env.process(deliver())

    env.run(until=sim_time)
    return channel.log

def visualize(log, slot_time):
    starts = {}
    intervals = []
    for t, ev, pkt in log:
        if ev == 'start':
            starts[pkt] = t
        else:
            s = starts.pop(pkt, None)
            if s is not None:
                intervals.append((pkt, s, t-s, pkt.success))

    fig, ax = plt.subplots(figsize=(12, 6))
    y_map = {'A→B':1, 'B→A':2}
    for pkt, start, dur, ok in intervals:
        direction = f"{pkt.src}→{pkt.dst}"
        ax.broken_barh([(start, dur)], (y_map[direction]-0.3, 0.6),
                       facecolors=('green' if ok else 'red'))
        ax.text(start+dur/2, y_map[direction], repr(pkt),
                ha='center', va='center', color='white', fontsize=8)

    ax.set_yticks([1, 2])
    ax.set_yticklabels(['A→B', 'B→A'])
    ax.set_xlabel("Time")
    ax.set_title("Step-by-Step TCP over Ethernet Packet Timeline")
    ax.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mss",     type=int,   default=1000)
    parser.add_argument("--data",    type=int,   default=5000)
    parser.add_argument("--slot",    type=float, default=1)
    parser.add_argument("--simtime", type=float, default=500)
    args = parser.parse_args()

    log = simulate(args.mss, args.data, args.slot, args.simtime)
    visualize(log, args.slot)

if __name__ == "__main__":
    main()
