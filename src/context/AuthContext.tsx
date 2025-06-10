// This context manages the user's authentication state, a critical component
// for a system that must differentiate between anonymous and known actors.
'use client';

import React, { createContext, useState, useContext, ReactNode } from 'react';

interface AuthContextType {
  loggedIn: boolean;
  user: { _id: string, username: string } | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  loggedIn: false,
  user: null,
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // In a real application, this would be determined by checking a token or session.
  // For this integration, we will simulate a logged-out state.
  const [authState] = useState<AuthContextType>({
    loggedIn: false,
    user: null,
    loading: false, // Set to false as we are not performing a real auth check.
  });

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);