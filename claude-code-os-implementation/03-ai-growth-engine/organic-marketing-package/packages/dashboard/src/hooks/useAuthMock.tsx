"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface MockUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  imageUrl: string;
}

interface MockAuthContextType {
  isLoaded: boolean;
  isSignedIn: boolean;
  user: MockUser | null;
  signIn: () => void;
  signOut: () => void;
  organization: any;
}

const MockAuthContext = createContext<MockAuthContextType | undefined>(undefined);

/**
 * Mock authentication provider for development without Clerk
 * This allows the dashboard to function in development mode without requiring Clerk setup
 */
export function MockAuthProvider({ children }: { children: ReactNode }) {
  const [isSignedIn, setIsSignedIn] = useState(true);
  const [user, setUser] = useState<MockUser | null>(null);

  useEffect(() => {
    // Auto sign in with mock user in development
    if (process.env.NEXT_PUBLIC_SKIP_AUTH === 'true') {
      setUser({
        id: 'dev-user-123',
        email: 'dev@example.com',
        firstName: 'Dev',
        lastName: 'User',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=dev',
      });
      setIsSignedIn(true);
    }
  }, []);

  const signIn = () => {
    setUser({
      id: 'dev-user-123',
      email: 'dev@example.com',
      firstName: 'Dev',
      lastName: 'User',
      imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=dev',
    });
    setIsSignedIn(true);
  };

  const signOut = () => {
    setUser(null);
    setIsSignedIn(false);
  };

  const value = {
    isLoaded: true,
    isSignedIn,
    user,
    signIn,
    signOut,
    organization: {
      id: 'dev-org-123',
      name: 'Development Organization',
      slug: 'dev-org',
    },
  };

  return (
    <MockAuthContext.Provider value={value}>
      {children}
    </MockAuthContext.Provider>
  );
}

/**
 * Hook to use mock authentication
 * Falls back to Clerk hooks when available
 */
export function useAuthMock() {
  const context = useContext(MockAuthContext);

  if (context === undefined) {
    // If no mock context, try to use Clerk
    try {
      // This will be replaced with actual Clerk import when available
      const { useUser, useOrganization } = require("@clerk/nextjs");
      const clerkUser = useUser();
      const clerkOrg = useOrganization();

      return {
        isLoaded: clerkUser.isLoaded,
        isSignedIn: clerkUser.isSignedIn,
        user: clerkUser.user,
        organization: clerkOrg.organization,
        signIn: () => console.log('Sign in via Clerk UI'),
        signOut: () => console.log('Sign out via Clerk UI'),
      };
    } catch (e) {
      // Clerk not available, return mock defaults
      return {
        isLoaded: true,
        isSignedIn: false,
        user: null,
        organization: null,
        signIn: () => {},
        signOut: () => {},
      };
    }
  }

  return context;
}