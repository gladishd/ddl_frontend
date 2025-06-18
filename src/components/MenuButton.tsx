// This component provides a reusable, context-aware button for controlling the main side menu.
// By encapsulating the logic and presentation, we create a decoupled UI element that can be
// placed anywhere in the component tree under the MenuProvider.
'use client';

import React from 'react';
import { FaBars } from 'react-icons/fa';
import { useMenu } from '@/context/MenuContext';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface MenuButtonProps {
  className?: string;
}

const MenuButton: React.FC<MenuButtonProps> = ({ className }) => {
  const { toggleMenu } = useMenu();

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={toggleMenu}
      className={cn("menu-button", className)}
      title="Toggle Menu"
    >
      <FaBars className="h-5 w-5" />
    </Button>
  );
};

export default MenuButton;