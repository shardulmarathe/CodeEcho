"use client";

import { useEffect, useRef, useState } from "react";
import { useMicLevel } from "@/lib/useMicLevel";
import { SketchWaveform } from "./sketch/SketchWaveform";

// Hard cap on a single answer (1:30), mirrors a typical interview answer length.
// The backend enforces the same limit before transcription; this is the UX side.
const MAX_DURATION_SEC = 90;

export interface RecordingResult {
  blob: Blob;
  liveTranscript: string;
}

interface AudioRecorderProps {
  onRecordingComplete: (result: RecordingResult) => void;
  disabled?: boolean;
}

function getSupportedMimeType(): string {
  const types = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return "";
}

async function getMicStream(): Promise<MediaStream> {
  const constraints: MediaStreamConstraints = {
    audio: {
      echoCancellation: true,
      noiseSuppression: false,
      autoGainControl: true,
      channelCount: 1,
    },
  };
  try {
    return await navigator.mediaDevices.getUserMedia(constraints);
  } catch {
    return navigator.mediaDevices.getUserMedia({ audio: true });
  }
}

export function AudioRecorder({ onRecordingComplete, disabled }: AudioRecorderProps) {
  const [recording, setRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [speechDetected, setSpeechDetected] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mimeTypeRef = useRef("");
  const { level, getPeak, start: startMicLevel, stop: stopMicLevel } = useMicLevel();

  const cleanup = () => {
    stopMicLevel();
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    mediaRecorderRef.current = null;
  };

  const startRecording = async () => {
    try {
      cleanup();
      setSpeechDetected(false);
      setMicError(null);

      const stream = await getMicStream();
      const audioTrack = stream.getAudioTracks()[0];
      if (!audioTrack) {
        setMicError("No microphone track available.");
        return;
      }
      audioTrack.enabled = true;

      streamRef.current = stream;
      await startMicLevel(stream);
      chunksRef.current = [];

      const mimeType = getSupportedMimeType();
      mimeTypeRef.current = mimeType;
      const options: MediaRecorderOptions = mimeType ? { mimeType } : {};
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onerror = () => {
        setMicError("Recording failed — try refreshing the page.");
        cleanup();
        setRecording(false);
        setDuration(0);
      };

      mediaRecorder.onstop = () => {
        const type = mimeTypeRef.current || "audio/webm";
        const blob = new Blob(chunksRef.current, { type });
        const peakLevel = getPeak();
        cleanup();
        setRecording(false);
        setDuration(0);
        setSpeechDetected(false);

        if (blob.size < 1000) {
          setMicError("That was too short — record at least 2–3 seconds and try again.");
          return;
        }
        if (peakLevel < 0.008) {
          setMicError(
            "No audio was picked up from your mic. Check your input device (System Settings → Sound → Input), then record again."
          );
          return;
        }
        onRecordingComplete({ blob, liveTranscript: "" });
      };

      mediaRecorder.start(250);
      setRecording(true);
      setDuration(0);
      timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
    } catch (err) {
      const message =
        err instanceof Error && err.name === "NotAllowedError"
          ? "Microphone permission denied."
          : "Could not access microphone.";
      setMicError(message);
      alert(`${message} Allow mic access in browser settings and try again.`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      try {
        mediaRecorderRef.current.requestData();
      } catch {
        // optional API
      }
      mediaRecorderRef.current.stop();
    }
  };

  useEffect(() => {
    if (recording && level > 0.012) {
      setSpeechDetected(true);
    }
  }, [recording, level]);

  // Enforce the answer cap: auto-stop at 1:30, like an interviewer calling time.
  useEffect(() => {
    if (recording && duration >= MAX_DURATION_SEC) {
      stopRecording();
    }
    // stopRecording only touches refs, so it's safe to omit from deps.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recording, duration]);

  const formatTime = (s: number) =>
    `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  return (
    <div className="panel flex flex-col items-center gap-6 py-10 px-6">
      <SketchWaveform bars={40} active={recording} height={56} />
      <div className="text-center">
        <p className="text-3xl font-bold tabular-nums mono">
          {formatTime(Math.min(duration, MAX_DURATION_SEC))}
          <span className="text-muted text-lg font-normal"> / {formatTime(MAX_DURATION_SEC)}</span>
        </p>
        <p className="text-sm text-muted mt-1">
          {recording
            ? MAX_DURATION_SEC - duration <= 15
              ? `${Math.max(0, MAX_DURATION_SEC - duration)}s left — wrap up your answer`
              : "Recording — speak clearly into your mic"
            : "Tap to record your answer · 1:30 max"}
        </p>
      </div>
      {micError && !recording && (
        <div
          className="wobble sketch-shadow w-full max-w-md p-4 text-center space-y-3"
          style={{ background: "var(--surface)", border: "2px solid var(--amber)" }}
        >
          <p className="text-sm" style={{ color: "var(--fg)" }}>{micError}</p>
          <button
            onClick={startRecording}
            disabled={disabled}
            className="btn btn-primary sketch-press"
          >
            Try recording again
          </button>
        </div>
      )}
      {recording && (
        <div className="w-full max-w-md space-y-2">
          <div
            className="h-2 w-full rounded-full overflow-hidden"
            style={{ background: "var(--surface-2)" }}
          >
            <div
              className="h-full transition-[width] duration-150 ease-out"
              style={{ width: `${Math.max(4, level * 100)}%`, background: "var(--amber)" }}
            />
          </div>
          <p className="text-xs text-center text-muted">
            {speechDetected
              ? "Mic detected — pauses are normal"
              : duration >= 4
                ? "Speak up — no mic signal yet"
                : "Waiting for speech…"}
          </p>
        </div>
      )}
      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={disabled}
        className="h-20 w-20 rounded-full border-4 flex items-center justify-center transition-all disabled:opacity-50"
        style={{
          borderColor: "var(--echo)",
          background: recording ? "var(--echo)" : "transparent",
        }}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? (
          <span className="block h-5 w-5 rounded-sm" style={{ background: "var(--on-echo)" }} />
        ) : (
          <span className="block h-5 w-5 rounded-full" style={{ background: "var(--echo)" }} />
        )}
      </button>
      {recording && (
        <button onClick={stopRecording} className="btn btn-primary">
          Stop &amp; analyze
        </button>
      )}
    </div>
  );
}

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export function FileUpload({ onFileSelect, disabled }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);

  const handleFile = (file: File) => {
    const allowed = ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/m4a", "audio/webm", "audio/ogg"];
    if (!allowed.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|webm|ogg)$/i)) {
      alert("Please upload MP3, WAV, or M4A files.");
      return;
    }
    if (file.size < 1000) {
      alert("File is too small or empty.");
      return;
    }
    onFileSelect(file);
  };

  return (
    <div
      className={`panel flex flex-col items-center gap-4 py-10 cursor-pointer transition-colors ${
        disabled ? "opacity-50 pointer-events-none" : ""
      }`}
      style={{ borderStyle: "dashed", borderColor: dragging ? "var(--echo)" : "var(--border)" }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
      }}
      onClick={() => {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".mp3,.wav,.m4a,.webm,.ogg,audio/*";
        input.onchange = (e) => {
          const file = (e.target as HTMLInputElement).files?.[0];
          if (file) handleFile(file);
        };
        input.click();
      }}
    >
      <div
        className="h-16 w-16 rounded-full border-2 flex items-center justify-center"
        style={{ borderColor: "var(--echo)", color: "var(--echo)" }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <div className="text-center">
        <p className="font-medium">Drop audio file here</p>
        <p className="text-sm text-neutral-500 mt-1">MP3, WAV, M4A supported</p>
      </div>
    </div>
  );
}
