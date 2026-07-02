"use client";

type MascotState = "idle" | "listening" | "analyzing" | "happy" | "concerned";

interface MascotProps {
  state?: MascotState;
  size?: number;
}

export function Mascot({ state = "idle", size = 80 }: MascotProps) {
  const eyeScale = state === "listening" ? 1.2 : state === "analyzing" ? 0.8 : 1;
  const mouthPath =
    state === "happy"
      ? "M 30 58 Q 40 68 50 58"
      : state === "concerned"
        ? "M 30 62 Q 40 56 50 62"
        : state === "listening"
          ? "M 32 58 Q 40 62 48 58"
          : "M 32 58 L 48 58";

  return (
    <div className="relative inline-flex items-center justify-center">
      {state === "analyzing" && (
        <div
          className="absolute rounded-full border-2 border-neutral-900 pulse-ring"
          style={{ width: size + 20, height: size + 20 }}
        />
      )}
      <svg
        width={size}
        height={size}
        viewBox="0 0 80 80"
        className={state === "idle" ? "mascot-bounce" : ""}
        aria-label="FillerAI mascot"
      >
        {/* Head */}
        <circle cx="40" cy="40" r="36" fill="white" stroke="#0a0a0a" strokeWidth="2.5" />

        {/* Eyes */}
        <ellipse
          cx="28"
          cy="36"
          rx="5"
          ry={6 * eyeScale}
          fill="#0a0a0a"
        />
        <ellipse
          cx="52"
          cy="36"
          rx="5"
          ry={6 * eyeScale}
          fill="#0a0a0a"
        />

        {/* Mouth */}
        <path
          d={mouthPath}
          fill="none"
          stroke="#0a0a0a"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* Listening indicator */}
        {state === "listening" && (
          <>
            <circle cx="68" cy="40" r="3" fill="#0a0a0a" className="pulse-ring" />
            <circle cx="12" cy="40" r="3" fill="#0a0a0a" className="pulse-ring" style={{ animationDelay: "0.5s" }} />
          </>
        )}
      </svg>
    </div>
  );
}
