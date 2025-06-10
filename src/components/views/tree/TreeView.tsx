import React, { useState } from 'react';
import { useMacMiniContext } from '@/context/MacMiniContext';
import { MacMini } from '@/types/MacMini';
import { MessageData } from '@/types/PortSnapshot';
import PortStatus from '@/components/views/tree/PortStatus';
import TreeNode from '@/components/views/tree/TreeNode';
import { HoveredPortInfo } from '@/types/HoveredPort';

const TreeView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();
  const [hoveredPortInfo, setHoveredPortInfo] = useState<HoveredPortInfo | null>(null);

  const renderMacMiniDetails = (macMini: MacMini) => {
    const message = messages[macMini.ip] as MessageData | undefined;
    if (!message) return null;

    return (
      <div key={macMini.ip} className="mb-4 flex flex-col w-[400px] border rounded p-4 shadow-sm">
        <div className="text-sm font-bold mb-2 border-b pb-1">{message.node_id} ({macMini.ip})</div>

        {/* Port Status Section */}
        {message.snapshots && Object.keys(message.snapshots).length > 0 && (
          <div className="mb-4">
            <div className="text-xs uppercase font-semibold text-gray-500 mb-1">Network Interfaces</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(message.snapshots).map(([port, snapshot]) => (
                <div
                  key={port}
                  className="flex-1 min-w-[300px] max-w-full"
                  onMouseEnter={() => setHoveredPortInfo({
                    macMiniIp: macMini.ip,
                    portId: snapshot.name,
                    neighborPortId: snapshot.connection?.neighbor_portid || null
                  })}
                  onMouseLeave={() => setHoveredPortInfo(null)}
                >
                  <PortStatus port={port} snapshot={snapshot} hoveredPortInfo={hoveredPortInfo} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trees Section */}
        {message.trees_dict && Object.keys(message.trees_dict).length > 0 && (
          <div>
            <div className="text-xs uppercase font-semibold text-gray-500 mb-1">Tree Connections</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(message.trees_dict).map(([nodeId, treeData]) => (
                <div key={nodeId} className="flex-1 min-w-[300px] max-w-full border rounded p-2">
                  <TreeNode nodeId={nodeId} treeData={treeData} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-2 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Tree View</h2>
      <div className="flex flex-wrap gap-4">
        {selectedMacMinis.length > 0
          ? selectedMacMinis.map((macMini) => (renderMacMiniDetails(macMini)))
          : <div className="text-gray-500">Select a connected node to view the Matrix type of details.</div>
        }
      </div>
    </div>
  );
};

export default TreeView;