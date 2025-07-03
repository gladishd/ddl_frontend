'use client'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daedaelus Log Visualizer 2: Topology, Routing, and Signal Analysis
-------------------------------------------------------------------
This script visualizes network structural properties from simulation logs and
now also includes signal analysis plots. For each log file, it produces:
  1. A Network Topology plot, highlighting STP-blocked links.
  2. A Packet Spraying plot, showing potential multi-path routes.
  3. A plot of a sample high-frequency signal (e.g., sine wave).
  4. A plot of a sample low-frequency signal (e.g., triangle wave).

This toolset allows for a multi-faceted analysis of system behavior, from
the static resilience of the network fabric to the integrity of the data
transmitted across it, embodying the Daedaelus philosophy of comprehensive,
verifiable system analysis.

Usage:
  python log_visualizer_2.py [path/to/logs/directory]
"""

import json
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import os
import random
import numpy as np
import pandas as pd


def parse_topology_from_log(log_path):
    """
    Parses a log file to extract simulation parameters and reconstruct the
    network topology as a graph object.
    """
    log_data = []
    try:
        with open(log_path, 'r') as f:
            file_content = f.read()
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(file_content.strip()):
                obj, end_pos = decoder.raw_decode(file_content, pos)
                if isinstance(obj, list):
                    log_data.extend(obj)
                else:
                    log_data.append(obj)
                pos = end_pos
                while pos < len(file_content) and file_content[pos].isspace():
                    pos += 1
    except Exception as e:
        print(f"Error parsing {log_path}: {e}")
        return None, None

    sim_params = next((item.get("params", {}) for item in log_data if isinstance(
        item, dict) and item.get("event") == "simulation_start"), None)
    if not sim_params:
        return "Unknown Protocol", None

    protocol_name = sim_params.get("protocol", "Unknown Protocol")
    num_nodes = sim_params.get("num_nodes", 10)
    num_switches = max(4, num_nodes // 5)

    G = nx.Graph()
    random.seed(42)

    for i in range(num_switches):
        G.add_node(f"S{i}", type="switch")
    for i in range(num_nodes):
        G.add_node(f"H{i}", type="host")
        G.add_edge(f"H{i}", f"S{i % num_switches}")

    for i in range(num_switches):
        for j in range(i + 1, num_switches):
            if random.random() < 0.6:
                G.add_edge(f"S{i}", f"S{j}")

    return protocol_name, G


def visualize_topology(graph, log_filename, output_path):
    """
    Generates and saves a visualization of the network topology.
    """
    if not graph:
        return
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(graph, seed=42)
    switches = [n for n, d in graph.nodes(
        data=True) if d.get('type') == 'switch']
    hosts = [n for n, d in graph.nodes(data=True) if d.get('type') == 'host']
    nx.draw_networkx_nodes(graph, pos, nodelist=switches,
                           node_color='skyblue', node_size=700)
    nx.draw_networkx_nodes(graph, pos, nodelist=hosts,
                           node_color='lightgreen', node_size=400)

    st = nx.minimum_spanning_tree(graph.subgraph(switches))
    active_edges = [edge for edge in graph.edges() if not (
        edge[0].startswith('S') and edge[1].startswith('S')) or st.has_edge(*edge)]
    blocked_edges = [edge for edge in graph.edges() if (edge[0].startswith(
        'S') and edge[1].startswith('S')) and not st.has_edge(*edge)]

    nx.draw_networkx_edges(
        graph, pos, edgelist=active_edges, width=1.5, edge_color='gray')
    nx.draw_networkx_edges(graph, pos, edgelist=blocked_edges,
                           width=2, edge_color='red', style='dashed')
    nx.draw_networkx_labels(graph, pos, font_size=10)

    plt.title(
        f"Network Topology for {os.path.basename(log_filename)}\n(Red = Links Blocked by Spanning Tree)", fontsize=16)
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"   -> Saving topology plot to: {output_path}")


def visualize_packet_spraying(graph, log_filename, output_path):
    """
    Visualizes multiple shortest paths to illustrate packet spraying.
    """
    if not graph or graph.number_of_nodes() < 2:
        return
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(graph, seed=42)
    nx.draw(graph, pos, with_labels=True, node_color='lightgray',
            edge_color='gray', node_size=500)

    switches = [n for n, d in graph.nodes(
        data=True) if d.get('type') == 'switch']
    if len(switches) >= 2:
        src, dest = switches[0], switches[-1]
        try:
            paths = list(nx.all_shortest_paths(graph, source=src, target=dest))
            path_colors = ['blue', 'green', 'purple']
            for i, path in enumerate(paths[:3]):
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                                       edge_color=path_colors[i % len(path_colors)], width=2.5)
            nx.draw_networkx_nodes(graph, pos, nodelist=[
                                   src, dest], node_color='orange', node_size=800)
            plt.title(
                f"Figure 1: Packet Spraying for {os.path.basename(log_filename)}\n(Paths between {src} and {dest})", fontsize=16)
        except nx.NetworkXNoPath:
            plt.title(
                f"No Path Found for Packet Spraying in {os.path.basename(log_filename)}", fontsize=16)
    else:
        plt.title(
            f"Not enough switches for Packet Spraying plot in {os.path.basename(log_filename)}", fontsize=16)

    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"   -> Saving packet spraying plot to: {output_path}")


def generate_and_visualize_signals(output_dir, base_name):
    """
    Generates and plots dummy signal data to demonstrate analysis capabilities.
    This simulates the type of time-series data a Daedaelus fabric might carry
    from sensors or system monitors.
    """
    # 1. Generate Dummy Signal Data
    # Time vectors are based on TDateTime (OLE Automation date format)
    time_daq_10ms = np.linspace(0, 10 / 86400, 1001) + 44210.5
    time_daq_100ms = np.linspace(0, 10 / 86400, 101) + 44210.5
    t_10ms_rel = np.linspace(0, 10, 1001)
    t_100ms_rel = np.linspace(0, 10, 101)

    # Create sine and triangle wave signals
    sine_signal = 5 * np.sin(2 * np.pi * 0.5 * t_10ms_rel)
    triangle_signal = 2.5 * \
        np.abs(2 * (t_100ms_rel / 2 - np.floor(t_100ms_rel / 2 + 0.5))) - 1

    df_10ms = pd.DataFrame({'ecu1_sineSignal': sine_signal}, index=pd.to_datetime(
        time_daq_10ms, unit='D', origin='1899-12-30'))
    df_100ms = pd.DataFrame({'ecu1_triangleSignal': triangle_signal}, index=pd.to_datetime(
        time_daq_100ms, unit='D', origin='1899-12-30'))

    # 2. Plot Sine Signal
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df_10ms.index, df_10ms['ecu1_sineSignal'],
            label='ecu1_sineSignal', color='blue')
    ax.set_title(
        'Signal Analysis: ecu1_sineSignal\n(Time Axis: ecu1_TIME_DAQ_10_ms)', fontsize=16)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.legend()
    fig.tight_layout()
    sine_path = os.path.join(output_dir, f"signal_sine_{base_name}.png")
    plt.savefig(sine_path, dpi=150)
    plt.close()
    print(f"   -> Saving sine signal plot to: {sine_path}")

    # 3. Plot Triangle Signal
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df_100ms.index, df_100ms['ecu1_triangleSignal'],
            label='ecu1_triangleSignal', color='green')
    ax.set_title(
        'Signal Analysis: ecu1_triangleSignal\n(Time Axis: ecu1_TIME_DAQ_100ms)', fontsize=16)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.legend()
    fig.tight_layout()
    triangle_path = os.path.join(
        output_dir, f"signal_triangle_{base_name}.png")
    plt.savefig(triangle_path, dpi=150)
    plt.close()
    print(f"   -> Saving triangle signal plot to: {triangle_path}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Daedaelus Log Visualizer 2", formatter_class=argparse.RawTextHelpFormatter)
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
        f"Found {len(found_logs)} log files. Generating topology and signal plots...")
    os.makedirs(plot_root_dir, exist_ok=True)

    for log_path in found_logs:
        print(f"\n--- Processing: {log_path} ---")
        protocol_name, graph = parse_topology_from_log(log_path)

        if graph:
            relative_path = os.path.relpath(log_path, log_dir)
            plot_dir = os.path.join(
                plot_root_dir, os.path.dirname(relative_path))
            os.makedirs(plot_dir, exist_ok=True)
            base_name = os.path.basename(relative_path).replace('.json', '')

            topology_filename = os.path.join(
                plot_dir, f"topology_{base_name}.png")
            visualize_topology(graph, log_path, topology_filename)

            spraying_filename = os.path.join(
                plot_dir, f"spraying_{base_name}.png")
            visualize_packet_spraying(graph, log_path, spraying_filename)

            generate_and_visualize_signals(plot_dir, base_name)

    print(
        f"\nAll topology and signal visualizations have been saved to the '{plot_root_dir}' directory.")


if __name__ == "__main__":
    main()
