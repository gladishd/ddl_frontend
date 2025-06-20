import socket
import threading
import time
import random
import sys
import os
from socketserver import ThreadingTCPServer, BaseRequestHandler

# ==============================================================================
# Dædælus Philosophy Integration
#
# This script emulates the foundational principles of a shared broadcast medium,
# drawing inspiration from the original 1976 Metcalfe & Boggs paper on Ethernet.
# We computationally model the core mechanisms of contention, collision, and
# recovery to understand their impact on network behavior.
#
# Our object is to design a communication system which can grow smoothly...
# We choose to distribute control of the communications facility among the
# communicating computers to eliminate the reliability problems of an active
# central controller, to avoid creating a bottleneck in a system rich in
# parallelism, and to reduce the fixed costs which make small systems
# uneconomical.
#
# This simulation serves as a "code as proof" artifact, demonstrating how
# coordinating access to a shared Ether via distributed, statistical
# arbitration leads to predictable performance characteristics.
# ==============================================================================

# --- Configuration ---
HOST, PORT = "localhost", 9999
NUM_STATIONS = 10
TIME_SLOT_MICROSECONDS = 100000  # 100ms per slot, as per simulation docs

# --- Embedded Station Input Data ---
# This data simulates the individual station_processX.txt files,
# defining the transmission tasks for each station controller.
STATION_INPUT_DATA = {
    1: [
        "Frame 1, To Station 3", "Frame 2, To Station 3", "Frame 3, To Station 3",
        "Frame 4, To Station 3", "Frame 5, To Station 3", "Frame 6, To Station 3",
        "Frame 7, To Station 3", "Frame 8, To Station 3", "Frame 9, To Station 3",
        "Frame 10, To Station 3"
    ],
    2: [
        "Frame 1, To Station 3", "Frame 2, To Station 4", "Frame 3, To Station 3",
        "Frame 4, To Station 2", "Frame 1, To Station 3", "Frame 2, To Station 4",
        "Frame 3, To Station 3", "Frame 4, To Station 2", "Frame 1, To Station 3",
        "Frame 2, To Station 4"
    ],
    3: [
        "Frame 1, To Station 3", "Frame 2, To Station 2", "Frame 3, To Station 3",
        "Frame 4, To Station 6", "Frame 1, To Station 7", "Frame 2, To Station 5",
        "Frame 3, To Station 3", "Frame 2, To Station 9", "Frame 3, To Station 10",
        "Frame 4, To Station 1"
    ],
    4: [
        "Frame 1, To Station 3", "Frame 2, To Station 4", "Frame 3, To Station 3",
        "Frame 4, To Station 2", "Frame 1, To Station 3", "Frame 2, To Station 4",
        "Frame 3, To Station 3", "Frame 4, To Station 2", "Frame 1, To Station 3",
        "Frame 2, To Station 4"
    ],
    5: [
        "Frame 1, To Station 3", "Frame 2, To Station 2", "Frame 3, To Station 3",
        "Frame 4, To Station 4", "Frame 5, To Station 7", "Frame 6, To Station 8",
        "Frame 7, To Station 3", "Frame 8, To Station 9", "Frame 9, To Station 10",
        "Frame 10, To Station 1"
    ],
    6: [
        "Frame 1, To Station 3", "Frame 2, To Station 4", "Frame 3, To Station 3",
        "Frame 4, To Station 2", "Frame 1, To Station 3", "Frame 2, To Station 4",
        "Frame 3, To Station 3", "Frame 4, To Station 2", "Frame 1, To Station 3",
        "Frame 2, To Station 4"
    ],
    7: [
        "Frame 3, To Station 3", "Frame 4, To Station 6", "Frame 1, To Station 2",
        "Frame 2, To Station 4", "Frame 3, To Station 3", "Frame 6, To Station 8",
        "Frame 7, To Station 3", "Frame 8, To Station 9", "Frame 9, To Station 10",
        "Frame 10, To Station 1"
    ],
    8: [
        "Frame 1, To Station 3", "Frame 2, To Station 2", "Frame 3, To Station 3",
        "Frame 4, To Station 6", "Frame 5, To Station 7", "Frame 6, To Station 8",
        "Frame 7, To Station 3", "Frame 8, To Station 9", "Frame 7, To Station 10",
        "Frame 9, To Station 1"
    ],
    9: [
        "Frame 1, To Station 3", "Frame 2, To Station 4", "Frame 1, To Station 7",
        "Frame 2, To Station 4", "Frame 3, To Station 3", "Frame 4, To Station 8",
        "Frame 1, To Station 3", "Frame 2, To Station 2", "Frame 3, To Station 10",
        "Frame 4, To Station 1"
    ],
    10: [
        "Frame 1, To Station 3", "Frame 4, To Station 6", "Frame 1, To Station 7",
        "Frame 2, To Station 4", "Frame 3, To Station 3", "Frame 4, To Station 8",
        "Frame 5, To Station 3", "Frame 6, To Station 9", "Frame 7, To Station 10",
        "Frame 8, To Station 1"
    ]
}

class Ether(ThreadingTCPServer):
    """
    Represents the shared communication facility, a passive broadcast medium.
    The Ether has no central control. Instead, it listens for transmission
    attempts from all stations and reports back whether a collision was detected,
    enabling the distributed statistical arbitration mechanism.
    """
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, num_stations):
        super().__init__(server_address, RequestHandlerClass)
        # The state of the Ether is shared across all connections. A lock is
        # required to prevent race conditions when multiple stations attempt
        # to acquire the Ether simultaneously.
        self.lock = threading.Lock()
        # This map tracks the state of each station's attempt to acquire the Ether.
        # True means a station is in the middle of a transmission (part 1 sent).
        self.transmitting_stations = [False] * num_stations
        # This map tracks which stations were involved in a collision.
        self.collided_stations = [False] * num_stations
        self.log_file = open("Communication_Bus_Output.txt", "w")
        self.log_lock = threading.Lock()

    def log(self, message):
        with self.log_lock:
            self.log_file.write(message + '\n')
            self.log_file.flush()

    def server_close(self):
        super().server_close()
        self.log_file.close()

class EtherRequestHandler(BaseRequestHandler):
    """
    Handles a single transmission attempt from a StationController.
    This is analogous to a transceiver tapping into the Ether.
    """
    def handle(self):
        data = self.request.recv(1024).strip().decode('utf-8')
        try:
            frame_id, part_no, from_station, to_station = map(int, data.split())
        except ValueError:
            print(f"Ether: Received malformed data: {data}")
            return

        server = self.server
        
        # Log the reception of the packet part on the bus.
        server.log(f"Receive part {part_no} of frame {frame_id} from Station {from_station}, to Station {to_station}")

        collision_detected = False
        with server.lock:
            # --- Carrier Sense and Interference Detection Logic ---
            # When a station attempts to send the first part of its frame,
            # it tries to acquire the Ether.
            if part_no == 1:
                server.transmitting_stations[from_station - 1] = True

            # Check for interference. A collision occurs if more than one station
            # is marked as transmitting.
            active_transmitters = [i + 1 for i, status in enumerate(server.transmitting_stations) if status]
            
            if len(active_transmitters) > 1:
                collision_detected = True
                # Collision Consensus Enforcement: Ensure all participants in the
                # collision know that it occurred.
                for station_idx in active_transmitters:
                    server.collided_stations[station_idx - 1] = True

            # Check if this station was part of a previously detected collision.
            if server.collided_stations[from_station - 1]:
                collision_detected = True

        # --- Respond to the Station ---
        if collision_detected:
            reply = b"collision"
            server.log(f"Inform Station {from_station} a collision")
        else:
            reply = b"success"
            # A successful transmission of part 2 implies the full frame has been
            # notionally transferred across the Ether.
            if part_no == 2:
                server.log(f"Transfer part 1 of frame {frame_id} from Station {from_station}, to Station {to_station}")
                server.log(f"Transfer part 2 of frame {frame_id} from Station {from_station}, to Station {to_station}")

        self.request.sendall(reply)

        # The Ether is now free. Reset the state for the station that just finished.
        # This must be done after the reply is sent.
        with server.lock:
            server.transmitting_stations[from_station - 1] = False
            server.collided_stations[from_station - 1] = False


class StationController(threading.Thread):
    """
    An Ethernet controller is the station-specific low-level logic for
    getting packets onto and out of the Ether. When a source-detected collision
    occurs, it is the source controller's responsibility to generate a new random
    retransmission interval based on the updated collision history.
    """
    def __init__(self, station_id, host, port, frames_to_send, log_lock, log_file):
        super().__init__()
        self.station_id = station_id
        self.host = host
        self.port = port
        self.frames_to_send = frames_to_send
        self.log_lock = log_lock
        self.log_file = log_file

    def log(self, message):
        with self.log_lock:
            self.log_file.write(f"Station {self.station_id}: {message}\n")
            self.log_file.flush()

    def run(self):
        self.log(f"Process started. Ready to transmit {len(self.frames_to_send)} frames.")
        for frame_data_line in self.frames_to_send:
            self.transmit_frame(frame_data_line)
        self.log("All frames sent. Process finished.")

    def _send_frame_part(self, frame_id, part_no, to_station):
        """
        Emulates the physical act of transmitting a single frame part.
        Critically, it establishes a new connection for each attempt, mirroring
        the stateless nature of the original C simulation's sendFrame function.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                message = f"{frame_id} {part_no} {self.station_id} {to_station}"
                sock.sendall(message.encode('utf-8'))
                reply = sock.recv(1024).decode('utf-8')
                return reply == "success"
        except ConnectionRefusedError:
            print(f"Station {self.station_id}: Connection refused. Is the Ether running?")
            return False
        except Exception as e:
            print(f"Station {self.station_id}: Error in _send_frame_part: {e}")
            return False

    def transmit_frame(self, frame_data_line):
        """
        Manages the transmission of a single, complete frame, including retries
        and the Binary Exponential Backoff algorithm for collision recovery.
        """
        parts = frame_data_line.split(',')
        frame_id_str = parts[0].split(' ')[1]
        to_station_str = parts[1].split(' ')[-1]
        frame_id = int(frame_id_str)
        to_station = int(to_station_str)
        
        attempts = 0
        while True:
            attempts += 1
            if attempts > 16:
                self.log(f"Transmission failure for frame {frame_id} after 16 attempts. Aborting.")
                return

            # Attempt to send the first part of the frame to acquire the Ether.
            self.log(f"Send part 1 of Frame {frame_id}, To Station {to_station} (Attempt {attempts})")
            if not self._send_frame_part(frame_id, 1, to_station):
                # --- Binary Exponential Backoff (BEBO) ---
                # This heuristic approximates an algorithm for adjusting retransmission
                # rates to maintain Ether efficiency under load.
                max_backoff_power = min(attempts, 10)
                k = random.randint(0, 2**max_backoff_power - 1)
                wait_time_us = k * TIME_SLOT_MICROSECONDS
                self.log(f"A collision was detected, waiting for {k} time slots.")
                time.sleep(wait_time_us / 1_000_000.0)
                continue  # Retry sending part 1

            # Part 1 was successful, now send part 2 immediately.
            self.log(f"Send part 2 of Frame {frame_id}, To Station {to_station}")
            if self._send_frame_part(frame_id, 2, to_station):
                # Both parts sent successfully, transmission is complete.
                self.log(f"Successfully transmitted Frame {frame_id}")
                break  # Exit the while loop and move to the next frame
            else:
                # This case (part 1 success, part 2 collision) is rare but possible in a
                # race condition. We'll simply retry the whole frame.
                self.log(f"Collision on part 2 of Frame {frame_id}. Retrying entire frame.")


if __name__ == "__main__":
    # Clean up old log files
    if os.path.exists("Communication_Bus_Output.txt"):
        os.remove("Communication_Bus_Output.txt")
    if os.path.exists("Station_Process_Output.txt"):
        os.remove("Station_Process_Output.txt")

    print(f"Starting the Ether on {HOST}:{PORT}...")
    ether_server = Ether((HOST, PORT), EtherRequestHandler, NUM_STATIONS)
    server_thread = threading.Thread(target=ether_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Ether is now active, listening for transmissions.")

    # A shared lock and file handle for station logging to prevent garbled output.
    station_log_lock = threading.Lock()
    station_log_file = open("Station_Process_Output.txt", "w")

    stations = []
    print(f"Initializing {NUM_STATIONS} station controllers...")
    for i in range(1, NUM_STATIONS + 1):
        station_data = STATION_INPUT_DATA.get(i, [])
        station = StationController(i, HOST, PORT, station_data, station_log_lock, station_log_file)
        stations.append(station)
        station.start()

    print("All stations are now active and contending for the Ether.")

    # Wait for all station threads to complete their work
    for station in stations:
        station.join()

    print("All stations have completed their transmissions.")
    
    # Clean shutdown
    station_log_file.close()
    ether_server.shutdown()
    ether_server.server_close()
    print("Ether has been shut down. Simulation complete.")
    print("\nLog files 'Communication_Bus_Output.txt' and 'Station_Process_Output.txt' have been generated.")