# ethernet_emulator.py
#
# Dædælus: Architecting the Future with Enduring Excellence
#
# This Python script emulates the functionality of the C and Verilog
# sources for the ethernet_dpi example. It provides a complete, self-contained
# simulation of two Ethernet controllers and their interaction over a purely
# virtual, shared medium.
#
# This revised version removes the dependency on a host-specific TUN/TAP
# interface, creating a portable emulation that runs on any OS. This aligns
# with the Daedaelus philosophy of understanding systems from first principles;
# here, we model the "Ether" itself as a software construct, allowing us to
# focus purely on the protocol dynamics and the behavior of the emulated cells.

import struct
import time
import sys
import threading
from collections import deque
import socket

# --- Constants and Configuration ---
# These constants represent the memory-mapped register layout and control
# flags of the simulated Ethernet controller.

# --- UART Definitions ---
EOL = "\r\n"

# --- Ethernet Controller Register Definitions ---
ETH_BASE = 0x92000000
# These are the full memory addresses for the registers
ETH_MODER, ETH_INT_SOURCE, ETH_INT_MASK, ETH_IPGT, ETH_IPGR1, ETH_IPGR2, \
ETH_PACKETLEN, ETH_COLLCONF, ETH_TX_BD_NUM, ETH_CTRLMODER, ETH_MIIMODER, \
ETH_MIICOMMAND, ETH_MIIADDRESS, ETH_MIITX_DATA, ETH_MIIRX_DATA, \
ETH_MIISTATUS, ETH_MAC_ADDR0, ETH_MAC_ADDR1, ETH_HASH0_ADR, ETH_HASH1_ADR, \
ETH_TXCTRL = [ETH_BASE + i * 4 for i in range(21)]

ETH_BD_OFFSET = 0x400

# Bitmasks for Registers and Descriptors
ETH_MODER_RXEN = 0x00000001
ETH_MODER_TXEN = 0x00000002
ETH_MODER_BRO = 0x00000008
ETH_MODER_FULLD = 0x00000400
ETH_MODER_CRCEN = 0x00002000
ETH_MODER_PAD = 0x00008000

ETH_INT_TXB = 0x00000001
ETH_INT_RXB = 0x00000004

# Common Buffer Descriptor bits
BD_IRQ = 0x4000
BD_WRAP = 0x2000

# Rx/Tx Specific Buffer Descriptor bits
ETH_RXBD_EMPTY = 0x8000
ETH_TXBD_READY = 0x8000
ETH_TXBD_PAD = 0x1000
ETH_TXBD_CRC = 0x0800

# --- Node-Specific Configuration ---
NODE_A_MAC = b'\x0A\x0A\x0A\x0A\x0A\x0A'
NODE_A_IP = "192.168.1.10"
NODE_A_IP_BYTES = socket.inet_aton(NODE_A_IP)

NODE_B_MAC = b'\x0B\x0B\x0B\x0B\x0B\x0B'
NODE_B_IP = "192.168.1.11"
NODE_B_IP_BYTES = socket.inet_aton(NODE_B_IP)

BROADCAST_MAC_ADDRESS = b'\xFF\xFF\xFF\xFF\xFF\xFF'

# --- Simulation Parameters ---
MAX_FRAME_LEN = 1536
BUFFER_DESCRIPTOR_COUNT = 8
TX_BD_COUNT = BUFFER_DESCRIPTOR_COUNT // 2


class Uart:
    """Emulates a basic UART for console output for a specific node."""
    def __init__(self, node_name="UART"):
        self._prefix = f"[{node_name}] "
        self.lock = threading.Lock()

    def print(self, text):
        with self.lock:
            sys.stdout.write(self._prefix + str(text))
            sys.stdout.flush()


class VirtualEther:
    """
    Represents the shared communication medium. In conventional networks, this
    is a physical cable. Here, it is a software object that holds frames
    broadcast by all attached nodes, decoupling the sender and receiver.
    This explicit modeling of the channel is key to understanding packet
    dynamics.
    """
    def __init__(self):
        self.channel = deque()
        self.lock = threading.Lock()

    def transmit(self, frame_data, source_node_name):
        with self.lock:
            self.channel.append((frame_data, source_node_name))

    def receive(self, receiving_node_name):
        with self.lock:
            for _ in range(len(self.channel)):
                frame, source = self.channel.popleft()
                if source != receiving_node_name:
                    return frame
                else:
                    self.channel.append((frame, source))
            return None


class SimulatedEthernetController:
    """Emulates the state and registers of an Ethernet controller for one node."""
    def __init__(self, uart, mac_address):
        self.uart = uart
        self.mac_address = mac_address
        self.registers = {}
        self.buffer_descriptors = []
        self.int_o = False
        self.initial_reset()

    def initial_reset(self):
        """Resets all registers to their default power-on state."""
        mac_val_0 = struct.unpack('<I', self.mac_address[2:6])[0]
        mac_val_1 = struct.unpack('<H', self.mac_address[0:2])[0]

        self.registers = {
            ETH_MODER: ETH_MODER_CRCEN | ETH_MODER_PAD | ETH_MODER_FULLD,
            ETH_MAC_ADDR0: mac_val_0,
            ETH_MAC_ADDR1: mac_val_1,
            ETH_TX_BD_NUM: TX_BD_COUNT,
            ETH_INT_SOURCE: 0,
            ETH_INT_MASK: 0,
            ETH_PACKETLEN: (64 << 16) | MAX_FRAME_LEN
        }
        self.buffer_descriptors = [{'flags': 0, 'addr': 0} for _ in range(BUFFER_DESCRIPTOR_COUNT)]
        self.int_o = False

    def read_reg(self, addr):
        """Simulates a CPU read from a register."""
        if ETH_BD_OFFSET <= (addr - ETH_BASE) < (ETH_BD_OFFSET + BUFFER_DESCRIPTOR_COUNT * 8):
            bd_index = (addr - ETH_BASE - ETH_BD_OFFSET) // 8
            is_addr_word = (addr % 8) != 0
            return self.buffer_descriptors[bd_index]['addr' if is_addr_word else 'flags']
        return self.registers.get(addr, 0)

    def write_reg(self, addr, value):
        """Simulates a CPU write to a register."""
        if addr == ETH_INT_SOURCE:
            self.registers[addr] &= ~value
        elif ETH_BD_OFFSET <= (addr - ETH_BASE) < (ETH_BD_OFFSET + BUFFER_DESCRIPTOR_COUNT * 8):
            bd_index = (addr - ETH_BASE - ETH_BD_OFFSET) // 8
            is_addr_word = (addr % 8) != 0
            if is_addr_word:
                self.buffer_descriptors[bd_index]['addr'] = value
            else:
                self.buffer_descriptors[bd_index]['flags'] = value
        else:
            self.registers[addr] = value
        self.check_interrupt()

    def trigger_interrupt(self, interrupt_bit):
        self.registers[ETH_INT_SOURCE] |= interrupt_bit
        self.check_interrupt()

    def check_interrupt(self):
        self.int_o = (self.registers.get(ETH_INT_SOURCE, 0) & self.registers.get(ETH_INT_MASK, 0)) != 0


class EthernetExampleClient:
    """
    Represents a single computational cell, with its own controller, memory,
    and application logic. It interacts with the outside world only through
    the VirtualEther object.
    """
    def __init__(self, name, mac, ip_str, ip_bytes, controller, uart, ether):
        self.name = name
        self.mac = mac
        self.ip_str = ip_str
        self.ip_bytes = ip_bytes
        self.controller = controller
        self.uart = uart
        self.ether = ether

        self.eth_tx_packet = bytearray(MAX_FRAME_LEN)
        self.eth_rx_packet = bytearray(MAX_FRAME_LEN)

        self.current_tx_bd_index = 0
        self.current_rx_bd_index = TX_BD_COUNT

    def start_app_logic(self):
        """Initializes the controller and prepares receive buffers."""
        self.uart.print("Initializing..." + EOL)
        moder_val = ETH_MODER_TXEN | ETH_MODER_RXEN | ETH_MODER_PAD | ETH_MODER_CRCEN | ETH_MODER_FULLD
        self.controller.write_reg(ETH_MODER, moder_val)
        self.controller.write_reg(ETH_INT_MASK, ETH_INT_RXB | ETH_INT_TXB)

        for i in range(TX_BD_COUNT, BUFFER_DESCRIPTOR_COUNT):
            self.controller.write_reg(ETH_BASE + ETH_BD_OFFSET + i * 8, ETH_RXBD_EMPTY | BD_IRQ)

    def process_received_frame(self, frame):
        """Handles incoming frames, parsing ARP requests and replies."""
        if len(frame) < 28: return

        dest_mac, src_mac, eth_type = struct.unpack('!6s6sH', frame[0:14])
        if eth_type != 0x0806: return

        htype, ptype, hlen, plen, oper, sha, spa, tha, tpa = struct.unpack('!HHBBH6s4s6s4s', frame[14:42])

        if oper == 1 and tpa == self.ip_bytes: # ARP Request for me
            self.uart.print(f"Received ARP request for my IP from {socket.inet_ntoa(spa)} ({sha.hex(':')})" + EOL)
            self.uart.print("Sending ARP reply..." + EOL)
            reply_eth = struct.pack('!6s6sH', sha, self.mac, 0x0806)
            reply_arp = struct.pack('!HHBBH6s4s6s4s', htype, ptype, hlen, plen, 2, self.mac, self.ip_bytes, sha, spa)
            self.send_frame(reply_eth + reply_arp)
        
        elif oper == 2 and tha == self.mac: # ARP Reply for me
            self.uart.print(f"Received ARP reply: {socket.inet_ntoa(spa)} is at {sha.hex(':')}" + EOL)

    def send_frame(self, data):
        """Places data in the transmit buffer and triggers a send."""
        length = len(data)
        self.eth_tx_packet[:length] = data

        bd_addr = ETH_BASE + ETH_BD_OFFSET + self.current_tx_bd_index * 8
        bd_flags = self.controller.read_reg(bd_addr)
        if not (bd_flags & ETH_TXBD_READY):
            status_word = (length << 16) | ETH_TXBD_READY | BD_IRQ | ETH_TXBD_CRC | ETH_TXBD_PAD
            if self.current_tx_bd_index == (TX_BD_COUNT - 1):
                status_word |= BD_WRAP
            self.controller.write_reg(bd_addr, status_word)
        else:
            self.uart.print("Error: Tx buffer not ready." + EOL)

    def send_arp_request(self, target_ip_bytes):
        """Broadcasts an ARP request to discover a MAC address."""
        self.uart.print(f"Broadcasting ARP request for {socket.inet_ntoa(target_ip_bytes)}" + EOL)
        eth_header = struct.pack('!6s6sH', BROADCAST_MAC_ADDRESS, self.mac, 0x0806)
        arp_payload = struct.pack('!HHBBH6s4s6s4s', 1, 0x0800, 6, 4, 1, self.mac, self.ip_bytes, b'\x00' * 6, target_ip_bytes)
        self.send_frame(eth_header + arp_payload)

    def tick(self):
        """A single slice of processing time for this node."""
        if self.controller.read_reg(ETH_MODER) & ETH_MODER_TXEN:
            tx_bd_addr = ETH_BASE + ETH_BD_OFFSET + self.current_tx_bd_index * 8
            tx_flags = self.controller.read_reg(tx_bd_addr)
            if tx_flags & ETH_TXBD_READY:
                length = tx_flags >> 16
                data_to_send = self.eth_tx_packet[:length]
                self.ether.transmit(data_to_send, self.name)
                self.uart.print(f"Frame of {length} bytes transmitted." + EOL)
                
                new_flags = tx_flags & ~ETH_TXBD_READY
                self.controller.write_reg(tx_bd_addr, new_flags)
                if tx_flags & BD_IRQ: self.controller.trigger_interrupt(ETH_INT_TXB)
                
                if tx_flags & BD_WRAP: self.current_tx_bd_index = 0
                else: self.current_tx_bd_index = (self.current_tx_bd_index + 1) % TX_BD_COUNT
        
        received_frame = self.ether.receive(self.name)
        if received_frame and (self.controller.read_reg(ETH_MODER) & ETH_MODER_RXEN):
            rx_bd_addr = ETH_BASE + ETH_BD_OFFSET + self.current_rx_bd_index * 8
            rx_flags = self.controller.read_reg(rx_bd_addr)
            if rx_flags & ETH_RXBD_EMPTY:
                frame_len = len(received_frame)
                self.uart.print(f"Frame of {frame_len} bytes received into buffer." + EOL)
                self.eth_rx_packet[:frame_len] = received_frame
                
                new_flags = (rx_flags & ~ETH_RXBD_EMPTY) | (frame_len << 16)
                self.controller.write_reg(rx_bd_addr, new_flags)
                if rx_flags & BD_IRQ: self.controller.trigger_interrupt(ETH_INT_RXB)
                
                if rx_flags & BD_WRAP: self.current_rx_bd_index = TX_BD_COUNT
                else: self.current_rx_bd_index = TX_BD_COUNT + ((self.current_rx_bd_index - TX_BD_COUNT + 1) % (BUFFER_DESCRIPTOR_COUNT - TX_BD_COUNT))

        for i in range(TX_BD_COUNT, BUFFER_DESCRIPTOR_COUNT):
            bd_addr = ETH_BASE + ETH_BD_OFFSET + i * 8
            flags = self.controller.read_reg(bd_addr)
            if not (flags & ETH_RXBD_EMPTY):
                frame_len = flags >> 16
                self.process_received_frame(self.eth_rx_packet[:frame_len])
                self.controller.write_reg(bd_addr, (flags | ETH_RXBD_EMPTY) & 0x0000FFFF)

        # Emulate CPU checking for interrupt flags
        if self.controller.int_o:
            source = self.controller.read_reg(ETH_INT_SOURCE)
            if source & ETH_INT_TXB: self.uart.print("Transmit interrupt asserted." + EOL)
            if source & ETH_INT_RXB: self.uart.print("Receive interrupt asserted." + EOL)
            self.controller.write_reg(ETH_INT_SOURCE, source) # Clear handled interrupts


def main():
    """Main simulation entry point."""
    virtual_ether = VirtualEther()

    uart_a = Uart("NodeA")
    controller_a = SimulatedEthernetController(uart_a, NODE_A_MAC)
    node_a = EthernetExampleClient("NodeA", NODE_A_MAC, NODE_A_IP, NODE_A_IP_BYTES, controller_a, uart_a, virtual_ether)

    uart_b = Uart("NodeB")
    controller_b = SimulatedEthernetController(uart_b, NODE_B_MAC)
    node_b = EthernetExampleClient("NodeB", NODE_B_MAC, NODE_B_IP, NODE_B_IP_BYTES, controller_b, uart_b, virtual_ether)

    node_a.start_app_logic()
    node_b.start_app_logic()

    print("\n--- Starting Emulation ---")
    print("Node A will now attempt to discover Node B via ARP.")
    
    node_a.send_arp_request(NODE_B_IP_BYTES)

    try:
        for tick_count in range(5): # Reduced ticks to show a concise interaction
            print(f"\n--- Tick {tick_count+1} ---")
            node_a.tick()
            node_b.tick()
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n--- Emulation stopped by user. ---")
    
    print("\n--- Emulation Finished ---")

if __name__ == "__main__":
    main()