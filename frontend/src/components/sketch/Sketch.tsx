"use client";

// Hand-drawn UI primitives (dark-code + sketch fusion). SketchBox overlays a rough.js
// wobbly border on a filled surface with a hard offset shadow — the signature look.
// Same export names/props as before so existing screens pick up the sketch style.

import { useEffect, useRef, useState } from "react";
import rough from "roughjs";

function cssVar(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

interface SketchBoxProps {
  children: React.ReactNode;
  className?: string;
  padding?: number;
  roughness?: number; // legacy prop (still honored)
  tilt?: "l" | "r" | null; // slight rotation, pinned-note feel
  accent?: boolean; // teal border instead of neutral
}

export function SketchBox({
  children,
  className = "",
  padding = 24,
  roughness = 1.5,
  tilt = null,
  accent = false,
}: SketchBoxProps) {
  const boxRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() =>
      setSize({ w: el.clientWidth, h: el.clientHeight })
    );
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || size.w < 4 || size.h < 4) return;
    svg.innerHTML = "";
    const rc = rough.svg(svg);
    const stroke = accent ? cssVar("--amber", "#eab308") : cssVar("--border", "#1b1b1b");
    const node = rc.rectangle(3, 3, size.w - 6, size.h - 6, {
      roughness,
      bowing: 1.4,
      stroke,
      strokeWidth: accent ? 2 : 1.6,
    });
    svg.appendChild(node);
  }, [size, accent, roughness]);

  const tiltClass = tilt === "l" ? "tilt-l" : tilt === "r" ? "tilt-r" : "";

  return (
    <div
      ref={boxRef}
      className={`relative wobble sketch-shadow ${tiltClass} ${className}`}
      style={{ padding, background: "var(--surface)" }}
    >
      <svg
        ref={svgRef}
        className="pointer-events-none absolute inset-0 h-full w-full"
        style={{ overflow: "visible" }}
        aria-hidden="true"
      />
      <div className="relative">{children}</div>
    </div>
  );
}

interface SketchBarProps {
  value: number;
  max?: number;
  height?: number;
  color?: string;
  smooth?: boolean;
}

export function SketchBar({ value, max = 100, height = 12, color, smooth = true }: SketchBarProps) {
  const pct = max > 0 ? Math.max(0, Math.min(1, value / max)) * 100 : 0;
  return (
    <div
      className="w-full overflow-hidden"
      style={{
        height,
        background: "var(--surface-2)",
        border: "1.5px solid var(--border)",
        borderRadius: "8px 12px 8px 12px",
      }}
    >
      <div
        className={smooth ? "h-full transition-[width] duration-500" : "h-full"}
        style={{
          width: `${pct}%`,
          background: color || "var(--echo)",
          borderRadius: "8px 12px 8px 12px",
        }}
      />
    </div>
  );
}

interface SketchPillProps {
  children: React.ReactNode;
  filled?: boolean;
  className?: string;
}

export function SketchPill({ children, filled = false, className = "" }: SketchPillProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 text-xs mono ${className}`}
      style={
        filled
          ? { background: "var(--echo)", color: "var(--on-echo)", borderRadius: "9px 13px 9px 13px" }
          : {
              border: "1.5px solid var(--border)",
              color: "var(--muted)",
              borderRadius: "9px 13px 9px 13px",
            }
      }
    >
      {children}
    </span>
  );
}
