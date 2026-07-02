"use client";

import Link from "next/link";
import { clerkEnabled } from "@/lib/identity";
import { AuthControls } from "@/components/auth/AuthControls";

export function Nav() {
  return (
    <nav className="border-b hairline">
      <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
        <Link
          href="/"
          className="hand text-2xl font-bold tracking-tight inline-flex items-center"
        >
          code<span className="text-echo">echo</span>
          <span className="text-amber cursor-blink ml-0.5">_</span>
        </Link>
        <div className="flex items-center gap-4 text-xs mono text-muted">
          {clerkEnabled && <AuthControls />}
        </div>
      </div>
    </nav>
  );
}
