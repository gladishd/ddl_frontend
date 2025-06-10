"use client";

import React, { useRef, useState } from "react";
import { useMacMiniContext } from "@/context/MacMiniContext";
import { Button } from "@/components/ui/button";
import { LayoutGrid, LayoutList, GitFork, LineChart, ChevronDown } from "lucide-react";
import FloatingPanel from "@/components/FloatingPanel";
import TreeView from "@/components/views/tree/TreeView";
import RawView from "./views/raw/RawView";
import DAGView from "./views/dag/DAGView";
import AnalysisView from "./views/analysis/AnalysisView";

// A direct manipulation of the view provides operators with different Observer Views of the system.
// This dropdown menu, inspired by clean UI principles, allows for scalable addition of future analysis tools.
const ViewSwitcher = () => {
  const { activeView, setActiveView } = useMacMiniContext();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const views = [
    { id: "tree", label: "Tree", icon: LayoutGrid },
    { id: "raw", label: "Raw", icon: LayoutList },
    { id: "dag", label: "DAG", icon: GitFork },
    { id: "analysis", label: "Analysis", icon: LineChart },
  ];

  const activeViewData = views.find(v => v.id === activeView) || views[0];

  // This effect handles closing the dropdown when clicking outside of it.
  // It's a fundamental aspect of creating a non-intrusive, excellent user interface.
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <Button variant="outline" size="sm" onClick={() => setIsOpen(!isOpen)}>
        <activeViewData.icon className="w-4 h-4 mr-2" />
        {activeViewData.label}
        <ChevronDown className="w-4 h-4 ml-2" />
      </Button>
      {isOpen && (
        <div className="daedalus-menu-dropdown mt-1">
          {views.map(view => (
            <div key={view.id} className="daedalus-menu-item" onClick={() => { setActiveView(view.id as any); setIsOpen(false); }}>
              <div className="daedalus-menu-icon-container">
                <view.icon className="daedalus-menu-icon" />
              </div>
              <div className="daedalus-menu-text-container">
                <span className="daedalus-menu-label">{view.label}</span>
              </div>
            </div>
          ))}
        </div>
      )}
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
      case "raw":
        return <RawView />;
      case "dag":
        return <DAGView />;
      case "analysis":
        return <AnalysisView />;
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
        className="relative w-full h-[calc(100vh-8rem)] border rounded bg-white shadow-inner"
      >
        <FloatingPanel containerRef={containerRef} />
        {renderCurrentView()}
      </div>
    </div>
  );
};

export default DashboardContent;