import type { HealthStatus } from "@/lib/api";
import type { BudgetStatus, Question } from "@/lib/types";
import type { WakeState } from "@/lib/useServiceReadiness";

export function HonestyBanner({
  title,
  children,
  tone = "warning",
}: {
  title: string;
  children: React.ReactNode;
  tone?: "info" | "warning" | "error";
}) {
  const color = tone === "error" ? "#b91c1c" : tone === "warning" ? "var(--amber)" : "var(--echo)";
  return (
    <div className="panel border-l-4 p-4 text-left" style={{ borderLeftColor: color }} role="status">
      <p className="text-sm font-semibold">{title}</p>
      <p className="mt-1 text-xs leading-relaxed text-muted">{children}</p>
    </div>
  );
}

export function ServiceStatusBanners({
  wakeState,
  health,
  budget,
  onRetry,
}: {
  wakeState: WakeState;
  health: HealthStatus | null;
  budget: BudgetStatus | null;
  onRetry: () => void;
}) {
  const hasBanner =
    wakeState === "waking" ||
    wakeState === "unavailable" ||
    budget?.budget_exceeded ||
    health?.llm_status === "mock" ||
    health?.llm_status === "degraded" ||
    health?.stt_status === "mock";
  if (!hasBanner) return null;

  return (
    <div className="mb-6 space-y-3">
      {wakeState === "waking" && (
        <HonestyBanner title="Waking free-tier server…" tone="info">
          This can take about a minute after inactivity. You can keep choosing your practice setup.
        </HonestyBanner>
      )}
      {wakeState === "unavailable" && (
        <HonestyBanner title="Server is still waking or unavailable" tone="error">
          <button type="button" onClick={onRetry} className="font-semibold underline underline-offset-2">
            Try the readiness check again.
          </button>
        </HonestyBanner>
      )}
      {budget?.budget_exceeded && (
        <HonestyBanner title="Shared demo budget reached">
          This is a shared limit for all visitors, not your personal quota. Static mock-bank questions
          remain available; paid scoring or transcription may be paused until the daily reset.
        </HonestyBanner>
      )}
      {!budget?.budget_exceeded && health?.llm_status === "mock" && (
        <HonestyBanner title="Static question bank mode">
          Live LLM generation is unavailable. Any bank question is labeled Mock bank at the prompt.
        </HonestyBanner>
      )}
      {!budget?.budget_exceeded && health?.llm_status === "degraded" && (
        <HonestyBanner title="Live generation is degraded">
          New questions may come from the labeled static mock bank. Existing practice remains usable.
        </HonestyBanner>
      )}
      {health?.stt_status === "mock" && (
        <HonestyBanner title="Demo transcription mode">
          Live audio transcription is unavailable. Analysis uses a clearly labeled sample transcript,
          not the recording.
        </HonestyBanner>
      )}
    </div>
  );
}

const SOURCE_LABELS: Record<Question["source"], string> = {
  mock: "Mock bank",
  generated: "Generated",
  pasted: "Pasted",
};

const FALLBACK_COPY: Record<string, string> = {
  budget_exceeded: "The shared demo budget declined live generation.",
  budget_check_failed: "The shared demo budget could not be verified, so the offline bank was used.",
  upstream_rate_limited: "The live generation provider rate-limited the request.",
  generation_failed: "Live generation failed, so practice can continue with the offline bank.",
  invalid_generation: "The generator returned an unusable response, so the offline bank was used.",
  llm_unavailable: "Live generation is not configured, so the offline bank was used.",
  no_transcript: "There was no transcript to ground a live follow-up.",
};

export function QuestionSourceChrome({ question }: { question: Question }) {
  return (
    <div className="space-y-3">
      <span className="wobble inline-flex border border-border bg-surface-2 px-2.5 py-1 text-xs font-semibold">
        {SOURCE_LABELS[question.source]}
        {question.source === "generated" && " · this session"}
      </span>
      {question.source === "mock" && (
        <HonestyBanner title="Static mock-bank question">
          {FALLBACK_COPY[question.fallback_reason ?? ""] ??
            "This question comes from CodeEcho’s offline bank, not live LLM generation."}
        </HonestyBanner>
      )}
    </div>
  );
}

export function TranscriptionStatusBanner({
  source,
  errorCode,
}: {
  source?: string | null;
  errorCode?: string | null;
}) {
  if (errorCode === "stt_failed") {
    return (
      <HonestyBanner title="Audio transcription failed" tone="error">
        The recording could not be transcribed. Retry the recording or upload a supported audio file.
      </HonestyBanner>
    );
  }
  if (source === "mock") {
    return (
      <HonestyBanner title="Sample transcript used">
        Demo STT analyzed a sample transcript—not the words in this recording.
      </HonestyBanner>
    );
  }
  if (source === "live") {
    return (
      <HonestyBanner title="Browser transcript used">
        Audio transcription was unavailable, so CodeEcho used the browser’s live transcript instead.
      </HonestyBanner>
    );
  }
  return null;
}
