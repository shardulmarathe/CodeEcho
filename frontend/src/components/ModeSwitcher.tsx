"use client";

// The two mode "circles" from the landing, now as small left-rail icons. The active
// one is highlighted; clicking the other switches flows.

import Link from "next/link";
import { usePathname } from "next/navigation";

const MODES = [
  {
    href: "/interview",
    label: "Mock Interview",
    icon: (
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M4 5h11a3 3 0 0 1 3 3v4a3 3 0 0 1-3 3H9l-4 3v-3H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z" />
      </svg>
    ),
  },
  {
    href: "/practice",
    label: "Practice Question",
    icon: (
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <rect x="9" y="3" width="6" height="11" rx="3" />
        <path d="M6 11a6 6 0 0 0 12 0M12 17v3" />
      </svg>
    ),
  },
];

export function ModeSwitcher() {
  const path = usePathname();
  return (
    <div className="flex gap-4">
      {MODES.map((m) => {
        const active = path.startsWith(m.href);
        return (
          <Link
            key={m.href}
            href={m.href}
            className="flex flex-col items-center gap-1.5 group"
            aria-current={active ? "page" : undefined}
          >
            <span
              className="flex h-14 w-14 items-center justify-center rounded-full transition-transform group-hover:scale-105 group-active:scale-95"
              style={{
                border: `2px solid ${active ? "var(--amber)" : "var(--border)"}`,
                background: active ? "var(--amber)" : "var(--surface)",
                color: active ? "#1a1206" : "var(--muted)",
                boxShadow: active ? "3px 3px 0 var(--ink)" : "none",
              }}
            >
              {m.icon}
            </span>
            <span
              className="text-[10px] mono leading-none text-center max-w-[4.5rem]"
              style={{ color: active ? "var(--fg)" : "var(--muted)" }}
            >
              {m.label}
            </span>
          </Link>
        );
      })}
    </div>
  );
}
