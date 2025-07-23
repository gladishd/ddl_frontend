import sys
import collections
import io
import os  # This is the required import that was missing.

# This Python script provides a functional equivalent of the C-based network simulation.
# It encapsulates the core concepts of Ethernet communication, such as MAC and IP addressing,
# station and switch behavior, and graph-based network topology management. The design
# reflects a move from low-level C structs to Python classes, improving readability
# while maintaining the original logic.

# The AdrIP class models a 4-byte IP address. In a distributed system, unique addresses
# are fundamental for routing and identifying endpoints. This class provides a structured
# way to handle and display these addresses.
class AdrIP:
    """Represents a 4-byte IP address."""
    ADDR_IP_LEN = 4

    def __init__(self, address_list=None):
        if address_list and len(address_list) == self.ADDR_IP_LEN:
            self._IPadr = list(address_list)
        else:
            self._IPadr = [0] * self.ADDR_IP_LEN

    def __str__(self):
        # Provides a human-readable string representation of the IP address,
        # which is essential for logging, debugging, and user interfaces.
        return "IP  : " + ".".join(map(str, self._IPadr))

    def copy(self):
        # Creates a new instance of an IP address, ensuring that modifications
        # to the copy do not affect the original. This is crucial for maintaining
        # state integrity when passing addresses between components.
        return AdrIP(self._IPadr)

# The AdrMac class models a 6-byte MAC address, the unique hardware identifier for a
# network interface. In Ethernet, MAC addresses are used for Layer 2 switching, forming
# the basis for forwarding decisions within a local network segment.
class AdrMac:
    """Represents a 6-byte MAC address."""
    ADDR_MAC_LEN = 6

    def __init__(self, hex_list=None):
        self._Macadr = [0] * self.ADDR_MAC_LEN
        if hex_list and len(hex_list) == self.ADDR_MAC_LEN:
            try:
                # This conversion from hex strings to integers mirrors the C code's
                # use of strtol, providing a necessary bridge from a human-readable
                # configuration to an internal binary representation.
                self._Macadr = [int(h, 16) for h in hex_list]
            except ValueError:
                print("Error: Invalid hexadecimal value in MAC address.", file=sys.stderr)


    def __str__(self):
        # The standardized hex format with delimiters is critical for interoperability
        # and conforming to network conventions.
        return "MAC : " + ":".join(f"{b:02x}" for b in self._Macadr)

    def __eq__(self, other):
        # Equality checking is a fundamental operation for network switches, which must
        # match a frame's destination MAC address against entries in their forwarding tables.
        if not isinstance(other, AdrMac):
            return NotImplemented
        return self._Macadr == other._Macadr

    def __lt__(self, other):
        # The less-than comparison implements the logic used in the Spanning Tree Protocol (STP)
        # to elect a root bridge. When priorities are equal, the switch with the numerically
        # lower MAC address becomes the root, making this comparison a key part of
        # establishing a stable, loop-free topology.
        if not isinstance(other, AdrMac):
            return NotImplemented
        return self._Macadr < other._Macadr
        
    def __hash__(self):
        return hash(tuple(self._Macadr))

    def is_null(self):
        # A null MAC address can be used to identify uninitialized or invalid entries
        # in a switch's forwarding table.
        return all(b == 0 for b in self._Macadr)

    def copy(self):
        # Creates a distinct copy of the MAC address object.
        new_adr = AdrMac()
        new_adr._Macadr = list(self._Macadr)
        return new_adr


# The Station class represents an end-user device on the network, such as a computer.
# It is a fundamental entity, acting as either a source or a destination for data.
# Each station is uniquely identified by its combination of a name, an IP address (Layer 3),
# and a MAC address (Layer 2).
class Station:
    """Represents an end-user device on the network."""
    def __init__(self, mac=None, ip=None, name=""):
        self.mac = mac if mac else AdrMac()
        self.ip = ip if ip else AdrIP()
        self.name = name

    def __str__(self):
        return f"NOM : {self.name}\n{self.mac}\n{self.ip}"

# An EthernetFrame encapsulates a single unit of data transmission. The structure of the frame,
# from the preamble to the checksum, is rigidly defined by the Ethernet standard to ensure
# that different devices can correctly interpret the data. This class models that structure.
class EthernetFrame:
    """Represents a single Ethernet frame."""
    def __init__(self, source_station=None, dest_station=None, msg=""):
        # The preamble and SFD (Start Frame Delimiter) are critical for physical layer
        # synchronization, allowing the receiving hardware to lock onto the incoming bitstream.
        self.preamble = [0xAA] * 7 # Using 0xAA as a common pattern, original used 0x55
        self.sfd = 0xAB
        self.destination = dest_station.mac if dest_station else AdrMac()
        self.source = source_station.mac if source_station else AdrMac()
        self.type = 0x0800  # Default to IPv4 type
        self.data = []
        self.longueurChaine = 0
        if msg:
            self.set_message(msg)

    def set_message(self, message):
        # Ethernet frames have a minimum payload size (46 bytes). This logic enforces that
        # requirement by padding smaller messages, a necessary step for protocol compliance.
        message_bytes = message.encode('utf-8')
        self.longueurChaine = len(message_bytes)
        
        if self.longueurChaine < 46:
            padding_len = 46 - self.longueurChaine
            self.data = list(message_bytes) + ([0] * padding_len)
            self.longueurChaine = 46
        elif self.longueurChaine <= 1500:
            self.data = list(message_bytes)
        else:
            raise ValueError("Message too long for a standard Ethernet frame")

    def __str__(self):
        # Displaying the frame's contents is vital for simulation and debugging, allowing
        # an observer to trace the flow of information through the network.
        preamble_str = ".".join(map(str, self.preamble))
        sfd_str = f"{self.sfd:02x}"
        data_str = " ".join(f"{b:02x}" for b in self.data)
        
        return (f"--- Ethernet Frame ---\n"
                f"Preamble: {preamble_str}\n"
                f"SFD: {sfd_str}\n"
                f"DESTINATION {self.destination}\n"
                f"SOURCE {self.source}\n"
                f"Type: {self.type:04x}\n"
                f"Data Length: {self.longueurChaine}\n"
                f"Data: {self.data_to_string()}\n"
                f"----------------------")
    
    def data_to_string(self):
        try:
            # Attempt to decode data as utf-8, falling back if it's not valid text.
            # This reflects how a receiving application would interpret the payload.
            return bytes(self.data).decode('utf-8', errors='replace').rstrip('\x00')
        except:
            return "[Binary Data]"


# The Switch class models a network switch, a device that operates at Layer 2. Its primary
# function is to forward Ethernet frames to their correct destination based on MAC addresses.
# This distributed forwarding logic is the cornerstone of modern Ethernet scalability.
class Switch:
    """Represents a network switch."""
    def __init__(self, mac=None, name="", num_ports=0, priority=32768):
        self.mac = mac if mac else AdrMac()
        self.name = name
        self.num_ports = num_ports
        self.priority = priority
        # The commutation_table (or MAC address table) is the switch's "brain". It learns
        # which MAC addresses are reachable through which ports, allowing it to make
        # intelligent forwarding decisions instead of broadcasting every frame. This learning
        # is a distributed process, key to Ethernet's self-organizing nature.
        self.commutation_table = {}  # MAC Address (str) -> Port (int)
        self.trame_en_cours = None
        self.sommet_arrive = -1
        self.sommet_precedent = -1

    def __str__(self):
        return (f"NOM : {self.name}\n"
                f"{self.mac}\n"
                f"NOMBRE DE PORTS : {self.num_ports}\n"
                f"PRIORITE : {self.priority}\n"
                f"LONGUEUR TABLE : {len(self.commutation_table)}")

    def display_commutation_table(self):
        print(f"---TABLE DE COMMUTATION for {self.name}---")
        if not self.commutation_table:
            print("(empty)")
        for mac, port in self.commutation_table.items():
            print(f"MAC : {mac} -> Port (Via le switch id): {port}")
        print("--------------------------")
        
    def learn_source_mac(self, source_mac, port):
        # This is the core of a switch's adaptive behavior. By observing the source
        # MAC address of incoming frames, the switch dynamically builds its forwarding table
        # without any need for manual configuration.
        mac_str = str(source_mac)
        if mac_str not in self.commutation_table:
            self.commutation_table[mac_str] = port


# The NetworkGraph class represents the entire network topology. It is the virtual space,
# or "Ether," in which all communication occurs. It manages the state of all components
# (stations, switches) and the connections (edges) between them.
class NetworkGraph:
    """Represents the entire network topology as a graph."""
    # This default topology is used if the stp_test file is not found.
    # This makes the script self-contained and demonstrates the STP algorithm's
    # ability to resolve loops.
    DEFAULT_TOPOLOGY = """10 12
2;00:00:00:00:00:01;4;100
2;00:00:00:00:00:02;4;200
2;00:00:00:00:00:03;4;300
1;aa:bb:cc:dd:ee:01;192.168.1.1
1;aa:bb:cc:dd:ee:02;192.168.1.2
1;aa:bb:cc:dd:ee:03;192.168.1.3
1;aa:bb:cc:dd:ee:04;192.168.1.4
1;aa:bb:cc:dd:ee:05;192.168.1.5
1;aa:bb:cc:dd:ee:06;192.168.1.6
1;aa:bb:cc:dd:ee:07;192.168.1.7
3;0;10
4;0;10
5;1;10
6;1;10
7;2;10
8;2;10
9;2;10
0;1;19
0;2;12
1;2;8
"""

    def __init__(self, filename):
        self.ordre = 0
        self.aretes_capacite = 0
        self.swListe = []
        self.stListe = []
        self.aretes = []
        self.conditionArret = False
        self._init_from_source(filename)

    def _init_from_source(self, source):
        # Parsing a configuration is the first step in constructing the network model.
        # This process translates a high-level description of a network into the concrete
        # data structures required for simulation.
        try:
            if os.path.exists(source):
                with open(source, 'r') as f:
                    lines = f.readlines()
            else:
                print(f"File not found: '{source}'. Using default built-in topology.", file=sys.stderr)
                lines = io.StringIO(self.DEFAULT_TOPOLOGY).readlines()
            
            # First line defines the order and number of edges
            self.ordre, self.aretes_capacite = map(int, lines[0].strip().split())
            
            # The next 'ordre' lines define the devices (switches and stations)
            for i in range(1, self.ordre + 1):
                parts = lines[i].strip().split(';')
                dev_type = int(parts[0])
                
                if dev_type == 2:  # Switch
                    mac_parts = parts[1].split(':')
                    num_ports = int(parts[2])
                    priority = int(parts[3])
                    sw = Switch(
                        mac=AdrMac(mac_parts), 
                        name=f"sw{len(self.swListe) + 1}",
                        num_ports=num_ports, 
                        priority=priority
                    )
                    self.swListe.append(sw)
                elif dev_type == 1: # Station
                    mac_parts = parts[1].split(':')
                    ip_parts = list(map(int, parts[2].split('.')))
                    st = Station(
                        mac=AdrMac(mac_parts),
                        ip=AdrIP(ip_parts),
                        name=f"st{len(self.stListe) + 1}"
                    )
                    self.stListe.append(st)
            
            # The remaining lines define the edges
            for i in range(self.ordre + 1, self.ordre + 1 + self.aretes_capacite):
                if i < len(lines):
                    s1, s2, cost = map(int, lines[i].strip().split(';'))
                    self.ajouter_arete(s1, s2, cost)

        except (FileNotFoundError, IOError):
            print(f"Erreur d'ouverture du fichier: {source}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing topology data: {e}", file=sys.stderr)
            sys.exit(1)

    # ... (the rest of the NetworkGraph class and other classes remain the same)

    def get_station_by_mac(self, mac):
        for station in self.stListe:
            if station.mac == mac:
                return station
        return None

    def get_device_by_index(self, index):
        if 0 <= index < len(self.swListe):
            return self.swListe[index]
        elif len(self.swListe) <= index < self.ordre:
            return self.stListe[index - len(self.swListe)]
        return None

    def get_index_by_mac(self, mac):
        for i, sw in enumerate(self.swListe):
            if sw.mac == mac:
                return i
        for i, st in enumerate(self.stListe):
            if st.mac == mac:
                return i + len(self.swListe)
        return -1
        
    def get_index_by_station(self, station):
        for i, st in enumerate(self.stListe):
            if st.mac == station.mac:
                return i + len(self.swListe)
        return -1

    def ajouter_arete(self, s1, s2, cost):
        # Edges represent the physical links between devices. Managing these connections
        # is fundamental to defining the network's topology and routing paths.
        if s1 >= self.ordre or s2 >= self.ordre or s1 == s2:
            return False
        
        # To maintain consistency, we store edges with the smaller index first. This simplifies
        # checks for existence and avoids duplicate representations of the same link.
        if s1 > s2:
            s1, s2 = s2, s1
            
        for arete in self.aretes:
            if arete[0] == s1 and arete[1] == s2:
                return False # Arete already exists
                
        self.aretes.append((s1, s2, cost))
        return True

    def sommets_adjacents(self, s):
        # Determining adjacency is a core graph operation, essential for any protocol
        # that needs to explore the network topology, like STP or frame flooding.
        adj = []
        for s1, s2, cost in self.aretes:
            if s1 == s:
                adj.append(s2)
            elif s2 == s:
                adj.append(s1)
        return adj

    def envoyer_trame(self, trame):
        print("######################")
        print("#  DEBUT DE L'ENVOIE #")
        print("######################")
        
        source_index = self.get_index_by_mac(trame.source)
        if source_index == -1:
            print("Source station not found in graph.")
            return

        adj_switches = self.sommets_adjacents(source_index)
        if not adj_switches:
            print(f"Station {source_index} is not connected to any switch.")
            return

        # The first hop is from the source station to its directly connected switch.
        premier_switch_index = adj_switches[0]
        print(f"Je pars du switch {premier_switch_index}!")
        
        # Start the recursive broadcast/flooding process from the first switch.
        self.envoyer_trame_recursive(trame, premier_switch_index, source_index)

    def envoyer_trame_recursive(self, trame, current_switch_idx, previous_hop_idx):
        # This function simulates how a real switch processes a frame: it first learns
        # the source MAC, then decides where to forward the frame.
        if current_switch_idx >= len(self.swListe): # It's a station
            station = self.stListe[current_switch_idx - len(self.swListe)]
            print(f"Trame passe par :  {current_switch_idx}")
            if station.mac == trame.destination:
                print(f"Bien arrivé ! (Station : {current_switch_idx})")
                print(trame)
            return

        current_switch = self.swListe[current_switch_idx]
        
        # MAC Address Learning
        current_switch.learn_source_mac(trame.source, previous_hop_idx)

        dest_mac_str = str(trame.destination)

        # Forwarding Logic: if destination is known, send to specific port.
        # If unknown, flood to all ports except the one it arrived on.
        # This is the fundamental algorithm of an Ethernet switch.
        if dest_mac_str in current_switch.commutation_table:
            next_hop_idx = current_switch.commutation_table[dest_mac_str]
            print(f"Je suis à {current_switch_idx}, je vais à {next_hop_idx} (from table)")
            self.envoyer_trame_recursive(trame, next_hop_idx, current_switch_idx)
        else:
            # Flooding: A key mechanism for discovery in Ethernet. When a destination is
            # unknown, the frame is broadcast to all possible paths, ensuring it eventually
            # reaches its target, at the cost of temporary network overhead.
            print(f"Trame passe par :  {current_switch_idx} (flooding)")
            for adjacent_idx in self.sommets_adjacents(current_switch_idx):
                if adjacent_idx != previous_hop_idx:
                    self.envoyer_trame_recursive(trame, adjacent_idx, current_switch_idx)
                    
    def determine_racine(self):
        # Spanning Tree Protocol (STP) elects a 'root bridge' to serve as the reference
        # point for building a loop-free tree. The election is a distributed process based
        # on priority and MAC address, ensuring a deterministic outcome without central control.
        if not self.swListe:
            return -1
        
        root_bridge = self.swListe[0]
        root_idx = 0
        for i, switch in enumerate(self.swListe[1:], 1):
            if switch.priority < root_bridge.priority:
                root_bridge = switch
                root_idx = i
            elif switch.priority == root_bridge.priority and switch.mac < root_bridge.mac:
                root_bridge = switch
                root_idx = i
        return root_idx

    def dijkstra(self, start_node_idx):
        # Dijkstra's algorithm finds the shortest path from a source to all other nodes.
        # In the context of STP, it's used to determine the lowest-cost path from each
        # switch to the root bridge, which is essential for selecting which ports to
        # keep active and which to block.
        distances = {i: float('inf') for i in range(self.ordre)}
        predecessors = {i: None for i in range(self.ordre)}
        distances[start_node_idx] = 0
        
        pq = [(0, start_node_idx)]
        
        while pq:
            dist, current_node = min(pq, key=lambda x: x[0])
            pq.remove((dist, current_node))

            for neighbor in self.sommets_adjacents(current_node):
                # Find cost of edge between current_node and neighbor
                edge_cost = 1 # Default cost if not found
                s1, s2 = min(current_node, neighbor), max(current_node, neighbor)
                for u, v, c in self.aretes:
                    if u == s1 and v == s2:
                        edge_cost = c
                        break
                
                new_dist = distances[current_node] + edge_cost
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current_node
                    pq.append((new_dist, neighbor))
                    
        return predecessors, distances
        
    def stp(self):
        # Spanning Tree Protocol (STP) is a crucial mechanism for preventing broadcast storms
        # and data instability caused by loops in a switched network. It does this by
        # algorithmically pruning the network into a loop-free tree topology, ensuring there
        # is only one active path between any two points.
        root_idx = self.determine_racine()
        if root_idx == -1:
            print("No switches to run STP.")
            return
            
        pred, _ = self.dijkstra(root_idx)
        
        new_aretes = []
        for i in range(self.ordre):
            if pred[i] is not None and i != root_idx:
                s1, s2 = min(i, pred[i]), max(i, pred[i])
                original_cost = 1
                for u, v, c in self.aretes:
                    if u == s1 and v == s2:
                        original_cost = c
                        break
                new_aretes.append((s1, s2, original_cost))
        
        self.aretes = new_aretes


    def afficher_graphe(self):
        print("---SWITCH---")
        for i, sw in enumerate(self.swListe):
            print(f"{i}. {sw.name}")
            print(f"Priorite : {sw.priority}")
            print(f"Nombre de ports : {sw.num_ports}")
            print(str(sw.mac))

        print("---STATION---")
        for i, st in enumerate(self.stListe):
            print(f"{i + len(self.swListe)}. {st.name}")
            print(str(st))

        print("--ARETES : COUT--")
        for s1, s2, cost in self.aretes:
            print(f"{s1} - {s2} : {cost}")
            
    def afficher_switch_route(self):
        root_idx = self.determine_racine()
        if root_idx != -1:
            print("---SWITCH RACINE---")
            print(self.swListe[root_idx])

def main():
    """Main function to run the simulation."""
    print("----TEST IP------")
    ip = AdrIP([10, 10, 10, 10])
    print(ip)

    print("----TEST MAC-----")
    mac = AdrMac(["a6", "0d", "a5", "d6", "c5", "f6"])
    print(mac)

    print("----TEST STATION----")
    station_test = Station(mac, ip, "Salut")
    print(station_test)

    print("-----TEST SWITCH-----")
    switch_test = Switch(mac, "Salut", 4, 8)
    # Manually add to table for testing as in the C code
    switch_test.commutation_table[str(mac)] = 2
    print(switch_test)
    switch_test.display_commutation_table()

    print("-----TEST GRAPHE-----")
    # The simulation now uses a built-in default topology if 'stp_test' is not found.
    g = NetworkGraph("stp_test")
    
    print(f"Ordre : {g.ordre}")
    print(f"Aretes : {len(g.aretes)}")
    print("AFFICHER GRAPHE AVANT STP\n")
    g.afficher_graphe()
    
    # Running STP prunes the graph to a loop-free tree, which is essential
    # before attempting any data transmission to avoid broadcast storms.
    g.stp()
    print("\nAFFICHER GRAPHE APRES STP\n")
    g.afficher_graphe()
    
    st1 = g.stListe[0] 
    st3 = g.stListe[6] 

    tr = EthernetFrame(st1, st3, "Auguste a vote Bardella alors qu'il est de gauche")
    print("\n---AFFICHAGE TRAME---")
    print(tr)
    
    print(f"st1 index: {g.get_index_by_station(st1)}")
    print(f"st3 index: {g.get_index_by_station(st3)}")
    print(st1.mac)
    print(st3.mac)
    
    print("\n---ENVOIE TRAME---")
    g.envoyer_trame(tr)
    
    print("\n---ENVOIE TRAME 2---")
    tr2 = EthernetFrame(st3, st1, "C'est un mensonge ?")
    g.envoyer_trame(tr2)

    print("\n---TABLES DE COMMUTATION FINALES---")
    for i in range(len(g.swListe)):
        g.swListe[i].display_commutation_table()

    g.afficher_switch_route()

if __name__ == "__main__":
    main()