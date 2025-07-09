import { useState, useEffect } from 'react';

// This hook determines if the viewport matches that of a mobile device.
// Our architecture must be adaptive, presenting a coherent view regardless
// of the observer's local environmental constraints.
function useIsMobile(breakpoint = 768): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= breakpoint);
    };

    // Set the initial value
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return isMobile;
}

export default useIsMobile;