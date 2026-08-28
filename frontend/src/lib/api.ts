import type {
  AttemptSummary,
  BudgetStatus,
  InterviewMode,
  InterviewQuestionResponse,
  InterviewReport,
  InterviewSession,
  ModelAnswer,
  Question,
  Scorecard,
  SessionResult,
  TechnicalSection,
} from "./types";
import { getAuthToken, getGuestToken } from "./identity";

// Production: same-origin /api/* (proxied to Render in next.config.ts).
// Development: local FastAPI on :8000.
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  const token = await getAuthToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const guest = getGuestToken();
  if (guest) headers.set("X-Guest-Token", guest);

  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new Error(
      API_URL
        ? `Cannot reach the backend at ${API_URL}. Is the server running?`
        : "Cannot reach the server. Please try again in a moment."
    );
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export interface MeStatus {
  authenticated: boolean;
  user_id: string | null;
  auth_configured: boolean;
  profile: {
    user_id: string;
    email?: string | null;
    target_role: string;
    seniority: string;
  } | null;
}

export async function getMe(): Promise<MeStatus> {
  return request<MeStatus>("/api/me");
}

export async function updateMe(body: {
  target_role?: string;
  seniority?: string;
}): Promise<MeStatus["profile"]> {
  return request<MeStatus["profile"]>("/api/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function listAttempts(): Promise<AttemptSummary[]> {
  return request<AttemptSummary[]>("/api/attempts");
}

export async function claimGuestAttempts(): Promise<{ transferred: number }> {
  return request<{ transferred: number }>("/api/attempts/claim", {
    method: "POST",
  });
}

export async function getHealth() {
  return request<{
    status: string;
    gemini_configured: boolean;
    whisper_configured?: boolean;
    transcription_configured?: boolean;
    mock_mode: boolean;
    transcription_provider: string;
    llm_model?: string;
    scoring_model?: string;
    whisper_deployment?: string | null;
    google_gemini_base_url?: string | null;
  }>("/api/health");
}

export interface GeminiTestResult {
  ok: boolean;
  provider: string;
  model: string;
  base_url: string | null;
  latency_ms: number;
  response?: string | null;
  input_text?: string;
  analysis?: string | null;
  error: string | null;
}

export async function pingGemini(): Promise<GeminiTestResult> {
  return request<GeminiTestResult>("/api/debug/gemini/ping");
}

export async function analyzeTextWithGemini(text: string): Promise<GeminiTestResult> {
  return request<GeminiTestResult>("/api/debug/gemini/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

let warmed = false;

/**
 * Fire-and-forget wake-up ping for the backend.
 *
 * The backend runs on Render's free tier, which spins the container down after 15
 * minutes idle and takes ~1 minute to come back. Without this the cold start lands on
 * the user's FIRST real action (generating a question), where it reads as a hang.
 * Calling this on page load spends that minute while they're reading the intro and
 * picking a mode instead.
 *
 * Deliberately not using `request()`: no auth token is needed to wake a container, and
 * this must never throw, never block render, and never surface an error to the user.
 * Once per page load — repeat calls are a no-op.
 */
export function warmBackend(): void {
  if (warmed || typeof window === "undefined") return;
  warmed = true;
  void fetch(`${API_URL}/api/health`, { method: "GET", cache: "no-store" }).catch(() => {});
}

export async function getBudget(): Promise<BudgetStatus> {
  return request<BudgetStatus>("/api/budget");
}

export interface GenerateQuestionRequest {
  qtype: string;
  role?: string;
  seniority?: string;
  difficulty?: string;
  topic?: string;
  track?: string; // technical only: "coding" | "project"
}

export async function generateQuestion(body: GenerateQuestionRequest): Promise<Question> {
  return request<Question>("/api/questions/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function submitQuestion(body: {
  qtype: string;
  prompt: string;
  meta?: Record<string, unknown>;
}): Promise<Question> {
  return request<Question>("/api/questions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function scoreAttempt(
  attemptId: string,
  pseudocode?: string
): Promise<Scorecard> {
  return request<Scorecard>(`/api/attempts/${attemptId}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pseudocode: pseudocode?.trim() || null }),
  });
}

export async function getModelAnswer(attemptId: string): Promise<ModelAnswer> {
  return request<ModelAnswer>(`/api/attempts/${attemptId}/model-answer`, { method: "POST" });
}

export async function getScorecard(attemptId: string): Promise<Scorecard> {
  return request<Scorecard>(`/api/attempts/${attemptId}/scorecard`);
}

export async function createAttempt(
  title = "Untitled Attempt",
  questionId?: string
): Promise<SessionResult> {
  const q = questionId ? `&question_id=${encodeURIComponent(questionId)}` : "";
  return request<SessionResult>(
    `/api/attempts?title=${encodeURIComponent(title)}${q}`,
    { method: "POST" }
  );
}

export async function getAttempt(attemptId: string): Promise<SessionResult> {
  return request<SessionResult>(`/api/attempts/${attemptId}`);
}

export async function uploadAudio(
  attemptId: string,
  file: Blob,
  filename: string,
  liveTranscript?: string
): Promise<SessionResult> {
  const form = new FormData();
  form.append("file", file, filename);
  if (liveTranscript?.trim()) {
    form.append("live_transcript", liveTranscript.trim());
  }
  return request<SessionResult>(`/api/attempts/${attemptId}/upload`, {
    method: "POST",
    body: form,
  });
}

export interface GeminiAudioTestResult {
  ok: boolean;
  provider: string;
  model: string;
  base_url: string | null;
  latency_ms: number;
  audio_duration_sec?: number;
  audio_bytes?: number;
  chunk_count?: number;
  raw_response?: string | null;
  cleaned_transcript?: string | null;
  transcript?: string | null;
  failure_reason?: string | null;
  transcript_source?: string | null;
  strategy?: string | null;
  usage?: {
    prompt_token_count?: number;
    candidates_token_count?: number;
    thoughts_token_count?: number;
    total_token_count?: number;
    finish_reason?: string;
  } | null;
  attempts?: Array<{
    strategy: string;
    model: string;
    ok: boolean;
    latency_ms: number;
    error?: string | null;
    finish_reason?: string | null;
    usage?: Record<string, unknown>;
  }> | null;
  likely_hallucination?: boolean;
  error: string | null;
}

export async function testGeminiAudio(file: Blob, filename: string): Promise<GeminiAudioTestResult> {
  const form = new FormData();
  form.append("file", file, filename);
  return request<GeminiAudioTestResult>("/api/debug/gemini/audio", {
    method: "POST",
    body: form,
  });
}

export async function analyzeAttempt(attemptId: string): Promise<SessionResult> {
  return request<SessionResult>(`/api/attempts/${attemptId}/analyze`, {
    method: "POST",
  });
}

/** Fetch-based SSE so Authorization: Bearer can be sent (EventSource cannot). */
export async function streamAttempt(
  attemptId: string,
  onEvent: (event: string, data: Record<string, unknown>) => void,
  signal?: AbortSignal
): Promise<void> {
  const headers = new Headers();
  const token = await getAuthToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const guest = getGuestToken();
  if (guest) headers.set("X-Guest-Token", guest);

  const res = await fetch(`${API_URL}/api/attempts/${attemptId}/stream`, {
    headers,
    signal,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  if (!res.body) throw new Error("No stream body");
  await readSse(res.body, onEvent, signal);
}

async function readSse(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: string, data: Record<string, unknown>) => void,
  signal?: AbortSignal
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let eventName = "message";
  try {
    while (true) {
      if (signal?.aborted) break;
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop() ?? "";
      for (const block of parts) {
        let dataLine = "";
        eventName = "message";
        for (const line of block.split("\n")) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          else if (line.startsWith("data:")) dataLine += line.slice(5).trim();
        }
        if (!dataLine) continue;
        let data: Record<string, unknown> = {};
        try {
          data = JSON.parse(dataLine) as Record<string, unknown>;
        } catch {
          data = { raw: dataLine };
        }
        onEvent(eventName, data);
        if (eventName === "complete" || eventName === "error") return;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// --- mock interview ---------------------------------------------------------

export interface StartInterviewRequest {
  mode: InterviewMode;
  section?: TechnicalSection;
  role?: string;
  seniority?: string;
  num_behavioral?: number;
}

export async function startInterview(
  body: StartInterviewRequest
): Promise<InterviewQuestionResponse> {
  return request<InterviewQuestionResponse>("/api/interviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function advanceInterview(
  interviewId: string,
  attemptId: string,
  turnId?: string,
  transcript?: string
): Promise<InterviewQuestionResponse> {
  return request<InterviewQuestionResponse>(`/api/interviews/${interviewId}/advance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      attempt_id: attemptId,
      turn_id: turnId ?? null,
      transcript: transcript ?? null,
    }),
  });
}

export async function getInterview(interviewId: string): Promise<InterviewSession> {
  return request<InterviewSession>(`/api/interviews/${interviewId}`);
}

/** The turn a resumed interview should land on.
 *
 * Same shape as startInterview/advanceInterview, so the resume path reuses the
 * caller's ordinary "here is the next question" handling. `done` means every turn
 * is answered and the report is what's next. Read-only: polling cannot advance. */
export async function getCurrentInterviewTurn(
  interviewId: string
): Promise<InterviewQuestionResponse> {
  return request<InterviewQuestionResponse>(`/api/interviews/${interviewId}/current`);
}

export async function getInterviewReport(interviewId: string): Promise<InterviewReport> {
  return request<InterviewReport>(`/api/interviews/${interviewId}/report`, {
    method: "POST",
  });
}

export async function listInterviews(): Promise<InterviewSession[]> {
  return request<InterviewSession[]>("/api/interviews");
}

export function getClipUrl(clipPath: string): string {
  if (clipPath.startsWith("http://") || clipPath.startsWith("https://")) return clipPath;
  return `${API_URL}${clipPath}`;
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}m ${s}s`;
}

export function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
