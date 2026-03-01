"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Key, ExternalLink, CheckCircle } from "lucide-react";

interface ClerkSetupGuardProps {
  children: React.ReactNode;
}

export function ClerkSetupGuard({ children }: ClerkSetupGuardProps) {
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we're in skip-auth mode
    const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';

    if (skipAuth) {
      // Skip auth mode enabled - allow access
      setIsConfigured(true);
      return;
    }

    // Check if Clerk is configured
    const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '';

    if (!publishableKey || publishableKey.includes('PLACEHOLDER')) {
      setIsConfigured(false);
      setError('Clerk authentication is not configured');
    } else {
      // Validate the key format
      if (!publishableKey.startsWith('pk_')) {
        setIsConfigured(false);
        setError('Invalid Clerk publishable key format');
      } else {
        setIsConfigured(true);
      }
    }
  }, []);

  // Loading state
  if (isConfigured === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication setup...</p>
        </div>
      </div>
    );
  }

  // Not configured - show setup screen
  if (!isConfigured) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-4">
              <AlertCircle className="h-8 w-8 text-yellow-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Authentication Setup Required
            </h1>
            <p className="text-gray-600">
              {error || 'Clerk authentication needs to be configured to use this dashboard'}
            </p>
          </div>

          <div className="space-y-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h2 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Key className="h-5 w-5 mr-2 text-blue-600" />
                Quick Setup Steps
              </h2>
              <ol className="space-y-3 text-sm">
                <li className="flex">
                  <span className="font-semibold mr-2 text-blue-600">1.</span>
                  <div>
                    <span>Create a free account at </span>
                    <a
                      href="https://dashboard.clerk.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline inline-flex items-center"
                    >
                      dashboard.clerk.com
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </a>
                  </div>
                </li>
                <li className="flex">
                  <span className="font-semibold mr-2 text-blue-600">2.</span>
                  <span>Create a new application in Clerk dashboard</span>
                </li>
                <li className="flex">
                  <span className="font-semibold mr-2 text-blue-600">3.</span>
                  <span>Copy your API keys from the dashboard</span>
                </li>
                <li className="flex">
                  <span className="font-semibold mr-2 text-blue-600">4.</span>
                  <div>
                    <span>Update your </span>
                    <code className="bg-gray-100 px-2 py-1 rounded text-xs">.env.local</code>
                    <span> file:</span>
                  </div>
                </li>
              </ol>

              <div className="mt-4 bg-gray-900 text-gray-100 rounded p-3 font-mono text-xs overflow-x-auto">
                <div className="text-green-400"># .env.local</div>
                <div>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<span className="text-yellow-300">pk_test_YOUR_KEY_HERE</span></div>
                <div>CLERK_SECRET_KEY=<span className="text-yellow-300">sk_test_YOUR_SECRET_HERE</span></div>
              </div>

              <p className="text-xs text-gray-600 mt-3">
                After updating the file, restart your development server.
              </p>
            </div>

            <div className="border-t pt-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                Alternative Options
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Development Mode</p>
                    <p className="text-gray-600">
                      You can run without authentication in development by setting{' '}
                      <code className="bg-gray-100 px-1 rounded">NEXT_PUBLIC_SKIP_AUTH=true</code>
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Use Existing Keys</p>
                    <p className="text-gray-600">
                      If you have Clerk configured in another project, you can reuse those keys temporarily
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center space-x-4 pt-4">
              <a
                href="https://dashboard.clerk.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Key className="h-5 w-5 mr-2" />
                Setup Clerk Account
              </a>
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Configured - render children
  return <>{children}</>;
}