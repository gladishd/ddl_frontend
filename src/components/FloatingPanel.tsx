"use client";

import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ChevronUp, ChevronDown, X } from "lucide-react";
import MacMiniConfigurator from "./MacMiniConfigurator";
import { useMacMiniContext } from "@/context/MacMiniContext";

interface FloatingPanelProps {
  containerRef: React.RefObject<HTMLDivElement | null>;
}

export default function FloatingPanel({ containerRef }: FloatingPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);
  const offsetRef = useRef({ x: 0, y: 0 });
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [minimized, setMinimized] = useState(false);
  const [visible, setVisible] = useState(true);

  // Use the context
  const { 
    activeView
  } = useMacMiniContext();

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!panelRef.current || !containerRef.current) return;

    const panelRect = panelRef.current.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();

    const offsetX = e.clientX - panelRect.left;
    const offsetY = e.clientY - panelRect.top;

    offsetRef.current = { x: offsetX, y: offsetY };
    draggingRef.current = true;

    e.preventDefault(); // prevent text selection
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!draggingRef.current || !panelRef.current || !containerRef.current) return;
  
    const container = containerRef.current;
    const panel = panelRef.current;
  
    const offset = offsetRef.current;
  
    let newX = e.clientX - container.getBoundingClientRect().left - offset.x;
    let newY = e.clientY - container.getBoundingClientRect().top - offset.y;
  
    // Clamp values to stay within the container
    newX = Math.max(0, Math.min(newX, container.offsetWidth - panel.offsetWidth));
    newY = Math.max(0, Math.min(newY, container.offsetHeight - panel.offsetHeight));
  
    setPosition({ x: newX, y: newY });
  };

  const handleMouseUp = () => {
    draggingRef.current = false;
  };

  useEffect(() => {
    if (containerRef.current && panelRef.current) {
      const updatePosition = () => {
        const container = containerRef.current;
        const panel = panelRef.current;
        if (!container || !panel) return;

        const containerWidth = container.offsetWidth;
        const panelWidth = panel.offsetWidth;
        const containerHeight = container.offsetHeight;
        const panelHeight = panel.offsetHeight;

        // Calculate new position
        let newX = containerWidth - panelWidth - 16; // 16px right margin
        let newY = 16; // 16px top margin

        // Ensure panel stays within container bounds
        newX = Math.max(0, Math.min(newX, containerWidth - panelWidth));
        newY = Math.max(0, Math.min(newY, containerHeight - panelHeight));

        setPosition({ x: newX, y: newY });
      };

      // Initial position
      updatePosition();

      // Add resize event listener
      window.addEventListener("resize", updatePosition);
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);

      return () => {
        window.removeEventListener("resize", updatePosition);
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [containerRef]);

  if (!visible) return null;

  return (
    <div
      ref={panelRef}
      className={cn(
        "absolute z-50 bg-white shadow-lg border rounded-md",
        minimized ? "w-64 h-auto" : "w-64"
      )}
      style={{ top: position.y, left: position.x }}
    >
      <div
        className="flex items-center justify-between px-3 py-2 border-b bg-gray-100 rounded-t-md cursor-move"
        onMouseDown={handleMouseDown}
      >
        <span className="text-sm font-medium">::: Actions</span>
        <div className="flex space-x-1">
          <Button
            size="icon"
            variant="ghost"
            onClick={() => setMinimized((prev) => !prev)}
          >
            {minimized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
          <Button
            size="icon"
            variant="ghost"
            onClick={() => setVisible(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
      {!minimized && (
        <div className="p-3 space-y-2">
          <Button className="w-full">Start Simulation</Button>
          <Button variant="outline" className="w-full">Reset</Button>

          <MacMiniConfigurator 
            multiSelect={true}
          />
        </div>
      )}
    </div>
  );
}
