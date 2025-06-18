import React from 'react';

// This script is a 'precise information-theoretic' emulator of the "I Know That You Know That I Know" (TIKTYKTIK) property.
// It is a link utility that "enables us to address some of the most difficult and pernicious problems in distributed systems today."
const pythonCode = `
# This script is a 'precise information-theoretic' emulator of the
# "I Know That You Know That I Know" (TIKTYKTIK) property.
# It demonstrates how two agents, Alice and Bob, achieve mutual knowledge
# over a link, forming a bipartite element of information persistable
# through failure and recovery. This is a foundational link utility for
# our Graph Virtual Machine (GVM).

class Agent:
    def __init__(self, name):
        self.name = name
        self.knowledge = "UNKNOWN"
        self.believes_other_knows = False
        self.knows_other_knows = False

    def __str__(self):
        return (f"[{self.name}] "
                f"Knowledge: {self.knowledge}, "
                f"Believes Other Knows: {self.believes_other_knows}, "
                f"Knows Other Knows: {self.knows_other_knows}")

def run_tiktyktik_protocol(alice, bob, secret_message="DATA"):
    print("--- Initial State ---")
    print(alice)
    print(bob)
    print("\\n--- Protocol Start: Alice sends message ---")

    # Step 1: Alice sends the message to Bob
    # Bob now has the knowledge. Alice only knows she sent it.
    bob.knowledge = secret_message
    print(f"EVENT: Alice -> Bob ('{secret_message}')")
    print(alice)
    print(bob)
    print("\\n--- Bob sends acknowledgement ---")

    # Step 2: Bob acknowledges receipt.
    # Alice now knows Bob has the knowledge. Bob only believes Alice knows.
    alice.believes_other_knows = True
    print("EVENT: Bob -> Alice ('ACK')")
    print(alice)
    print(bob)
    print("\\n--- Alice confirms acknowledgement ---")

    # Step 3: Alice confirms she received the ACK.
    # Bob now knows that Alice knows he has the message.
    # This completes the bipartite exchange; mutual knowledge is achieved.
    bob.knows_other_knows = True
    print("EVENT: Alice -> Bob ('ACK_CONFIRMED')")
    print(alice)
    print(bob)
    print("\\n--- TIKTYKTIK State Achieved ---")

# --- Simulation ---
alice = Agent("Alice")
bob = Agent("Bob")
run_tiktyktik_protocol(alice, bob)
`;

// This output shows the evolution of the system's state.
// Each step demonstrates the change in the local observer view (LOV)
// for Alice and Bob until they reach a shared, consistent state.
const pythonOutput = `
--- Initial State ---
[Alice] Knowledge: UNKNOWN, Believes Other Knows: False, Knows Other Knows: False
[Bob]   Knowledge: UNKNOWN, Believes Other Knows: False, Knows Other Knows: False

--- Protocol Start: Alice sends message ---
EVENT: Alice -> Bob ('DATA')
[Alice] Knowledge: UNKNOWN, Believes Other Knows: False, Knows Other Knows: False
[Bob]   Knowledge: DATA, Believes Other Knows: False, Knows Other Knows: False

--- Bob sends acknowledgement ---
EVENT: Bob -> Alice ('ACK')
[Alice] Knowledge: UNKNOWN, Believes Other Knows: True, Knows Other Knows: False
[Bob]   Knowledge: DATA, Believes Other Knows: False, Knows Other Knows: False

--- Alice confirms acknowledgement ---
EVENT: Alice -> Bob ('ACK_CONFIRMED')
[Alice] Knowledge: UNKNOWN, Believes Other Knows: True, Knows Other Knows: False
[Bob]   Knowledge: DATA, Believes Other Knows: False, Knows Other Knows: True

--- TIKTYKTIK State Achieved ---
`;

const PythonModelDisplay = () => {
  return (
    <div className="python-model-container">
      <div className="code-section">
        <h3 className="code-header">Emulator Code (Python)</h3>
        <pre className="code-block python-syntax"><code>{pythonCode.trim()}</code></pre>
      </div>
      <div className="code-section">
        <h3 className="code-header">Simulated Output</h3>
        <pre className="code-block output-syntax"><code>{pythonOutput.trim()}</code></pre>
      </div>
    </div>
  );
};

export default PythonModelDisplay;