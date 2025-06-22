#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daedaelus Log Visualizer 3: Comprehensive System Performance Analysis
----------------------------------------------------------------------
This script provides a computational model of network performance and system
behavior by analyzing a collection of simulation logs. It generates multiple
types of visualizations:

1. For network-level logs:
   a. An aggregate plot of "Throughput vs. Offered Load (Elbow Analysis)".
   b. An interactive, multi-dimensional parallel coordinates plot.
   c. A "Fitness over Iterations" plot analyzing performance trends.
   d. A "Performance Variance" plot analyzing the trade-off between throughput and collisions.
   e. "Signal Analysis" plots for packet latency and jitter.

2. For agent-based logs (e.g., Active Building): It runs a dedicated,
   self-contained agent simulation to produce a summary plot.

This toolset embodies the Daedaelus philosophy of providing rich, verifiable
insights into complex system dynamics from multiple analytical perspectives.

Usage:
  python log_visualizer_3.py [path/to/logs/directory]
"""

import json
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import random
import threading
import queue
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ========== AGENT-BASED SIMULATION (Active Building) ==========
# This section is a self-contained module for simulating and plotting
# the "Active Building" scenario, triggered when corresponding logs are found.


class Agent(threading.Thread):
    def __init__(self, name, sim_duration, tick_interval=0.01):
        super().__init__()
        self.name, self.daemon, self.sim_duration, self.tick_interval = name, True, sim_duration, tick_interval
        self.state, self.logs, self.time, self._stats = {}, [], 0, []
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set() and self.time < self.sim_duration:
            self.step()
            self.time += 1
            time.sleep(self.tick_interval)

    def step(self): pass
    def stop(self): self._stop.set()
    def record_stat(self, d): self._stats.append(d)
    def get_stats(self): return self._stats


def simulate_sensor(mean, stddev, minval, maxval): return min(
    max(random.gauss(mean, stddev), minval), maxval)


class HVACAgent(Agent):
    def __init__(self, d): super().__init__("HVAC", d); self.state = {
        "temperature": 22.0, "humidity": 45.0, "co2": 500.0}

    def step(self):
        self.state["temperature"] += simulate_sensor(0, 0.2, -0.5, 0.5)
        self.state["humidity"] += simulate_sensor(0, 0.5, -1, 1)
        self.state["co2"] += simulate_sensor(0, 5, -20, 20)
        self.record_stat(dict(time=self.time, **self.state))


class LightingAgent(Agent):
    def __init__(self, d, r=("Hallway", "Office", "Lab")): super().__init__(
        "Lighting", d); self.rooms, self.state, self.presence = list(r), {n: "off" for n in r}, {n: False for n in r}

    def step(self):
        for room in self.rooms:
            if random.random() < 0.1:
                self.presence[room] = not self.presence[room]
            self.state[room] = "on" if self.presence[room] else "off"
        self.record_stat(dict(time=self.time, **self.state))


class LiftAgent(Agent):
    def __init__(self, d, f=4): super().__init__("Lift", d); self.n_floors, self.state, self.requests = f, {
        "current_floor": 0, "moving": False}, queue.Queue()

    def step(self):
        if random.random() < 0.2:
            self.requests.put(random.randint(0, self.n_floors-1))
        if not self.state["moving"] and not self.requests.empty():
            if self.requests.get() != self.state["current_floor"]:
                self.state["moving"] = True
        if self.state["moving"]:
            self.state["current_floor"] = (
                self.state["current_floor"] + 1) % self.n_floors
            self.state["moving"] = False
        self.record_stat(dict(time=self.time, **self.state))


class SecurityAgent(Agent):
    def __init__(self, d): super().__init__(
        "Security", d); self.state = {"alarm": False}
    def step(self): self.state["alarm"] = random.random(
    ) < 0.05; self.record_stat(dict(time=self.time, **self.state))


class SmartEnergyAgent(Agent):
    def __init__(self, d): super().__init__("SmartEnergy", d); self.state = {
        "solar_kw": 0.0, "battery_kwh": 10.0, "load_kw": 1.0}

    def step(self):
        self.state["solar_kw"] = max(
            0.0, 5.0 * (1+0.8*random.random())*max(0, (1-abs(self.time-50)/50)))
        self.state["load_kw"] = simulate_sensor(1.5, 0.5, 0.5, 3.0)
        net = self.state["solar_kw"] - self.state["load_kw"]
        self.state["battery_kwh"] = min(
            max(self.state["battery_kwh"] + net*0.1, 0), 20)
        self.record_stat(dict(time=self.time, **self.state))


def run_and_plot_active_building(output_path, sim_duration=100, tick_interval=0.05):
    agents = [HVACAgent(sim_duration), LightingAgent(sim_duration), LiftAgent(
        sim_duration), SecurityAgent(sim_duration), SmartEnergyAgent(sim_duration)]
    for agent in agents:
        agent.start()
    for agent in agents:
        agent.join()
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Dædælus Active Building Simulation Summary", fontsize=16)
    axes = axes.flatten()
    stats = {a.name: a.get_stats() for a in agents}
    t = [x["time"] for x in stats["HVAC"]]
    axes[0].plot(t, [x["temperature"]
                 for x in stats["HVAC"]], label="Temp (°C)")
    axes[0].plot(t, [x["humidity"]
                 for x in stats["HVAC"]], label="Humidity (%)")
    axes[0].set_title("HVAC Environment")
    for room in ["Hallway", "Office", "Lab"]:
        axes[1].plot(
            t, [1 if x[room] == "on" else 0 for x in stats["Lighting"]], label=f"{room}")
    axes[1].set_title("Lighting On/Off")
    axes[2].plot([x["time"] for x in stats["Lift"]], [x["current_floor"]
                 for x in stats["Lift"]], label="Floor")
    axes[2].set_title("Lift Position")
    axes[3].plot([x["time"] for x in stats["Security"]], [
                 1 if x["alarm"] else 0 for x in stats["Security"]], label="Alarm", c='r')
    axes[3].set_title("Security Alarm")
    axes[4].plot([x["time"] for x in stats["SmartEnergy"]], [x["solar_kw"]
                 for x in stats["SmartEnergy"]], label="Solar kW")
    axes[4].plot([x["time"] for x in stats["SmartEnergy"]], [x["battery_kwh"]
                 for x in stats["SmartEnergy"]], label="Battery kWh")
    axes[4].plot([x["time"] for x in stats["SmartEnergy"]], [x["load_kw"]
                 for x in stats["SmartEnergy"]], label="Load kW")
    axes[4].set_title("Smart Energy System")
    axes[5].axis('off')
    [ax.legend() for ax in axes[:5]]
    [ax.grid(True, ls='--') for ax in axes[:5]]
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"   -> Active Building plot saved to: {output_path}")

# ========== NETWORK LOG PARSING AND PLOTTING ==========


def parse_log_for_metrics(log_path):
    log_data = []
    try:
        with open(log_path, 'r') as f:
            content = f.read()
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(content.strip()):
                obj, end_pos = decoder.raw_decode(content, pos)
                log_data.extend(obj if isinstance(obj, list) else [obj])
                pos = end_pos
                while pos < len(content) and content[pos].isspace():
                    pos += 1
    except Exception:
        return None
    params = next((i.get("params", {}) for i in log_data if isinstance(
        i, dict) and i.get("event") == "simulation_start"), {})
    if not params:
        return None
    p_name = params.get("protocol", "Unknown")
    events = sorted([e for e in log_data if isinstance(e, dict)
                    and e.get("event") == "end_tx"], key=lambda x: x['time'])
    success = sum(1 for e in events if e.get("success"))
    failure = len(events) - success
    total = len(events)
    metrics = {"protocol": p_name, "num_nodes": params.get("num_nodes"), "bandwidth_bps": params.get(
        "bandwidth_bps"), "data_size": params.get("data_size"), "arrival_rate": params.get("arrival_rate"), "events": events}
    if total > 0:
        metrics.update({"offered_load": params.get("num_nodes", 0)*params.get("arrival_rate", 0),
                       "achieved_throughput": success/total, "collision_rate": failure/total})
    return metrics


def create_throughput_vs_load_plot(throughput_data, output_path):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 8))
    for protocol_name, data_points in throughput_data.items():
        if data_points:
            data_points.sort()
            loads, throughputs = zip(*data_points)
            plt.plot(loads, throughputs, marker='o',
                     linestyle='-', label=f'{protocol_name}')
    plt.xlabel("Offered Load (λ * N)")
    plt.ylabel("Achieved Throughput")
    plt.title("Throughput vs. Offered Load (Elbow Analysis)")
    plt.legend()
    plt.grid(True)
    plt.ylim(bottom=0, top=1.0)
    plt.xlim(left=0)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"  -> Summary contention plot saved to: {output_path}")


def create_parallel_coordinates_plot(df, output_path):
    if df.empty:
        return
    dimensions = [{'label': 'Nodes', 'values': df['num_nodes']}, {'label': 'Arrival Rate', 'values': df['arrival_rate']}, {'label': 'Bandwidth (Gbps)', 'values': df['bandwidth_bps']/1e9}, {'label': 'Data Size (bytes)', 'values': df['data_size']}, {
        'label': 'Offered Load', 'values': df['offered_load']}, {'label': 'Collision Rate', 'values': df['collision_rate']}, {'label': 'Throughput', 'values': df['achieved_throughput'], 'range': [0, 1]}]
    fig = go.Figure(data=go.Parcoords(line=dict(color=df['achieved_throughput'], colorscale='Viridis', showscale=True, colorbar={
                    'title': 'Throughput'}), dimensions=dimensions))
    fig.update_layout(title={
                      'text': "Protocol Performance: A Multi-Dimensional Analysis", 'y': 0.95, 'x': 0.5})
    fig.write_html(output_path)
    print(f"  -> Parallel coordinates plot saved to: {output_path}")


def create_fitness_plots(protocol_name, events, output_path):
    if not events:
        return
    iterations = np.arange(1, len(events)+1)
    outcomes = np.array([1 if e.get('success') else 0 for e in events])
    cumulative_success_rate = np.cumsum(outcomes)/iterations
    window_size = max(1, len(events)//10)
    moving_avg_success = np.convolve(
        outcomes, np.ones(window_size), 'valid')/window_size
    collision_rate = np.cumsum(1-outcomes)/iterations
    knapsack_fitness = cumulative_success_rate*(1-collision_rate)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 15), sharex=True)
    fig.suptitle(f"Protocol Fitness Analysis: {protocol_name}", fontsize=16)
    ax1.plot(iterations, cumulative_success_rate,
             label='Cumulative Success Rate', color='green')
    ax1.set_title('Fitness over Iterations for Count Ones (Throughput)')
    ax1.set_ylabel('Fitness (Success Rate)')
    ax2.plot(range(window_size-1, len(events)), moving_avg_success,
             label=f'Success Rate (Window={window_size})', color='purple')
    ax2.set_title('Fitness over Iterations for Four Peaks (Stability)')
    ax2.set_ylabel('Fitness (Moving Avg)')
    ax3.plot(iterations, knapsack_fitness,
             label='Throughput * (1-Collision Rate)', color='orange')
    ax3.set_title('Fitness over Iterations for Knapsack Problem (Balanced)')
    ax3.set_xlabel('Iterations (Tx Events)')
    ax3.set_ylabel('Fitness (Composite Score)')
    for ax in [ax1, ax2, ax3]:
        ax.legend()
        ax.grid(True, linestyle='--')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"   -> Fitness analysis plot saved to: {output_path}")


def create_performance_variance_plot(protocol_name, events, output_path):
    """Generates a plot comparing throughput and collision rate, inspired by budget variance analysis."""
    if not events:
        return
    times = [e['time'] for e in events]
    successes = np.cumsum([1 if e.get('success') else 0 for e in events])
    collisions = np.cumsum([1 if not e.get('success') else 0 for e in events])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=successes, name='Cumulative Throughput',
                  mode='lines+markers', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=times, y=collisions, name='Cumulative Collisions',
                  mode='lines+markers', line=dict(color='red')))

    fig.update_layout(title=f"Performance Variance Analysis: {protocol_name}",
                      xaxis_title="Time (s)", yaxis_title="Cumulative Count", legend_title="Metric")
    fig.write_html(output_path)
    print(f"   -> Performance variance plot saved to: {output_path}")


def create_signal_analysis_plots(protocol_name, events, output_path):
    """Generates plots for latency and jitter analysis, inspired by array analysis."""
    if not events:
        return

    latencies = [e['time'] - next((s['time'] for s in events if s.get('pkt_id') == e.get(
        'pkt_id') and s.get('event') == 'start_tx'), e['time']) for e in events]
    arrival_times = [e['time'] for e in events]
    inter_arrivals = np.diff(arrival_times, prepend=arrival_times[0])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f"Signal Analysis for {protocol_name}", fontsize=16)

    ax1.plot(arrival_times, latencies, marker='.', linestyle='-',
             color='teal', label='Latency per Packet')
    ax1.set_title("Linear Array Analysis (Packet Latency over Time)")
    ax1.set_ylabel("Latency (s)")
    ax1.grid(True, ls='--')

    ax2.plot(arrival_times, inter_arrivals, marker='.', linestyle='-',
             color='purple', label='Inter-Arrival Time')
    ax2.set_title("Curvilinear Array Analysis (Packet Jitter)")
    ax2.set_ylabel("Time Between Packets (s)")
    ax2.set_xlabel("Time (s)")
    ax2.grid(True, ls='--')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path)
    plt.close(fig)
    print(f"   -> Signal analysis plot saved to: {output_path}")

# ========== MAIN EXECUTION BLOCK ==========


def main():
    parser = argparse.ArgumentParser(
        description="Daedaelus Log Visualizer 3", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("log_directory", nargs='?',
                        default="Logs", help="Path to the log directory.")
    args = parser.parse_args()
    log_dir, plot_root_dir = args.log_directory, "plots"
    if not os.path.isdir(log_dir):
        return print(f"Error: Log directory not found at '{log_dir}'")
    found_logs = [os.path.join(r, f) for r, _, files in os.walk(
        log_dir) for f in files if f.endswith(".json")]
    if not found_logs:
        return print(f"No .json logs found in '{log_dir}'.")

    print(
        f"Found {len(found_logs)} log files. Aggregating data for visualizations...")
    os.makedirs(plot_root_dir, exist_ok=True)

    network_metrics_list, active_building_logs = [], []
    for log_path in found_logs:
        metrics = parse_log_for_metrics(log_path)
        if metrics:
            metrics['log_path'] = log_path
            if "active building" in metrics["protocol"].lower():
                active_building_logs.append(log_path)
            else:
                network_metrics_list.append(metrics)

    if network_metrics_list:
        # Generate plots that aggregate data across all network logs
        throughput_summary = defaultdict(list)
        for m in network_metrics_list:
            if "achieved_throughput" in m:
                throughput_summary[m["protocol"]].append(
                    (m["offered_load"], m["achieved_throughput"]))
        if throughput_summary:
            print("\n--- Generating Aggregate Network Performance Plots ---")
            create_throughput_vs_load_plot(throughput_summary, os.path.join(
                plot_root_dir, "throughput_vs_load_summary.png"))
        df_multi = pd.DataFrame(
            [m for m in network_metrics_list if m.get("num_nodes")])
        if not df_multi.empty:
            create_parallel_coordinates_plot(df_multi, os.path.join(
                plot_root_dir, "protocol_multidimensional_analysis.html"))

        # Generate per-log analysis plots
        print("\n--- Generating Per-Log Analysis Plots ---")
        for metrics in network_metrics_list:
            print(
                f"  Processing plots for {os.path.basename(metrics['log_path'])}...")
            relative_path = os.path.relpath(metrics['log_path'], log_dir)
            plot_dir = os.path.join(
                plot_root_dir, os.path.dirname(relative_path))
            os.makedirs(plot_dir, exist_ok=True)
            base_name = os.path.basename(relative_path).replace('.json', '')
            create_fitness_plots(metrics["protocol"], metrics["events"], os.path.join(
                plot_dir, f"fitness_analysis_{base_name}.png"))
            create_performance_variance_plot(metrics["protocol"], metrics["events"], os.path.join(
                plot_dir, f"variance_analysis_{base_name}.html"))
            create_signal_analysis_plots(metrics["protocol"], metrics["events"], os.path.join(
                plot_dir, f"signal_analysis_{base_name}.png"))

    if active_building_logs:
        print("\n--- Generating Active Building Simulation Plots ---")
        for log_path in active_building_logs:
            relative_path = os.path.relpath(log_path, log_dir)
            plot_dir = os.path.join(
                plot_root_dir, os.path.dirname(relative_path))
            os.makedirs(plot_dir, exist_ok=True)
            base_name = os.path.basename(relative_path).replace('.json', '')
            output_path = os.path.join(
                plot_dir, f"active_building_{base_name}.png")
            run_and_plot_active_building(output_path)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
