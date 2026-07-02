"use client";

// Hand-drawn CTA: wobbly corners + hard offset shadow; presses "into" the shadow.
// primary = teal fill; ghost = outline.

import type { ButtonHTMLAttributes } from "react";

interface SketchButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  hand?: boolean; // use the hand-drawn font
}

export function SketchButton({
  children,
  variant = "primary",
  hand = false,
  className = "",
  style,
  ...rest
}: SketchButtonProps) {
  const base =
    "wobble sketch-shadow sketch-press inline-flex items-center justify-center gap-2 font-semibold transition-colors cursor-pointer disabled:opacity-45 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--echo)]";
  const skin =
    variant === "primary"
      ? { background: "var(--echo)", color: "var(--on-echo)", border: "2px solid var(--ink)" }
      : { background: "var(--surface)", color: "var(--fg)", border: "2px solid var(--border)" };
  return (
    <button
      className={`${base} ${hand ? "hand" : ""} ${className}`}
      style={{ padding: "0.7rem 1.4rem", fontSize: "1rem", ...skin, ...style }}
      {...rest}
    >
      {children}
    </button>
  );
}
