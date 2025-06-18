"use client";

import { useEffect, useState } from "react";
import { ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * A UI control for returning the Local Observer View (LOV) to the top of the document.
 * In a complex information space, providing a deterministic way to return to a known state
 * is crucial for user orientation. This component acts as a 'time-reversible' user action,
 * instantly resetting the vertical scroll without the "irreversible smash and restart" of a full page reload.
 */
const ScrollToTopOverlay = () => {
  // Manages the visibility of the button based on the user's scroll depth.
  // The control only appears when needed, reducing visual noise.
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // We listen to the scroll event to determine if the overlay should be presented.
    // This is an event-only protocol, reacting to user action rather than polling.
    const toggleVisibility = () => {
      if (window.scrollY > 200) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);

    // On component unmount, the event listener is cleanly removed to prevent memory leaks.
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  // A simple, reliable action to scroll the view to the top.
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <button
      className={cn(
        "fixed bottom-6 right-6 z-50 p-3 rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-opacity duration-300",
        isVisible ? "opacity-100" : "opacity-0 pointer-events-none"
      )}
      onClick={scrollToTop}
      aria-label="Scroll to top"
      title="Scroll to top"
    >
      <ArrowUp className="h-6 w-6" />
    </button>
  );
};

export default ScrollToTopOverlay;