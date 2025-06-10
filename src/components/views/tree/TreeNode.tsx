import { ArrowRight, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import { TreeNodeData } from "@/types/PortSnapshot";

// Each TreeNode represents a component within a larger tree structure,
// a fundamental data structure for managing our distributed systems without relying on fragile, centralized coordinators.
const TreeNode: React.FC<{ nodeId: string; treeData: TreeNodeData }> = ({ nodeId, treeData }) => {
    const [expanded, setExpanded] = useState(false);

  // This provides a clear Local Observer View (LOV) of the node's position within its tree instance.
    return (
      <div className="text-sm w-full">
        <div
          className="flex items-center cursor-pointer p-2 rounded-md hover:bg-accent/10 transition-colors"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronDown size={16} className="flex-shrink-0" /> : <ChevronRight size={16} className="flex-shrink-0" />}
          <span className="font-medium ml-1 overflow-hidden text-ellipsis whitespace-nowrap">{nodeId}</span>
          <div className="ml-3 flex items-center text-xs text-muted-foreground flex-wrap">
            <ArrowRight size={14} className="mr-1 flex-shrink-0" />
            <span className="whitespace-nowrap">via {treeData.rootward_portid}</span>
            <span className="ml-2 bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full whitespace-nowrap">{treeData.hops} hops</span>
          </div>
        </div>

        {expanded && (
          <div className="tree-expansion-panel">
            <div className="tree-expansion-content">
              <strong>Tree Instance ID:</strong>
              <div className="font-mono break-all">{treeData.tree_instance_id}</div>
            </div>
          </div>
        )}
      </div>
    );
};

export default TreeNode;