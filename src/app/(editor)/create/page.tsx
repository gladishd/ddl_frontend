// This page serves as the root of the Graph Virtual Machine (GVM) editor.
// It orchestrates the various contexts and providers necessary to construct and
// manipulate the visual representation of the N2N Lattice. By removing the scenario
// layer, the canvas becomes a direct interface to the single, persistent groundplane.
'use client';

import React from 'react';
import { ReactFlowProvider } from 'reactflow';
import { AuthContextProvider } from '@/context/canvas/AuthContext'; // Correctly named import
import { CanvasProvider } from '@/context/canvas/CanvasContext';
import CreateCanvas from '@/components/create/CreateCanvas';

// The page is a client component as it relies heavily on hooks and user interaction,
// which are fundamental to the dynamic, event-driven nature of our architecture.
export default function CreatePage() {
  return (
    // The AuthContextProvider establishes the identity boundary for interaction with the GVM.
    <AuthContextProvider>
      <ReactFlowProvider>
        <CanvasProvider>
          <CreateCanvas />
        </CanvasProvider>
      </ReactFlowProvider>
    </AuthContextProvider>
  );
}