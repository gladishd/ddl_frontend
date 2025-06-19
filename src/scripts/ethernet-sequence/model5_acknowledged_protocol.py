# Notes. I want to have WITH contention not just WITHOUT contention. The idea is to have clearly explainable visualizations to show for Monday..for what we show at O.A.E. it has to be shown in Mathematica; need the link logs; need to be able to interpret and render (what I render is inconsequential just need to show that we have packet-level simulations in Mathematica & that we're working on that)..if we can just show ALOHA throughput and Latency in ALOHA and Half-Duplex Ethernet and Full-Duplex Ethernet, that should be good! We've modeled every kind of inter-point channel and now we can extend this over multiple ops. Don't want us to be divergent on the code that we write; the emulator should work for this also. And the problem with the emulator is that all the links are asynchronous; you can't exactly line up an event between two links! You can have a start of simulation but if the transfer happens on one link..there's no correlation it's very hard to correlate it with the transfer of the packet on the other link. Could be solved with Packet IDs or Packet Hashes. At some point we're going to have to extend the Emulator so that it's compatible with my Mathematica Visualizations.

# Do you think we can get this together by October 15th? Thinking of submitting this as abstract for OCP Global Symposium
# We present DynamicNetworks, a Mathematica based simulation toolkit for interactively modeling and visualizing packet networks across historical and modern topologies. Starting from early protocols like ALOHA and 1970s #Ethernet, the framework reproduces phenomena such as collision domains, retransmission timing, and congestion collapse. We then extend the simulation to Clos networks and experimental systems like Open Atomic #Ethernet, enabling direct experimentation with deterministic multicast and atomic commit semantics.
# The tool emphasizes time-evolving visualizations, packet flow tracking, and parameter tuning in real time — bridging the gap between textbook theory and live systems intuition. Engineers and researchers can use the model to explore network efficiency under different topologies and protocols, with built-in support for latency tracing and congestion visualization. This talk will include a live demonstration and is intended to spark cross-domain dialogue between protocol designers, network operators, and educators.
# I’m wondering, can the emulator and your simulator be merged in some way? They seem to be similar but it’s the reliance on a global ordering of events to line up transmission events in your simulator that makes it incompatible
# If there was some synchronization mechanism between the link logs in the emulator where we could replay a multiple packet traces in Mathematica we could remove the need for a global priority queue and instead model it using the existing emulator code
# My code was written with the assumption of point to point links so broadcast interfaces like 1976 Ethernet would be hard to model at..This is just a thought, keep working on the python!

# How do we simulate this stuff and simulate it in Mathematica..at some point trash the Python code I'm writing and use the Mathematica side of it with PowerEmulator. Don't go too overboard with refactor..can just take this knowledge and put it into the Emulator..how do we track throughput in the emulator..data center project..boiling an ocean keep working on this code..keep the emulator and the simulator separate! The purpose of this simulator is to create packet trace groups that are analyzable in Mathematica and we'll do a lot of learning on what kind of information has to be tracked so that we can make visualizations out of it and then build those logs into the Emulator.. no longer going to be able to use SimPy..**

# **SimPy assumes a global time order..instead we have to track throughput over a whole bunch of asynchronous logs which is its own..we'll have to design an architecture for that.

# DDL_Emulator: Acknowledged Ethernet Simulation
#
# This script provides a more specific agent-based simulation of a reliable,
# acknowledged data transfer over a contentious Ethernet medium. It moves beyond
# simple broadcast to model a bidirectional, TCP-like flow.
#
# Inspired by the Daedaelus philosophy, this simulation demonstrates the mechanics
# of reliable protocols and the importance of round-trip interactions, providing
# a computational basis for the arguments in "Bandwidth Works in Practice, not in Theory."
#
# It models a protocol similar to the EFTP described by Metcalfe, where data
# packets require explicit acknowledgment to be considered successfully delivered.
# "Each data packet is retransmitted periodically by the sender until an ack packet
# with a matching sequence number is returned from the receiver."
#
# The simulation visually distinguishes between DATA and ACK packets to provide a
# clear, step-by-step view of the entire transaction lifecycle.
#

import simpy
import random
import math
import collections
import pygame
import sys
import imageio

# --- Simulation Configuration ---

# NEED to figure out this Interface between Mathematica and Python
# Eventually the Mathematica package would be in Rust..before we convert the emulator to Rust we have to figure out how to generate the logs that Mathematica will use
# Not just packets but bit for bit what's going on this is more of an exploration on the Emulator side the exact bits TODO Keep doing this in Python..after the conference
# then we'll integrate it all into one Rust


class Config:
    """
    Configuration parameters for the Ethernet simulation.
    Adjust these values to explore different network scenarios.
    """
    # General Simulation Settings
    SIMULATION_MODE = 'CSMA_CD'
    SIM_DURATION_S = 4.0  # Maximum simulation time in seconds, acts as a safeguard
    RANDOM_SEED = 42

    # NEW: Slow down the animation for better viewing. Higher value = slower animation.
    ANIMATION_SPEED_FACTOR = 50.0

    # Protocol-Specific Settings
    SENDER_ID = 0
    RECEIVER_ID = 1
    TOTAL_DATA_PACKETS = 50
    RETRANSMISSION_TIMEOUT_S = 0.1

    # Physical Layer Parameters
    NUM_STATIONS = 5
    ETHER_LENGTH_M = 500
    PROPAGATION_SPEED_M_S = 2e8
    ETHER_SPEED_BPS = 3e6

    # Packet Parameters
    DATA_PACKET_BITS = 4096
    ACK_PACKET_BITS = 256
    JAM_SIGNAL_BITS = 32
    MEAN_BACKGROUND_ARRIVAL_S = 100.0  # Set high to minimize background noise

    # Visualization Settings
    VISUALIZATION = True
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    DATA_COLOR = (100, 255, 100)
    ACK_COLOR = (100, 200, 255)
    PACKET_HEIGHT = 15
    STATION_COLOR = (200, 200, 200)
    IDLE_COLOR = (100, 100, 255)

    # Calculated Parameters
    @staticmethod
    def get_params():
        p = {}
        p['propagation_delay_s'] = Config.ETHER_LENGTH_M / \
            Config.PROPAGATION_SPEED_M_S
        p['slot_time_s'] = 2 * p['propagation_delay_s']
        p['data_tx_time_s'] = Config.DATA_PACKET_BITS / Config.ETHER_SPEED_BPS
        p['ack_tx_time_s'] = Config.ACK_PACKET_BITS / Config.ETHER_SPEED_BPS
        p['jam_tx_time_s'] = Config.JAM_SIGNAL_BITS / Config.ETHER_SPEED_BPS
        return p


class Packet:
    """Represents a packet with type, sequence and ack numbers."""

    def __init__(self, packet_type, seq_num, ack_num, source_id, destination_id):
        self.packet_type = packet_type
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.source_id = source_id
        self.destination_id = destination_id
        self.color = Config.DATA_COLOR if packet_type == 'DATA' else Config.ACK_COLOR


class Ether:
    """
    Represents the shared communication medium. It is a passive facility
    that broadcasts signals to all stations and allows for collision detection.
    """

    def __init__(self, env):
        self.env = env
        # station_id -> (packet, start_time)
        self.transmitting_stations = {}
        self.is_jammed = False
        self.pipes = {}     # station_id -> simpy.Store

    def is_busy(self):
        return len(self.transmitting_stations) > 0

    def has_collision(self):
        return len(self.transmitting_stations) > 1

    def broadcast(self, sender_id, packet):
        """Delivers a packet to all other stations' input pipes."""
        for sid, pipe in self.pipes.items():
            if sid != sender_id:
                pipe.put(packet)


class Station:
    """
    Represents a station with TCP-like logic for sending DATA and receiving ACKs,
    or receiving DATA and sending ACKs.
    """

    def __init__(self, env, station_id, ether, params, stats, viz):
        self.env = env
        self.id = station_id
        self.ether = ether
        self.params = params
        self.stats = stats
        self.viz = viz
        self.packet_queue = simpy.Store(env)
        self.is_sender = (station_id == Config.SENDER_ID)
        self.is_receiver = (station_id == Config.RECEIVER_ID)
        if self.is_sender:
            self.unacked_seq = -1
            self.retx_proc = None
        if self.is_receiver:
            self.expected_seq_num = 0
        self.collisions = 0
        env.process(self.packet_generator())
        env.process(self.receiver_logic())
        env.process(self.sender_logic())

    def packet_generator(self):
        """The Sender generates a stream of DATA packets to be sent. Produce DATA packets (sender) or background traffic."""
        if self.is_sender:
            for i in range(Config.TOTAL_DATA_PACKETS):
                pkt = Packet('DATA', i, -1, self.id, Config.RECEIVER_ID)
                yield self.packet_queue.put(pkt)
        else:
            while True:
                yield self.env.timeout(random.expovariate(1.0/Config.MEAN_BACKGROUND_ARRIVAL_S))
                dest = random.choice(
                    [i for i in range(Config.NUM_STATIONS) if i != self.id])
                pkt = Packet('DATA', -1, -1, self.id, dest)
                yield self.packet_queue.put(pkt)

    def receiver_logic(self):
        """Process that continuously listens for incoming packets. Listen for incoming DATA, send ACKs, handle ACKs. Listen for incoming DATA, send ACKs, handle ACKs."""
        pipe = self.ether.pipes[self.id]
        while True:
            pkt = yield pipe.get()
            # Receiver: on DATA
            if self.is_receiver and pkt.packet_type == 'DATA' and pkt.destination_id == self.id:
                if pkt.seq_num == self.expected_seq_num:
                    self.stats['app_packets_received'] += 1
                    self.expected_seq_num += 1
                # send ACK
                ack = Packet('ACK', -1, pkt.seq_num, self.id, pkt.source_id)
                yield self.packet_queue.put(ack)
            # Sender: on ACK
            if self.is_sender and pkt.packet_type == 'ACK' and pkt.destination_id == self.id:
                if pkt.ack_num == self.unacked_seq:
                    self.stats['acks_received'] += 1
                    if self.retx_proc and not self.retx_proc.triggered:
                        self.retx_proc.interrupt()
                    self.unacked_seq = -1

    def sender_logic(self):
        """Process that takes packets from the queue and attempts to send them. Take from queue and initiate transmit/retransmit."""
        while True:
            # Wait if unacked
            if self.is_sender and self.unacked_seq != -1:
                yield self.env.timeout(self.params['slot_time_s'])
                continue
            pkt = yield self.packet_queue.get()
            self.collisions = 0
            if self.is_sender and pkt.packet_type == 'DATA':
                self.unacked_seq = pkt.seq_num
            yield self.env.process(self.transmit_retx_loop(pkt))

    def transmit_retx_loop(self, pkt):
        """Manages the transmission and timeout/retransmission logic for a single packet. CSMA/CD transmit loop with timeout for DATA."""
        while True:
            reliable = (self.is_sender and pkt.packet_type == 'DATA')
            tx_proc = self.env.process(self.csma_cd_transmit(pkt))
            if not reliable:
                yield tx_proc
                return
            # set timeout
            self.retx_proc = self.env.timeout(Config.RETRANSMISSION_TIMEOUT_S)
            res = yield tx_proc | self.retx_proc
            if tx_proc in res:
                return
            else:
                self.stats['timeouts'] += 1
                self.collisions = 0
                if not tx_proc.triggered:
                    tx_proc.interrupt()

    def csma_cd_transmit(self, pkt):
        """The core CSMA/CD logic. Returns True on success, False on collision. Core CSMA/CD; return True on success."""
        tx_time = self.params['data_tx_time_s'] if pkt.packet_type == 'DATA' else self.params['ack_tx_time_s']
        try:
            while True:
                if not self.ether.is_busy():
                    if self.viz:
                        self.viz.update_station_state(self.id, 'transmitting')
                    self.ether.transmitting_stations[self.id] = (
                        pkt, self.env.now)
                    yield self.env.timeout(self.params['propagation_delay_s'])
                    if self.ether.has_collision():
                        if self.viz:
                            self.viz.update_station_state(self.id, 'collision')
                        del self.ether.transmitting_stations[self.id]
                        yield self.env.process(self.handle_collision())
                        return False
                    yield self.env.timeout(tx_time - self.params['propagation_delay_s'])
                    del self.ether.transmitting_stations[self.id]
                    self.stats['total_tx_time'] += tx_time
                    self.ether.broadcast(self.id, pkt)
                    if self.viz:
                        self.viz.update_station_state(self.id, 'idle')
                    return True
                else:
                    if self.viz:
                        self.viz.update_station_state(self.id, 'deferring')
                    yield self.env.timeout(self.params['slot_time_s'])
        except simpy.Interrupt:
            if self.id in self.ether.transmitting_stations:
                del self.ether.transmitting_stations[self.id]

    def handle_collision(self):
        """Handles collision detection, jamming, and the backoff procedure."""
        self.stats['collisions'] += 1
        self.stats['total_busy_time'] += self.params['jam_tx_time_s']
        self.collisions += 1
        self.ether.is_jammed = True
        if self.viz:
            self.viz.trigger_jam()
        yield self.env.timeout(self.params['jam_tx_time_s'])
        self.ether.is_jammed = False
        max_slots = (2**min(self.collisions, 10))-1
        slots = random.randint(0, max_slots)
        backoff = slots*self.params['slot_time_s']
        if self.viz:
            self.viz.update_station_state(self.id, 'backing off')
        if backoff > 0:
            yield self.env.timeout(backoff)


class Visualization:
    """Pygame visualization + GIF capture."""

    def __init__(self, params):
        if not Config.VISUALIZATION:
            return
        pygame.init()
        self.params = params
        self.screen = pygame.display.set_mode(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(
            'Dædælus - Acknowledged Ethernet Simulation')
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.clock = pygame.time.Clock()
        self.station_positions = {}
        self.station_states = {}
        self.jam_animation = 0
        self.frames = []
        y = Config.SCREEN_HEIGHT//2
        for i in range(Config.NUM_STATIONS):
            x = int(Config.SCREEN_WIDTH*(i+1)/(Config.NUM_STATIONS+1))
            self.station_positions[i] = (x, y)
            self.station_states[i] = {'state': 'idle',
                                      'color': Config.IDLE_COLOR, 'queue_size': 0}

    def trigger_jam(self): self.jam_animation = 10

    def update_station_state(self, sid, state, qs=None):
        cmap = {'idle': Config.IDLE_COLOR, 'queued': (255, 255, 100), 'transmitting': (
            100, 255, 100), 'collision': (255, 100, 100), 'deferring': (100, 180, 255), 'backing off': (200, 0, 200)}
        st = self.station_states[sid]
        st['state'] = state
        st['color'] = cmap.get(state, (200, 0, 200))
        if qs is not None:
            st['queue_size'] = qs

    def draw(self, env, ether, stations):
        self.screen.fill((0, 0, 0))
        y = Config.SCREEN_HEIGHT//2
        # Ether line
        col = Config.IDLE_COLOR
        if ether.is_jammed or self.jam_animation > 0:
            col = Config.JAM_COLOR
            self.jam_animation -= 1
        elif ether.has_collision():
            col = Config.COLLISION_COLOR
        elif ether.is_busy():
            col = (100, 255, 100)
        pygame.draw.line(self.screen, col, (50, y),
                         (Config.SCREEN_WIDTH-50, y), 3)
        # Stations
        for i, stn in enumerate(stations):
            pos = self.station_positions[i]
            self.station_states[i]['queue_size'] = len(stn.packet_queue.items)
            s = self.station_states[i]
            pygame.draw.circle(self.screen, Config.STATION_COLOR, pos, 20)
            pygame.draw.circle(self.screen, s['color'], pos, 15)
            pygame.draw.line(self.screen, Config.STATION_COLOR,
                             pos, (pos[0], pos[1]-20), 2)
            idtxt = self.font.render(f"S{i}", True, (255, 255, 255))
            statetxt = self.font.render(s['state'], True, s['color'])
            qtxt = self.font.render(
                f"Q:{s['queue_size']}", True, (255, 255, 255))
            self.screen.blit(idtxt, (pos[0]-8, pos[1]+25))
            self.screen.blit(
                statetxt, (pos[0]-statetxt.get_width()//2, pos[1]+45))
            self.screen.blit(qtxt, (pos[0]-qtxt.get_width()//2, pos[1]+65))
        # Packets in flight
        for sid, (pkt, start) in ether.transmitting_stations.items():
            x0 = self.station_positions[sid][0]
            pd = (env.now-start)*Config.PROPAGATION_SPEED_M_S
            prog = min(pd/Config.ETHER_LENGTH_M, 1.0)
            w = prog*(Config.SCREEN_WIDTH-100)
            h = Config.PACKET_HEIGHT if pkt.packet_type == 'DATA' else Config.PACKET_HEIGHT-5
            left = pygame.Rect(x0-w/2, y-h/2, w/2, h)
            right = pygame.Rect(x0, y-h/2, w/2, h)
            pygame.draw.rect(self.screen, pkt.color, left, border_radius=3)
            pygame.draw.rect(self.screen, pkt.color, right, border_radius=3)
            info = pkt.packet_type + \
                (f" {pkt.seq_num}" if pkt.packet_type ==
                 'DATA' else f" {pkt.ack_num}")
            infs = self.small_font.render(info, True, (0, 0, 0))
            self.screen.blit(
                infs, (x0-infs.get_width()/2, y-infs.get_height()/2))

        # Info
        lines = [f"Time: {env.now:.4f}s", f"Mode: {Config.SIMULATION_MODE}",
                 f"Status: {'JAM' if ether.is_jammed else 'Collision' if ether.has_collision() else 'Busy' if ether.is_busy() else 'Idle'}"]

        for i, ln in enumerate(lines):
            self.screen.blit(self.font.render(
                ln, True, (255, 255, 255)), (10, 10+i*25))
        pygame.display.flip()
        self.clock.tick(60)
        # capture
        frame = pygame.surfarray.array3d(self.screen).transpose((1, 0, 2))
        self.frames.append(frame.copy())

    def save_gif(self, filename='comprehensive4.gif', fps=30):
        imageio.mimsave(filename, self.frames, fps=fps)


def run_simulation():
    print("--- Daedaelus Acknowledged Ethernet Simulation ---")
    print(f"Mode: {Config.SIMULATION_MODE}, Stations: {Config.NUM_STATIONS}, Transferring {Config.TOTAL_DATA_PACKETS} packets")
    print("-" * 50)
    random.seed(Config.RANDOM_SEED)
    params = Config.get_params()
    stats = collections.defaultdict(int)
    env = simpy.Environment()
    env.params = params
    ether = Ether(env)
    # create pipes
    for i in range(Config.NUM_STATIONS):
        ether.pipes[i] = simpy.Store(env)
    viz = Visualization(params) if Config.VISUALIZATION else None
    stations = [Station(env, i, ether, params, stats, viz)
                for i in range(Config.NUM_STATIONS)]
    running = True
    sim_end = Config.SIM_DURATION_S*Config.ANIMATION_SPEED_FACTOR
    while running and stats['acks_received'] < Config.TOTAL_DATA_PACKETS and env.now < sim_end:
        if Config.VISUALIZATION:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
            viz.draw(env, ether, stations)
        tstep = (1/60.0)/Config.ANIMATION_SPEED_FACTOR
        env.run(until=env.now+tstep)
    stats['total_sim_time'] = env.now
    return stats, params, viz, env, ether, stations, running


def print_results(stats, params):
    print("\n--- Simulation Results ---")
    t = stats['total_sim_time']
    print(f"Total time simulated: {t:.4f} s")
    print(f"Total DATA packets generated: {Config.TOTAL_DATA_PACKETS}")
    print(f"DATA received: {stats.get('app_packets_received', 0)}")
    print(f"ACKs received: {stats.get('acks_received', 0)}")
    print(f"Collisions: {stats.get('collisions', 0)}")
    print(f"Timeouts: {stats.get('timeouts', 0)}")
    if stats.get('app_packets_received', 0) > 0:
        bits = stats['app_packets_received']*Config.DATA_PACKET_BITS
        thr = bits/t
        print(f"Application Goodput: {thr/1e6:.4f} Mbps")
    eff = stats['total_tx_time']/t if t > 0 else 0
    print(f"Channel Efficiency: {eff:.4%}")
    print("-"*28)


if __name__ == '__main__':
    # pygame banner
    print(
        f"pygame {pygame.version.ver} (SDL {'.'.join(map(str, pygame.get_sdl_version()))}, Python {sys.version.split()[0]})\n")
    print("Hello from the pygame community. https://www.pygame.org/contribute.html\n")
    print("--- Daedaelus Acknowledged Ethernet Simulation ---")
    print(f"Mode: {Config.SIMULATION_MODE}, Stations: {Config.NUM_STATIONS}, Packets: {Config.TOTAL_DATA_PACKETS}")
    print("-"*50)
    print()
    stats, params, viz, env, ether, stations, run_flag = run_simulation()
    print_results(stats, params)
    if Config.VISUALIZATION and viz:
        viz.save_gif('comprehensive4.gif', fps=30)
        pygame.quit()
        sys.exit()
