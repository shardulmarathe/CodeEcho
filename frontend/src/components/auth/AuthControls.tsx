"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { claimGuestAttempts } from "@/lib/api";
import { getGuestToken } from "@/lib/identity";
import { getBrowserClient } from "@/lib/supabase";

/**
 * On sign-in, transfers the guest's prior attempts. Renders nothing.
 */
export function AuthBridge() {
  const client = getBrowserClient();

  useEffect(() => {
    if (!client) return;
    const {
      data: { subscription },
    } = client.auth.onAuthStateChange((_event, session) => {
      if (session) {
        const guest = getGuestToken();
        if (guest) claimGuestAttempts().catch(() => {});
      }
    });
    return () => subscription.unsubscribe();
  }, [client]);

  return null;
}

/** Sign-in link / account chip for the nav. */
export function AuthControls() {
  const client = getBrowserClient();
  const [email, setEmail] = useState<string | null | undefined>(undefined);

  useEffect(() => {
    if (!client) {
      setEmail(null);
      return;
    }
    client.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? null);
    });
    const {
      data: { subscription },
    } = client.auth.onAuthStateChange((_event, session) => {
      setEmail(session?.user?.email ?? null);
    });
    return () => subscription.unsubscribe();
  }, [client]);

  if (!client || email === undefined) return null;
  return email ? (
    <Link href="/account" className="text-xs mono hover:text-echo">
      {email}
    </Link>
  ) : (
    <Link
      href="/sign-in"
      className="btn-circle border border-neutral-900 text-xs hover:bg-neutral-50 px-3 py-1"
    >
      Sign in
    </Link>
  );
}
