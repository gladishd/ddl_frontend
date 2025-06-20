# python ethernet18.py 8080 2
# This script unifies the server and client simulations into a single executable.
# It models a complete, self-contained distributed system where multiple stations
# contend for a single, shared communication medium—the classic Ethernet.
#
# The server component simulates the "Ether," a passive broadcast medium that uses
# statistical arbitration to manage access. The client components simulate the
# individual stations, each employing the CSMA/CD protocol with binary exponential
# backoff to recover from the inevitable packet collisions.
#
# This entire model stands in contrast to the Daedaelus philosophy, which replaces
# such probabilistic contention with deterministic, time-reversible constructors,
# ensuring that the network does not create a mess the application must discover
# and then clean up.

import socket
import select
import threading
import sys
import time
import random

# -----------------------------------------------------------------------------
# Shared Constants and Configuration
# -----------------------------------------------------------------------------

# -- In classic Ethernet, the slot time is the critical parameter for collision detection.
#    It's the round-trip time of the Ether. For a software simulation using threads,
#    this value must be substantially larger than the physical value to overcome OS
#    scheduling latencies and allow the backoff algorithm to effectively de-synchronize stations. --
SLOT_TIME_SECONDS = 0.01  # Increased from 51.2us to 10ms to prevent livelock

# Log types as defined in the original C code
LOG_SEND = 2
LOG_COLLISION = 3
LOG_RECEIVE = 1
LOG_TRANSFER = 2

# Global lock for writing to log files to prevent interleaved lines from different threads
log_lock = threading.Lock()
# -- A threading event to synchronize the startup of all stations. This ensures
#    contention begins only after all participants have joined the Ether. --
server_ready = threading.Event()

# -----------------------------------------------------------------------------
# Unified Logging Function
# -----------------------------------------------------------------------------

def write_log(filename, log_type, frame_part=0, frame=0, src_id=0, dest_id=0, time_slot=0):
    """
    // This implements logging for the Ether simulation.
    // It records the fundamental events of a contended medium from the perspective
    // of either the Ether (server) or a Station (client).
    """
    with log_lock:
        with open(filename, "a") as fp:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if log_type == LOG_SEND:
                fp.write(f"{timestamp} - Send part {frame_part} of frame {frame} to Station {dest_id}\n")
            elif log_type == LOG_COLLISION and "client" in filename:
                fp.write(f"{timestamp} - A collision informed, wait for {time_slot} time slot(s)\n")
            elif log_type == LOG_RECEIVE:
                fp.write(f"{timestamp} - Receive part {frame_part} of frame {frame} from Station {src_id}, to Station {dest_id}\n")
            elif log_type == LOG_TRANSFER:
                fp.write(f"{timestamp} - Transfer part {frame_part} of frame {frame} from Station {src_id}, to Station {dest_id}\n")
            elif log_type == LOG_COLLISION and "server" in filename:
                fp.write(f"{timestamp} - Inform Station {src_id} a collision\n")


# -----------------------------------------------------------------------------
# Server (The "Ether") Logic
# -----------------------------------------------------------------------------
# Global lists to be managed by the server thread
server_clients = []
server_station_ids = {} # Maps conn -> station_id

def run_server(port, num_stations):
    """
    // This function contains the logic for the server, which simulates the shared Ether.
    // It accepts connections from stations and then enters the main arbitration loop.
    """
    global server_clients, server_station_ids, server_thread

    bus_lock = threading.Lock()
    bus_buffer = {}  # {'conn': client_socket, 'data': received_data}
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(num_stations)
    
    print("[Server] Server startup.")
    print(f"[Server] Waiting for {num_stations} station processes to connect...")

    def remove_client(conn):
        # Helper to safely remove a client
        print(f"[Server] Station {server_station_ids.get(conn, 'unknown')} disconnected.")
        if conn in server_clients:
            server_clients.remove(conn)
        if conn in server_station_ids:
            del server_station_ids[conn]
        conn.close()

    # Accept connections
    for i in range(num_stations):
        conn, addr = server_socket.accept()
        server_clients.append(conn)
        try:
            data = conn.recv(1024).decode().strip()
            if data:
                station_id = int(data)
                server_station_ids[conn] = station_id
                print(f"[Server] Connected with station process of ID: {station_id}")
        except (ConnectionResetError, BrokenPipeError, OSError):
            remove_client(conn)

    print("[Server] All station processes connected. Begin of data transmission...")
    server_ready.set() # Signal that clients can start their main logic

    # Main data processing loop
    while len(server_clients) > 0:
        try:
            readable, _, _ = select.select(server_clients, [], [], 0.1)
        except ValueError:
            continue

        with bus_lock:
            # COLLISION CASE
            if len(readable) > 1:
                print(f"[Server] Collision detected among {len(readable)} stations.")
                for conn in readable:
                    try:
                        conn.recv(1024, socket.MSG_DONTWAIT)
                        conn.sendall(b"COLL")
                        write_log("server_output.txt", LOG_COLLISION, src_id=server_station_ids.get(conn, -1))
                    except (ConnectionResetError, BrokenPipeError, BlockingIOError, OSError):
                        remove_client(conn)
                bus_buffer = {}
            
            # SINGLE SENDER CASE
            elif len(readable) == 1:
                conn = readable[0]
                try:
                    data = conn.recv(1024).decode()
                    if not data: # Client disconnected gracefully
                        remove_client(conn)
                        continue
                    
                    parts = data.strip().split()
                    frame_part, frame, src_id, dest_id = map(int, parts)
                    write_log("server_output.txt", LOG_RECEIVE, frame_part, frame, src_id, dest_id)
                    
                    if not bus_buffer:
                        bus_buffer = {'conn': conn, 'data': data}
                        conn.sendall(b"RECE")
                    else:
                        print(f"[Server] Latent Collision: Station {src_id} sent while bus held by {server_station_ids.get(bus_buffer.get('conn'), 'unknown')}")
                        conn.sendall(b"COLL")
                        if bus_buffer.get('conn') in server_clients:
                            bus_buffer['conn'].sendall(b"COLL")
                        bus_buffer = {}
                except (ConnectionResetError, BrokenPipeError, OSError):
                    remove_client(conn)

            # IDLE SLOT CASE
            elif len(readable) == 0:
                if bus_buffer:
                    sender_conn = bus_buffer.get('conn')
                    if sender_conn and sender_conn in server_clients:
                        parts = bus_buffer['data'].strip().split()
                        frame_part, frame, src_id, dest_id = map(int, parts)
                        print(f"[Server] Frame {frame} from station {src_id} successfully transferred.")
                        write_log("server_output.txt", LOG_TRANSFER, frame_part, frame, src_id, dest_id)
                        try:
                            sender_conn.sendall(b"SUCC")
                        except (ConnectionResetError, BrokenPipeError, OSError):
                            remove_client(sender_conn)
                    bus_buffer = {}
    
    server_socket.close()
    print("[Server] All clients disconnected. Server shutting down.")


# -----------------------------------------------------------------------------
# Client (Station) Logic
# -----------------------------------------------------------------------------

def run_client(station_id, server_ip, port):
    client_log_file = f"client_{station_id}_output.txt"
    with open(client_log_file, "w") as f:
        f.write(f"Client {station_id} Log Initialized\n")
    
    frames_to_send = [
        "Frame 1, To Station 2",
        "Frame 2, To Station 2",
        "Frame 3, To Station 1"
    ]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, port))
        sock.sendall(str(station_id).encode())
        
        server_ready.wait()

        for line in frames_to_send:
            line = line.strip()
            if not line: continue

            parts = line.split()
            frame_num = int(parts[1].replace(',', ''))
            dest_id = int(parts[4])

            collision_count = 0
            frame_sent = False

            while not frame_sent:
                if collision_count >= 16:
                    print(f"[Client {station_id}] Frame {frame_num} dropped after 16 collisions.")
                    break
                
                message = f"1 {frame_num} {station_id} {dest_id}"
                
                sock.sendall(message.encode())
                write_log(client_log_file, LOG_SEND, 1, frame_num, dest_id)

                response = sock.recv(1024).decode()
                
                if "SUCC" in response:
                    print(f"[Client {station_id}] Frame {frame_num} successfully sent.")
                    frame_sent = True
                elif "COLL" in response:
                    collision_count += 1
                    print(f"[Client {station_id}] Collision for frame {frame_num}. Attempt #{collision_count}")
                    k = min(collision_count, 10)
                    max_slots = (2**k) - 1
                    backoff_slots = random.randint(0, max_slots if max_slots > 0 else 0)
                    write_log(client_log_file, LOG_COLLISION, time_slot=backoff_slots)
                    time.sleep(backoff_slots * SLOT_TIME_SECONDS)
                elif "RECE" in response:
                    response = sock.recv(1024).decode()
                    if "SUCC" in response:
                        print(f"[Client {station_id}] Frame {frame_num} successfully sent.")
                        frame_sent = True
                    elif "COLL" in response:
                       collision_count += 1
                       print(f"[Client {station_id}] Latent collision for frame {frame_num}. Attempt #{collision_count}")
                       k = min(collision_count, 10)
                       max_slots = (2**k) - 1
                       backoff_slots = random.randint(0, max_slots if max_slots > 0 else 0)
                       write_log(client_log_file, LOG_COLLISION, time_slot=backoff_slots)
                       time.sleep(backoff_slots * SLOT_TIME_SECONDS)
    
    except ConnectionRefusedError:
        print(f"[Client {station_id}] Connection refused. Is the server running?")
    except Exception as e:
        print(f"[Client {station_id}] An error occurred: {e}")
    finally:
        print(f"[Client {station_id}] Shutting down.")
        sock.close()

# -----------------------------------------------------------------------------
# Main Orchestration
# -----------------------------------------------------------------------------
server_thread = None

def main():
    global server_thread
    if len(sys.argv) != 3:
        print("Usage: python ethernet18.py <port_number> <num_stations>")
        sys.exit(1)

    port = int(sys.argv[1])
    num_stations = int(sys.argv[2])
    server_ip = '127.0.0.1'

    with open("server_output.txt", "w") as f: f.write("Server Log Initialized\n")

    server_thread = threading.Thread(target=run_server, args=(port, num_stations))
    server_thread.start()

    client_threads = []
    for i in range(num_stations):
        station_id = i + 1
        client = threading.Thread(target=run_client, args=(station_id, server_ip, port))
        client_threads.append(client)
        client.start()

    for client in client_threads:
        client.join()

    print("\nAll client simulations have finished.")
    server_thread.join()
    print("Simulation complete.")

if __name__ == "__main__":
    main()