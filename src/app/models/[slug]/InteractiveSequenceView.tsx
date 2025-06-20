'use client';

import React, { useState, useEffect, useRef } from 'react';
import { PanelRightOpen, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Syntax highlighter imports
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface SequenceData {
  title: string;
  script: string;
  output: string | null;
  image: string;
  secondImage?: string;
  thirdImage?: string;
  fourthImage?: string;
}

interface InteractiveSequenceViewProps {
  sequenceData: SequenceData[];
}

const InteractiveSequenceView: React.FC<InteractiveSequenceViewProps> = ({ sequenceData }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeModelIndex, setActiveModelIndex] = useState<number>(0);
  const mainContentRef = useRef<HTMLDivElement>(null);

  // refs for each .model-code-container
  const itemRefs = useRef<Array<HTMLDivElement | null>>([]);

  // Auto-open on mount if there is any data
  useEffect(() => {
    if (sequenceData.length > 0) {
      setIsSidebarOpen(true);
    }
  }, [sequenceData]);

  // Watch scroll so that whenever a code block comes into view,
  // we update activeModelIndex and re-open the sidebar.
  useEffect(() => {
    const root = mainContentRef.current;
    if (!root) return;

    const items = itemRefs.current.filter(Boolean) as HTMLDivElement[];
    const observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const idx = items.indexOf(entry.target as HTMLDivElement);
            if (idx !== -1) {
              setActiveModelIndex(idx);
              setIsSidebarOpen(true);
            }
          }
        }
      },
      { root, threshold: 0.6 }
    );

    items.forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, [sequenceData]);

  const activeModel = sequenceData[activeModelIndex];
  const toggleSidebar = () => setIsSidebarOpen(open => !open);

  // Helper to change index AND scroll into view
  const goToIndex = (newIndex: number) => {
    setActiveModelIndex(newIndex);
    setIsSidebarOpen(true);
    const el = itemRefs.current[newIndex];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className={cn('sequence-layout-container', { 'sidebar-open': isSidebarOpen })}>
      {/* TOGGLE BUTTON */}
      <div className="sequence-sidebar-toggle">
        <Button
          size="icon"
          variant="outline"
          onClick={toggleSidebar}
          aria-label={isSidebarOpen ? 'Close simulation output' : 'Open simulation output'}
        >
          {isSidebarOpen ? <X /> : <PanelRightOpen />}
        </Button>
      </div>

      {/* MAIN CODE LISTING */}
      <div className="sequence-main-content" ref={mainContentRef}>
        {sequenceData.map((data, index) => (
          <div
            key={index}
            className="model-code-container"
            ref={el => { itemRefs.current[index] = el; }}  // <-- fixed: use block-bodied callback
          >
            <h2 className="model-code-title">{data.title}</h2>

            {/* SYNTAX-HIGHLIGHTED PYTHON */}
            <SyntaxHighlighter
              language="python"
              style={materialDark}
              wrapLongLines={true}
              customStyle={{
                margin: 0,
                borderRadius: 0,
                backgroundColor: 'transparent',
                padding: '1rem 1.25rem'
              }}
            >
              {data.script.trim()}
            </SyntaxHighlighter>

            {/* OVERLAY: only when sidebar is closed AND this is the active block */}
            {!isSidebarOpen && activeModelIndex === index && (
              <div className="model-select-overlay">
                <Button size="sm" variant="outline" onClick={() => goToIndex(index)}>
                  View Simulation Output
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* SIDEBAR */}
      <aside className={cn('sequence-sidebar', { open: isSidebarOpen })}>
        <div className="sequence-sidebar-header">
          <h3 className="sequence-sidebar-title">Simulation Output</h3>
          <Button size="icon" variant="ghost" onClick={toggleSidebar} aria-label="Close">
            <X />
          </Button>
        </div>

        {/* ←/→ NAV */}
        <div className="flex justify-between px-4 py-2 border-b border-gray-700">
          <Button
            size="sm"
            variant="outline"
            disabled={activeModelIndex === 0}
            onClick={() => goToIndex(Math.max(activeModelIndex - 1, 0))}
          >
            ← Prev
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={activeModelIndex === sequenceData.length - 1}
            onClick={() => goToIndex(Math.min(activeModelIndex + 1, sequenceData.length - 1))}
          >
            Next →
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
                {activeModel.image && (
                  <div className="bg-gray-800 p-2 rounded-lg mb-4">
                    <img
                      src={activeModel.image}
                      alt={`Visualization for ${activeModel.title} (1)`}
                      className="w-full h-auto rounded-md border border-gray-600"
                    />
                  </div>
                )}
                {activeModel.secondImage && (
                  <div className="bg-gray-800 p-2 rounded-lg mb-4">
                    <img
                      src={activeModel.secondImage}
                      alt={`Visualization for ${activeModel.title} (2)`}
                      className="w-full h-auto rounded-md border border-gray-600"
                    />
                  </div>
                )}
                {activeModel.thirdImage && (
                  <div className="bg-gray-800 p-2 rounded-lg mb-4">
                    <img
                      src={activeModel.thirdImage}
                      alt={`Visualization for ${activeModel.title} (3)`}
                      className="w-full h-auto rounded-md border border-gray-600"
                    />
                  </div>
                )}
                {activeModel.fourthImage && (
                  <div className="bg-gray-800 p-2 rounded-lg">
                    <img
                      src={activeModel.fourthImage}
                      alt={`Visualization for ${activeModel.title} (4)`}
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
