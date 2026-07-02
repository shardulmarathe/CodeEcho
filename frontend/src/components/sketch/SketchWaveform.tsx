"use client";

// A hand-drawn "voice" waveform: wobbly bars with a slight tilt (sketchy, not clean
// lines). Mostly ink, with the odd yellow bar for the accent. Animates when `active`.

const SEED = [0.55, 0.9, 0.35, 1, 0.6, 0.42, 0.85, 0.3, 0.72, 0.5, 0.95, 0.4, 0.8, 0.48, 0.66, 0.38];

export function SketchWaveform({
  bars = 36,
  height = 72,
  active = true,
  className = "",
}: {
  bars?: number;
  height?: number;
  active?: boolean;
  className?: string;
}) {
  return (
    <div
      className={`flex items-center justify-center gap-1.5 ${className}`}
      style={{ height }}
      aria-hidden
    >
      {Array.from({ length: bars }).map((_, i) => {
        const base = SEED[i % SEED.length];
        const tilt = ((i % 3) - 1) * 5; // -5 / 0 / +5 deg wobble
        const isAccent = i % 6 === 3;
        return (
          <span
            key={i}
            className="flex items-end"
            style={{
              height: `${30 + base * 70}%`,
              width: 4 + (i % 2),
              transform: `rotate(${tilt}deg)`,
              color: isAccent ? "var(--amber)" : "var(--fg)",
            }}
          >
            <span
              className={active ? "sketch-wave-bar" : ""}
              style={{
                background: "currentColor",
                width: "100%",
                height: "100%",
                borderRadius: "46% 54% 50% 50% / 34% 30% 70% 66%",
                animationDelay: active ? `${(i % 8) * 0.08}s` : undefined,
                opacity: active ? undefined : 0.5,
              }}
            />
          </span>
        );
      })}
    </div>
  );
}
