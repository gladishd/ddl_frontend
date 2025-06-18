// This component encapsulates all client-side logic for the main layout,
// including state management for the side menu. By isolating client-specific hooks
// and context providers, we maintain a clean separation from the server-rendered
// RootLayout, creating a more robust and less fragile architecture.
'use client';

import React, { useEffect } from 'react';
import { MenuProvider, useMenu } from '@/context/MenuContext';
import SideMenu from '@/components/layout/SideMenu';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import ScrollToTopOverlay from '@/components/ScrollToTopOverlay';
import ScrollToBottomAnchorOverlay from '@/components/ScrollToBottomAnchorOverlay';

// The LayoutManager is a pure client-side effect handler.
// It observes the state of the MenuContext and applies side effects to the DOM (the body class),
// acting as a bridge between our React-based state machine and the global document structure.
function LayoutManager({ children }: { children: React.ReactNode }) {
  const { isMenuOpen } = useMenu();

  useEffect(() => {
    if (isMenuOpen) {
      document.body.classList.add('menu-open');
    } else {
      document.body.classList.remove('menu-open');
    }
  }, [isMenuOpen]);

  return <>{children}</>;
}

export default function ClientLayoutWrapper({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <MenuProvider>
      <LayoutManager>
        <SideMenu />
        <div className="flex flex-col min-h-screen content-pusher">
          <Navbar />
          <main className="flex-grow" style={{ paddingTop: 'var(--navbar-height)' }}>
            {children}
          </main>
          <Footer />
          <ScrollToTopOverlay />
          <ScrollToBottomAnchorOverlay />
        </div>
      </LayoutManager>
    </MenuProvider>
  );
}