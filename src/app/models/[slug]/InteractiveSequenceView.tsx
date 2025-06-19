'use client';

import React, { useState } from 'react';
import { PanelRightOpen, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import ModelDisplay from './ModelDisplay';

interface SequenceData {
  title: string;
  script: string;
  output: string | null;
  image: string;
  secondImage?: string;
}

interface InteractiveSequenceViewProps {
  sequenceData: SequenceData[];
}

const InteractiveSequenceView: React.FC<InteractiveSequenceViewProps> = ({ sequenceData }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeModelIndex, setActiveModelIndex] = useState<number | null>(null);

  const activeModel = activeModelIndex !== null ? sequenceData[activeModelIndex] : null;

  const handleToggleSidebar = () => {
    setIsSidebarOpen(open => !open);
  };

  const handleSelectModel = (index: number) => {
    setActiveModelIndex(index);
    setIsSidebarOpen(true);
  };

  return (
    <div className={cn('sequence-layout-container', { 'sidebar-open': isSidebarOpen })}>
      {/* TOGGLE BUTTON */}
      <div className="sequence-sidebar-toggle">
        <Button
          size="icon"
          variant="outline"
          onClick={handleToggleSidebar}
          aria-label={isSidebarOpen ? 'Close simulation output' : 'Open simulation output'}
        >
          {isSidebarOpen ? <X /> : <PanelRightOpen />}
        </Button>
      </div>

      {/* MAIN CODE LISTING */}
      <div className="sequence-main-content">
        {sequenceData.map((data, index) => (
          <div key={index} className="model-code-container">
            <h2 className="model-code-title">{data.title}</h2>
            <pre className="code-block python-syntax">
              <code>{data.script}</code>
            </pre>
            <div className="model-select-overlay">
              <Button style={{ backgroundColor: "white", color: "black" }} onClick={() => handleSelectModel(index)}>
                View Output &amp; Visualization
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* SIDEBAR */}
      <aside className={cn('sequence-sidebar', { open: isSidebarOpen })}>
        <div className="sequence-sidebar-header">
          <h3 className="sequence-sidebar-title">Simulation Output</h3>
          <Button size="icon" variant="ghost" onClick={handleToggleSidebar} aria-label="Close">
            <X />
          </Button>
        </div>
        <div className="sequence-sidebar-content">
          {activeModel ? (
            <>
              <h4 className="text-lg font-bold mb-4">{activeModel.title}</h4>
              {activeModel.output && (
                <div className="code-section">
                  <h3 className="code-header">Simulated Output</h3>
                  <pre className="code-block output-syntax">
                    <code>{activeModel.output.trim()}</code>
                  </pre>
                </div>
              )}
              <div className="code-section mt-4">
                <h3 className="code-header">Visualization</h3>
                <div className="bg-gray-800 p-2 rounded-lg">
                  <img
                    src={activeModel.image}
                    alt={`Visualization for ${activeModel.title}`}
                    className="w-full h-auto rounded-md border border-gray-600"
                  />
                </div>
                {activeModel.secondImage && (
                  <div className="bg-gray-800 p-2 rounded-lg mt-4">
                    <img
                      src={activeModel.secondImage}
                      alt={`Second visualization for ${activeModel.title}`}
                      className="w-full h-auto rounded-md border border-gray-600"
                    />
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>Select a model to view its output.</p>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
};

export default InteractiveSequenceView;
