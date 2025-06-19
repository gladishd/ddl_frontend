import React from 'react';

interface ModelDisplayProps {
  title: string;
  script: string;
  output: string | null;
  image: string;
  secondImage?: string;
}

const ModelDisplay: React.FC<ModelDisplayProps> = ({ title, script, output, image, secondImage }) => {
  return (
    <div className="python-model-container">
      <h2 className="text-2xl font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">{title}</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="code-section">
          <h3 className="code-header">Emulator Code (Python)</h3>
          <pre className="code-block python-syntax"><code>{script.trim()}</code></pre>
        </div>
        <div>
          {output && (
            <div className="code-section">
              <h3 className="code-header">Simulated Output</h3>
              <pre className="code-block output-syntax"><code>{output.trim()}</code></pre>
            </div>
          )}
          <div className="code-section">
            <h3 className="code-header">Visualization</h3>
            <div className="bg-gray-800 p-2 rounded-lg">
              <img src={image} alt={`Visualization for ${title}`} className="w-full h-auto rounded-md border border-gray-600" />
            </div>
            {secondImage && (
              <div className="bg-gray-800 p-2 rounded-lg mt-4">
                <img src={secondImage} alt={`Second visualization for ${title}`} className="w-full h-auto rounded-md border border-gray-600" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelDisplay;