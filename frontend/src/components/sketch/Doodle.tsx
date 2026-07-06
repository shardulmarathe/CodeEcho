"use client";

// Hand-drawn accent SVGs. Stroke uses currentColor, so set color via className
// (e.g. text-echo / text-amber). Decorative → aria-hidden.

type DoodleName =
  | "underline"
  | "arrow"
  | "circle"
  | "star"
  | "squiggle"
  | "scribble";

const PATHS: Record<DoodleName, { vb: string; el: React.ReactNode; fill?: boolean }> = {
  underline: {
    vb: "0 0 120 12",
    el: <path d="M2 7 C 30 11, 60 3, 90 8 S 116 6, 118 5" />,
  },
  arrow: {
    vb: "0 0 80 40",
    el: (
      <>
        <path d="M4 20 C 25 8, 50 30, 72 16" />
        <path d="M62 10 L74 15 L64 24" />
      </>
    ),
  },
  circle: {
    vb: "0 0 120 60",
    el: (
      <path d="M60 4 C 20 4, 6 20, 8 32 C 10 50, 45 56, 70 55 C 104 53, 116 36, 112 24 C 108 10, 80 3, 55 5" />
    ),
  },
  star: {
    vb: "0 0 40 40",
    el: (
      <>
        <path d="M20 5 L20 35" />
        <path d="M5 20 L35 20" />
        <path d="M9 9 L31 31" />
        <path d="M31 9 L9 31" />
      </>
    ),
  },
  squiggle: {
    vb: "0 0 120 20",
    el: <path d="M2 10 Q 12 2, 22 10 T 42 10 T 62 10 T 82 10 T 102 10 T 118 10" />,
  },
  scribble: {
    vb: "0 0 100 100",
    el: (
      <path d="M10 30 C 40 10, 70 40, 90 20 M15 55 C 45 35, 70 65, 92 45 M12 80 C 42 60, 68 88, 90 70" />
    ),
  },
};

export function Doodle({
  name,
  className = "text-echo",
  width = 120,
  strokeWidth = 2.4,
  draw = false,
  style,
}: {
  name: DoodleName;
  className?: string;
  width?: number;
  strokeWidth?: number;
  draw?: boolean; // animate stroke "draw-on"
  style?: React.CSSProperties;
}) {
  const d = PATHS[name];
  return (
    <svg
      viewBox={d.vb}
      width={width}
      className={className}
      style={{ overflow: "visible", maxWidth: "100%", ...style }}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <g className={draw ? "draw-path" : ""} style={draw ? { ["--len" as string]: 400 } : undefined}>
        {d.el}
      </g>
    </svg>
  );
}
