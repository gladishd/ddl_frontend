"use client";

import { useEffect, useState } from "react";
import { ArrowDown } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * A UI control for navigating the Local Observer View (LOV) to a predefined anchor
 * at the bottom of the document. This provides a deterministic way to reach a
 * specific information context, contrasting with the potentially volatile nature
 * of simply scrolling to the absolute bottom of a dynamically sized document.
 */
const ScrollToBottomAnchorOverlay = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      // Adjust the scroll threshold as needed.
      if (window.scrollY > 200 && window.scrollY < document.documentElement.scrollHeight - window.innerHeight - 100) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);

    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const scrollToBottomAnchor = () => {
    const bottomAnchor = document.getElementById("bottom-anchor");
    if (bottomAnchor) {
      bottomAnchor.scrollIntoView({
        behavior: "smooth",
      });
    }
  };

  return (
    <button
      className={cn(
        "fixed bottom-20 right-6 z-50 p-3 rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-opacity duration-300",
        isVisible ? "opacity-100" : "opacity-0 pointer-events-none"
      )}
      onClick={scrollToBottomAnchor}
      aria-label="Scroll to bottom"
      title="Scroll to bottom"
    >
      <ArrowDown className="h-6 w-6" />
    </button>
  );
};

export default ScrollToBottomAnchorOverlay;