"use client";

/**
 * Mock Sign Up Page for development without Clerk
 */
function MockSignUp() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold">Sign Up</h2>
          <p className="mt-2 text-gray-600">Development Mode - Authentication Disabled</p>
        </div>
        <div className="mt-8 space-y-4">
          <p className="text-sm text-gray-500">
            You are running in development mode with NEXT_PUBLIC_SKIP_AUTH=true.
            Account creation is disabled and you're automatically signed in.
          </p>
          <a
            href="/"
            className="block w-full rounded-md bg-blue-600 px-4 py-2 text-center text-white hover:bg-blue-700 transition-colors"
          >
            Continue to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}

/**
 * Sign-up page using Clerk authentication
 * The [[...sign-up]] catch-all route allows Clerk to handle all sign-up flows
 * including email/password, OAuth providers, email verification, etc.
 *
 * In development mode with NEXT_PUBLIC_SKIP_AUTH=true, shows a mock sign-up page
 */
export default function SignUpPage() {
  // Check if we're in skip-auth mode
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
  const hasClerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
                      !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('PLACEHOLDER');

  // In skip-auth mode, show mock sign-up
  if (skipAuth || !hasClerkKey) {
    return <MockSignUp />;
  }

  // Try to use Clerk SignUp component
  try {
    const { SignUp } = require("@clerk/nextjs");

    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <SignUp
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg",
            },
          }}
        />
      </div>
    );
  } catch (error) {
    // Fallback to mock if Clerk isn't available
    return <MockSignUp />;
  }
}