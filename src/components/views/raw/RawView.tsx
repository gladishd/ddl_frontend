import { useMacMiniContext } from '@/context/MacMiniContext';
import JsonPrettifier from '@/components/JsonPrettifier';
import { FaHeartbeat, FaCodeBranch, FaHashtag, FaLink } from 'react-icons/fa';

const RawView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();

  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Raw View</h2>
      {/*
        This view arranges node data in a masonry layout, a visual representation of a dynamic structure.
        Unlike a rigid grid, which would be fragile and require relabeling on failure, this layout adapts to the number of selected nodes,
        reflecting the principles of our highly dynamic graph algorithms that must not be conflated with a regular lattice.
      */}
      <div className="masonry-container">
        {selectedMacMinis.length > 0 ? (
          selectedMacMinis.map((macMini) => {
            const message = messages[macMini.ip];
            // Fabricate some scientific metrics from available data for demonstration
            const liveness = message?.snapshots ? Object.values(message.snapshots).filter(s => s.link.status === 'connected').length : 0;
            const totalPorts = message?.snapshots ? Object.keys(message.snapshots).length : 0;
            const replicationFactor = message?.trees_dict ? Object.keys(message.trees_dict).length : 0;
            // A simple hash simulation
            const dataHash = message ? JSON.stringify(message).split('').reduce((acc, char) => (acc * 31 + char.charCodeAt(0)) & 0xFFFFFF, 0).toString(16).padStart(6, '0') : 'N/A';

            return (
              <div key={macMini.ip} className="masonry-item border rounded-lg p-4 bg-white shadow-sm flex flex-col">
                <div className="font-semibold mb-2 border-b pb-2">{macMini.ip}</div>
                <div className="bg-gray-100 p-2 rounded flex-grow">
                  {message ? (
                    <JsonPrettifier data={message} />
                  ) : 'Awaiting message...'}
                </div>
                {/* This metrics bar reframes user-centric concepts into scientific data points,
                     providing a precise, information-theoretic view of the node's state. */}
                <div className="stats-container mt-2">
                  <div className="stat-item" title="Liveness (Connected/Total Ports)">
                    <FaHeartbeat className="stat-icon" />
                    <span>{liveness}/{totalPorts}</span>
                  </div>
                  <div className="stat-item" title="Replication Factor (Tree Instances)">
                    <FaCodeBranch className="stat-icon" />
                    <span>{replicationFactor}</span>
                  </div>
                  <div className="stat-item" title="Data Hash">
                    <FaHashtag className="stat-icon" />
                    <span className="font-mono text-xs">{dataHash}</span>
                  </div>
                  <div className="stat-item" title="Connections">
                    <FaLink className="stat-icon" />
                    <span>{totalPorts}</span>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-gray-500">Select one or more connected nodes to view their raw data.</div>
        )}
      </div>
    </div>
  );
};

export default RawView;