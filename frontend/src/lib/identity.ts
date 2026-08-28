"use client";

// Guest identity + Supabase access token, shared by the API client.
// Guests get a stable random token in localStorage; signed-in users send a
// Supabase access token as Authorization: Bearer. The backend prefers Bearer
// when present and falls back to the guest token.

import { getBrowserClient, supabaseConfigured } from "./supabase";

const GUEST_KEY = "codeecho_guest_token";

export const authEnabled = supabaseConfigured;

export function getGuestToken(): string {
  if (typeof window === "undefined") return "";
  let token = localStorage.getItem(GUEST_KEY);
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem(GUEST_KEY, token);
  }
  return token;
}

export async function getAuthToken(): Promise<string | null> {
  const client = getBrowserClient();
  if (!client) return null;
  try {
    const { data } = await client.auth.getSession();
    return data.session?.access_token ?? null;
  } catch {
    return null;
  }
}
