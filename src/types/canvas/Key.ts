// A Key is a conserved quantity that represents a capability or condition within the system.
// It is used to gate the visibility and accessibility of Links (Choices), enabling
// dynamic, state-based pathfinding and security without relying on brittle, centralized ACLs.
// As a global entity, a Key's state change propagates throughout the entire fabric.
export interface Key {
  _id: string;
  name: string;
  description?: string;
}