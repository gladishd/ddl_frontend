#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Agent-Based Ethernet Simulation with Visualizations
----------------------------------------------------------------
Implements:
  1. Pure ALOHA
  2. Slotted ALOHA
  3. CSMA/CD with Binary Exponential Backoff

Core mechanisms:
  - Shared medium contention
  - Collision detection & jamming
  - Randomized retransmission (Metcalfe & Boggs 1976)
  - Truncated binary exponential backoff
  - Comparative throughput analysis

Adds visualizations:
  1. Medium usage timeline
  2. Per-station transmission Gantt chart (green=success, red=collision)
  3. Per-station success counts bar chart

Usage:
  python ethernet_sim.py --nodes N --time T --rate λ --protocol [pure|slotted|csma]
"""

import simpy
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Globals
SLOT_TIME = 1
FRAME_TIME = 1
MAX_BACKOFF_EXP = 10

class Channel:
    def __init__(self, env):
        self.env = env
        self.current = []
        self.collided = False
        self.log = []  # (time, 'start'/'end', node_id, success)

    def start_tx(self, node_id, duration):
        self.current.append(node_id)
        if len(self.current) > 1:
            self.collided = True
        self.log.append((self.env.now, 'start', node_id, None))
        return self.env.process(self._finish_tx(node_id, duration))

    def _finish_tx(self, node_id, duration):
        yield self.env.timeout(duration)
        self.current.remove(node_id)
        success = not self.collided
        self.log.append((self.env.now, 'end', node_id, success))
        if not self.current:
            self.collided = False

class Node:
    def __init__(self, env, node_id, channel, arrival_rate, protocol):
        self.env = env
        self.id = node_id
        self.channel = channel
        self.arrival_rate = arrival_rate
        self.protocol = protocol
        self.backoff_exp = 0
        self.packets = 0
        self.successes = 0
        env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            self.packets += 1
            if self.protocol == 'pure':
                yield from self.pure_aloha()
            elif self.protocol == 'slotted':
                yield from self.slotted_aloha()
            else:
                yield from self.csma_cd()

    def pure_aloha(self):
        while True:
            # start transmission
            proc = self.channel.start_tx(self.id, FRAME_TIME)
            yield proc
            # check outcome
            t, typ, nid, ok = self.channel.log[-1]
            if nid == self.id and ok:
                self.successes += 1
                self.backoff_exp = 0
                return
            # collision: random exponential backoff
            self.backoff_exp = min(self.backoff_exp + 1, MAX_BACKOFF_EXP)
            yield self.env.timeout(random.uniform(0, 2**self.backoff_exp))

    def slotted_aloha(self):
        while True:
            # wait for slot boundary
            yield self.env.timeout(SLOT_TIME - (self.env.now % SLOT_TIME))
            proc = self.channel.start_tx(self.id, FRAME_TIME)
            yield proc
            t, typ, nid, ok = self.channel.log[-1]
            if nid == self.id and ok:
                self.successes += 1
                self.backoff_exp = 0
                return
            # collision: integer-slot backoff
            self.backoff_exp = min(self.backoff_exp + 1, MAX_BACKOFF_EXP)
            slots = random.randint(0, 2**self.backoff_exp)
            yield self.env.timeout(slots * SLOT_TIME)

    def csma_cd(self):
        while True:
            # sense channel idle
            while self.channel.current:
                yield self.env.timeout(SLOT_TIME/10)
            proc = self.channel.start_tx(self.id, FRAME_TIME)
            yield proc
            t, typ, nid, ok = self.channel.log[-1]
            if nid == self.id and ok:
                self.successes += 1
                self.backoff_exp = 0
                return
            # collision: jam + backoff
            yield self.env.timeout(FRAME_TIME * 0.1)
            self.backoff_exp = min(self.backoff_exp + 1, MAX_BACKOFF_EXP)
            backoff = random.randint(0, 2**self.backoff_exp) * SLOT_TIME
            yield self.env.timeout(backoff)

def simulate(nodes, sim_time, arrival_rate, protocol):
    env = simpy.Environment()
    channel = Channel(env)
    stations = [Node(env, i+1, channel, arrival_rate, protocol) for i in range(nodes)]
    env.run(until=sim_time)
    return stations, arrival_rate * nodes * FRAME_TIME, channel.log

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes",   type=int,   default=10)
    parser.add_argument("--time",    type=float, default=10000)
    parser.add_argument("--rate",    type=float, default=0.005)
    parser.add_argument("--protocol",choices=['pure','slotted','csma'], default='csma')
    args = parser.parse_args()

    stations, G, log = simulate(args.nodes, args.time, args.rate, args.protocol)

    S = sum(n.successes for n in stations) / args.time
    print(f"Protocol: {args.protocol}")
    print(f"Offered load G = {G:.3f}")
    print(f"Throughput S = {S:.3f} pkts/unit time")

    # Medium usage timeline
    times = [t for (t,_,_,_) in log]
    deltas = [1 if typ=='start' else -1 for (_,typ,_,_) in log]
    usage = np.cumsum(deltas)

    # Station intervals
    intervals = []
    start_times = {}
    for t, typ, nid, ok in log:
        if typ == 'start':
            start_times[nid] = t
        else:
            s = start_times.pop(nid, None)
            if s is not None:
                intervals.append((nid, s, t-s, ok))

    fig, (ax1, ax2, ax3) = plt.subplots(3,1,figsize=(12,10), sharex=True)

    # 1) Medium contention
    ax1.step(times, usage, where='post')
    ax1.set_ylabel("Active TXs")
    ax1.set_title("Medium Contention Timeline")
    ax1.grid(True)

    # 2) Gantt chart
    for nid, start, dur, ok in intervals:
        color = 'green' if ok else 'red'
        ax2.broken_barh([(start, dur)], (nid-0.4,0.8), facecolors=color)
    ax2.set_ylabel("Node")
    ax2.set_title("Per-Node Transmission Events")
    ax2.set_yticks(range(1, args.nodes+1))
    ax2.grid(True)

    # 3) Success counts
    ids = [n.id for n in stations]
    succ = [n.successes for n in stations]
    ax3.bar(ids, succ)
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Successful TXs")
    ax3.set_title("Per-Node Success Counts")
    ax3.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
