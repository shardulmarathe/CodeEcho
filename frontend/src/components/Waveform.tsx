"use client";

// The "echo" signature motif — a row of bars that read as an audio waveform.
// `active` animates them (recording / listening); otherwise they sit static.

interface WaveformProps {
  bars?: number;
  active?: boolean;
  height?: number;
  className?: string;
  color?: string;
  /** stretch bars evenly across the full container width (an audio "track") */
  spread?: boolean;
}

// Deterministic per-bar heights/delays (no RNG → stable SSR)
const SEED = [0.5, 0.85, 0.35, 1, 0.6, 0.45, 0.9, 0.3, 0.7, 0.55, 0.95, 0.4, 0.8, 0.5, 0.65];

export function Waveform({
  bars = 28,
  active = false,
  height = 40,
  className = "",
  color,
  spread = false,
}: WaveformProps) {
  return (
    <div
      className={`flex items-center overflow-hidden max-w-full ${spread ? "w-full justify-between" : "justify-center gap-[3px]"} ${className}`}
      style={{ height }}
      aria-hidden
    >
      {Array.from({ length: bars }).map((_, i) => {
        const base = SEED[i % SEED.length];
        return (
          <span
            key={i}
            className={active ? "echo-bar" : ""}
            style={{
              height: `${base * 100}%`,
              width: 3,
              borderRadius: 2,
              background: color || "var(--echo)",
              opacity: active ? undefined : 0.25 + base * 0.5,
              animationDelay: active ? `${(i % 7) * 0.09}s` : undefined,
            }}
          />
        );
      })}
    </div>
  );
}
