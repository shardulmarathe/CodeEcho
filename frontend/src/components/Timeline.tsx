"use client";

import { useRef, useState } from "react";
import type { FillerOccurrence } from "@/lib/types";
import { formatTimestamp, getClipUrl } from "@/lib/api";
import { tagLabel } from "@/lib/tags";
import { SketchBox, SketchPill } from "./sketch/Sketch";

interface TimelineProps {
  durationSec: number;
  fillers: FillerOccurrence[];
}

export function Timeline({ durationSec, fillers }: TimelineProps) {
  const [selected, setSelected] = useState<FillerOccurrence | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const playClip = (filler: FillerOccurrence) => {
    setSelected(filler);
    if (filler.clip_url && audioRef.current) {
      audioRef.current.src = getClipUrl(filler.clip_url);
      audioRef.current.play();
    }
  };

  return (
    <SketchBox className="space-y-6">
      <h3 className="font-semibold">Filler Timeline</h3>

      {/* Timeline bar */}
      <div className="relative h-2 rounded-full bg-neutral-100">
        {fillers.map((f, i) => (
          <button
            key={i}
            className={`timeline-marker absolute top-1/2 -translate-y-1/2 -translate-x-1/2 ${
              selected?.index === f.index ? "scale-150 ring-2 ring-neutral-400" : ""
            }`}
            style={{ left: `${(f.start / durationSec) * 100}%` }}
            onClick={() => playClip(f)}
            title={`${f.word} at ${formatTimestamp(f.start)}`}
            aria-label={`Filler "${f.word}" at ${formatTimestamp(f.start)}`}
          />
        ))}
      </div>

      <div className="flex justify-between text-xs text-neutral-400">
        <span>0:00</span>
        <span>{formatTimestamp(durationSec)}</span>
      </div>

      {/* Selected filler detail */}
      {selected && (
        <div className="rounded-2xl bg-neutral-50 p-4 space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <SketchPill filled>
              <span className="capitalize">{selected.word}</span>
            </SketchPill>
            <span className="text-sm text-neutral-500">
              {formatTimestamp(selected.start)}
            </span>
            <SketchPill>
              <span className="capitalize">{selected.sentence_position}</span>
            </SketchPill>
            {selected.tag && <SketchPill>{tagLabel(selected.tag)}</SketchPill>}
          </div>
          {selected.tag_reason && (
            <p className="text-sm text-neutral-700">
              <span className="font-medium">Why: </span>
              {selected.tag_reason}
              {selected.topic ? ` (topic: ${selected.topic})` : ""}
            </p>
          )}
          <p className="text-sm text-neutral-600 italic">
            &ldquo;...{selected.context}...&rdquo;
          </p>
          {selected.clip_url ? (
            <audio ref={audioRef} controls className="w-full h-8" />
          ) : (
            <p className="text-xs text-neutral-400">Clip not available (FFmpeg required)</p>
          )}
        </div>
      )}

      {!selected && fillers.length > 0 && (
        <p className="text-sm text-neutral-400 text-center">
          Click a marker to hear the ±3s clip around that filler
        </p>
      )}

      {fillers.length === 0 && (
        <p className="text-sm text-neutral-500 text-center">No fillers detected in this speech</p>
      )}
    </SketchBox>
  );
}
