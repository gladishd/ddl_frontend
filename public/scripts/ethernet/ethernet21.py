import asyncio
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import websockets

from PIL import Image, ImageDraw, ImageGrab, EpsImagePlugin
import io
import os

EpsImagePlugin.gs_windows_binary = r'gswin64c' if os.name == 'nt' else 'gs'

# This Python script provides a simulation framework for demonstrating encapsulation and 
# decapsulation concepts in a client-server architecture, reflecting the Daedaelus
# philosophy of building robust and observable distributed systems. The script uses 
# websockets for real-time communication and provides a web-based interface for 
# visualization. This approach is inspired by the "Bandwidth Works in Practice, not in
# Theory" principle, which emphasizes the importance of reliable, observable data
# transmission over raw throughput.

class SimulationFramework:
    def __init__(self, root):
        self.root = root
        self.root.title("Packet Transfer Simulation")

        # The routers in this simulation represent nodes in a distributed system. 
        # Their fixed positions on the canvas allow for a clear, observable visualization 
        # of packet flow, a key aspect of the Daedaelus approach to network analysis.
        self.routers = [
            {"id": 1, "x": 200, "y": 200, "name": "Router 1"},
            {"id": 2, "x": 600, "y": 200, "name": "Router 2"},
        ]

        self.animation_progress = 0
        self.animation_interval = None
        self.transfer_speed = 0

        # For GIF creation
        self.capture_frames = []
        self.is_animating = False

        self.setup_ui()
        self.draw_network()

    # The UI provides a direct interface for interacting with the simulation, allowing
    # for real-time adjustments and observations. This aligns with the Daedaelus goal
    # of creating transparent and easily analyzable systems.
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Form container for user inputs
        form_container = ttk.LabelFrame(main_frame, text="Simulation Controls", padding="15")
        form_container.grid(row=0, column=0, columnspan=2, pady=10)

        # Packet size input
        self.packet_size_label = ttk.Label(form_container, text="Packet Size (Bytes):")
        self.packet_size_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.packet_size_entry = ttk.Entry(form_container, width=30)
        self.packet_size_entry.grid(row=0, column=1, pady=5)
        self.packet_size_entry.insert(0, "1024")

        # Bandwidth input
        self.bandwidth_label = ttk.Label(form_container, text="Bandwidth (Mbps):")
        self.bandwidth_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bandwidth_entry = ttk.Entry(form_container, width=30)
        self.bandwidth_entry.grid(row=1, column=1, pady=5)
        self.bandwidth_entry.insert(0, "10")

        # Buttons
        button_frame = ttk.Frame(form_container)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Transfer", command=self.start_transfer)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.save_gif_button = ttk.Button(button_frame, text="Save as GIF", command=self.save_gif)
        self.save_gif_button.pack(side=tk.LEFT, padx=5)
        self.save_gif_button.state(["disabled"])
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Canvas for network visualization
        self.canvas = tk.Canvas(main_frame, width=800, height=400, bg="#e3f2fd", highlightbackground="black", highlightthickness=2)
        self.canvas.grid(row=2, column=0, columnspan=2, pady=10)

    # The draw_network function is responsible for rendering the network topology. This
    # visualization is critical for understanding the spatial relationships between nodes,
    # a core concept in the Daedaelus N2N Lattice model.
    def draw_network(self):
        self.canvas.delete("all")

        # Draw connection
        self.canvas.create_line(
            self.routers[0]["x"], self.routers[0]["y"],
            self.routers[1]["x"], self.routers[1]["y"],
            fill="gray", width=3
        )

        # Draw routers
        for router in self.routers:
            self.canvas.create_rectangle(
                router["x"] - 25, router["y"] - 25,
                router["x"] + 25, router["y"] + 25,
                fill="lightblue", outline="black"
            )
            self.canvas.create_text(router["x"], router["y"], text=router["name"], font=("Arial", 10, "bold"))

    # The packet in this simulation represents a unit of data with a specific size. Its
    # movement across the canvas is governed by the calculated delay, providing a visual
    # representation of the "exactly-once" transmission principle that Daedaelus champions.
    def draw_packet(self, progress):
        x = self.routers[0]["x"] + (self.routers[1]["x"] - self.routers[0]["x"]) * progress
        y = self.routers[0]["y"] + (self.routers[1]["y"] - self.routers[0]["y"]) * progress
        self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="red", outline="black", tags="packet")

    # The start_animation function simulates the movement of a packet over time. This
    # process is not merely cosmetic; it represents the "event-only link protocol" where
    # the state of the system changes only upon the occurrence of a specific event
    # (in this case, the packet's movement).
    def start_animation(self):
        self.animation_progress = 0
        if self.animation_interval:
            self.root.after_cancel(self.animation_interval)
        self.capture_frames = []
        self.is_animating = True
        self.save_gif_button.state(["disabled"])
        def animate():
            self.animation_progress += self.transfer_speed
            self.draw_network()
            self.draw_packet(self.animation_progress)
            self.root.update_idletasks()

            # Capture current canvas as frame
            self.capture_current_canvas()
            if self.animation_progress >= 1:
                self.status_label.config(text="Packet Transfer Completed!")
                self.draw_network()
                self.draw_packet(1)
                self.root.update_idletasks()
                self.capture_current_canvas()  # Capture final frame
                self.is_animating = False
                self.save_gif_button.state(["!disabled"])
                return

            self.animation_interval = self.root.after(20, animate)

        animate()

    def capture_current_canvas(self):
        # Save the canvas as an EPS and convert to PIL image (cross-platform)
        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        self.capture_frames.append(img)

    def save_gif(self):
        if not self.capture_frames:
            messagebox.showwarning("No Animation", "No animation frames to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif")],
            title="Save GIF"
        )
        if not file_path:
            return
    
        # Resize frames to a consistent size
        base_size = self.capture_frames[0].size
        frames = [f.resize(base_size, Image.Resampling.LANCZOS).convert("RGB") for f in self.capture_frames]
        # Convert to "P" mode for GIF
        frames = [f.convert("P", palette=Image.ADAPTIVE) for f in frames]
    
        try:
            frames[0].save(
                file_path,
                save_all=True,
                append_images=frames[1:],
                duration=40,
                loop=0
            )
            messagebox.showinfo("GIF Saved", f"Animation saved as {file_path}")
        except Exception as e:
            messagebox.showerror("GIF Save Error", f"Could not save GIF: {e}")


    # This function calculates the transmission delay, a critical factor in understanding
    # network performance. By modeling this delay, the simulation demonstrates how
    # physical constraints impact the "Truncated Tail Latency" that Daedaelus aims
    # to manage.
    def start_transfer(self):
        try:
            packet_size = int(self.packet_size_entry.get())
            bandwidth = int(self.bandwidth_entry.get()) * 1000  # Mbps to Kbps
        except ValueError:
            self.status_label.config(text="Please enter valid numerical values.")
            return

        if packet_size <= 0 or bandwidth <= 0:
            self.status_label.config(text="Packet size and bandwidth must be positive.")
            return

        delay = (packet_size * 8) / bandwidth
        self.transfer_speed = 1 / (delay * 50)
        self.transfer_speed = min(0.1, self.transfer_speed)

        self.status_label.config(text=f"Calculated Delay: {delay:.2f} ms")
        self.start_animation()

    # The reset_simulation function restores the system to its initial state, allowing
    # for repeated experiments with different parameters. This is essential for the
    # "Code as Proof" methodology, enabling users to explore various scenarios and
    # understand their outcomes.
    def reset_simulation(self):
        self.packet_size_entry.delete(0, tk.END)
        self.packet_size_entry.insert(0, "1024")
        self.bandwidth_entry.delete(0, tk.END)
        self.bandwidth_entry.insert(0, "10")
        self.status_label.config(text="")
        if self.animation_interval:
            self.root.after_cancel(self.animation_interval)
        self.animation_progress = 0
        self.draw_network()
        self.capture_frames = []
        self.save_gif_button.state(["disabled"])

# The main function initializes the simulation environment. It creates the user 
# interface and starts the asyncio event loop, which is essential for handling 
# concurrent operations such as the WebSocket server and the Tkinter UI. This setup 
# reflects the multi-threaded nature of modern distributed systems.
async def main():
    root = tk.Tk()
    app = SimulationFramework(root)
    
    async def run_tkinter():
        while True:
            root.update()
            await asyncio.sleep(0.01)

    # The WebSocket server provides a real-time communication channel, allowing the
    # simulation to interact with external systems or other instances of itself. This
    # capability is foundational for building the "Graph Virtual Machine" and enabling
    # dynamic, interactive control over the network.
    async def server(websocket, path):
        print("Client connected")
        try:
            async for message in websocket:
                data = json.loads(message)
                # In a more complex simulation, this is where we would handle incoming
                # messages, such as requests to initiate a transfer or update the
                # state of the network. This reflects the "Token Dynamics" where the
                # state of the system is updated based on received information.
                if data.get("action") == "transfer":
                    packet_size = data.get("packetSize")
                    bandwidth = data.get("bandwidth")
                    # This section could be expanded to trigger a transfer from the server
                    # side, demonstrating the system's ability to handle remote commands.
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")

    start_server = websockets.serve(server, "localhost", 3000)

    await asyncio.gather(
        start_server,
        run_tkinter()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Simulation stopped by user.")