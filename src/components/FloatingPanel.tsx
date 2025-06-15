"use client";

import { useRef, useState, useEffect, MouseEvent } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ChevronUp, ChevronDown, X } from "lucide-react";
import MacMiniConfigurator from "./MacMiniConfigurator";
import { useMacMiniContext } from "@/context/MacMiniContext";

interface FloatingPanelProps {
  /** The element that bounds dragging (usually your page wrapper) */
  containerRef: React.RefObject<HTMLDivElement>;
}

export default function FloatingPanel({ containerRef }: FloatingPanelProps) {
  /* ------------------------------------------------------------------ */
  /*  Refs – give all of them an initial value to satisfy TS strict-null */
  /* ------------------------------------------------------------------ */
  const panelRef = useRef<HTMLDivElement | null>(null);
  const draggingRef = useRef<boolean>(false);
  const offsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  /* ------------------------------------------------------------------ */
  /*  Local state                                                       */
  /* ------------------------------------------------------------------ */
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [minimized, setMinimized] = useState(false);
  const [visible, setVisible] = useState(true);

  /* Context – we might eventually change behaviour based on the view   */
  const { activeView } = useMacMiniContext();

  /* ------------------------------------------------------------------ */
  /*  Drag handlers                                                     */
  /* ------------------------------------------------------------------ */
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!panelRef.current || !containerRef.current) return;

    const panelRect = panelRef.current.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();

    offsetRef.current = {
      x: e.clientX - panelRect.left + containerRect.left,
      y: e.clientY - panelRect.top + containerRect.top,
    };
    draggingRef.current = true;
    e.preventDefault(); // stop text-selection
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (
      !draggingRef.current ||
      !panelRef.current ||
      !containerRef.current
    ) return;

    const { left, top } = containerRef.current.getBoundingClientRect();
    const newX = e.clientX - offsetRef.current.x + left;
    const newY = e.clientY - offsetRef.current.y + top;

    const maxX = containerRef.current.offsetWidth - panelRef.current.offsetWidth;
    const maxY = containerRef.current.offsetHeight - panelRef.current.offsetHeight;

    setPosition({
      x: Math.max(0, Math.min(newX, maxX)),
      y: Math.max(0, Math.min(newY, maxY)),
    });
  };

  /* ------------------------------------------------------------------ */
  /*  Lifecycle – attach & clean up listeners                           */
  /* ------------------------------------------------------------------ */
  useEffect(() => {
    const handleMouseUp = () => (draggingRef.current = false);

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  /* ------------------------------------------------------------------ */
  /*  Initial placement on first mount & window-resize                  */
  /* ------------------------------------------------------------------ */
  useEffect(() => {
    const reposition = () => {
      if (!containerRef.current || !panelRef.current) return;
      const c = containerRef.current;
      const p = panelRef.current;
      setPosition({
        x: Math.max(0, c.offsetWidth - p.offsetWidth - 16),
        y: Math.max(0, 16),
      });
    };
    reposition();
    window.addEventListener("resize", reposition);
    return () => window.removeEventListener("resize", reposition);
  }, [containerRef]);

  if (!visible) return null;

  /* ------------------------------------------------------------------ */
  /*  Render                                                            */
  /* ------------------------------------------------------------------ */
  return (
    <div
      ref={panelRef}
      className={cn(
        "absolute z-50 bg-white shadow-lg border rounded-md",
        minimized ? "w-64 h-auto" : "w-64"
      )}
      style={{ left: position.x, top: position.y }}
    >
      {/* ─────── Header / drag handle ─────── */}
      <div
        className="flex items-center justify-between px-3 py-2 border-b bg-gray-100 rounded-t-md cursor-move"
        onMouseDown={handleMouseDown}
      >
        <span className="text-sm font-medium">::: Actions</span>
        <div className="flex gap-1">
          <Button size="icon" variant="ghost" onClick={() => setMinimized(v => !v)}>
            {minimized ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
          </Button>
          <Button size="icon" variant="ghost" onClick={() => setVisible(false)}>
            <X className="size-4" />
          </Button>
        </div>
      </div>

      {/* ─────── Body ─────── */}
      {!minimized && (
        <div className="p-3 space-y-2">
          <Button className="w-full">Start Simulation</Button>
          <Button variant="outline" className="w-full">
            Reset
          </Button>

          <MacMiniConfigurator multiSelect />
        </div>
      )}
    </div>
  );
}
