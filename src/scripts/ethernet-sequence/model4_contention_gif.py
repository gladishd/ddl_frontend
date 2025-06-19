#
# DDL_Emulator: Ethernet Contention Simulation (with GIF export)
#
# This script provides an agent-based simulation of the Ethernet contention mechanism,
# embodying the principles of distributed packet switching as originally described
# by Metcalfe and Boggs. It is designed to serve as a 'computational model' to
# explore the dynamics of a shared communication medium, the Ether.
#
# Inspired by the Daedaelus philosophy, this simulation aims to provide a deeper
# understanding of why classical approaches to network contention, which treat
# bandwidth as a resource to be divided, lead to inherent inefficiencies.
#
# GIF export powered by imageio.
#

import simpy
import random
import math
import pygame
import sys
import imageio

# --- Simulation Configuration ---


class Config:
    """
    Configuration parameters for the Ethernet simulation.
    Adjust these values to explore different network scenarios.
    """
    # General Simulation Settings
    SIMULATION_MODE = 'CSMA_CD'   # Options: 'PURE_ALOHA', 'SLOTTED_ALOHA', 'CSMA_CD'
    SIM_DURATION_S = 0.5        # Total simulation time in seconds
    RANDOM_SEED = 42

    # Physical Layer Parameters
    NUM_STATIONS = 10            # Number of stations on the Ether
    ETHER_LENGTH_M = 500           # Cable length in meters
    PROPAGATION_SPEED_M_S = 2e8        # Propagation speed (≈2/3 c)
    ETHER_SPEED_BPS = 3e6          # Link bit rate in bps

    # Packet Parameters
    PACKET_BITS = 4096        # Packet size in bits
    JAM_SIGNAL_BITS = 32          # Jam signal size in bits
    MEAN_PACKET_ARRIVAL_S = 0.01      # Mean inter-arrival time per station

    # Visualization Settings
    VISUALIZATION = True
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    STATION_COLOR = (200, 200, 200)
    IDLE_COLOR = (100, 100, 255)
    TRANSMIT_COLOR = (100, 255, 100)
    COLLISION_COLOR = (255, 100, 100)
    JAM_COLOR = (255, 150, 50)
    PACKET_HEIGHT = 20

    @staticmethod
    def get_params():
        p = {}
        p['propagation_delay_s'] = Config.ETHER_LENGTH_M / \
            Config.PROPAGATION_SPEED_M_S
        p['slot_time_s'] = 2 * p['propagation_delay_s']
        p['packet_tx_time_s'] = Config.PACKET_BITS / Config.ETHER_SPEED_BPS
        p['jam_tx_time_s'] = Config.JAM_SIGNAL_BITS / Config.ETHER_SPEED_BPS
        return p


class Packet:
    """Represents a single data packet to be transmitted."""

    def __init__(self, source_id, destination_id, creation_time):
        self.source_id = source_id
        self.destination_id = destination_id
        self.creation_time = creation_time


class Ether:
    """Shared communication medium allowing detection of collisions."""

    def __init__(self, env):
        self.env = env
        self.transmitting_stations = {}
        self.is_jammed = False

    def is_busy(self):
        return bool(self.transmitting_stations)

    def has_collision(self):
        return len(self.transmitting_stations) > 1


class Station:
    """Agent implementing packet generation, transmission, and contention resolution."""

    def __init__(self, env, station_id, ether, params, stats, viz):
        self.env = env
        self.id = station_id
        self.ether = ether
        self.params = params
        self.stats = stats
        self.viz = viz
        self.packet_queue = simpy.Store(env)
        self.collisions = 0
        env.process(self.packet_generator())
        env.process(self.run())

    def packet_generator(self):
        while True:
            yield self.env.timeout(random.expovariate(1.0 / Config.MEAN_PACKET_ARRIVAL_S))
            dest = random.choice(
                [i for i in range(Config.NUM_STATIONS) if i != self.id])
            pkt = Packet(self.id, dest, self.env.now)
            self.stats['packets_generated'] += 1
            yield self.packet_queue.put(pkt)
            if self.viz:
                self.viz.update_station_state(
                    self.id, 'queued', len(self.packet_queue.items))

    def run(self):
        while True:
            pkt = yield self.packet_queue.get()
            if self.viz:
                self.viz.update_station_state(
                    self.id, 'queued', len(self.packet_queue.items))
            yield self.env.process(self.transmit(pkt))

    def transmit(self, pkt):
        if Config.SIMULATION_MODE == 'PURE_ALOHA':
            yield from self.send_packet(pkt)

        elif Config.SIMULATION_MODE == 'SLOTTED_ALOHA':
            wait = (math.ceil(self.env.now / self.params['slot_time_s'])
                    * self.params['slot_time_s'] - self.env.now)
            if wait > 0:
                yield self.env.timeout(wait)
            yield from self.send_packet(pkt)

        else:  # CSMA_CD
            while True:
                if not self.ether.is_busy():
                    if self.viz:
                        self.viz.update_station_state(
                            self.id, 'transmitting', len(self.packet_queue.items))
                    self.ether.transmitting_stations[self.id] = self.env.now
                    yield self.env.timeout(self.params['propagation_delay_s'])

                    if self.ether.has_collision():
                        if self.viz:
                            self.viz.update_station_state(
                                self.id, 'collision', len(self.packet_queue.items))
                        del self.ether.transmitting_stations[self.id]
                        yield self.handle_collision(pkt)
                        return

                    yield self.env.timeout(self.params['packet_tx_time_s']
                                           - self.params['propagation_delay_s'])
                    del self.ether.transmitting_stations[self.id]
                    self.stats['packets_sent'] += 1
                    self.stats['total_delay'] += (self.env.now -
                                                  pkt.creation_time)
                    self.collisions = 0
                    if self.viz:
                        self.viz.update_station_state(
                            self.id, 'idle', len(self.packet_queue.items))
                    return

                else:
                    if self.viz:
                        self.viz.update_station_state(
                            self.id, 'deferring', len(self.packet_queue.items))
                    yield self.env.timeout(self.params['slot_time_s'])

    def send_packet(self, pkt):
        if self.viz:
            self.viz.update_station_state(
                self.id, 'transmitting', len(self.packet_queue.items))
        self.ether.transmitting_stations[self.id] = self.env.now
        yield self.env.timeout(self.params['packet_tx_time_s'])
        del self.ether.transmitting_stations[self.id]

        if self.ether.has_collision():
            if self.viz:
                self.viz.update_station_state(
                    self.id, 'collision', len(self.packet_queue.items))
            yield self.handle_collision(pkt)
        else:
            self.stats['packets_sent'] += 1
            self.stats['total_delay'] += (self.env.now - pkt.creation_time)
            self.collisions = 0
            if self.viz:
                self.viz.update_station_state(
                    self.id, 'idle', len(self.packet_queue.items))

    def handle_collision(self, pkt):
        self.stats['collisions'] += 1
        self.collisions += 1

        if Config.SIMULATION_MODE == 'CSMA_CD':
            self.ether.is_jammed = True
            if self.viz:
                self.viz.trigger_jam()
            yield self.env.timeout(self.params['jam_tx_time_s'])
            self.ether.is_jammed = False

        slots = random.randint(0, (2 ** min(self.collisions, 10)) - 1)
        backoff = slots * self.params['slot_time_s']
        if self.viz:
            self.viz.update_station_state(
                self.id, f'backing off for {slots} slots', len(self.packet_queue.items))
        if backoff > 0:
            yield self.env.timeout(backoff)

        new_q = simpy.Store(self.env)
        yield new_q.put(pkt)
        while self.packet_queue.items:
            p = yield self.packet_queue.get()
            yield new_q.put(p)
        self.packet_queue = new_q


class Visualization:
    """Handles Pygame visualization and GIF capture."""

    def __init__(self, params):
        if not Config.VISUALIZATION:
            return
        pygame.init()
        self.params = params
        self.screen = pygame.display.set_mode(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption('Dædælus - Ethernet Contention Simulation')
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.station_positions = {}
        self.station_states = {}
        self.jam_animation = 0
        self.frames = []

        y = Config.SCREEN_HEIGHT // 2
        for i in range(Config.NUM_STATIONS):
            x = int(Config.SCREEN_WIDTH * (i + 1) / (Config.NUM_STATIONS + 1))
            self.station_positions[i] = (x, y)
            self.station_states[i] = {'state': 'idle',
                                      'color': Config.IDLE_COLOR, 'queue_size': 0}

    def trigger_jam(self):
        if Config.VISUALIZATION:
            self.jam_animation = 10

    def update_station_state(self, sid, state, qsize=None):
        if not Config.VISUALIZATION:
            return
        cmap = {
            'idle':       Config.IDLE_COLOR,
            'queued':     (255, 255, 100),
            'transmitting': Config.TRANSMIT_COLOR,
            'collision':  Config.COLLISION_COLOR,
            'deferring':  (100, 180, 255)
        }
        self.station_states[sid]['state'] = state
        self.station_states[sid]['color'] = cmap.get(state, (200, 0, 200))
        if qsize is not None:
            self.station_states[sid]['queue_size'] = qsize

    def draw(self, env, ether, stations):
        if not Config.VISUALIZATION:
            return
        self.screen.fill((0, 0, 0))
        y = Config.SCREEN_HEIGHT // 2

        # Ether line
        col = Config.IDLE_COLOR
        if ether.is_jammed or self.jam_animation > 0:
            col = Config.JAM_COLOR
            self.jam_animation -= 1
        elif ether.has_collision():
            col = Config.COLLISION_COLOR
        elif ether.is_busy():
            col = Config.TRANSMIT_COLOR
        pygame.draw.line(self.screen, col, (50, y),
                         (Config.SCREEN_WIDTH-50, y), 3)

        # Stations
        for i, st in enumerate(stations):
            pos = self.station_positions[i]
            self.station_states[i]['queue_size'] = len(st.packet_queue.items)
            s = self.station_states[i]
            pygame.draw.circle(self.screen, Config.STATION_COLOR, pos, 20)
            pygame.draw.circle(self.screen, s['color'], pos, 15)
            pygame.draw.line(self.screen, Config.STATION_COLOR,
                             pos, (pos[0], pos[1]-20), 2)
            idtxt = self.font.render(f"S{i}",        True, (255, 255, 255))
            statetxt = self.font.render(
                s['state'].split()[0], True, s['color'])
            qtxt = self.font.render(
                f"Q:{s['queue_size']}", True, (255, 255, 255))
            self.screen.blit(idtxt,    (pos[0]-8, pos[1]+25))
            self.screen.blit(
                statetxt, (pos[0]-statetxt.get_width()//2, pos[1]+45))
            self.screen.blit(
                qtxt,     (pos[0]-qtxt.get_width()//2,     pos[1]+65))

        # Packets in flight
        for sid, start in ether.transmitting_stations.items():
            x0 = self.station_positions[sid][0]
            dist = (env.now - start)*Config.PROPAGATION_SPEED_M_S
            prog = min(dist/Config.ETHER_LENGTH_M, 1.0)
            w = prog*(Config.SCREEN_WIDTH-100)/2
            left = pygame.Rect(x0-w, y-Config.PACKET_HEIGHT /
                               2, w, Config.PACKET_HEIGHT)
            right = pygame.Rect(
                x0,   y-Config.PACKET_HEIGHT/2, w, Config.PACKET_HEIGHT)
            pygame.draw.rect(self.screen, col, left,  border_radius=3)
            pygame.draw.rect(self.screen, col, right, border_radius=3)

        # Info text
        lines = [
            f"Time: {env.now:.6f} s / {Config.SIM_DURATION_S} s",
            f"Mode: {Config.SIMULATION_MODE}",
            f"Ether Status: {'JAMMED' if ether.is_jammed else 'Collision' if ether.has_collision() else 'Busy' if ether.is_busy() else 'Idle'}"
        ]
        for i, ln in enumerate(lines):
            surf = self.font.render(ln, True, (255, 255, 255))
            self.screen.blit(surf, (10, 10 + i*25))

        pygame.display.flip()
        self.clock.tick(60)

        # Capture frame for GIF
        frame = pygame.surfarray.array3d(self.screen).transpose((1, 0, 2))
        self.frames.append(frame.copy())

    def save_gif(self, filename='comprehensive3.py_ethernet_contention.gif', fps=30):
        """Write captured frames out as a looping GIF."""
        imageio.mimsave(filename, self.frames, fps=fps)


def run_simulation():
    """Sets up and runs the SimPy environment."""
    random.seed(Config.RANDOM_SEED)
    params = Config.get_params()
    stats = {'packets_generated': 0, 'packets_sent': 0,
             'collisions': 0, 'total_delay': 0.0}
    env = simpy.Environment()
    ether = Ether(env)
    viz = Visualization(params) if Config.VISUALIZATION else None
    stations = [Station(env, i, ether, params, stats, viz)
                for i in range(Config.NUM_STATIONS)]
    running = True

    while running and env.now < Config.SIM_DURATION_S:
        if Config.VISUALIZATION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            viz.draw(env, ether, stations)
        env.run(until=env.now + 1/120.0)

    return stats, params, viz, env, ether, stations, running


def print_results(stats, params):
    print("\n--- Simulation Results ---\n")
    print(f"Total time simulated: {Config.SIM_DURATION_S:.4f} s\n")
    print(f"Packets generated: {stats['packets_generated']}\n")
    print(f"Packets successfully sent: {stats['packets_sent']}\n")
    print(f"Total collisions detected: {stats['collisions']}\n")
    if stats['packets_sent'] > 0:
        avg_delay = stats['total_delay'] / stats['packets_sent']
        print(f"Average packet delay: {avg_delay:.6f} s\n")
    throughput_bps = (stats['packets_sent'] *
                      Config.PACKET_BITS) / Config.SIM_DURATION_S
    efficiency = (stats['packets_sent'] *
                  params['packet_tx_time_s']) / Config.SIM_DURATION_S
    print(f"Throughput: {throughput_bps/1e6:.4f} Mbps\n")
    print(f"Channel Efficiency: {efficiency*100:.4f}%\n")
    print("-"*26)


if __name__ == '__main__':
    # pygame banner
    print(f"pygame {pygame.version.ver} (SDL " +
          f"{'.'.join(map(str, pygame.get_sdl_version()))}, " +
          f"Python {sys.version.split()[0]})\n")
    print("Hello from the pygame community. https://www.pygame.org/contribute.html\n")

    # simulation header
    print("--- Daedaelus Ethernet Contention Simulation ---\n")
    print(f"Mode: {Config.SIMULATION_MODE}, Stations: {Config.NUM_STATIONS}, " +
          f"Link Speed: {Config.ETHER_SPEED_BPS/1e6:.1f} Mbps\n")
    print(
        f"Packet Size: {Config.PACKET_BITS} bits, Sim Duration: {Config.SIM_DURATION_S}s\n")
    print("-"*50 + "\n\n")

    stats, params, viz, env, ether, stations, sim_run = run_simulation()
    print_results(stats, params)

    # Save GIF before quitting
    if Config.VISUALIZATION and viz:
        viz.save_gif('comprehensive3.py_ethernet_contention.gif', fps=30)
        pygame.quit()
        sys.exit()
