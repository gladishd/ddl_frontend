# soqosmw_emulator.py
#
# This script provides a Python-based architectural model of the Service-Oriented
# Quality-of-Service MiddleWare (SOQoSMW) framework. It translates the core
# components and their relationships from the OMNeT++ implementation into a
# high-level, object-oriented representation.
#
# The goal is not a line-by-line translation, but an emulation of the system's
# design philosophy. This moves from a purely statistical simulation of network
# phenomena towards a computational model of deterministic, stateful interactions.
# This architecture is a foundational step for the Graph Virtual Machine (GVM),
# where named graph relationships are built and torn down to facilitate reliable
# transactions.

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

# ---------------------------------------------------------------------------
# Core Data Structures and Types (Inspired by .msg and .h files)
# ---------------------------------------------------------------------------

class QoSGroups(Enum):
    """
    # Represents the fundamental classes of service. In a Daedaelus Transaction Fabric,
    # these would map to hardware-enforced confinement zones within the stacked tree architecture,
    # ensuring that different traffic classes cannot interfere.
    """
    RT = 0          # Real-Time (e.g., AVB/TSN)
    STD_TCP = 1     # Standard, Connection-Oriented
    STD_UDP = 2     # Standard, Connection-Less
    WEB = 3         # Web Services

@dataclass
class EndpointDescription:
    """
    # A named, addressable entity within the network. This is more than a simple
    # IP address; it is a handle to a process or service, a fundamental element
    # in our model of building 'named' graph relationships.
    """
    path: str
    network_addr: str
    network_port: int

@dataclass
class IQoSPolicy:
    """
    # Base class for Quality of Service policies. These policies are the 'rulesets'
    # that govern the behavior of communication, enabling non-zero-sum game outcomes
    # where trustable, cooperative behavior is enforced by the fabric itself.
    """
    value: Any

@dataclass
class StreamIDQoSPolicy(IQoSPolicy):
    name: str = "StreamID"

@dataclass
class FramesizeQoSPolicy(IQoSPolicy):
    name: str = "Framesize"

# A map to hold all policies for a given connection request.
QoSPolicyMap = Dict[str, IQoSPolicy]

# ---------------------------------------------------------------------------
# Base Classes for Communication Endpoints (Inspired by endpoints/base)
# ---------------------------------------------------------------------------

class EndpointBase:
    """
    # An Endpoint is a local terminus of a communication channel. It is not merely
    # a passive data sink or source; it is an active participant in the 'Token Dynamics'
    # of a link, responsible for upholding the guarantees of its QoS policies.
    """
    def __init__(self, endpoint_path: str, qos: QoSGroups, local_address: str, local_port: int):
        self.endpoint_path = endpoint_path
        self.qos = qos
        self.local_address = local_address
        self.local_port = local_port
        self._connector: Optional['ConnectorBase'] = None
        print(f"    - Endpoint '{self.endpoint_path}' ({self.qos.name}) created.")

    def set_connector(self, connector: 'ConnectorBase'):
        self._connector = connector

    def get_connection_specific_information(self) -> EndpointDescription:
        # This returns a description for addressing, not the full state.
        return EndpointDescription(self.endpoint_path, self.local_address, self.local_port)

class PublisherEndpoint(EndpointBase):
    """
    # A Publisher Endpoint is responsible for originating a data stream, governed by
    # a negotiated set of QoS policies. It ensures that data is only sent when
    # the fabric can guarantee its transport, avoiding the conventional "best-effort"
    # approach that leads to silent data loss.
    """
    def __init__(self, endpoint_path, qos, local_address, local_port):
        super().__init__(endpoint_path, qos, local_address, local_port)
        self._is_connected = False

    def publish(self, data: str):
        if self._is_connected:
            print(f"      - Publisher [{self.endpoint_path}] sending data: '{data}'")
            # In a real system, this forwards to the transport layer.
        else:
            print(f"      - Publisher [{self.endpoint_path}] dropped data (no subscribers): '{data}'")

    def add_subscriber(self, subscriber_info: EndpointDescription):
        print(f"    - PublisherEndpoint '{self.endpoint_path}' noted new subscriber: {subscriber_info.path}")
        self._is_connected = True

class SubscriberEndpoint(EndpointBase):
    """
    # A Subscriber Endpoint receives data. Its primary role is to participate
    # in the protocol that establishes a reliable channel, providing the necessary
    # acknowledgements or flow control signals that prevent packet loss, thus
    # eliminating the need for timeouts and retries.
    """
    def receive(self, data: str):
        print(f"    - SubscriberEndpoint '{self.endpoint_path}' received data: '{data}'")

# ---------------------------------------------------------------------------
# Connector and Application Shells (Inspired by connector/ and applications/)
# ---------------------------------------------------------------------------

class ConnectorBase:
    """
    # A Connector serves as the dynamic link between a logical application and its
    # underlying physical endpoints. It embodies the principle of separation of
    # concerns, allowing application logic to remain independent of the specific
    # protocols used for transport. This is a key abstraction for building dynamic
    # computational strata.
    """
    def __init__(self, name: str):
        self.name = name
        self.applications: List[Any] = []
        self.endpoints: List[EndpointBase] = []
        print(f"  - Connector '{self.name}' created.")

    def add_application(self, app: Any):
        if app not in self.applications:
            self.applications.append(app)

    def add_endpoint(self, endpoint: EndpointBase):
        if endpoint not in self.endpoints:
            self.endpoints.append(endpoint)
            endpoint.set_connector(self)

class SOQoSMWApplicationBase:
    """
    # Represents the user-level application logic. In the Daedaelus model, applications
    # do not contend for bandwidth on a lossy medium; instead, they request the
    # creation of reliable, stateful transaction channels via the LocalServiceManager.
    """
    def __init__(self, service_name: str, local_service_manager: 'LocalServiceManager'):
        self.service_name = service_name
        self.lsm = local_service_manager
        self._connector: Optional[ConnectorBase] = None

class PublisherApp(SOQoSMWApplicationBase):
    def __init__(self, service_name, lsm, qos_policies: QoSPolicyMap):
        super().__init__(service_name, lsm)
        print(f"  - PublisherApp '{service_name}' initializing...")
        self._connector = self.lsm.register_publisher_service(service_name, qos_policies, self)

    def send_data(self, data: str):
        print(f"  - PublisherApp '{self.service_name}' requesting to send '{data}'.")
        # In a real system, this sends to the connector, which forwards to endpoints.
        for endpoint in self._connector.endpoints:
            if isinstance(endpoint, PublisherEndpoint):
                endpoint.publish(data)

class SubscriberApp(SOQoSMWApplicationBase):
    def __init__(self, service_name, lsm, publisher_name: str, qos_policies: QoSPolicyMap):
        super().__init__(service_name, lsm)
        print(f"  - SubscriberApp '{service_name}' initializing to subscribe to '{publisher_name}'...")
        self._connector = self.lsm.register_subscriber_service(service_name, publisher_name, qos_policies, self)


# ---------------------------------------------------------------------------
# Core Middleware Services (Inspired by servicemanager/ and qosmanagement/)
# ---------------------------------------------------------------------------

class QoSNegotiationProtocol:
    """
    # This protocol is the engine of the 'time-reversible constructor'. It replaces
    # unreliable, best-effort delivery with a formal negotiation. A connection
    # is either successfully established with all parties agreeing on its state
    # and properties, or it provably fails, leaving no ambiguity and no need
    # for recovery via the 'irreversible smash and restart' of timeouts.
    """
    def __init__(self, lsm: 'LocalServiceManager'):
        self.lsm = lsm
        print(f" - QoSNegotiationProtocol active for host '{self.lsm.host.hostname}'.")

    def client_request_negotiation(self, local_desc, remote_desc, policies):
        print(f"  - QOSNP: Client '{local_desc.path}' starting negotiation with '{remote_desc.path}'.")
        # Step 1: Client sends request to server's QOSNP
        server_qosnp = self.lsm.host.network.get_host(remote_desc.network_addr).qosnp
        response_policies, publisher_csi = server_qosnp.server_handle_request(remote_desc, local_desc, policies)

        if response_policies:
            print(f"  - QOSNP: Client received SUCCESS response from '{remote_desc.path}'.")
            # Step 3: Client receives response and sends establish message
            subscriber_desc = self.lsm.create_or_find_subscriber_for(remote_desc.path, publisher_csi, response_policies)
            final_status = server_qosnp.server_handle_establish(remote_desc, local_desc, subscriber_desc)
            if final_status:
                print(f"  - QOSNP: Client received FINAL success. Connection established.")
                # Final step: update publisher with subscriber info
                qos_group_value = response_policies['QoSGroup'].value
                publisher_endpoint = self.lsm.find_publisher_like(remote_desc.path, qos_group_value)
                if publisher_endpoint:
                    publisher_endpoint.add_subscriber(subscriber_desc)
        else:
            print(f"  - QOSNP: Client received FAILURE response from '{remote_desc.path}'.")

    def server_handle_request(self, local_desc, remote_desc, policies):
        print(f"   - QOSNP: Server '{local_desc.path}' received request from '{remote_desc.path}'.")
        # Step 2: Server evaluates request and creates its own endpoint
        publisher_endpoint = self.lsm.create_or_find_publisher_for(local_desc.path, policies['QoSGroup'].value)
        if publisher_endpoint:
            print(f"   - QOSNP: Server approves request. Sending SUCCESS response.")
            # The server returns both the policies it agreed to and its connection info
            return policies, publisher_endpoint.get_connection_specific_information()
        else:
            print(f"   - QOSNP: Server rejects request. Sending FAILURE response.")
            return None, None

    def server_handle_establish(self, local_desc, remote_desc, subscriber_desc: EndpointDescription):
        print(f"   - QOSNP: Server '{local_desc.path}' received establish from '{remote_desc.path}'.")
        # Step 4: Server receives establish, connects endpoints, and returns final ack.
        print(f"   - QOSNP: Server connecting publisher to new subscriber.")
        return True # Success

class LocalServiceManager:
    """
    # The Local Service Manager (LSM) is the local agent of the Graph Virtual Machine.
    # It is responsible for interpreting service requests and instantiating the necessary
    # local resources (connectors, endpoints) to build the 'named graph relationships'
    # that form the Transaction Fabric.
    """
    def __init__(self, host: 'SOQoSMWHost'):
        self.host = host
        self.publisher_connectors: Dict[str, ConnectorBase] = {}
        self.subscriber_connectors: Dict[str, ConnectorBase] = {}

    def register_publisher_service(self, service_name, policies, app):
        if service_name not in self.publisher_connectors:
            self.publisher_connectors[service_name] = ConnectorBase(f"{service_name}-pub-connector")
        connector = self.publisher_connectors[service_name]
        connector.add_application(app)
        return connector

    def register_subscriber_service(self, service_name, publisher_name, policies, app):
        if publisher_name not in self.subscriber_connectors:
            self.subscriber_connectors[publisher_name] = ConnectorBase(f"{service_name}-sub-connector")
        connector = self.subscriber_connectors[publisher_name]
        connector.add_application(app)

        # Initiate the negotiation to establish the connection
        local_desc = EndpointDescription(service_name, self.host.hostname, 0) # Port 0 as placeholder
        remote_host = self.host.network.get_host_for_service(publisher_name)
        if not remote_host:
            raise RuntimeError(f"Service '{publisher_name}' not found in network.")
        remote_desc = EndpointDescription(publisher_name, remote_host, 0)
        self.host.qosnp.client_request_negotiation(local_desc, remote_desc, policies)
        return connector

    def create_or_find_publisher_for(self, service_path, qos_group_value):
        connector = self.publisher_connectors.get(service_path)
        if not connector: return None
        # Find existing endpoint or create a new one
        for ep in connector.endpoints:
            if ep.qos.value == qos_group_value:
                return ep
        # Create new endpoint
        new_ep = PublisherEndpoint(f"{service_path}/ep/{qos_group_value}", QoSGroups(qos_group_value), self.host.hostname, 5000 + qos_group_value)
        connector.add_endpoint(new_ep)
        return new_ep

    def find_publisher_like(self, service_path, qos_group_value):
        connector = self.publisher_connectors.get(service_path)
        if not connector: return None
        for ep in connector.endpoints:
            if isinstance(ep, PublisherEndpoint) and ep.qos.value == qos_group_value:
                return ep
        return None

    def create_or_find_subscriber_for(self, service_path: str, publisher_csi: EndpointDescription, policies: QoSPolicyMap):
        connector = self.subscriber_connectors.get(service_path)
        if not connector: return None
        # Create new subscriber endpoint
        qos_policy = policies.get("QoSGroup")
        if not qos_policy:
             raise ValueError("QoSGroup policy not found in negotiation response")
        qos_group = QoSGroups(qos_policy.value)

        new_ep = SubscriberEndpoint(f"{connector.name}/ep/{qos_group.value}", qos_group, self.host.hostname, 6000 + qos_group.value)
        connector.add_endpoint(new_ep)
        return new_ep.get_connection_specific_information()

# ---------------------------------------------------------------------------
# Host and Network Containers
# ---------------------------------------------------------------------------

class SOQoSMWHost:
    """
    # A Host is an autonomous unit of compute, storage, and packet processing. It is a 'cell'
    # in the N2N Lattice, containing all the necessary middleware to participate in the
    # Transaction Fabric.
    """
    def __init__(self, hostname: str, network: 'Network'):
        self.hostname = hostname
        self.network = network
        print(f"- Initializing Host: {self.hostname}")
        self.lsm = LocalServiceManager(self)
        self.qosnp = QoSNegotiationProtocol(self.lsm)
        self.apps: Dict[str, SOQoSMWApplicationBase] = {}

    def add_app(self, app: SOQoSMWApplicationBase):
        self.apps[app.service_name] = app

class Network:
    """
    # Represents the entire physical mesh, the 'groundplane' upon which logical,
    # stacked trees of communication are built.
    """
    def __init__(self):
        self.hosts: Dict[str, SOQoSMWHost] = {}

    def add_host(self, hostname: str):
        if hostname not in self.hosts:
            self.hosts[hostname] = SOQoSMWHost(hostname, self)

    def get_host(self, hostname: str) -> SOQoSMWHost:
        return self.hosts[hostname]

    def get_host_for_service(self, service_name: str) -> Optional[str]:
        # Simple static service discovery
        for host in self.hosts.values():
            if service_name in host.lsm.publisher_connectors:
                return host.hostname
        return None

# ---------------------------------------------------------------------------
# Main Simulation
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("--- Daedaelus SOQoSMW Architectural Emulation ---")
    print("Building network fabric...")
    net = Network()
    net.add_host("PublisherHost")
    net.add_host("SubscriberHost")

    print("\nDeploying services...")
    pub_host = net.get_host("PublisherHost")
    sub_host = net.get_host("SubscriberHost")

    # Define QoS policies for a reliable UDP stream
    publisher_policies = {
        "QoSGroup": IQoSPolicy(QoSGroups.STD_UDP.value),
        "StreamID": StreamIDQoSPolicy(42),
        "Framesize": FramesizeQoSPolicy(1024)
    }

    subscriber_policies = {
        "QoSGroup": IQoSPolicy(QoSGroups.STD_UDP.value)
    }

    # Instantiate and register the Publisher application
    publisher_app = PublisherApp("Sensor/Temp/1", pub_host.lsm, publisher_policies)
    pub_host.add_app(publisher_app)

    print("\n--- Negotiation Phase ---")
    # Instantiate the Subscriber, which triggers the negotiation process
    subscriber_app = SubscriberApp("Dashboard/Temp/Reader", sub_host.lsm, "Sensor/Temp/1", subscriber_policies)
    sub_host.add_app(subscriber_app)


    print("\n--- Data Transmission Phase ---")
    # A publisher sends data, which should now succeed because a subscriber is connected.
    publisher_app.send_data("Temperature is 21.5C")
    publisher_app.send_data("Temperature is 21.6C")

    print("\n--- Emulation Complete ---")