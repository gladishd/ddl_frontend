"use client";

import React, { useRef, useEffect } from "react";
import { useMacMiniContext } from "@/context/MacMiniContext";
import { Button } from "@/components/ui/button";
import { Layout, Grid, List } from "lucide-react";
import FloatingPanel from "@/components/FloatingPanel";
import TreeView from "@/components/views/TreeView";

const ViewSwitcher = () => {
  const { activeView, setActiveView } = useMacMiniContext();
  
  return (
    <div className="flex gap-2">
      <Button 
        variant={activeView === "tree" ? "default" : "outline"} 
        size="sm"
        onClick={() => setActiveView("tree")}
      >
        <Layout className="w-4 h-4 mr-1" />
        Tree
      </Button>
      <Button 
        variant={activeView === "grid" ? "default" : "outline"} 
        size="sm"
        onClick={() => setActiveView("grid")}
      >
        <Grid className="w-4 h-4 mr-1" />
        Grid
      </Button>
      <Button 
        variant={activeView === "list" ? "default" : "outline"} 
        size="sm"
        onClick={() => setActiveView("list")}
      >
        <List className="w-4 h-4 mr-1" />
        List
      </Button>
    </div>
  );
};

const DashboardContent = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { activeView, isClient } = useMacMiniContext();

  const renderCurrentView = () => {
    switch (activeView) {
      case "tree":
        return <TreeView />;
      case "grid":
        return <TreeView />;
      case "list":
        return <TreeView />;
      default:
        return <TreeView />;
    }
  };

  if (!isClient) return null;

  return (
    <div className="relative min-h-screen bg-gray-100 p-6">
      <header className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Network Dashboard</h1>
            <p className="text-muted-foreground">Visualize and interact with your Mac Mini network</p>
          </div>
          <ViewSwitcher />
        </div>
      </header>

      <div
        ref={containerRef}
        className="relative w-full h-[calc(100vh-8rem)] border rounded bg-white"
      >
        <FloatingPanel containerRef={containerRef} />
        {renderCurrentView()}
      </div>
    </div>
  );
};

export default DashboardContent;
