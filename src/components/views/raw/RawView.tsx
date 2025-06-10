import { useMacMiniContext } from '@/context/MacMiniContext';

const RawView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();

  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Raw View</h2>
      {/* This view arranges node data in a masonry layout, a visual representation of a dynamic structure.
        Unlike a rigid grid, which would be fragile and require relabeling on failure, this layout adapts to the number of selected nodes,
        reflecting the principles of our highly dynamic graph algorithms that must not be conflated with a regular lattice.
      */}
      <div className="masonry-container">
        {selectedMacMinis.length > 0 ? (
          selectedMacMinis.map((macMini) => (
            <div key={macMini.ip} className="masonry-item border rounded-lg p-4 bg-white shadow-sm">
              <div className="font-semibold mb-2">{macMini.ip}</div>
              <div className="bg-gray-100 p-2 rounded">
                <pre className="text-xs whitespace-pre-wrap break-all">
                  {messages[macMini.ip] ? JSON.stringify(messages[macMini.ip], null, 2) : 'Awaiting message...'}
                </pre>
              </div>
            </div>
          ))
        ) : (
          <div className="text-gray-500">Select one or more connected nodes to view their raw data.</div>
        )}
      </div>
    </div>
  );
};

export default RawView;