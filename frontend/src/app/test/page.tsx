"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  analyzeTextWithGemini,
  getHealth,
  pingGemini,
  testGeminiAudio,
  type GeminiAudioTestResult,
  type GeminiTestResult,
} from "@/lib/api";
import { Mascot } from "@/components/Mascot";

const SAMPLE_TEXT =
  "So um I think like the key point is uh we need to focus.";

export default function TestPage() {
  const [health, setHealth] = useState<{
    mock_mode: boolean;
    transcription_provider: string;
    llm_model?: string;
    transcription_model?: string;
    google_gemini_base_url?: string | null;
  } | null>(null);
  const [text, setText] = useState(SAMPLE_TEXT);
  const [pingResult, setPingResult] = useState<GeminiTestResult | null>(null);
  const [analyzeResult, setAnalyzeResult] = useState<GeminiTestResult | null>(null);
  const [pingLoading, setPingLoading] = useState(false);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioResult, setAudioResult] = useState<GeminiAudioTestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((h) => setHealth(h))
      .catch(() => setError("Could not reach backend. Is it running on port 8000?"));
  }, []);

  const runPing = async () => {
    setPingLoading(true);
    setPingResult(null);
    setError(null);
    try {
      const result = await pingGemini();
      setPingResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ping failed");
    } finally {
      setPingLoading(false);
    }
  };

  const runAnalyze = async () => {
    if (text.trim().length < 5) {
      setError("Enter at least 5 characters of speech text.");
      return;
    }
    setAnalyzeLoading(true);
    setAnalyzeResult(null);
    setError(null);
    try {
      const result = await analyzeTextWithGemini(text.trim());
      setAnalyzeResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzeLoading(false);
    }
  };

  const runAudioTest = async (file: File) => {
    setAudioLoading(true);
    setAudioResult(null);
    setError(null);
    try {
      const result = await testGeminiAudio(file, file.name);
      setAudioResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Audio test failed");
    } finally {
      setAudioLoading(false);
    }
  };

  return (
    <main className="min-h-screen">
      <nav className="border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Mascot state="idle" size={36} />
          <span className="font-bold text-lg tracking-tight">FillerAI</span>
          <span className="text-xs text-neutral-400">API test</span>
        </div>
        <Link href="/" className="text-sm text-neutral-500 hover:text-neutral-900">
          Back to app
        </Link>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-10 space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">Gemini API smoke test</h1>
          <p className="text-sm text-neutral-500">
            Text-only — verifies your API key and proxy. Step 3 tests audio transcription.
          </p>
        </div>

        {health && (
          <div className="card-circle text-sm space-y-1">
            <p>
              <span className="text-neutral-500">Provider:</span>{" "}
              {health.transcription_provider}
            </p>
            <p>
              <span className="text-neutral-500">Text model:</span>{" "}
              {health.llm_model || "—"}
            </p>
            <p>
              <span className="text-neutral-500">Transcription model:</span>{" "}
              {health.transcription_model || health.llm_model || "—"}
            </p>
            <p>
              <span className="text-neutral-500">Base URL:</span>{" "}
              {health.google_gemini_base_url || "default"}
            </p>
            <p>
              <span className="text-neutral-500">Mock mode:</span>{" "}
              {health.mock_mode ? "yes" : "no"}
            </p>
          </div>
        )}

        <div className="card-circle space-y-4">
          <h2 className="font-semibold">Step 1 — Ping</h2>
          <p className="text-sm text-neutral-500">
            Sends a minimal prompt and expects the model to reply with OK.
          </p>
          <button
            onClick={runPing}
            disabled={pingLoading}
            className="btn-circle bg-neutral-900 text-white text-sm disabled:opacity-50"
          >
            {pingLoading ? "Pinging..." : "Ping Gemini"}
          </button>
          {pingResult && <ResultPanel title="Ping result" result={pingResult} />}
        </div>

        <div className="card-circle space-y-4">
          <h2 className="font-semibold">Step 2 — Analyze speech text</h2>
          <p className="text-sm text-neutral-500">
            Paste a transcript and get filler-word analysis from Gemini.
          </p>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            className="w-full rounded-2xl border border-neutral-200 px-4 py-3 text-sm resize-y focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="Paste speech transcript..."
          />
          <button
            onClick={runAnalyze}
            disabled={analyzeLoading}
            className="btn-circle bg-neutral-900 text-white text-sm disabled:opacity-50"
          >
            {analyzeLoading ? "Analyzing..." : "Analyze with Gemini"}
          </button>
          {analyzeResult && (
            <ResultPanel title="Analysis result" result={analyzeResult} />
          )}
        </div>

        <div className="card-circle space-y-4">
          <h2 className="font-semibold">Step 3 — Transcribe audio</h2>
          <p className="text-sm text-neutral-500">
            Upload or record a short clip. Say something obvious like &quot;My name is Shar and I am testing um filler words.&quot;
          </p>
          <label className="block">
            <input
              type="file"
              accept="audio/*,.webm,.wav,.mp3,.m4a"
              disabled={audioLoading}
              className="text-sm"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) runAudioTest(file);
              }}
            />
          </label>
          {audioLoading && (
            <p className="text-sm text-neutral-500">Sending audio to Gemini...</p>
          )}
          {audioResult && <AudioResultPanel result={audioResult} />}
        </div>

        {error && (
          <div className="card-circle text-red-600 text-sm">{error}</div>
        )}
      </div>
    </main>
  );
}

function ResultPanel({
  title,
  result,
}: {
  title: string;
  result: GeminiTestResult;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 text-sm space-y-3 ${
        result.ok
          ? "border-green-200 bg-green-50"
          : "border-red-200 bg-red-50"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium">{title}</span>
        <span
          className={`text-xs font-semibold uppercase ${
            result.ok ? "text-green-700" : "text-red-700"
          }`}
        >
          {result.ok ? "Success" : "Failed"}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-neutral-600">
        <p>Provider: {result.provider}</p>
        <p>Model: {result.model}</p>
        <p>Latency: {result.latency_ms}ms</p>
        <p>Base URL: {result.base_url || "—"}</p>
      </div>
      {result.response && (
        <div>
          <p className="text-xs text-neutral-500 mb-1">Response</p>
          <pre className="whitespace-pre-wrap text-neutral-800">{result.response}</pre>
        </div>
      )}
      {result.analysis && (
        <div>
          <p className="text-xs text-neutral-500 mb-1">Analysis</p>
          <pre className="whitespace-pre-wrap text-neutral-800">{result.analysis}</pre>
        </div>
      )}
      {result.error && (
        <div>
          <p className="text-xs text-red-600 mb-1">Error</p>
          <pre className="whitespace-pre-wrap text-red-800">{result.error}</pre>
        </div>
      )}
    </div>
  );
}

function AudioResultPanel({ result }: { result: GeminiAudioTestResult }) {
  return (
    <div
      className={`rounded-2xl border p-4 text-sm space-y-3 ${
        result.ok ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium">Audio transcription result</span>
        <span
          className={`text-xs font-semibold uppercase ${
            result.ok ? "text-green-700" : "text-red-700"
          }`}
        >
          {result.ok ? "Success" : "Failed"}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-neutral-600">
        <p>Model: {result.model}</p>
        <p>Strategy: {result.strategy ?? "—"}</p>
        <p>Latency: {result.latency_ms}ms</p>
        <p>Duration: {result.audio_duration_sec ?? "—"}s</p>
        <p>Bytes: {result.audio_bytes ?? "—"}</p>
        <p>Chunks: {result.chunk_count ?? 1}</p>
        <p>Prompt tokens: {result.usage?.prompt_token_count ?? "—"}</p>
        <p>Output tokens: {result.usage?.candidates_token_count ?? "—"}</p>
        <p>Failure: {result.failure_reason ?? "none"}</p>
      </div>
      {result.attempts && result.attempts.length > 0 && (
        <div>
          <p className="text-xs text-neutral-500 mb-1">Strategy attempts</p>
          <ul className="text-xs space-y-1 text-neutral-700">
            {result.attempts.map((a) => (
              <li key={a.strategy}>
                {a.ok ? "✓" : "✗"} {a.strategy} ({a.model}, {a.latency_ms}ms)
                {a.error ? ` — ${a.error}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
      {result.failure_reason && (
        <p className="text-xs text-red-700">
          Failure reason: {result.failure_reason}
        </p>
      )}
      {result.likely_hallucination && !result.failure_reason && (
        <p className="text-xs text-red-700">
          Likely hallucination — model invented text instead of hearing your audio.
        </p>
      )}
      {(result.cleaned_transcript || result.transcript) && (
        <div>
          <p className="text-xs text-neutral-500 mb-1">Transcript</p>
          <pre className="whitespace-pre-wrap text-neutral-800">
            {result.cleaned_transcript || result.transcript}
          </pre>
        </div>
      )}
      {result.raw_response && result.raw_response !== result.transcript && (
        <div>
          <p className="text-xs text-neutral-500 mb-1">Raw response</p>
          <pre className="whitespace-pre-wrap text-neutral-800">{result.raw_response}</pre>
        </div>
      )}
      {result.error && (
        <div>
          <p className="text-xs text-red-600 mb-1">Error</p>
          <pre className="whitespace-pre-wrap text-red-800">{result.error}</pre>
        </div>
      )}
    </div>
  );
}
