export interface ConnectionDetails {
    local_address: string;
    neighbor_address: string;
    neighbor_portid: undefined | string;
    is_client: boolean;
}

export interface Link {
    protocol: string;
    status: string;
    statistics?: Record<string, any>;
}

export interface PortSnapshot {
    name: string;
    connection: ConnectionDetails | undefined;
    link: Link;
}

export interface TreeNodeData {
    rootward_portid: string;
    hops: number;
    tree_instance_id: string;
}

export interface PortPath {
    nodes: string[];
    edges: Edge[];
}

export interface Edge {
    source: string;
    target: string;
}

export interface MessageData {
    type: string;
    node_id: string;
    snapshots: Record<string, PortSnapshot>;
    trees_dict: Record<string, TreeNodeData>;
    port_paths: Record<string, PortPath>;
}