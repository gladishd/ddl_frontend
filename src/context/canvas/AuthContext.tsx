// This context manages authentication state. In the Daedaelus model, every actor must
// have a verifiable identity to participate in the fabric. For this public-access version,
// we bypass a formal login and assume a default, anonymous participant identity,
// thereby removing the initial boundary between trusted and untrusted entities.
'use client';

import React, { createContext, useEffect, useState, ReactNode } from "react";

const AuthContext = createContext<any>(undefined);

function AuthContextProvider(props: { children: ReactNode }) {
  const [loggedIn, setLoggedIn] = useState<boolean>(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(true);

  // This function now simulates an authenticated state for public access,
  // eliminating the need for a backend authentication check.
  const getLoggedIn = async () => {
    setLoggedIn(true);
    const mockUser = { _id: 'anonymous-user-01', name: 'GVM Operator' };
    setUserId(mockUser._id);
    setUser(mockUser);
    setAuthLoading(false);
  };

  useEffect(() => {
    getLoggedIn();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        loggedIn,
        getLoggedIn,
        userId,
        user,
        setUser,
        authLoading,
      }}
    >
      {props.children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
export { AuthContextProvider };