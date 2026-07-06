"use client";

import { useState } from "react";
import { IntroSequence } from "@/components/IntroSequence";
import { ModeSelect } from "@/components/ModeSelect";

export default function Home() {
  const [phase, setPhase] = useState<"intro" | "choose">("intro");
  const [leaving, setLeaving] = useState(false);

  // Fade the intro out, then swap to the mode-select (which rises in via SketchReveal).
  const start = () => {
    setLeaving(true);
    setTimeout(() => {
      setPhase("choose");
      setLeaving(false);
    }, 280);
  };

  return (
    <main className="min-h-dvh w-full flex flex-col items-center justify-center px-4 sm:px-6 py-10 overflow-x-hidden">
      <div
        className="w-full max-w-7xl flex flex-col items-center justify-center"
        style={{
          opacity: leaving ? 0 : 1,
          transform: leaving ? "translateY(-10px) scale(0.98)" : "none",
          transition: "opacity 0.28s ease, transform 0.28s ease",
        }}
      >
        {phase === "intro" ? <IntroSequence onStart={start} /> : <ModeSelect />}
      </div>
    </main>
  );
}
