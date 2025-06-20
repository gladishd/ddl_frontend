"""
Dædælus Active Building Agent-Based Simulation
Version: 1.0
Author: (see code history)
Formal agent-based simulation of an Active Building, with multiple subsystems (HVAC, Lighting, Lift, Security, Smart Energy).
This script is designed to demonstrate autonomous agent control, logging, event-driven communication, and 
research-grade timeline emergence, as specified in the Active_Building_Model documentation.

- Each subsystem is a Python thread/agent with simulated sensors/actuators.
- The MainController coordinates actions and logs events.
- Results are plotted and logged.
- No hardware dependencies; all logic is pure Python.

--- Foundations:
- Agent model and communication inspired by Metcalfe & Boggs (1976) style distributed control
- Dædælus critique: Each subsystem's inability to maintain full "epistemic state" under contention is manifest as lost/colliding events
"""

import threading
import queue
import time
import logging
import os
import random
from datetime import datetime
import matplotlib.pyplot as plt

# ========== LOGGING AND FILE MANAGEMENT ==========

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_today_logfile():
    today = datetime.now().strftime("%Y_%m_%d")
    log_dir = "Logs"
    ensure_dir(log_dir)
    return os.path.join(log_dir, f"log_{today}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(get_today_logfile(), mode='a'),
        logging.StreamHandler()
    ]
)

def log_event(level, message):
    {
        "debug": logging.debug,
        "info": logging.info,
        "warning": logging.warning,
        "error": logging.error
    }.get(level, logging.info)(message)

# ========== AGENT BASE CLASS ==========

class Agent(threading.Thread):
    """
    Abstract agent (subsystem).
    Each agent runs in its own thread, processes events from its input queue,
    simulates its own sensors/actuators, and communicates via the event bus.
    """
    def __init__(self, name, event_bus, sim_duration, tick_interval=1.0):
        super().__init__()
        self.name = name
        self.event_bus = event_bus
        self.daemon = True
        self.state = {}
        self.logs = []
        self.sim_duration = sim_duration
        self.tick_interval = tick_interval
        self.time = 0
        self._stop = threading.Event()
        self._stats = []

    def run(self):
        while not self._stop.is_set() and self.time < self.sim_duration:
            self.step()
            self.time += 1
            time.sleep(self.tick_interval)

    def step(self):
        """Override this in subclasses to implement per-tick agent logic."""
        pass

    def stop(self):
        self._stop.set()

    def log(self, msg):
        entry = f"[{self.name}][T={self.time}] {msg}"
        log_event("info", entry)
        self.logs.append((self.time, msg))

    def record_stat(self, d):
        """For statistics/plotting."""
        self._stats.append(d)

    def get_stats(self):
        return self._stats

# ========== SENSOR/ACTUATOR SIMULATION HELPERS ==========

def simulate_sensor(mean, stddev, minval, maxval):
    return min(max(random.gauss(mean, stddev), minval), maxval)

# ========== SUBSYSTEM AGENTS ==========

class HVACAgent(Agent):
    """Simulates HVAC (air quality, temp, humidity, simple rule-based control)."""
    def __init__(self, event_bus, sim_duration):
        super().__init__("HVAC", event_bus, sim_duration)
        self.state = {
            "temperature": 22.0, # degrees C
            "humidity": 20.0,    # percent
            "co2": 500.0,        # ppm
            "mode": "idle"
        }

    def step(self):
        # Simulate environment drift
        self.state["temperature"] += simulate_sensor(0.0, 0.2, -0.5, 0.5)
        self.state["humidity"] += simulate_sensor(0.0, 0.5, -1, 1)
        self.state["co2"] += simulate_sensor(0.0, 5, -20, 20)
        # Clamp values
        self.state["temperature"] = min(max(self.state["temperature"], 15), 30)
        self.state["humidity"] = min(max(self.state["humidity"], 10), 50)
        self.state["co2"] = min(max(self.state["co2"], 350), 2000)
        # Control logic: respond to over-threshold values
        actions = []
        if self.state["co2"] >= 800:
            self.state["mode"] = "air_circulation"
            actions.append("CO₂ high, starting air circulation.")
        elif self.state["temperature"] > 24:
            self.state["mode"] = "cooling"
            actions.append("Temp high, starting cooling.")
        elif self.state["temperature"] < 20:
            self.state["mode"] = "heating"
            actions.append("Temp low, starting heating.")
        elif self.state["humidity"] > 35:
            self.state["mode"] = "dehumidify"
            actions.append("Humidity high, starting dehumidification.")
        elif self.state["humidity"] < 15:
            self.state["mode"] = "humidify"
            actions.append("Humidity low, starting humidification.")
        else:
            self.state["mode"] = "idle"

        for action in actions:
            self.log(action)

        # Record for plotting
        self.record_stat(dict(time=self.time, **self.state))

class LightingAgent(Agent):
    """Simulates Lighting: rooms, relays, user presence, scheduling."""
    def __init__(self, event_bus, sim_duration, room_names=("Hallway","Office","Lab")):
        super().__init__("Lighting", event_bus, sim_duration)
        self.room_names = list(room_names)
        self.state = {name: "off" for name in self.room_names}
        self.presence = {name: False for name in self.room_names}

    def step(self):
        # Simulate random room usage (occupancy triggers)
        for room in self.room_names:
            if random.random() < 0.1:  # 10% chance presence changes
                self.presence[room] = not self.presence[room]
            # Lights on if presence, else off
            old = self.state[room]
            self.state[room] = "on" if self.presence[room] else "off"
            if old != self.state[room]:
                action = f"Room '{room}' presence={'yes' if self.presence[room] else 'no'} -> light {self.state[room]}"
                self.log(action)
        # Record state for plotting
        stat = dict(time=self.time)
        stat.update(self.state)
        self.record_stat(stat)

class LiftAgent(Agent):
    """Simulates Lift/Elevator, random requests, security overrides."""
    def __init__(self, event_bus, sim_duration, n_floors=4):
        super().__init__("Lift", event_bus, sim_duration)
        self.n_floors = n_floors
        self.state = {
            "current_floor": 0,
            "direction": "idle",
            "moving": False,
        }
        self.requests = queue.Queue()

    def step(self):
        # Randomly generate floor requests
        if random.random() < 0.2:
            requested = random.randint(0, self.n_floors-1)
            self.requests.put(requested)
            self.log(f"New floor request: {requested}")

        # Process request if idle
        if not self.state["moving"] and not self.requests.empty():
            target = self.requests.get()
            if target != self.state["current_floor"]:
                self.state["direction"] = "up" if target > self.state["current_floor"] else "down"
                self.state["moving"] = True
                self.log(f"Moving from {self.state['current_floor']} to {target}")
            else:
                self.log(f"Already at floor {target}")

        # Move if moving
        if self.state["moving"]:
            if self.state["direction"] == "up":
                self.state["current_floor"] += 1
            elif self.state["direction"] == "down":
                self.state["current_floor"] -= 1
            self.log(f"Arrived at floor {self.state['current_floor']}")
            self.state["moving"] = False
            self.state["direction"] = "idle"

        # Record state
        self.record_stat(dict(time=self.time, **self.state))

class SecurityAgent(Agent):
    """Simulates Security subsystem (alarm triggers, logging, stub actions)."""
    def __init__(self, event_bus, sim_duration):
        super().__init__("Security", event_bus, sim_duration)
        self.state = {
            "alarm": False,
            "last_event": ""
        }

    def step(self):
        # Random alarm trigger
        if random.random() < 0.05:
            self.state["alarm"] = True
            self.state["last_event"] = "intrusion"
            self.log("Alarm triggered: intrusion detected")
        else:
            self.state["alarm"] = False
            self.state["last_event"] = ""
        self.record_stat(dict(time=self.time, **self.state))

class SmartEnergyAgent(Agent):
    """Simulates smart energy subsystem (solar generation, battery, load)."""
    def __init__(self, event_bus, sim_duration):
        super().__init__("SmartEnergy", event_bus, sim_duration)
        self.state = {
            "solar_kw": 0.0,
            "battery_kwh": 10.0,
            "load_kw": 1.0,
        }

    def step(self):
        # Solar output simulates daily sinusoid
        solar = max(0.0, 5.0 * (1 + 0.8 * random.random()) * max(0, (1 - abs(self.time-50)/50)))
        self.state["solar_kw"] = solar
        # Random load
        self.state["load_kw"] = simulate_sensor(1.5, 0.5, 0.5, 3.0)
        # Battery charge/discharge
        net = self.state["solar_kw"] - self.state["load_kw"]
        self.state["battery_kwh"] = min(max(self.state["battery_kwh"] + net*0.1, 0), 20)
        self.record_stat(dict(time=self.time, **self.state))
        if net > 0:
            self.log(f"Net positive: charging battery by {net*0.1:.2f} kWh")
        elif net < 0:
            self.log(f"Net negative: discharging battery by {abs(net*0.1):.2f} kWh")

# ========== MAIN CONTROLLER ==========

class MainController:
    """
    Orchestrates the simulation, initializes agents, event bus, handles logging/plots.
    """
    def __init__(self, sim_duration=100, tick_interval=0.1):
        self.sim_duration = sim_duration
        self.tick_interval = tick_interval
        self.event_bus = queue.Queue()  # Not used in this stub, but could be expanded for message passing
        # Initialize agents
        self.agents = [
            HVACAgent(self.event_bus, sim_duration),
            LightingAgent(self.event_bus, sim_duration),
            LiftAgent(self.event_bus, sim_duration),
            SecurityAgent(self.event_bus, sim_duration),
            SmartEnergyAgent(self.event_bus, sim_duration)
        ]

    def start(self):
        log_event("info", "==== Dædælus Active Building Simulation Started ====")
        for agent in self.agents:
            agent.start()
        # Wait for all agents to finish
        for agent in self.agents:
            agent.join()
        log_event("info", "==== Dædælus Active Building Simulation Complete ====")

    def plot_results(self):
        # HVAC
        hvac_stats = [a for a in self.agents if a.name == "HVAC"][0].get_stats()
        lighting_stats = [a for a in self.agents if a.name == "Lighting"][0].get_stats()
        lift_stats = [a for a in self.agents if a.name == "Lift"][0].get_stats()
        sec_stats = [a for a in self.agents if a.name == "Security"][0].get_stats()
        energy_stats = [a for a in self.agents if a.name == "SmartEnergy"][0].get_stats()

        plt.figure(figsize=(16,12))
        plt.suptitle("Dædælus Active Building Simulation Summary", fontsize=16)

        # HVAC: Temp, CO₂, Humidity
        plt.subplot(2,3,1)
        t = [x["time"] for x in hvac_stats]
        plt.plot(t, [x["temperature"] for x in hvac_stats], label="Temp (°C)")
        plt.plot(t, [x["co2"] for x in hvac_stats], label="CO₂ (ppm)")
        plt.plot(t, [x["humidity"] for x in hvac_stats], label="Humidity (%)")
        plt.title("HVAC Environment")
        plt.xlabel("Time")
        plt.legend()

        # Lighting: Room States
        plt.subplot(2,3,2)
        for room in ["Hallway","Office","Lab"]:
            plt.plot(t, [1 if x[room]=="on" else 0 for x in lighting_stats], label=f"{room}")
        plt.title("Lighting On/Off")
        plt.xlabel("Time")
        plt.ylabel("State")
        plt.legend()

        # Lift: Floor position
        plt.subplot(2,3,3)
        plt.plot([x["time"] for x in lift_stats], [x["current_floor"] for x in lift_stats], label="Floor")
        plt.title("Lift Position Over Time")
        plt.xlabel("Time")
        plt.ylabel("Floor")
        plt.legend()

        # Security: Alarm events
        plt.subplot(2,3,4)
        plt.plot([x["time"] for x in sec_stats], [1 if x["alarm"] else 0 for x in sec_stats], label="Alarm")
        plt.title("Security Alarm Triggered")
        plt.xlabel("Time")
        plt.ylabel("Alarm (1=On)")
        plt.legend()

        # SmartEnergy: Battery, Solar, Load
        plt.subplot(2,3,5)
        plt.plot([x["time"] for x in energy_stats], [x["solar_kw"] for x in energy_stats], label="Solar kW")
        plt.plot([x["time"] for x in energy_stats], [x["battery_kwh"] for x in energy_stats], label="Battery kWh")
        plt.plot([x["time"] for x in energy_stats], [x["load_kw"] for x in energy_stats], label="Load kW")
        plt.title("Smart Energy System")
        plt.xlabel("Time")
        plt.legend()

        plt.tight_layout(rect=[0,0,1,0.95])
        plt.show()

# ========== ENTRY POINT ==========

if __name__ == "__main__":
    controller = MainController(sim_duration=100, tick_interval=0.05)
    controller.start()
    controller.plot_results()
