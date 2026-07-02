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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
      `Cannot reach the backend at ${API_URL}. Start it with: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
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
  clerk_configured: boolean;
}

export async function getMe(): Promise<MeStatus> {
  return request<MeStatus>("/api/me");
}

export async function listAttempts(): Promise<AttemptSummary[]> {
  return request<AttemptSummary[]>("/api/attempts");
}

export async function claimGuestAttempts(guestToken: string): Promise<{ transferred: number }> {
  return request<{ transferred: number }>("/api/attempts/claim", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ guest_token: guestToken }),
  });
}

export async function getHealth() {
  return request<{
    status: string;
    gemini_configured: boolean;
    mock_mode: boolean;
    transcription_provider: string;
    llm_model?: string;
    transcription_model?: string;
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

export function getStreamUrl(attemptId: string): string {
  return `${API_URL}/api/attempts/${attemptId}/stream`;
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
  turnId?: string
): Promise<InterviewQuestionResponse> {
  return request<InterviewQuestionResponse>(`/api/interviews/${interviewId}/advance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ attempt_id: attemptId, turn_id: turnId ?? null }),
  });
}

export async function getInterview(interviewId: string): Promise<InterviewSession> {
  return request<InterviewSession>(`/api/interviews/${interviewId}`);
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
  if (clipPath.startsWith("http")) return clipPath;
  return `${API_URL}${clipPath}`;
}

export function getAudioUrl(audioPath: string): string {
  if (audioPath.startsWith("http")) return audioPath;
  return `${API_URL}${audioPath}`;
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
