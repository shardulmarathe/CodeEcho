"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/Nav";
import { SketchBox } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { getBrowserClient } from "@/lib/supabase";

export default function SignInPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGoogle, setShowGoogle] = useState(true);

  useEffect(() => {
    const reason = new URLSearchParams(window.location.search).get("error");
    if (reason === "otp_expired" || reason === "exchange_failed" || reason === "missing_code") {
      setError("Email apps often open that link before you do, which burns it. Use the 6-digit code instead.");
    } else if (reason === "config") {
      setError("Sign-in isn’t configured on this server.");
    }
  }, []);

  useEffect(() => {
    const client = getBrowserClient();
    if (!client) {
      setReady(true);
      return;
    }
    client.auth.getUser().then(({ data }) => {
      if (data.user) router.replace("/account");
      else setReady(true);
    });
  }, [router]);

  const redirectTo = () => `${window.location.origin}/auth/callback`;

  const sendCode = async (e: FormEvent) => {
    e.preventDefault();
    const client = getBrowserClient();
    if (!client) return;
    const trimmed = email.trim();
    if (!trimmed) return;
    setBusy(true);
    setError(null);
    const { error: err } = await client.auth.signInWithOtp({
      email: trimmed,
    });
    setBusy(false);
    if (err) {
      setError(err.message);
      return;
    }
    setSent(true);
  };

  const verifyCode = async (e: FormEvent) => {
    e.preventDefault();
    const client = getBrowserClient();
    if (!client) return;
    const token = code.replace(/\s/g, "");
    if (token.length < 6) return;
    setBusy(true);
    setError(null);
    const { error: err } = await client.auth.verifyOtp({
      email: email.trim(),
      token,
      type: "email",
    });
    setBusy(false);
    if (err) {
      setError(err.message);
      return;
    }
    router.replace("/account");
  };

  const google = async () => {
    const client = getBrowserClient();
    if (!client) return;
    setBusy(true);
    setError(null);
    const { error: err } = await client.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: redirectTo() },
    });
    if (err) {
      setShowGoogle(false);
      setBusy(false);
    }
  };

  const client = getBrowserClient();

  return (
    <main className="min-h-dvh flex flex-col overflow-x-hidden">
      <Nav />
      <div className="max-w-xl mx-auto px-4 sm:px-8 py-10 w-full flex-1 flex flex-col justify-center">
        <div className="mb-8 text-center">
          <h1 className="hand text-4xl md:text-5xl font-bold">Sign in</h1>
          <p className="text-muted text-sm mt-2">A 6-digit code to your inbox. No password.</p>
        </div>

        {!ready ? (
          <p className="text-sm text-muted text-center">Loading…</p>
        ) : !client ? (
          <p className="text-sm text-muted text-center">Sign-in isn&rsquo;t available right now.</p>
        ) : sent ? (
          <form onSubmit={verifyCode} className="flex flex-col items-center gap-6">
            <p className="hand text-2xl text-center">Check your email</p>
            <p className="text-sm text-muted text-center">
              Enter the 6-digit code sent to {email.trim()}. Ignore any link in that email.
            </p>
            <div className="w-full space-y-2">
              <p className="eyebrow text-center">code</p>
              <SketchBox padding={4}>
                <input
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  pattern="[0-9]*"
                  maxLength={8}
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/[^\d]/g, ""))}
                  disabled={busy}
                  placeholder="123456"
                  className="w-full p-4 text-base text-center tracking-[0.4em] bg-transparent focus:outline-none"
                  style={{ border: "none", boxShadow: "none" }}
                />
              </SketchBox>
            </div>
            <SketchButton
              type="submit"
              hand
              disabled={busy || code.replace(/\s/g, "").length < 6}
              style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}
            >
              {busy ? "Signing in…" : "Sign in"}
            </SketchButton>
            <SketchButton
              type="button"
              variant="ghost"
              disabled={busy}
              onClick={() => {
                setSent(false);
                setCode("");
                setError(null);
              }}
            >
              Use a different email
            </SketchButton>
            {error && (
              <p className="text-sm text-center" style={{ color: "#f87171" }}>
                {error}
              </p>
            )}
          </form>
        ) : (
          <form onSubmit={sendCode} className="flex flex-col items-center gap-6">
            <div className="w-full space-y-2">
              <p className="eyebrow text-center">email</p>
              <SketchBox padding={4}>
                <input
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={busy}
                  placeholder="you@example.com"
                  className="w-full p-4 text-base bg-transparent focus:outline-none"
                  style={{ border: "none", boxShadow: "none" }}
                />
              </SketchBox>
            </div>

            <SketchButton
              type="submit"
              hand
              disabled={busy || !email.trim()}
              style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}
            >
              {busy ? "Sending…" : "Send code"}
            </SketchButton>

            {showGoogle && (
              <SketchButton type="button" variant="ghost" disabled={busy} onClick={google}>
                Continue with Google
              </SketchButton>
            )}

            {error && (
              <p className="text-sm text-center" style={{ color: "#f87171" }}>
                {error}
              </p>
            )}
          </form>
        )}
      </div>
    </main>
  );
}
