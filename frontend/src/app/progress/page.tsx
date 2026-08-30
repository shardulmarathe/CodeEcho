"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/Nav";
import { ProgressSparkline } from "@/components/ProgressSparkline";
import { Doodle } from "@/components/sketch/Doodle";
import { SketchBar, SketchBox, SketchPill } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { getMe, listAttempts } from "@/lib/api";
import { getGuestToken } from "@/lib/identity";
import type { AttemptSummary } from "@/lib/types";

const HEADLINE_SKIP = new Set(["delivery", "conciseness", "relevance"]);

type DimAvg = { dimension: string; avg: number; n: number };

function scoreColor(score: number): string {
  return score >= 3.5 ? "var(--echo)" : "var(--amber)";
}

function isScored(a: AttemptSummary): boolean {
  return a.overall_score != null || a.dimensions.length > 0;
}

function chronological(attempts: AttemptSummary[]): AttemptSummary[] {
  return [...attempts].sort((a, b) => (a.created_at ?? "").localeCompare(b.created_at ?? ""));
}

function averageDimensions(attempts: AttemptSummary[], skip?: Set<string>): DimAvg[] {
  const sums = new Map<string, { total: number; n: number }>();
  for (const a of attempts) {
    for (const d of a.dimensions) {
      const name = d.dimension.trim();
      if (!name) continue;
      if (skip?.has(name.toLowerCase())) continue;
      const cur = sums.get(name) ?? { total: 0, n: 0 };
      cur.total += d.score;
      cur.n += 1;
      sums.set(name, cur);
    }
  }
  return [...sums.entries()]
    .map(([dimension, { total, n }]) => ({ dimension, avg: total / n, n }))
    .sort((a, b) => a.avg - b.avg || a.dimension.localeCompare(b.dimension));
}

function formatDate(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const thisYear = d.getFullYear() === new Date().getFullYear();
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: thisYear ? undefined : "numeric",
  });
}

function attemptKind(a: AttemptSummary): string {
  const bucket = (a.bucket ?? "").replace(/_/g, " ");
  const qtype = (a.qtype ?? "").replace(/_/g, " ");
  if (bucket && qtype && bucket !== qtype) return `${qtype} · ${bucket}`;
  return bucket || qtype || "attempt";
}

function fmtScore(n: number, digits = 1): string {
  return n.toFixed(digits);
}

export default function ProgressPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [authAvailable, setAuthAvailable] = useState(false);
  const [attempts, setAttempts] = useState<AttemptSummary[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        // Initialize the same stable browser identity used by practice and listAttempts.
        getGuestToken();
        const me = await getMe();
        if (cancelled) return;
        setAuthenticated(me.authenticated);
        setAuthAvailable(me.auth_configured);
      } catch {
        if (cancelled) return;
        // A guest can still have local history if the optional account probe fails.
        setAuthenticated(false);
      }

      try {
        const rows = await listAttempts();
        if (cancelled) return;
        setAttempts(rows);
      } catch (e) {
        if (cancelled) return;
        setLoadError(e instanceof Error ? e.message : "Could not load browser history.");
      } finally {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const scored = attempts.filter(isScored);
  const contentRank = averageDimensions(scored, HEADLINE_SKIP);
  const weakest = contentRank[0] ?? null;
  const allRank = averageDimensions(scored);
  const chrono = chronological(attempts);
  const overallSeries = chrono
    .map((a) => a.overall_score)
    .filter((n): n is number => n != null);
  const fillerSeries = chrono.map((a) => a.fillers_per_minute);
  const wpmSeries = chrono.map((a) => a.words_per_minute);
  const recent = attempts.slice(0, 20);

  const lastOverall = overallSeries[overallSeries.length - 1];
  const lastFiller = fillerSeries[fillerSeries.length - 1];
  const lastWpm = wpmSeries[wpmSeries.length - 1];

  return (
    <main className="min-h-dvh flex flex-col overflow-x-hidden">
      <Nav />
      <div
        className={`max-w-5xl mx-auto px-4 sm:px-8 py-10 w-full flex-1 flex flex-col ${
          !ready || attempts.length === 0 ? "justify-center" : ""
        }`}
      >
        <div className="mb-10 text-center">
          <p className="eyebrow">
            {authenticated === false ? "this browser · guest history" : "over time"}
          </p>
          <div className="relative inline-block mt-2">
            <h1 className="hand text-4xl md:text-5xl font-bold">Progress</h1>
            <Doodle
              name="squiggle"
              className="text-amber absolute -bottom-3 left-1/2 -translate-x-1/2"
              width={160}
            />
          </div>
        </div>

        {loadError ? (
          <p className="text-sm text-center" style={{ color: "#f87171" }}>
            {loadError}
          </p>
        ) : !ready ? (
          <p className="text-sm text-muted text-center">Loading…</p>
        ) : attempts.length === 0 ? (
          <div className="max-w-xl mx-auto w-full">
            <SketchBox className="text-center space-y-5" padding={40}>
              <p className="hand text-2xl font-bold">Nothing here yet</p>
              <p className="text-sm text-muted max-w-sm mx-auto">
                This is history for this browser&apos;s guest token. Practice a question
                out loud, then scored answers will appear here with trends and history.
              </p>
              <SketchButton
                type="button"
                hand
                onClick={() => router.push("/practice")}
                style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}
              >
                Practice
              </SketchButton>
            </SketchBox>
          </div>
        ) : (
          <div className="space-y-10">
            {authenticated === false && authAvailable && scored.length > 0 && (
              <SketchBox className="space-y-3" padding={20}>
                <p className="font-semibold">Keep this history beyond this browser</p>
                <p className="text-sm text-muted">
                  Sign in with an email code after seeing your results. The existing guest
                  token stays in this browser while CodeEcho claims these attempts for the
                  signed-in account.
                </p>
                <Link
                  href="/sign-in?next=%2Fprogress"
                  className="text-sm font-semibold text-echo underline underline-offset-4"
                >
                  Save history with email code →
                </Link>
              </SketchBox>
            )}
            <SketchBox accent className="text-center space-y-3" padding={32}>
              <p className="eyebrow">weakest content dimension</p>
              {weakest ? (
                <>
                  <div className="relative inline-block">
                    <h2 className="hand text-3xl md:text-4xl font-bold">{weakest.dimension}</h2>
                    <Doodle
                      name="underline"
                      className="text-amber absolute -bottom-2 left-0"
                      width={180}
                    />
                  </div>
                  <p className="text-sm text-muted pt-2">
                    Average {fmtScore(weakest.avg)} / 5 across {weakest.n} scored{" "}
                    {weakest.n === 1 ? "answer" : "answers"}.
                  </p>
                </>
              ) : (
                <>
                  <h2 className="hand text-3xl font-bold">Score a few answers</h2>
                  <p className="text-sm text-muted max-w-md mx-auto">
                    You need a few scored answers before this page can name a weakest
                    content dimension.
                  </p>
                </>
              )}
            </SketchBox>

            <div>
              <p className="eyebrow mb-4">trends</p>
              <div className="grid gap-5 sm:grid-cols-3">
                <SketchBox padding={16} className="space-y-2">
                  <div className="flex items-baseline justify-between gap-2">
                    <p className="text-sm text-muted">Overall score</p>
                    <p className="hand text-2xl font-bold tabular-nums">
                      {lastOverall != null ? fmtScore(lastOverall) : "—"}
                    </p>
                  </div>
                  <ProgressSparkline values={overallSeries} />
                </SketchBox>
                <SketchBox padding={16} className="space-y-2">
                  <div className="flex items-baseline justify-between gap-2">
                    <p className="text-sm text-muted">Fillers / min</p>
                    <p className="hand text-2xl font-bold tabular-nums">
                      {lastFiller != null ? fmtScore(lastFiller) : "—"}
                    </p>
                  </div>
                  <ProgressSparkline values={fillerSeries} color="var(--amber)" />
                </SketchBox>
                <SketchBox padding={16} className="space-y-2">
                  <div className="flex items-baseline justify-between gap-2">
                    <p className="text-sm text-muted">Words / min</p>
                    <p className="hand text-2xl font-bold tabular-nums">
                      {lastWpm != null ? Math.round(lastWpm) : "—"}
                    </p>
                  </div>
                  <ProgressSparkline values={wpmSeries} />
                </SketchBox>
              </div>
            </div>

            <div>
              <p className="eyebrow mb-4">dimension ranking · weakest first</p>
              <SketchBox className="space-y-4">
                {allRank.length === 0 ? (
                  <p className="text-sm text-muted text-center">
                    Score an answer to rank dimensions.
                  </p>
                ) : (
                  allRank.map((d) => (
                    <div key={d.dimension} className="flex items-center gap-3">
                      <span className="w-40 sm:w-52 text-sm shrink-0">{d.dimension}</span>
                      <div className="flex-1 min-w-0">
                        <SketchBar
                          value={d.avg}
                          max={5}
                          height={12}
                          color={scoreColor(d.avg)}
                        />
                      </div>
                      <span
                        className="text-sm font-medium tabular-nums w-12 text-right shrink-0"
                        style={{ color: scoreColor(d.avg) }}
                      >
                        {fmtScore(d.avg)}
                      </span>
                    </div>
                  ))
                )}
              </SketchBox>
            </div>

            <div>
              <div className="flex items-baseline justify-between gap-3 mb-4">
                <p className="eyebrow">recent attempts</p>
                <Link href="/practice" className="text-xs mono text-muted hover:text-echo">
                  practice →
                </Link>
              </div>
              <SketchBox className="space-y-0" padding={8}>
                {recent.map((a, i) => (
                  <div
                    key={a.session_id}
                    className="flex items-center justify-between gap-4 px-4 py-3"
                    style={
                      i > 0
                        ? { borderTop: "1.5px solid var(--border)" }
                        : undefined
                    }
                  >
                    <div className="min-w-0">
                      <p className="font-medium truncate">{a.title || "Untitled attempt"}</p>
                      <div className="flex flex-wrap items-center gap-2 mt-1">
                        <span className="text-xs text-muted">{formatDate(a.created_at)}</span>
                        <SketchPill>{attemptKind(a)}</SketchPill>
                      </div>
                    </div>
                    <span
                      className="hand text-2xl font-bold tabular-nums shrink-0"
                      style={
                        a.overall_score != null
                          ? { color: scoreColor(a.overall_score) }
                          : { color: "var(--muted)" }
                      }
                    >
                      {a.overall_score != null ? fmtScore(a.overall_score) : "—"}
                    </span>
                  </div>
                ))}
              </SketchBox>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
