# To host on website. host python on the backend so that the simulation can run on the website.
# Backpressure ripples stops throughput going through to drop the thing, that's the Daedaelus method. For the Metcalfe full duplex method we should be able to see congestion on the center link and on each switch. Simulate Buffer credits on each of the Fibre channel switches. Send a few of them, don't send more unacknowledged packets if you receive an ACK then you send more; sliding window. The width of that window depends on..that's when things like TCP reno or TCP fast will tell you its schemes for side throughput throttling. Cells links and data center projects onto Sumon..go full steam ahead on this..
#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import io
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import websockets

import simpy
import random
import enum
from math import cos, sin, pi
from PIL import Image, EpsImagePlugin, ImageDraw

# External modules
import daedaelus_fabric_sim as fabric_sim
import ethernet24 as tsn_mod
import ethernet25 as building_mod

EpsImagePlugin.gs_windows_binary = r'gswin64c' if os.name == 'nt' else 'gs'

# -----------------------------------------------------------------------------
# Logging setup: packet & link logs (capture all modules)
# -----------------------------------------------------------------------------
logger = logging.getLogger("net_sim")
logger.setLevel(logging.DEBUG)
log_buffer = io.StringIO()
handler = logging.StreamHandler(log_buffer)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# also capture root logger so external sims get recorded
root_logger = logging.getLogger()
root_logger.addHandler(handler)


def export_logs(path: str):
    """Write the entire logging buffer to a JSON file for Mathematica."""
    raw = log_buffer.getvalue().strip().splitlines()
    records = [json.loads(line) for line in raw]
    with open(path, 'w') as f:
        json.dump(records, f, indent=2)
    logger.info(json.dumps({"event":"export_logs","path":path}))

# -----------------------------------------------------------------------------
# Address classes
# -----------------------------------------------------------------------------
class AdrIP:
    ADDR_IP_LEN = 4
    def __init__(self, addr=None):
        self._IPadr = list(addr) if addr and len(addr)==4 else [0]*4
    def __str__(self):
        return ".".join(map(str, self._IPadr))
    def copy(self):
        return AdrIP(self._IPadr)

class AdrMac:
    ADDR_MAC_LEN = 6
    def __init__(self, hex_list=None):
        self._Macadr = [int(h,16) for h in hex_list] if hex_list and len(hex_list)==6 else [0]*6
    def __str__(self):
        return ":".join(f"{b:02x}" for b in self._Macadr)
    def copy(self):
        return AdrMac([f"{b:02x}" for b in self._Macadr])

# -----------------------------------------------------------------------------
# Packet Type & Packet
# -----------------------------------------------------------------------------
class PacketType(enum.Enum):
    SYN      = "SYN"
    SYN_ACK  = "SYN-ACK"
    ACK      = "ACK"
    DATA     = "DATA"

class Packet:
    def __init__(self, ptype, src=None, dst=None, size=0, seq=0, ack=0,
                 src_mac=None, dst_mac=None, src_ip=None, dst_ip=None):
        self.id       = str(uuid.uuid4())
        self.ptype    = ptype
        self.src      = src
        self.dst      = dst
        self.size     = size
        self.seq      = seq
        self.ack      = ack
        self.success  = True
        self.src_mac  = src_mac  or AdrMac()
        self.dst_mac  = dst_mac  or AdrMac()
        self.src_ip   = src_ip   or AdrIP()
        self.dst_ip   = dst_ip   or AdrIP()

    def bits(self):
        return self.size * 8

    def to_dict(self):
        return {
            "time": getattr(self, 'start_time', None),
            "pkt_id": self.id,
            "type": self.ptype.value,
            "src": getattr(self.src, 'name', None),
            "dst": getattr(self.dst, 'name', None),
            "seq": self.seq,
            "ack": self.ack,
            "size": self.size,
            "success": self.success
        }

    def __repr__(self):
        return f"<{self.ptype.value} id={self.id[:8]} seq={self.seq}→{getattr(self.dst,'name',None)}>"

# -----------------------------------------------------------------------------
# Channel with optional contention
# -----------------------------------------------------------------------------
class Channel:
    def __init__(self, env, name="chan", contention=True):
        self.env        = env
        self.name       = name
        self.contention = contention
        self.current    = []
        self.log        = []
        self.latencies  = []

    def transmit(self, packet: Packet, duration: float):
        packet.start_time = self.env.now
        self.current.append(packet)
        collided = self.contention and len(self.current) > 1
        entry = {
            "time": self.env.now,
            "event": "start_tx",
            "chan": self.name,
            **packet.to_dict(),
            "collided": collided
        }
        logger.info(json.dumps(entry))
        self.log.append(entry)
        return self.env.process(self._finish(packet, duration))

    def _finish(self, packet: Packet, duration: float):
        yield self.env.timeout(duration)
        self.current.remove(packet)
        if self.contention and any(p != packet for p in self.current):
            packet.success = False
        packet.end_time = self.env.now
        latency = packet.end_time - packet.start_time
        entry = {
            "time": self.env.now,
            "event": "end_tx",
            "chan": self.name,
            **packet.to_dict(),
            "latency": latency
        }
        logger.info(json.dumps(entry))
        self.log.append(entry)
        self.latencies.append(latency)

# -----------------------------------------------------------------------------
# TCP-like Endpoint
# -----------------------------------------------------------------------------
class TCPEndpoint:
    def __init__(self, env, name, channel: Channel, peer, mss, data_size, slot_time):
        self.env        = env
        self.name       = name
        self.channel    = channel
        self.peer       = peer
        self.mss        = mss
        self.data_size  = data_size
        self.slot_time  = slot_time
        self.next_seq   = 0
        self.acked      = set()
        env.process(self.run())

    def send_packet(self, pkt: Packet):
        pkt.src = self
        pkt.dst = self.peer
        duration = self.slot_time if pkt.ptype != PacketType.DATA else (pkt.size/self.mss)*self.slot_time
        return self.channel.transmit(pkt, duration)

    def receive(self, pkt: Packet):
        def _handler():
            if pkt.dst != self or not pkt.success:
                return
            if pkt.ptype == PacketType.SYN:
                yield self.send_packet(Packet(PacketType.SYN_ACK))
            elif pkt.ptype == PacketType.SYN_ACK:
                yield self.send_packet(Packet(PacketType.ACK))
            elif pkt.ptype == PacketType.DATA:
                yield self.send_packet(Packet(PacketType.ACK, seq=0, ack=pkt.seq))
            elif pkt.ptype == PacketType.ACK:
                self.acked.add(pkt.ack)
        self.env.process(_handler())

    def run(self):
        if self.name == "A":
            yield self.send_packet(Packet(PacketType.SYN))
        while True:
            log = self.channel.log
            if self.name=="A" and any(r["type"]=="SYN-ACK" and r["dst"]==self.name for r in log):
                break
            if self.name=="B" and any(r["type"]=="SYN" and r["dst"]==self.name for r in log):
                break
            yield self.env.timeout(self.slot_time/10)
        if self.name == "A":
            while self.next_seq < self.data_size:
                pkt = Packet(PacketType.DATA, size=self.mss, seq=self.next_seq)
                yield self.send_packet(pkt)
                while self.next_seq not in self.acked:
                    yield self.env.timeout(self.slot_time/10)
                self.next_seq += self.mss

# -----------------------------------------------------------------------------
# ALOHA / CSMA Simulation
# -----------------------------------------------------------------------------
def simulate_aloha(num_nodes, duration, rate, protocol='csma', contention=True, priorities=None):
    SLOT, FRAME = 1, 1
    env  = simpy.Environment()
    chan = Channel(env, name="aloha_chan", contention=contention)
    # assign names A, B, C...
    names = [chr(ord('A')+i%26) for i in range(num_nodes)]

    class Node:
        def __init__(self, env, idx, chan, arr, prot, prio):
            self.env, self.id, self.chan, self.arr, self.prot = env, idx, chan, arr, prot
            self.prio = prio
            self.name = names[idx]
            self.sent, self.coll, self.succ = 0,0,0
            env.process(self.run())

        def run(self):
            while True:
                yield self.env.timeout(random.expovariate(self.arr))
                if self.prot == 'csma':
                    yield from self.csma_cd()
                else:
                    # pure and slotted ALOHA treated the same visually
                    yield self.env.timeout((0 if self.prot=='slotted' else 0))
                    yield from self._aloha(SLOT)

        def _aloha(self, backoff):
            pkt = Packet(PacketType.DATA, size=FRAME)
            pkt.src = self
            pkt.dst = None
            proc = self.chan.transmit(pkt, backoff)
            yield proc
            self.sent += 1
            if pkt.success:
                self.succ += 1
            else:
                self.coll += 1

        def csma_cd(self):
            while True:
                while self.chan.current:
                    yield self.env.timeout(SLOT/10)
                pkt = Packet(PacketType.DATA, size=FRAME)
                pkt.src = self
                pkt.dst = None
                proc = self.chan.transmit(pkt, FRAME)
                yield proc
                self.sent += 1
                if pkt.success:
                    self.succ += 1
                    return
                self.coll += 1
                yield self.env.timeout((2**self.coll)//self.prio * SLOT)

    if not priorities or len(priorities) != num_nodes:
        priorities = [1]*num_nodes
    nodes = [Node(env,i,chan,rate,protocol,priorities[i]) for i in range(num_nodes)]
    env.run(until=duration)
    throughput = sum(n.succ for n in nodes)/duration
    avg_lat   = sum(chan.latencies)/len(chan.latencies) if chan.latencies else None
    return chan.log, {"throughput":throughput, "avg_latency":avg_lat}

# -----------------------------------------------------------------------------
# Half-Duplex & Full-Duplex Ethernet Simulations
# -----------------------------------------------------------------------------
def simulate_half_duplex(duration, rate, contention=True):
    env = simpy.Environment()
    chan = Channel(env, name="eth_hd", contention=contention)
    # two endpoints only
    B = TCPEndpoint(env,'B',chan,None,rate,rate*5,slot_time=1)
    A = TCPEndpoint(env,'A',chan,B,   rate,rate*5,slot_time=1)
    B.peer = A
    env.run(until=duration)
    acks = [r for r in chan.log if r.get("type")=="ACK"]
    throughput = len(acks)/duration
    avg_lat   = sum(r.get("latency",0) for r in chan.log)/len(chan.log)
    return chan.log, {"throughput":throughput, "avg_latency":avg_lat}

def simulate_full_duplex(duration, rate):
    env = simpy.Environment()
    chan_ab = Channel(env, name="eth_fd_ab", contention=False)
    chan_ba = Channel(env, name="eth_fd_ba", contention=False)
    class FDEndpoint(TCPEndpoint):
        def send_packet(self, pkt):
            chan = chan_ab if self.name=="A" else chan_ba
            pkt.src = self
            pkt.dst = self.peer
            return chan.transmit(pkt, pkt.size/rate)
    B = FDEndpoint(env,'B',chan_ba,None,rate,rate*5,1)
    A = FDEndpoint(env,'A',chan_ab,B,   rate,rate*5,1)
    B.peer = A
    env.run(until=duration)
    logs = chan_ab.log + chan_ba.log
    throughput = len([r for r in logs if r.get("type")=="ACK"] )/duration
    avg_lat   = sum(r.get("latency",0) for r in logs)/len(logs)
    return logs, {"throughput":throughput, "avg_latency":avg_lat}

# -----------------------------------------------------------------------------
# UI & Animation
# -----------------------------------------------------------------------------
class SimulationFramework:
    def __init__(self, root):
        self.root, self.frames = root, []
        self.root.title("Enhanced Packet Transfer Simulation")
        self.setup_ui()
        self.draw_network()

    def setup_ui(self):
        mf = ttk.Frame(self.root, padding="10"); mf.grid()
        lf = ttk.LabelFrame(mf, text="Controls", padding="10"); lf.grid(row=0, column=0, sticky="w")
        ttk.Label(lf, text="Protocol:").grid(row=0, column=0, sticky=tk.W)
        self.proto = ttk.Combobox(lf, values=[
            "TCP Handshake (HD, no contention)",
            "TCP Handshake (HD, contention)",
            "TCP Handshake (FD)",
            "CSMA/CD (ALOHA)",
            "Pure ALOHA", "Slotted ALOHA",
            "Half-Duplex Ethernet",
            "Full-Duplex Ethernet",
            "Daedaelus Fabric", "Automotive TSN", "Active Building"
        ], state="readonly")
        self.proto.current(0); self.proto.grid(row=0, column=1)

        labels   = ["Pkt Size","Bandwidth","Arrival λ","Sim Time","Priorities","Num Nodes","Export Logs?" ]
        defaults = ["1024","1e6","0.1","10","1,1","3","False"]
        for i,(txt,defv) in enumerate(zip(labels, defaults), start=1):
            ttk.Label(lf, text=f"{txt}:").grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(lf, width=12); entry.insert(0, defv)
            setattr(self, f"e{i}", entry); entry.grid(row=i, column=1)

        bf = ttk.Frame(lf); bf.grid(row=8, column=0, columnspan=2, pady=5)
        self.start_btn  = ttk.Button(bf, text="Start", command=self.start_sim)
        self.export_btn = ttk.Button(bf, text="Export Logs", command=self.export_logs, state="disabled")
        for w in (self.start_btn, self.export_btn): w.pack(side=tk.LEFT, padx=2)

        self.status = ttk.Label(mf, text="", font=(None,10,'bold'))
        self.status.grid(row=1, column=0, sticky="w")

        self.canvas = tk.Canvas(mf, width=800, height=400, bg="#eef")
        self.canvas.grid(row=2, column=0)

        self.routers = []  # populated in start_sim

    def draw_network(self):
        self.canvas.delete("all")
        for i,r in enumerate(self.routers):
            for j in range(i+1, len(self.routers)):
                r2 = self.routers[j]
                self.canvas.create_line(r['x'], r['y'], r2['x'], r2['y'], fill="gray", width=2)
        for r in self.routers:
            self.canvas.create_rectangle(r['x']-25, r['y']-25, r['x']+25, r['y']+25, fill="lightblue")
            self.canvas.create_text(r['x'], r['y'], text=r['name'], font=(None,12,'bold'))

    def start_sim(self):
        self.export_btn.config(state="disabled")
        proto    = self.proto.get()
        try:
            ps      = int(self.e1.get())
            bw      = float(self.e2.get())
            rate    = float(self.e3.get())
            st      = float(self.e4.get())
            prio    = [int(p) for p in self.e5.get().split(',')]
            num_nd  = max(2, int(self.e6.get()))
            do_export = self.e7.get().lower() in ("true","1","yes")
        except Exception:
            self.status.config(text="Invalid inputs")
            return

        # layout nodes on circle
        cx, cy, rad = 400,200,150
        self.routers = []
        for i in range(num_nd):
            ang = 2*pi*i/num_nd
            x = cx + rad*cos(ang)
            y = cy + rad*sin(ang)
            name = chr(ord('A')+i%26)
            self.routers.append({'id':i,'x':x,'y':y,'name':name})

        self.draw_network()
        self.status.config(text="Running simulation...")
        handler.flush(); log_buffer.truncate(0); log_buffer.seek(0)

        if "ALOHA" in proto:
            key = proto.lower().split()[0]
            log, stats = simulate_aloha(num_nd, st, rate,
                                        protocol=key,
                                        contention="contention" in proto,
                                        priorities=prio)
        elif "Half-Duplex Ethernet" in proto:
            log, stats = simulate_half_duplex(st, rate,
                                              contention="no contention" not in proto)
        elif "Full-Duplex Ethernet" in proto:
            log, stats = simulate_full_duplex(st, rate)
        elif "TCP Handshake" in proto:
            cd  = "no contention" not in proto
            log, stats = simulate_half_duplex(st, rate, contention=cd)
        elif proto=="Daedaelus Fabric":
            sim = fabric_sim.Simulation()
            sim.run(until=st)
            # dump captured fabric events
            export_logs(os.path.join(os.getcwd(),"fabric_state.json"))
            self.status.config(text=f"Fabric sim complete → {os.getcwd()}/fabric_state.json")
            self.draw_network()
            return
        elif proto=="Automotive TSN":
            tsn_mod.env.run(until=st)
            self.status.config(text="TSN sim complete; check console")
            self.draw_network()
            return
        elif proto=="Active Building":
            building_mod.MainController(sim_duration=int(st),tick_interval=0.1).start()
            self.status.config(text="Building sim complete; logs & plots")
            self.draw_network()
            return
        else:
            self.status.config(text="Unknown protocol")
            return

        self.animate_log(log, ps, stats)
        if do_export:
            self.export_btn.config(state="normal")
            self.status.config(text=f"Done — throughput {stats['throughput']:.2f} pkt/s, avg lat {stats['avg_latency']:.2f}s")

    def animate_log(self, log, psize, stats=None):
        events = sorted(log, key=lambda e: e["time"])
        tmax   = max((e["time"] for e in events), default=1)
        if tmax <= 0: tmax = 1
        scale  = max(1, int(500/tmax))

        self.draw_network()
        self.frames.clear()

        def step(i):
            if i >= len(events):
                self.export_btn.config(state="normal")
                return
            ev = events[i]
            self.draw_network()
            if ev.get("src") and ev.get("dst"):
                self.draw_bits(ev["src"], ev["dst"], psize*8)
            elif ev.get("src"):
                self.draw_radial_bits(ev["src"], psize*8)
            self.canvas.update()
            self.capture_frame()
            self.root.after(scale, lambda: step(i+1))

        step(0)

    def draw_bits(self, src_name, dst_name, bits):
        src = next((r for r in self.routers if r['name']==src_name), None)
        dst = next((r for r in self.routers if r['name']==dst_name), None)
        if not src or not dst: return
        x0,y0 = src['x'], src['y']
        x1,y1 = dst['x'], dst['y']
        dx,dy = x1-x0, y1-y0
        n = min(bits//256, 30)
        for i in range(n):
            bp = (i+1)/n
            x = x0 + dx*bp
            y = y0 + dy*bp
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="yellow")

    def draw_radial_bits(self, src_name, bits):
        src = next((r for r in self.routers if r['name']==src_name), None)
        if not src: return
        x0,y0 = src['x'], src['y']
        n = min(bits//256, 30)
        for _ in range(n):
            ang = random.uniform(0, 2*pi)
            x = x0 + cos(ang)*20
            y = y0 + sin(ang)*20
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="yellow")

    def capture_frame(self):
        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        self.frames.append(img)

    def export_logs(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path: return
        export_logs(path)
        messagebox.showinfo("Export", f"Logs exported to {path}")

async def main():
    root = tk.Tk()
    app  = SimulationFramework(root)

    async def run_tk():
        while True:
            root.update()
            await asyncio.sleep(0.01)

    async def server(ws, path):
        async for _ in ws: pass

    srv = websockets.serve(server, 'localhost', 3000)
    await asyncio.gather(srv, run_tk())

if __name__=="__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")