"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SketchReveal } from "@/components/sketch/SketchReveal";
import { SketchWaveform } from "@/components/sketch/SketchWaveform";
import { CircleChoice } from "@/components/sketch/CircleChoice";
import { Doodle } from "@/components/sketch/Doodle";

const MODES = [
  { href: "/interview", title: "Mock Interview", desc: "Guided questions with live follow-ups", float: "float" },
  { href: "/practice", title: "Practice Question", desc: "One question, deep feedback, retry", float: "float-delay" },
];

export function ModeSelect() {
  const router = useRouter();
  const [picked, setPicked] = useState<string | null>(null);

  const pick = (href: string) => {
    if (picked) return;
    setPicked(href);
    setTimeout(() => router.push(href), 420);
  };

  return (
    <div className="flex flex-col items-center gap-12 py-6 w-full">
      <SketchReveal delay={40}>
        <div className="relative inline-block">
          <h2 className="hand text-4xl sm:text-5xl md:text-6xl font-bold">How do you want to practice?</h2>
          <Doodle name="squiggle" className="text-amber absolute -bottom-5 left-1/2 -translate-x-1/2" width={240} />
        </div>
      </SketchReveal>

      <div
        className="flex flex-wrap items-center justify-center gap-12 sm:gap-16 md:gap-28 pt-4"
        style={{
          opacity: picked ? 0 : 1,
          transform: picked ? "scale(0.85)" : "scale(1)",
          transition: "opacity 0.4s ease, transform 0.4s ease",
        }}
      >
        {MODES.map((m, i) => (
          <SketchReveal key={m.href} delay={160 + i * 130}>
            <CircleChoice title={m.title} desc={m.desc} size={340} floatClass={m.float} onPick={() => pick(m.href)} />
          </SketchReveal>
        ))}
      </div>

      <SketchReveal delay={460} className="w-full flex justify-center pt-6">
        <SketchWaveform bars={48} height={64} active={!picked} className="w-full max-w-2xl opacity-80" />
      </SketchReveal>
    </div>
  );
}
