"use client";

import Link from "next/link";
import { useEffect } from "react";
import { Doodle } from "@/components/sketch/Doodle";
import { ScorecardView } from "@/components/ScorecardView";
import { SAMPLE_SCORECARD } from "@/fixtures/sample-scorecard";
import { warmBackend } from "@/lib/api";

export default function Home() {
  // Start waking the (free-tier, spun-down) backend now, so the ~1 min cold start
  // overlaps browsing the sample instead of the first question generation.
  useEffect(() => {
    warmBackend();
  }, []);

  return (
    <main className="min-h-dvh w-full overflow-x-hidden px-4 py-6 sm:px-6 sm:py-10">
      <div className="mx-auto grid w-full max-w-7xl items-start gap-10 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:gap-14">
        <section className="flex min-w-0 flex-col items-start pt-2 lg:sticky lg:top-10 lg:pt-8">
          <p className="eyebrow">SWE interview practice · reasoning + delivery</p>
          <div className="relative mt-3 inline-block">
            <p className="hand text-5xl font-bold tracking-tight sm:text-6xl">
              Code<span className="text-echo">Echo</span>
            </p>
            <Doodle
              name="underline"
              className="absolute -bottom-3 left-0 w-full text-amber"
              width={250}
              draw
            />
          </div>

          <h1 className="mt-9 max-w-xl font-display text-3xl font-bold leading-tight sm:text-5xl">
            See how an interview answer lands—before the real interview.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-muted sm:text-lg">
            CodeEcho turns a spoken software-engineering interview answer into a dual-axis
            scorecard for reasoning and delivery.
          </p>

          <div className="mt-7 flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:flex-wrap">
            <a
              href="#sample-scorecard"
              className="wobble sketch-shadow sketch-press inline-flex min-h-12 w-full cursor-pointer items-center justify-center border-2 border-border bg-echo px-6 py-3 font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-echo sm:w-auto"
              style={{ color: "var(--on-echo)" }}
            >
              View the sample scorecard ↓
            </a>
            <Link
              href="/practice"
              className="wobble sketch-press inline-flex min-h-12 w-full items-center justify-center border-2 border-border bg-surface px-6 py-3 font-semibold text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-echo sm:w-auto"
            >
              Practice one question →
            </Link>
          </div>
          <p className="mt-4 text-xs text-muted">
            Inspect the worked example without an account or microphone.
          </p>
        </section>

        <section id="sample-scorecard" className="min-w-0 scroll-mt-4" aria-labelledby="sample-heading">
          <div className="wobble sticky top-2 z-20 mb-3 flex w-fit max-w-full flex-wrap items-center gap-2 border border-border bg-surface p-1 pr-3">
            <span className="wobble bg-amber px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-fg">
              Sample
            </span>
            <h2 id="sample-heading" className="text-sm font-semibold">
              Worked example · not a visitor result
            </h2>
          </div>
          <p className="mb-4 text-sm leading-relaxed text-muted">
            Example prompt: “Walk me through a technically challenging project and your role in it.”
          </p>
          <ScorecardView scorecard={SAMPLE_SCORECARD} />
          <div className="mt-8 flex flex-col items-start gap-3 border-t-2 border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted">Ready to get feedback on an answer of your own?</p>
            <Link
              href="/practice"
              className="wobble sketch-shadow sketch-press inline-flex min-h-12 w-full items-center justify-center border-2 border-border bg-echo px-6 py-3 font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-echo sm:w-auto"
              style={{ color: "var(--on-echo)" }}
            >
              Practice one question →
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
