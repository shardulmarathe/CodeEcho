"use client";

import { useEffect, useRef, useState } from "react";
import rough from "roughjs";

function cssVar(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

// A hand-drawn (rough.js) circular choice button. Reused across the mode-select and the
// interview setup so the whole flow reads as circles converting into circles.
export function CircleChoice({
  title,
  desc,
  size = 220,
  floatClass = "",
  selected = false,
  onPick,
}: {
  title: string;
  desc?: string;
  size?: number;
  floatClass?: string;
  selected?: boolean;
  onPick: () => void;
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hover, setHover] = useState(false);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    svg.innerHTML = "";
    const rc = rough.svg(svg);
    const stroke = selected ? cssVar("--amber", "#eab308") : cssVar("--fg", "#1b1b1b");
    const c = size / 2;
    svg.appendChild(rc.ellipse(c, c, size - 16, size - 16, { roughness: 2, stroke, strokeWidth: selected ? 3.4 : 2.6 }));
    svg.appendChild(rc.ellipse(c, c, size - 22, size - 24, { roughness: 2.8, stroke, strokeWidth: 1.2 }));
  }, [size, selected]);

  return (
    <button
      onClick={onPick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      className={`group relative flex flex-col items-center justify-center text-center ${floatClass} focus-visible:outline-none cursor-pointer max-w-full`}
      style={{
        width: `min(${size}px, 82vw)`,
        aspectRatio: "1 / 1",
        transition: "transform 0.25s cubic-bezier(0.2,0.8,0.2,1)",
        transform: hover ? "scale(1.06) rotate(-1deg)" : "scale(1)",
      }}
    >
      <svg
        viewBox={`0 0 ${size} ${size}`}
        ref={svgRef}
        className="absolute inset-0 h-full w-full transition-[filter] duration-200"
        style={{ overflow: "visible", filter: hover ? "drop-shadow(5px 7px 0 var(--amber))" : "none" }}
        aria-hidden
      />
      <span className="hand text-2xl md:text-3xl font-bold px-4" style={{ color: selected ? "var(--amber)" : "var(--fg)" }}>
        {title}
      </span>
      {desc && (
        <span className="hand-body mt-2 max-w-[11rem] text-sm text-muted leading-snug px-4">{desc}</span>
      )}
    </button>
  );
}
