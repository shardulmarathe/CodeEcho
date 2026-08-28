"use client";

import type { ReactNode } from "react";
import type { FillerOccurrence, PauseOccurrence, WordTimestamp } from "@/lib/types";
import { tagLabel } from "@/lib/tags";
import { SketchBox } from "./sketch/Sketch";

const EVIDENCE_TITLE = "Scorecard evidence";

interface TranscriptViewProps {
  words: WordTimestamp[];
  fillerIndices: Set<number>;
  fillers?: FillerOccurrence[];
  pauses?: PauseOccurrence[];
  streaming?: boolean;
  transcriptText?: string;
  label?: string;
  /** Scorecard dimension quotes to highlight (case-insensitive substring / overlapping words). */
  evidenceQuotes?: string[];
}

function trimEdgePunct(s: string): string {
  return s.replace(/^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$/g, "");
}

function findSubstringRanges(haystack: string, needles: string[]): Array<[number, number]> {
  const hay = haystack.toLowerCase();
  const ranges: Array<[number, number]> = [];
  for (const raw of needles) {
    const needle = raw.trim().replace(/\s+/g, " ").toLowerCase();
    if (needle.length < 3) continue;
    let from = 0;
    while (from <= hay.length - needle.length) {
      const idx = hay.indexOf(needle, from);
      if (idx === -1) break;
      ranges.push([idx, idx + needle.length]);
      from = idx + 1;
    }
  }
  return ranges;
}

function mergeRanges(ranges: Array<[number, number]>): Array<[number, number]> {
  if (ranges.length === 0) return [];
  const sorted = [...ranges].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const out: Array<[number, number]> = [[sorted[0][0], sorted[0][1]]];
  for (let i = 1; i < sorted.length; i++) {
    const last = out[out.length - 1];
    const [a, b] = sorted[i];
    if (a <= last[1]) last[1] = Math.max(last[1], b);
    else out.push([a, b]);
  }
  return out;
}

function spansForParts(parts: string[]): Array<[number, number]> {
  const spans: Array<[number, number]> = [];
  let cursor = 0;
  for (const part of parts) {
    spans.push([cursor, cursor + part.length]);
    cursor += part.length + 1;
  }
  return spans;
}

/** Word indices whose text overlaps any evidence quote (case-insensitive substring). */
function evidenceWordIndices(words: WordTimestamp[], quotes: string[]): Set<number> {
  const indices = new Set<number>();
  if (words.length === 0 || quotes.length === 0) return indices;

  const mark = (parts: string[], needles: string[]) => {
    const spans = spansForParts(parts);
    for (const [a, b] of findSubstringRanges(parts.join(" "), needles)) {
      for (let i = 0; i < spans.length; i++) {
        const [start, end] = spans[i];
        if (start < b && end > a) indices.add(i);
      }
    }
  };

  const rawParts = words.map((w) => w.word);
  mark(rawParts, quotes);
  mark(
    rawParts.map((p) => trimEdgePunct(p) || p),
    quotes.map((q) => trimEdgePunct(q) || q),
  );
  return indices;
}

function evidenceClass(): string {
  return "underline decoration-2 underline-offset-2";
}

function evidenceStyle(): { textDecorationColor: string; background: string } {
  return { textDecorationColor: "var(--amber)", background: "rgba(234, 179, 8, 0.1)" };
}

function highlightTranscriptText(text: string, quotes: string[]): ReactNode {
  const ranges = mergeRanges(findSubstringRanges(text, quotes));
  if (ranges.length === 0) return text;
  const nodes: ReactNode[] = [];
  let pos = 0;
  ranges.forEach(([a, b], i) => {
    if (pos < a) nodes.push(text.slice(pos, a));
    nodes.push(
      <span
        key={`ev-${i}`}
        className={evidenceClass()}
        style={evidenceStyle()}
        title={EVIDENCE_TITLE}
      >
        {text.slice(a, b)}
      </span>,
    );
    pos = b;
  });
  if (pos < text.length) nodes.push(text.slice(pos));
  return nodes;
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
  evidenceQuotes,
}: TranscriptViewProps) {
  const fillerByIndex = new Map((fillers ?? []).map((f) => [f.index, f]));
  const pauseByAfterIndex = new Map((pauses ?? []).map((p) => [p.after_index, p]));
  const evidenceIndices = evidenceWordIndices(words, evidenceQuotes ?? []);

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
            const isFiller = fillerIndices.has(i);
            const isEvidence = evidenceIndices.has(i);
            const title = isFiller
              ? [fillerTitle(i, w.word), isEvidence ? EVIDENCE_TITLE : null]
                  .filter(Boolean)
                  .join(" · ")
              : isEvidence
                ? EVIDENCE_TITLE
                : undefined;
            return (
              <span key={i}>
                {isFiller ? (
                  <span
                    className={`filler-word mx-0.5${isEvidence ? ` ${evidenceClass()}` : ""}`}
                    style={isEvidence ? { textDecorationColor: "var(--amber)" } : undefined}
                    title={title}
                  >
                    {w.word}
                  </span>
                ) : isEvidence ? (
                  <span className={`mx-0.5 ${evidenceClass()}`} style={evidenceStyle()} title={title}>
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
        <p className="text-sm leading-relaxed text-neutral-600">
          {evidenceQuotes && evidenceQuotes.length > 0 && transcriptText
            ? highlightTranscriptText(transcriptText, evidenceQuotes)
            : transcriptText}
        </p>
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
