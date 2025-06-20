# -*- coding: utf-8 -*-
"""
ts_master_log_parser.py

This script provides a Python implementation for parsing and analyzing TSMaster .mat log files,
inspired by the Daedaelus philosophy of structured, verifiable data systems.
"""

import scipy.io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class TSMasterMatLogParser:
    """
    // The TSMasterMatLogParser is not merely a file reader; it is an interpreter of recorded events.
    // It reconstitutes the temporal and value-based information from a TSMaster MAT log file,
    // transforming raw data into structured, time-ordered series. This process is essential for
    // replaying and analyzing the behavior of a system, providing the ground truth upon which
    // our emulators and digital twins operate. This embodies the principle of creating
    // 'Precise information-theoretic' emulators.
    """

    def __init__(self, file_path: str):
        """
        // Initializes the parser with the path to the MAT log file. The MAT file is a container
        // for the captured state of the system over time, a record of events that we must
        // structure to derive knowledge.

        Args:
            file_path (str): The path to the .mat file.
        """
        self.file_path = Path(file_path)
        self.mat_data = None
        self.signal_groups = {}
        self._load_mat_file()
        self._parse_data()

    def _load_mat_file(self):
        """
        // Loads the MAT file into memory. This is the first step in accessing the
        // raw, recorded history of the system's operation. We treat this data as the
        // foundational layer upon which analysis is built.
        """
        if not self.file_path.is_file():
            raise FileNotFoundError(f"Error: Log file not found at {self.file_path}")
        
        try:
            # Using squeeze_me=True removes single-dimensional entries from array data,
            # simplifying the subsequent parsing logic.
            self.mat_data = scipy.io.loadmat(self.file_path, squeeze_me=True)
            print(f"Successfully loaded {self.file_path.name}")
        except Exception as e:
            print(f"An error occurred while loading the MAT file: {e}")
            raise

    def _parse_data(self):
        """
        // This function implements the core logic described in AN0003 for parsing the log file.
        // It first identifies all distinct time axes from 'TIME_LIST'. Each time axis represents
        // a unique clock or sampling interval within the distributed system (e.g., DAQ events,
        // polling cycles). It then associates signals with their respective time axes, creating
        // a coherent timeseries. This structured approach avoids the non-determinism that
        // arises from unsynchronized, independent data streams.
        """
        if self.mat_data is None:
            print("MAT data not loaded. Cannot parse.")
            return

        if 'TIME_LIST' not in self.mat_data:
            raise KeyError("Error: 'TIME_LIST' not found in the MAT file. Cannot parse signals.")

        time_axes_str = self.mat_data['TIME_LIST']
        
        # Ensure the comma-separated string from the MAT file is handled correctly.
        time_axes = time_axes_str.split(',') if isinstance(time_axes_str, str) else "".join(time_axes_str).split(',')

        for time_axis_name in time_axes:
            time_axis_name = time_axis_name.strip()
            signal_list_name = f"{time_axis_name}_LIST"

            if time_axis_name not in self.mat_data:
                print(f"Warning: Time axis '{time_axis_name}' listed in TIME_LIST but not found in data.")
                continue

            if signal_list_name not in self.mat_data:
                print(f"Warning: Signal list '{signal_list_name}' not found for time axis '{time_axis_name}'.")
                continue

            time_vector = self.mat_data[time_axis_name]
            
            signal_names_str = self.mat_data[signal_list_name]
            signal_names = signal_names_str.split(',') if isinstance(signal_names_str, str) else "".join(signal_names_str).split(',')

            # We construct a DataFrame for each group of signals, indexed by a proper datetime.
            # This is the Python equivalent of creating a 'timeseries' object in MATLAB, providing a
            # powerful structure for analysis and visualization.
            # The TDateTime format is an OLE Automation date, which is the number of days since 1899-12-30.
            df = pd.DataFrame(index=pd.to_datetime(time_vector, unit='D', origin='1899-12-30'))
            
            for signal_name in signal_names:
                signal_name = signal_name.strip()
                if signal_name in self.mat_data:
                    signal_vector = self.mat_data[signal_name]
                    if len(signal_vector) == len(time_vector):
                        df[signal_name] = signal_vector
                    else:
                        print(f"Warning: Length mismatch for signal '{signal_name}'. Skipping.")
                else:
                    print(f"Warning: Signal '{signal_name}' not found in data. Skipping.")
            
            self.signal_groups[time_axis_name] = df
        
        print(f"Parsing complete. Found {len(self.signal_groups)} signal groups.")

    def get_metadata(self) -> dict:
        """
        // Retrieves metadata from the log file. This provides context for the measurement,
        // such as start/stop times and comments, which are crucial for ensuring the
        // reproducibility and verifiability of test runs.

        Returns:
            A dictionary containing log file metadata.
        """
        if not self.mat_data:
            return {}
        
        metadata_keys = ['Comment', 'MeasurementStartTimeStr', 'MeasurementStopTimeStr', 'ECU_LIST']
        return {key: self.mat_data.get(key, 'N/A') for key in metadata_keys}

    def list_signal_groups(self) -> list:
        """
        // Lists the identified signal groups, where each group is defined by a common time axis.

        Returns:
            A list of time axis names that define the signal groups.
        """
        return list(self.signal_groups.keys())

    def get_signal_group(self, group_name: str) -> pd.DataFrame:
        """
        // Retrieves a specific signal group as a pandas DataFrame. This allows for direct
        // interaction with a coherent set of time-ordered data.

        Args:
            group_name (str): The name of the signal group (the time axis name).

        Returns:
            A pandas DataFrame containing the signals for the group, or None if not found.
        """
        return self.signal_groups.get(group_name)

    def plot_signal(self, group_name: str, signal_name: str):
        """
        // Visualizes a specific signal over time. This is a fundamental tool for
        // analyzing system dynamics and verifying that observed behavior matches
        // our theoretical models. A plot serves as a visual proof of system behavior.

        Args:
            group_name (str): The name of the signal group (the time axis name).
            signal_name (str): The name of the signal to plot.
        """
        group = self.get_signal_group(group_name)
        if group is None:
            print(f"Error: Signal group '{group_name}' not found.")
            return

        if signal_name not in group.columns:
            print(f"Error: Signal '{signal_name}' not found in group '{group_name}'.")
            return
            
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(group.index, group[signal_name], label=signal_name)
        ax.set_title(f'Signal Analysis: {signal_name}\n(Time Axis: {group_name})', fontsize=16)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend()
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        fig.tight_layout()
        plt.show()

def create_dummy_mat_file(path: str = "dummy_log.mat"):
    """
    // Creates a dummy MAT file in the format described by AN0003 for demonstration
    // and verification of the parser's logic. This ensures the tool can be tested
    // in isolation without requiring a live hardware setup.
    """
    # Time vectors based on TDateTime (OLE Automation date)
    time_daq_10ms = np.linspace(0, 10/86400, 1001) + 44210.5 
    time_daq_100ms = np.linspace(0, 10/86400, 101) + 44210.5
    
    # Signal vectors
    t_10ms_rel = np.linspace(0, 10, 1001)
    t_100ms_rel = np.linspace(0, 10, 101)
    sine_signal = 5 * np.sin(2 * np.pi * 0.5 * t_10ms_rel)
    triangle_signal = 2.5 * np.abs(2 * (t_100ms_rel/2 - np.floor(t_100ms_rel/2 + 0.5))) - 1

    mat_dict = {
        'Comment': 'This is a test log file generated for demonstration.',
        'MeasurementStartTimeStr': '2021-01-17 12:00:00',
        'MeasurementStopTimeStr': '2021-01-17 12:00:10',
        'ECU_LIST': 'ecu1',
        'TIME_LIST': 'ecu1_TIME_DAQ_10_ms,ecu1_TIME_DAQ_100ms',
        'ecu1_TIME_DAQ_10_ms': time_daq_10ms,
        'ecu1_TIME_DAQ_100ms': time_daq_100ms,
        'ecu1_TIME_DAQ_10_ms_LIST': 'ecu1_sineSignal',
        'ecu1_TIME_DAQ_100ms_LIST': 'ecu1_triangleSignal',
        'ecu1_sineSignal': sine_signal,
        'ecu1_triangleSignal': triangle_signal
    }
    
    scipy.io.savemat(path, mat_dict)
    print(f"Dummy MAT file '{path}' created for demonstration.")
    return path

if __name__ == '__main__':
    # This section demonstrates the intended use of the TSMasterMatLogParser.
    # It first creates a verifiable, dummy .mat file that conforms to the AN0003 spec,
    # and then uses the parser to load, analyze, and visualize its contents.
    
    try:
        dummy_file_path = create_dummy_mat_file()
        
        # Initialize the parser with the log file
        parser = TSMasterMatLogParser(dummy_file_path)

        # Retrieve and display the log's contextual metadata
        metadata = parser.get_metadata()
        print("\n--- Log Metadata ---")
        for key, value in metadata.items():
            # Handle potential array-to-string conversion for clean printing
            display_value = "".join(value) if isinstance(value, np.ndarray) else value
            print(f"  {key:<25}: {display_value}")
        
        # Discover and list the signal groups found in the file
        groups = parser.list_signal_groups()
        print(f"\n--- Signal Groups Found ({len(groups)}) ---")
        print(f"  {groups}")

        # Analyze and plot signals from each group
        if not groups:
            print("\nNo signal groups were parsed.")
        else:
            for group_name in groups:
                print(f"\n--- Inspecting Group: {group_name} ---")
                df_group = parser.get_signal_group(group_name)
                
                if df_group is None or df_group.empty:
                    print("  Group is empty or could not be retrieved.")
                    continue
                    
                print("  First 5 data points:")
                print(df_group.head().to_string(float_format="%.4f"))
                
                for signal_name in df_group.columns:
                    print(f"\n  Plotting signal '{signal_name}'...")
                    parser.plot_signal(group_name, signal_name)

    except (FileNotFoundError, KeyError) as e:
        print(f"\nOperation failed: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")