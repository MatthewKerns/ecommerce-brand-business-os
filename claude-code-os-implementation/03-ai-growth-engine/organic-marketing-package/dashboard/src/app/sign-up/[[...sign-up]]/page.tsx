import { SignUp } from "@clerk/nextjs";

/**
 * Sign-up page using Clerk authentication
 * The [[...sign-up]] catch-all route allows Clerk to handle all sign-up flows
 * including email/password, OAuth providers, email verification, etc.
 */
export default function SignUpPage() {
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
}
