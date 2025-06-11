"use client";

import React, { useEffect, useRef } from 'react';

// Declare the WolframCloud object to satisfy TypeScript
declare const WolframCloud: any;

interface WolframNotebookEmbedProps {
  notebookUrl: string;
}

const WolframNotebookEmbed: React.FC<WolframNotebookEmbedProps> = ({ notebookUrl }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const scriptLoaded = useRef(false);

  useEffect(() => {
    const loadWolframScript = () => {
      const script = document.createElement('script');
      script.src = 'https://www.wolframcloud.com/static/embedded.js';
      script.onload = () => {
        if (containerRef.current) {
          WolframCloud.embed(notebookUrl, containerRef.current);
        }
      };
      document.head.appendChild(script);
      scriptLoaded.current = true;
    };

    if (typeof WolframCloud === 'undefined') {
      if (!scriptLoaded.current) {
        loadWolframScript();
      }
    } else if (containerRef.current) {
      WolframCloud.embed(notebookUrl, containerRef.current);
    }
  }, [notebookUrl]);

  return (
    <div ref={containerRef} className="wolfram-notebook-container w-full my-4" style={{ minHeight: '600px' }}>
      {/* The Wolfram Notebook will be embedded here */}
    </div>
  );
};

export default WolframNotebookEmbed;