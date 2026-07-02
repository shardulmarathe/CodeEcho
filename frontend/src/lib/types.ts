export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  index: number;
}

export interface FillerOccurrence {
  word: string;
  start: number;
  end: number;
  index: number;
  context: string;
  sentence_position: string;
  is_transition_related: boolean;
  tag?: string | null; // idea_transition | topic_mention | hesitation
  tag_reason?: string | null;
  topic?: string | null;
  clip_url?: string | null;
}

export interface PauseOccurrence {
  start: number;
  end: number;
  duration: number;
  after_index: number;
  is_long: boolean;
}

export interface PositionBreakdown {
  beginning: number;
  middle: number;
  end: number;
}

export interface SessionMetrics {
  duration_sec: number;
  total_fillers: number;
  fillers_per_minute: number;
  words_per_minute: number;
  avg_pause_sec: number;
  avg_pause_before_filler_sec: number;
  avg_pause_elsewhere_sec: number;
  total_pauses: number;
  long_pauses: number;
  pauses_per_minute: number;
  total_pause_sec: number;
  long_pause_filler_pct: number;
  transition_filler_pct: number;
  position_breakdown: PositionBreakdown;
  filler_breakdown: Record<string, number>;
  tag_breakdown: Record<string, number>;
}

export type SessionStatus =
  | "pending"
  | "transcribing"
  | "analyzing"
  | "complete"
  | "failed";

export interface SessionResult {
  session_id: string;
  status: SessionStatus;
  title: string;
  words: WordTimestamp[];
  fillers: FillerOccurrence[];
  pauses: PauseOccurrence[];
  metrics: SessionMetrics;
  transcript_text: string;
  audio_url?: string | null;
  error?: string | null;
}

export interface QuestionExample {
  input: string;
  output: string;
  explanation: string;
}

export interface Question {
  id: string;
  qtype: string; // "behavioral" | "technical"
  prompt: string;
  source: string;
  constraints?: string | null;
  examples: QuestionExample[];
  meta: Record<string, unknown>;
  created_at?: string | null;
}

export interface ModelAnswer {
  rubric: string;
  approach: string;
  complexity: string;
  outline: string;
  key_points: string[];
}

export interface ScoreDimension {
  dimension: string;
  score: number; // 1–5
  rationale: string;
  evidence: string;
  suggestion: string;
}

export interface Scorecard {
  attempt_id: string;
  rubric: string; // "star" | "technical"
  overall_score: number;
  overall_summary: string;
  dimensions: ScoreDimension[];
  created_at?: string | null;
}

export interface AttemptSummary {
  session_id: string;
  title: string;
  status: SessionStatus;
  created_at?: string | null;
  total_fillers: number;
  duration_sec: number;
}

export interface BudgetStatus {
  cap_usd: number;
  spent_usd: number;
  remaining_usd: number;
  budget_exceeded: boolean;
}

export type TabId = "overview" | "timeline" | "analytics" | "history";

// --- Mock interview ---------------------------------------------------------

export type InterviewMode = "behavioral" | "technical";
export type TechnicalSection = "coding" | "system_design" | "project";

export interface InterviewQuestionResponse {
  done: boolean;
  session_id: string;
  turn_id?: string | null;
  question?: Question | null;
  is_followup: boolean;
  progress: string; // e.g. "Question 2 of 3" | "Follow-up"
}

export interface InterviewReportTurn {
  turn_id: string;
  question: string;
  is_followup: boolean;
  attempt_id?: string | null; // to score this single question on demand
  rubric?: string;
  overall_score?: number;
  scorecard?: Scorecard | null;
}

export interface InterviewReport {
  overall_score: number;
  verdict: string; // strong | mixed | needs work
  summary: string;
  strengths: string[];
  improvements: string[];
  followup_handling: string;
  general_scorecard?: Scorecard | null; // one generalized rubric for the whole interview
  total_fillers: number;
  avg_words_per_minute: number;
  total_pauses: number;
  turns: InterviewReportTurn[];
}

export interface InterviewTurn {
  turn_id: string;
  plan_index: number;
  is_followup: boolean;
  parent_turn_id?: string | null;
  question_id: string;
  attempt_id?: string | null;
  answered: boolean;
}

export interface InterviewSession {
  session_id: string;
  status: string; // active | complete | abandoned
  mode: InterviewMode;
  config: Record<string, unknown>;
  turns: InterviewTurn[];
  report?: InterviewReport | null;
  created_at?: string | null;
  updated_at?: string | null;
}
