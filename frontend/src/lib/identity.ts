"use client";

// Guest identity + Clerk token registry, shared by the API client.
// Guests get a stable random token in localStorage; logged-in users get a Clerk
// session token attached as a Bearer header. The backend prefers the Bearer
// token when present and falls back to the guest token.

const GUEST_KEY = "codeecho_guest_token";

export const clerkEnabled = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export function getGuestToken(): string {
  if (typeof window === "undefined") return "";
  let token = localStorage.getItem(GUEST_KEY);
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem(GUEST_KEY, token);
  }
  return token;
}

type TokenGetter = () => Promise<string | null>;
let _tokenGetter: TokenGetter | null = null;

/** Registered once by <AuthBridge> so the API client can fetch Clerk tokens. */
export function setTokenGetter(fn: TokenGetter | null) {
  _tokenGetter = fn;
}

export async function getAuthToken(): Promise<string | null> {
  if (!_tokenGetter) return null;
  try {
    return await _tokenGetter();
  } catch {
    return null;
  }
}
