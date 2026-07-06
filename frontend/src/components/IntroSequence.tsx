"use client";

import { SketchBox } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { SketchReveal } from "@/components/sketch/SketchReveal";
import { SketchWaveform } from "@/components/sketch/SketchWaveform";
import { Doodle } from "@/components/sketch/Doodle";

// Three hand-drawn comic panels telling the tiny story, then the wordmark + CTA.
const strokeProps = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.4,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function PanelQuestion() {
  return (
    <svg viewBox="0 0 120 90" className="w-full text-echo" {...strokeProps} aria-hidden>
      {/* terminal window */}
      <rect x="14" y="18" width="92" height="58" rx="6" />
      <path d="M14 30 H106" />
      <circle cx="24" cy="24" r="2" />
      <circle cx="32" cy="24" r="2" />
      {/* prompt + big question mark */}
      <path d="M26 46 l8 6 l-8 6" />
      <path d="M52 62 q6 -18 16 -14 q8 4 2 12 q-4 5 -4 9" />
      <circle cx="66" cy="72" r="1.4" fill="currentColor" />
    </svg>
  );
}

function PanelAnswer() {
  return (
    <svg viewBox="0 0 120 90" className="w-full text-fg" {...strokeProps} aria-hidden>
      {/* head */}
      <circle cx="34" cy="46" r="16" />
      <path d="M28 44 h2 M39 44 h2" />
      <path d="M29 54 q5 4 11 0" />
      {/* speech bubble with waveform */}
      <path d="M60 30 h44 a6 6 0 0 1 6 6 v22 a6 6 0 0 1 -6 6 H74 l-8 8 v-8 h-6 a6 6 0 0 1 -6 -6 V36 a6 6 0 0 1 6 -6 z" />
      <path d="M70 52 v-8 M78 56 v-16 M86 54 v-12 M94 58 v-20 M102 52 v-8" className="text-echo" stroke="currentColor" />
    </svg>
  );
}

function PanelScore() {
  return (
    <svg viewBox="0 0 120 90" className="w-full text-echo" {...strokeProps} aria-hidden>
      {/* scorecard */}
      <rect x="20" y="16" width="62" height="60" rx="6" />
      <path d="M30 34 h30 M30 46 h40 M30 58 h22" />
      {/* big check + spark */}
      <path d="M74 52 l10 12 l20 -30" strokeWidth={3.4} />
      <path d="M100 20 l0 8 M96 24 l8 0" />
    </svg>
  );
}

const PANELS = [
  { el: <PanelQuestion />, caption: "A real question appears." },
  { el: <PanelAnswer />, caption: "You explain it out loud." },
  { el: <PanelScore />, caption: "CodeEcho scores your reasoning & delivery." },
];

export function IntroSequence({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-col items-center text-center gap-10 w-full">
      <div className="grid md:grid-cols-3 gap-8 w-full max-w-5xl">
        {PANELS.map((p, i) => (
          <SketchReveal key={i} delay={200 + i * 240}>
            <SketchBox padding={22} tilt={i === 0 ? "l" : i === 2 ? "r" : null}>
              <div className="flex flex-col items-center gap-3">
                <div className="w-full">{p.el}</div>
                <p className="hand-body text-base text-muted leading-snug">{p.caption}</p>
              </div>
            </SketchBox>
          </SketchReveal>
        ))}
      </div>

      <SketchReveal delay={1050} className="flex flex-col items-center gap-4">
        <div className="relative inline-block">
          <h1 className="hand text-6xl sm:text-7xl md:text-8xl font-bold tracking-tight">
            Code<span className="text-echo">Echo</span>
          </h1>
          <Doodle name="underline" className="text-amber absolute -bottom-4 left-0 w-full" width={320} draw />
        </div>
        <p className="text-muted max-w-lg text-base sm:text-lg leading-relaxed mt-3 px-2">
          Answer real interview questions out loud. Get scored on what you say
          <span className="text-fg"> and </span>how you say it.
        </p>
      </SketchReveal>

      <SketchReveal delay={1300}>
        <SketchWaveform bars={44} height={80} className="w-full max-w-xl" />
      </SketchReveal>

      <SketchReveal delay={1550}>
        <div className="relative inline-block">
          <SketchButton hand style={{ fontSize: "1.5rem", padding: "1rem 2.6rem" }} onClick={onStart}>
            Get Started!
          </SketchButton>
          <Doodle name="arrow" className="text-amber absolute -right-20 top-1 hidden md:block" width={64} />
        </div>
      </SketchReveal>
    </div>
  );
}
