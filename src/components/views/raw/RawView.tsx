import { useMacMiniContext } from '@/context/MacMiniContext';

const RawView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();

  return (
    <div className="p-2 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Raw View</h2>
      <div className="flex flex-wrap gap-4">
        {selectedMacMinis.length > 0 ? (
          selectedMacMinis.map((macMini) => (
            <div key={macMini.ip} className="border rounded p-4 min-w-[300px]">
              <div className="font-semibold mb-2">{macMini.ip}</div>
              <div className="bg-gray-100 p-2 rounded">
                <pre className="text-xs whitespace-pre-wrap">
                  {messages[macMini.ip] ? JSON.stringify(messages[macMini.ip], null, 2) : 'Awaiting message...'}
                </pre>
              </div>
            </div>
          ))) : (
          <div className="text-gray-500">Select a connected node to view its raw data (since this is what we've got for now).</div>
        )}
      </div>
    </div>
  );
};

export default RawView;