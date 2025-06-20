#
# DDL_Emulator_Fabric.py (ethernet9.py)
#
# This script provides a unified interface for interacting with various network 
# fabrics, serving as a foundational component of the DDL_Emulator. This version
# includes a Virtual Fabric Mode, allowing it to run as a self-contained, 
# information-theoretic emulator without requiring physical hardware.
#

import sys
import os
import platform
import threading
import time
import ctypes
import queue
from typing import List, Optional

# --- Daedalus Virtual Fabric Configuration ---
# Set to True to run in software-only emulation mode without physical hardware.
# Set to False to attempt to connect to a real TSMaster device.
VIRTUAL_MODE = True

# --- Data Structures & API Definitions (shared by real and virtual mode) ---
try:
    # Attempt to import the real library structures if available, otherwise define stubs.
    if platform.system() == "Windows":
        from TSMasterAPI import *
    else:
        # On non-windows, we must ensure the path is set for the real library,
        # even if we end up not using it in virtual mode.
        script_dir = os.path.dirname(os.path.realpath(__file__))
        lib_path = os.path.abspath(os.path.join(script_dir, 'TSMasterDemos/Python/Linux/lib'))
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        from libTOSUN import *
except (ImportError, NameError):
    if not VIRTUAL_MODE:
        print("Error: Real hardware libraries (TSMasterAPI/libTOSUN) not found. To run without them, set VIRTUAL_MODE = True.")
        exit()
    else:
        # Define minimal structures needed for the script to be syntactically valid
        # when the real libraries are missing and VIRTUAL_MODE is on.
        print("Info: Real hardware libraries not found. Proceeding in VIRTUAL_MODE.")
        class Structure: pass
        class TLIBCAN(Structure):
             def __init__(self, **kwargs): [setattr(self, k, v) for k, v in kwargs.items()]
        class TLIBCANFD(Structure):
             def __init__(self, **kwargs): [setattr(self, k, v) for k, v in kwargs.items()]
        class TLIBLIN(Structure):
            def __init__(self, **kwargs): [setattr(self, k, v) for k, v in kwargs.items()]
        class TLIBApplicationChannelType: APP_CAN, APP_LIN = 0, 1
        class TLIBBusToolDeviceType: TS_USB_DEVICE = 3
        class TLIB_TS_Device_Sub_Type: TC1016 = 11
        class TLIBCANFDControllerType: lfdtISOCAN = 1
        class TLIBCANFDControllerMode: lfdmNormal = 0
        class TLINProtocol: LIN_PROTOCL_21 = 2
        class READ_TX_RX_DEF: TX_RX_MESSAGES, ONLY_RX_MESSAGES = 1, 0
        def c_float(val): return val


# --- Daedalus Virtual Hardware Abstraction Layer ---

class VirtualTSMasterAPI:
    """
    This class is a software emulation of the TSMaster hardware API. It acts as
    a "Digital Twin" for the physical device, allowing the emulator logic to run
    identically with or without hardware. It maintains virtual channels and FIFO
    buffers to simulate the flow of tokens.
    """
    def __init__(self):
        self._channels = {}
        self._is_connected = False
        print("Virtual TSMaster API initialized.")

    def initialize_lib_tsmaster(self, *args): pass
    def tsapp_set_can_channel_count(self, count): pass
    def tsapp_set_lin_channel_count(self, count): pass
    def tsapp_set_mapping_verbose(self, *args): pass
    def tsapp_configure_baudrate_canfd(self, *args): pass
    def tsapp_configure_baudrate_can(self, *args): pass
    def tsapp_configure_baudrate_lin(self, *args): pass
    
    def tsapp_connect(self, *args):
        self._is_connected = True
        return 0 # Success

    def tsfifo_enable_receive_fifo(self): pass

    def tsapp_transmit_can_async(self, handle, msg):
        # Emulate loopback: a sent message is placed in the receive queue.
        if msg.FIdxChn not in self._channels:
            self._channels[msg.FIdxChn] = queue.Queue()
        
        # In a real fabric, this token would propagate on the Ether. Here, we loop it back.
        tx_msg = TLIBCAN()
        ctypes.memmove(ctypes.addressof(tx_msg), ctypes.addressof(msg), ctypes.sizeof(TLIBCAN))
        tx_msg.FProperties = tx_msg.FProperties | 1 # Set direction to TX
        self._channels[msg.FIdxChn].put(tx_msg)

        rx_msg = TLIBCAN()
        ctypes.memmove(ctypes.addressof(rx_msg), ctypes.addressof(msg), ctypes.sizeof(TLIBCAN))
        rx_msg.FProperties = rx_msg.FProperties & ~1 # Set direction to RX
        self._channels[msg.FIdxChn].put(rx_msg)

        return 0

    def tsfifo_receive_can_msgs(self, handle, buffer, buffer_size, channel, include_tx_flag):
        if channel not in self._channels:
            buffer_size.value = 0
            return 0

        count = 0
        while count < buffer_size.value and not self._channels[channel].empty():
            msg = self._channels[channel].get()
            is_tx = msg.FProperties & 1
            if include_tx_flag == READ_TX_RX_DEF.TX_RX_MESSAGES or (include_tx_flag == READ_TX_RX_DEF.ONLY_RX_MESSAGES and not is_tx):
                buffer[count] = msg
                count += 1
        buffer_size.value = count
        return 0

    def tsdiag_can_create(self, *args): return 0
    def tsdiag_can_delete(self, *args): return 0

    def tstp_can_request_and_get_response(self, handle, req_bytes, req_len, res_buf, res_size):
        # Simulate a reversible transaction for UDS TesterPresent
        if list(req_bytes) == [0x3E, 0x80]:
            # Positive response for TesterPresent is 0x7E, 0x80
            response = bytes([0x7E, 0x80])
            ctypes.memmove(res_buf, response, len(response))
            res_size.value = len(response)
            return 0 # Success
        return 161 # Timeout error

    def tsapp_disconnect_all(self):
        self._is_connected = False
        return 0

    def finalize_lib_tsmaster(self): pass
    def tsapp_get_error_description(self, code): return b"Virtual Fabric Error"

# --- Main Emulator Class ---
class DDL_Emulator_Fabric:
    """
    The DDL_Emulator_Fabric orchestrates interactions on the network. It can
    operate on either a physical hardware fabric or a virtualized emulation.
    """
    def __init__(self, app_name: bytes = b"DDL_Emulator"):
        print("Initializing DDL_Emulator Fabric...")
        self.api = VirtualTSMasterAPI() if VIRTUAL_MODE else sys.modules[__name__]
        
        if VIRTUAL_MODE:
            self.api.initialize_lib_tsmaster()
        else:
            if platform.system() == "Windows":
                self.api.initialize_lib_tsmaster(app_name)
            else:
                self.api.initialize_lib_tsmaster(True, True) 
        
        self._connected = False
        print("Fabric Initialized.")

    def connect_fabric(self, channel_configs: list):
        # ... (rest of the class is identical to the previous version)
        can_channels = sum(1 for cfg in channel_configs if cfg.get('type') in ('CAN', 'CANFD'))
        lin_channels = sum(1 for cfg in channel_configs if cfg.get('type') == 'LIN')
        self.api.tsapp_set_can_channel_count(can_channels)
        self.api.tsapp_set_lin_channel_count(lin_channels)
        for i, config in enumerate(channel_configs):
            if VIRTUAL_MODE: continue
            self.api.tsapp_set_mapping_verbose(
                b"DDL_Emulator", config.get('app_type', TLIBApplicationChannelType.APP_CAN), i,
                config.get('hw_name', b"TC1016"), TLIBBusToolDeviceType.TS_USB_DEVICE,
                config.get('hw_subtype', TLIB_TS_Device_Sub_Type.TC1016),
                config.get('hw_index', 0), config.get('hw_channel', i), True)
            if config.get('type') == 'CANFD':
                self.api.tsapp_configure_baudrate_canfd(i, c_float(config.get('rate_kbps', 500.0)), c_float(config.get('data_kbps', 2000.0)), TLIBCANFDControllerType.lfdtISOCAN, TLIBCANFDControllerMode.lfdmNormal, config.get('termination', True))
            elif config.get('type') == 'CAN':
                self.api.tsapp_configure_baudrate_can(i, c_float(config.get('rate_kbps', 500.0)), False, config.get('termination', True))
        
        connect_fn = self.api.tsapp_connect if not VIRTUAL_MODE else self.api.tsapp_connect
        ret = connect_fn() if VIRTUAL_MODE else connect_fn(b'', c_size_t(0))

        if ret == 0:
            self._connected = True
            self.api.tsfifo_enable_receive_fifo()
            print("Fabric is online. Links are active.")
        else:
            error_desc = self.api.tsapp_get_error_description(ret)
            raise ConnectionError(f"Failed to connect. Error {ret}: {error_desc.decode() if error_desc else 'Unknown'}")

    def send_token(self, msg_object):
        if not self._connected: return
        handle = c_size_t(0)
        if isinstance(msg_object, TLIBCAN):
            self.api.tsapp_transmit_can_async(handle, msg_object)
        elif isinstance(msg_object, TLIBCANFD):
            self.api.tsapp_transmit_canfd_async(handle, msg_object)

    def receive_token_stream(self, channel_index: int, msg_type: str, count: int, include_tx: bool = False):
        if not self._connected: return []
        handle = c_size_t(0)    
        buf_size = ctypes.c_int32(count)
        flag = READ_TX_RX_DEF.TX_RX_MESSAGES if include_tx else READ_TX_RX_DEF.ONLY_RX_MESSAGES
        if msg_type.upper() == 'CAN':
            buf = (TLIBCAN * count)()
            self.api.tsfifo_receive_can_msgs(handle, buf, buf_size, channel_index, flag)
        elif msg_type.upper() == 'CANFD':
            buf = (TLIBCANFD * count)()
            self.api.tsfifo_receive_canfd_msgs(handle, buf, buf_size, channel_index, flag)
        else:
            return []
        return [buf[i] for i in range(buf_size.value)]

    def execute_reversible_subtransaction(self, channel_index: int, request_data: List[int], req_id: int, res_id: int):
        if not self._connected: raise ConnectionError("Fabric is not online.")
        diag_handle = ctypes.c_int32(0)
        try:
            self.api.tsdiag_can_create(diag_handle, channel_index, 0, 8, req_id, True, res_id, True, 0, False)
            req_bytes = bytes(request_data)
            res_buf = (ctypes.c_uint8 * 4095)()
            res_size = ctypes.c_int32(4095)
            ret = self.api.tstp_can_request_and_get_response(diag_handle, req_bytes, len(req_bytes), res_buf, res_size)
            if ret == 0:
                print(f"Reversible subtransaction successful. Response: {bytes(res_buf[:res_size.value]).hex()}")
                return bytes(res_buf[:res_size.value])
            else:
                desc = self.api.tsapp_get_error_description(ret)
                print(f"Reversible subtransaction failed: {desc.decode() if desc else 'Unknown Error'}")
                return None
        finally:
            if diag_handle.value != 0: self.api.tsdiag_can_delete(diag_handle)
    
    def shutdown(self):
        if self._connected:
            print("Shutting down fabric...")
            self.api.tsapp_disconnect_all()
            self._connected = False
        self.api.finalize_lib_tsmaster()
        print("Fabric is offline.")

# --- Main Execution Block ---
def main():
    """
    Demonstrates the orchestration of the emulated fabric.
    """
    configs = [{'type': 'CAN'}] # Dummy config for virtual mode
    fabric = DDL_Emulator_Fabric()
    try:
        fabric.connect_fabric(configs)
        
        print("\n--- DEMO 1: Transmitting a single token ---")
        tok = TLIBCAN(FIdentifier=0x123, FDLC=8, FData=[1,2,3,4,5,6,7,8])
        fabric.send_token(tok)
        print(f"Token 0x{tok.FIdentifier:X} sent on channel {tok.FIdxChn}.")
        time.sleep(0.1)

        print("\n--- DEMO 2: Receiving tokens from the Ether ---")
        rec = fabric.receive_token_stream(0, 'CAN', 10, include_tx=True)
        if rec:
            print(f"Captured {len(rec)} tokens:")
            for t in rec:
                dirn = "Tx" if (t.FProperties & 1) else "Rx"
                print(f"  > [{dirn}] ID: 0x{t.FIdentifier:X}, Data: {bytes(t.FData[:t.FDLC]).hex()}")
        else:
            print("No tokens captured.")
            
        print("\n--- DEMO 3: Reversible Subtransaction ---")
        resp = fabric.execute_reversible_subtransaction(0, [0x3E,0x80], 0x7E0, 0x7E8)
        if resp is None:
            print("Diagnostic echo failed.")
            
    except Exception as e:
        print(f"\nAn unrecoverable error occurred in the fabric emulator: {e}")
    finally:
        fabric.shutdown()

if __name__ == '__main__':
    main()