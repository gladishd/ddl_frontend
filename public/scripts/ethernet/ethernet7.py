import socket
import threading
import time
import logging
import sys

# Configure logging to provide a clear, step-by-step view of the transaction,
# similar to the output one would expect from the VProc simulation environment.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(message)s',
                    stream=sys.stdout)

# -- Begin Daedaelus Configuration --
# These parameters are inspired by the constants defined in the test environment,
# particularly in 'src/tcpCommon.h'. They establish the context for our
# Neighbor-to-Neighbor (N2N) interaction.
SERVER_IPV4_ADDR = '127.0.0.1'  # Using localhost for this self-contained simulation
TCP_PORT_NUM = 16384             # An ephemeral port, akin to the 0x0400 in the test
CLIENT_DATA = b"*** Data Packet from node 0 ***\n\n"

# The sequence numbers are managed by the OS kernel's TCP stack, but we acknowledge
# their conceptual importance. The protocol uses these 'conserved quantities'
# to ensure ordered, exactly-once delivery of the data stream.
CLIENT_TCP_INIT_SEQ = 0x0c3
SERVER_TCP_INIT_SEQ = 0x2ff
# -- End Daedaelus Configuration --


class TCPServer(threading.Thread):
    """
    This TCPServer class emulates Node 1 from the test environment.
    It acts as a listener, establishing a connection and reliably receiving a file.
    Its behavior is governed by the principles of a deterministic, stateful protocol,
    ensuring the transaction completes with full end-to-end knowledge.
    """

    def __init__(self, host, port):
        super().__init__(name="TCPServer-Node1")
        self.host = host
        self.port = port
        self.daemon = True # Allows main thread to exit even if this thread is blocked

    def run(self):
        """
        The server process begins. It will listen, accept a single connection,
        and participate in a full, reliable transaction before shutting down.
        """
        # The server socket is bound to a specific address, becoming a 'listener'.
        # This is the first step in establishing a service that can form reliable
        # connections.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            logging.info(f"Listening on {self.host}:{self.port}, awaiting connection...")

            try:
                # The accept call blocks until an initiator requests a connection.
                # This is the server's side of the rendezvous.
                conn, addr = server_socket.accept()
            except OSError:
                logging.warning("Server socket closed before connection.")
                return

            with conn:
                logging.info(f"Connection established with client {addr}.")

                # -- Begin Data Transfer --
                # The protocol now transitions from connection management to data transfer.
                # The server is now responsible for reliably receiving data.
                data = conn.recv(1024)
                if data:
                    # An acknowledgment is implicitly sent by the TCP stack upon successful receipt.
                    # This completes the two-way exchange, confirming to the sender that the
                    # information was successfully transferred. This mechanism is fundamental to
                    # avoiding the "irreversible smash and restart of Shannon information" that
                    # plagues unreliable protocols.
                    logging.info(f"Received data: {data.decode().strip()}")
                    logging.info("Data received and acknowledged. Awaiting connection termination.")

                    # -- Begin Connection Termination --
                    # A robust server waits for the client to signal the end of the connection.
                    # A recv() call returning an empty byte string (b'') is the definitive signal
                    # that the client has performed a graceful shutdown.
                    final_chunk = conn.recv(1024)
                    if not final_chunk:
                         logging.info("Client has closed its end. Connection gracefully terminated.")

                else:
                    # This case handles if the client connects and disconnects without sending data.
                    logging.warning("Connection closed by client before data was sent.")

        logging.info("Server thread finished.")


class TCPClient(threading.Thread):
    """
    This TCPClient class emulates Node 0 from the test environment.
    It initiates a connection, sends a single data packet, and then cleanly
    terminates the transaction, demonstrating a full, reliable communication cycle.
    """
    def __init__(self, host, port):
        super().__init__(name="TCPClient-Node0")
        self.host = host
        self.port = port

    def run(self):
        """
        The client process begins. It will initiate the three-way handshake,
        send its data, and then initiate the four-way teardown.
        """
        # A brief pause allows the server thread to start and begin listening.
        time.sleep(1)

        try:
            # Here, we model a point-to-point link in the N2N Lattice.
            # The client initiates the transaction. The 'with' statement ensures
            # that the socket is properly closed, which handles the TCP
            # termination sequence (FIN/ACK exchange).
            with socket.create_connection((self.host, self.port)) as client_socket:
                logging.info(f"Connection initiated. SYN sent to {self.host}:{self.port}.")

                # The `create_connection` call handles the three-way handshake (SYN, SYN-ACK, ACK),
                # a fundamental protocol for establishing a shared state of mutual knowledge
                # between two nodes before any application data is exchanged.
                logging.info("Connection established. SYN-ACK received and ACK sent.")

                # -- Begin Data Transfer --
                # The client now sends its payload. The protocol guarantees that this data
                # is delivered exactly-once. It is the responsibility of processes in the
                # source and destination stations to ensure this level of reliability.
                client_socket.sendall(CLIENT_DATA)
                logging.info(f"Sent data: {CLIENT_DATA.decode().strip()}")
                logging.info("Data sent. Initiating graceful shutdown by closing the socket.")

            # Exiting the 'with' block implicitly calls client_socket.close(),
            # which initiates the graceful TCP teardown (sends a FIN packet).

        except ConnectionRefusedError:
            logging.error(f"Connection refused. Is the server running on {self.host}:{self.port}?")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

        logging.info("Client thread finished.")


def main():
    """
    This main function serves as the testbench controller.
    It orchestrates the simulation by setting up the server and client nodes
    and running them to completion, demonstrating a full TCP/IP transaction.
    This process is analogous to executing the 'simg.do' or 'run' targets
    in the provided makefiles.
    """

    logging.info("--- Starting Dædælus TCP/IP Transaction Simulation ---")

    # Instantiate the server (Node 1) and client (Node 0)
    server = TCPServer(SERVER_IPV4_ADDR, TCP_PORT_NUM)
    client = TCPClient(SERVER_IPV4_ADDR, TCP_PORT_NUM)

    # Start both threads to run the simulation concurrently.
    # This emulates the two VProc nodes running in parallel in the HDL simulation.
    server.start()
    client.start()

    # Wait for both nodes to complete their execution.
    client.join()
    server.join(timeout=3) # Add a timeout to ensure server doesn't hang

    logging.info("--- Simulation Complete ---")


if __name__ == "__main__":
    main()