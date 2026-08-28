"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/Nav";
import { CircleChoice } from "@/components/sketch/CircleChoice";
import { SketchBox } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { getMe, updateMe } from "@/lib/api";
import { getBrowserClient } from "@/lib/supabase";

const LEVELS = [
  { v: "intern", title: "Intern" },
  { v: "new-grad", title: "New grad" },
  { v: "mid", title: "Mid-level" },
  { v: "senior", title: "Senior" },
];

export default function AccountPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const [role, setRole] = useState("Software Engineer");
  const [seniority, setSeniority] = useState("mid");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const me = await getMe();
        if (cancelled) return;
        if (!me.authenticated) {
          router.replace("/sign-in");
          return;
        }
        setEmail(me.profile?.email ?? null);
        setRole(me.profile?.target_role || "Software Engineer");
        setSeniority(me.profile?.seniority || "mid");
        setReady(true);
      } catch (e) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : "Could not load your account.";
        if (/authentication|unauthorized|401/i.test(msg)) {
          router.replace("/sign-in");
          return;
        }
        setLoadError(msg);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      const profile = await updateMe({
        target_role: role.trim() || "Software Engineer",
        seniority,
      });
      if (profile) {
        setRole(profile.target_role || "Software Engineer");
        setSeniority(profile.seniority || "mid");
        setEmail(profile.email ?? email);
      }
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save.");
    } finally {
      setBusy(false);
    }
  };

  const signOut = async () => {
    const client = getBrowserClient();
    if (client) await client.auth.signOut();
    router.replace("/");
  };

  return (
    <main className="min-h-dvh flex flex-col overflow-x-hidden">
      <Nav />
      <div className="max-w-3xl mx-auto px-4 sm:px-8 py-10 w-full flex-1 flex flex-col justify-center">
        <div className="mb-8 text-center">
          <h1 className="hand text-4xl md:text-5xl font-bold">Account</h1>
          {email && <p className="text-muted text-sm mt-2 mono">{email}</p>}
        </div>

        {loadError ? (
          <p className="text-sm text-center" style={{ color: "#f87171" }}>
            {loadError}
          </p>
        ) : !ready ? (
          <p className="text-sm text-muted text-center">Loading…</p>
        ) : (
          <form onSubmit={save} className="flex flex-col items-center gap-10">
            <div className="w-full max-w-xl space-y-2">
              <p className="eyebrow text-center">target role</p>
              <SketchBox padding={4}>
                <input
                  type="text"
                  value={role}
                  onChange={(e) => {
                    setRole(e.target.value);
                    setSaved(false);
                  }}
                  disabled={busy}
                  placeholder="Software Engineer"
                  className="w-full p-4 text-base bg-transparent focus:outline-none"
                  style={{ border: "none", boxShadow: "none" }}
                />
              </SketchBox>
            </div>

            <div className="flex flex-col items-center gap-4">
              <p className="eyebrow">who are you?</p>
              <div className="flex flex-wrap justify-center gap-8">
                {LEVELS.map((l) => (
                  <CircleChoice
                    key={l.v}
                    title={l.title}
                    size={144}
                    selected={seniority === l.v}
                    onPick={() => {
                      setSeniority(l.v);
                      setSaved(false);
                    }}
                  />
                ))}
              </div>
            </div>

            <div className="flex flex-wrap gap-3 justify-center">
              <SketchButton
                type="submit"
                hand
                disabled={busy}
                style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}
              >
                {busy ? "Saving…" : saved ? "Saved" : "Save"}
              </SketchButton>
              <SketchButton type="button" variant="ghost" disabled={busy} onClick={signOut}>
                Sign out
              </SketchButton>
            </div>

            {error && (
              <p className="text-sm" style={{ color: "#f87171" }}>
                {error}
              </p>
            )}
          </form>
        )}
      </div>
    </main>
  );
}
