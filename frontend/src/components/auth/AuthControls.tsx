"use client";

import { SignInButton, UserButton, useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { claimGuestAttempts } from "@/lib/api";
import { getGuestToken, setTokenGetter } from "@/lib/identity";

/**
 * Registers Clerk's token getter with the API client and, on sign-in, transfers
 * the guest's prior attempts to their new account. Renders nothing.
 * Only mounted when Clerk is configured (inside <ClerkProvider>).
 */
export function AuthBridge() {
  const { isSignedIn, getToken } = useAuth();

  useEffect(() => {
    setTokenGetter(() => getToken());
    return () => setTokenGetter(null);
  }, [getToken]);

  useEffect(() => {
    if (isSignedIn) {
      const guest = getGuestToken();
      if (guest) claimGuestAttempts(guest).catch(() => {});
    }
  }, [isSignedIn]);

  return null;
}

/** Sign-in button / user avatar for the nav. */
export function AuthControls() {
  const { isLoaded, isSignedIn } = useAuth();
  if (!isLoaded) return null;
  return isSignedIn ? (
    <UserButton />
  ) : (
    <SignInButton mode="modal">
      <button className="btn-circle border border-neutral-900 text-xs hover:bg-neutral-50">
        Sign in
      </button>
    </SignInButton>
  );
}
