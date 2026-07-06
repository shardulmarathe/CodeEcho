"use client";

import type { FillerOccurrence, PauseOccurrence, WordTimestamp } from "@/lib/types";
import { tagLabel } from "@/lib/tags";
import { SketchBox } from "./sketch/Sketch";

interface TranscriptViewProps {
  words: WordTimestamp[];
  fillerIndices: Set<number>;
  fillers?: FillerOccurrence[];
  pauses?: PauseOccurrence[];
  streaming?: boolean;
  transcriptText?: string;
  label?: string;
}

function PauseMarker({ pause }: { pause: PauseOccurrence }) {
  return (
    <span
      className={`pause-marker mx-0.5 inline-block rounded px-1.5 text-xs tabular-nums align-middle ${
        pause.is_long
          ? "bg-amber-100 text-amber-700"
          : "bg-neutral-100 text-neutral-500"
      }`}
      title={`${pause.is_long ? "Long pause" : "Pause"} — ${pause.duration.toFixed(1)}s of silence`}
    >
      ⏸ {pause.duration.toFixed(1)}s
    </span>
  );
}

export function TranscriptView({
  words,
  fillerIndices,
  fillers,
  pauses,
  streaming = false,
  transcriptText,
  label,
}: TranscriptViewProps) {
  const fillerByIndex = new Map((fillers ?? []).map((f) => [f.index, f]));
  const pauseByAfterIndex = new Map((pauses ?? []).map((p) => [p.after_index, p]));

  const fillerTitle = (index: number, word: string): string => {
    const f = fillerByIndex.get(index);
    if (!f) return word;
    const parts = [word];
    if (f.tag) parts.push(tagLabel(f.tag));
    if (f.tag_reason) parts.push(`— ${f.tag_reason}`);
    return parts.join(" · ");
  };

  if (words.length === 0 && !transcriptText) {
    return (
      <SketchBox className="text-center text-neutral-400 text-sm" padding={32}>
        Transcript will appear here...
      </SketchBox>
    );
  }

  return (
    <SketchBox>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">{label || "Transcript"}</h3>
        {streaming && (
          <span className="text-xs text-neutral-500 animate-pulse">Streaming in...</span>
        )}
      </div>
      {words.length > 0 ? (
        <p className="text-sm leading-relaxed break-words">
          {words.map((w, i) => {
            const pause = pauseByAfterIndex.get(i);
            return (
              <span key={i}>
                {fillerIndices.has(i) ? (
                  <span className="filler-word mx-0.5" title={fillerTitle(i, w.word)}>
                    {w.word}
                  </span>
                ) : (
                  <span>{w.word} </span>
                )}
                {pause && <PauseMarker pause={pause} />}
                {pause && " "}
              </span>
            );
          })}
        </p>
      ) : (
        <p className="text-sm leading-relaxed text-neutral-600">{transcriptText}</p>
      )}
    </SketchBox>
  );
}

interface ProcessingStepsProps {
  step: "uploading" | "transcribing" | "analyzing" | "complete" | "error";
  mockMode?: boolean;
  statusMessage?: string | null;
}

const STEPS = [
  { id: "transcribing", label: "Transcribing speech" },
  { id: "analyzing", label: "Detecting fillers" },
  { id: "complete", label: "Done" },
];

export function ProcessingSteps({ step, mockMode, statusMessage }: ProcessingStepsProps) {
  return (
    <SketchBox className="space-y-4">
      {mockMode && (
        <div className="rounded-full bg-neutral-100 px-4 py-2 text-xs text-neutral-600 text-center">
          Demo mode — using sample transcript, not your recording
        </div>
      )}
      {statusMessage && step !== "complete" && step !== "error" && (
        <p className="text-sm text-neutral-600 text-center">{statusMessage}</p>
      )}
      {STEPS.map((s) => {
        const stepOrder = ["uploading", "transcribing", "analyzing", "complete"];
        const currentIdx = stepOrder.indexOf(step);
        const thisIdx = stepOrder.indexOf(s.id);
        const done = currentIdx > thisIdx;
        const active = step === s.id;

        return (
          <div key={s.id} className="flex items-center gap-3">
            <div
              className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium transition-all ${
                done
                  ? "bg-neutral-900 text-white"
                  : active
                    ? "border-2 border-neutral-900 animate-pulse"
                    : "border border-neutral-200 text-neutral-400"
              }`}
            >
              {done ? "✓" : thisIdx + 1}
            </div>
            <span
              className={`text-sm ${
                active ? "font-medium" : done ? "text-neutral-600" : "text-neutral-400"
              }`}
            >
              {s.label}
            </span>
          </div>
        );
      })}
    </SketchBox>
  );
}
