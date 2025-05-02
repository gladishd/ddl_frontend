import { ArrowRight, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import { TreeNodeData } from "@/types/PortSnapshot";

// Tree Node Component
const TreeNode: React.FC<{ nodeId: string; treeData: TreeNodeData }> = ({ nodeId, treeData }) => {
    const [expanded, setExpanded] = useState(false);
    
    return (
      <div className="mb-2 border-l-2 border-blue-300 pl-2 flex-1 min-w-0 max-w-full">
        <div 
          className="flex items-center cursor-pointer flex-wrap" 
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronDown size={16} className="flex-shrink-0" /> : <ChevronRight size={16} className="flex-shrink-0" />}
          <span className="font-medium ml-1 overflow-hidden text-ellipsis whitespace-nowrap">{nodeId}</span>
          <div className="ml-3 flex items-center text-xs text-gray-600 flex-wrap">
            <ArrowRight size={14} className="mr-1 flex-shrink-0" />
            <span className="whitespace-nowrap">via {treeData.rootward_portid}</span>
            <span className="ml-2 bg-blue-100 px-1 rounded whitespace-nowrap">{treeData.hops} hops</span>
          </div>
        </div>
        
        {expanded && (
          <div className="mt-1 ml-6 text-xs">
            <div>Tree Instance: <span className="font-mono break-all">{treeData.tree_instance_id}</span></div>
          </div>
        )}
      </div>
    );
};

export default TreeNode
  