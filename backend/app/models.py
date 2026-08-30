from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class SessionStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    index: int


class FillerOccurrence(BaseModel):
    word: str
    start: float
    end: float
    index: int
    context: str
    sentence_position: str  # beginning | middle | end
    is_transition_related: bool = False
    tag: Optional[str] = None  # idea_transition | topic_mention | hesitation | None
    tag_reason: Optional[str] = None  # short human explanation of why the filler occurred
    topic: Optional[str] = None  # subject named, when tag == topic_mention
    clip_url: Optional[str] = None


class PauseOccurrence(BaseModel):
    """A silent gap between two consecutive words, surfaced for delivery analysis."""

    start: float          # end of the preceding word
    end: float            # start of the following word
    duration: float       # seconds of silence
    after_index: int      # the pause follows the word at this index
    is_long: bool = False  # notably long hesitation (see pause_detect.LONG_PAUSE_SEC)


class PositionBreakdown(BaseModel):
    beginning: float = 0.0
    middle: float = 0.0
    end: float = 0.0


class SessionMetrics(BaseModel):
    duration_sec: float = 0.0
    total_fillers: int = 0
    fillers_per_minute: float = 0.0
    words_per_minute: float = 0.0
    avg_pause_sec: float = 0.0
    avg_pause_before_filler_sec: float = 0.0
    avg_pause_elsewhere_sec: float = 0.0
    total_pauses: int = 0
    long_pauses: int = 0
    pauses_per_minute: float = 0.0
    total_pause_sec: float = 0.0
    long_pause_filler_pct: float = 0.0
    transition_filler_pct: float = 0.0
    position_breakdown: PositionBreakdown = Field(default_factory=PositionBreakdown)
    filler_breakdown: dict[str, int] = Field(default_factory=dict)
    tag_breakdown: dict[str, int] = Field(default_factory=dict)


class SessionResult(BaseModel):
    session_id: str  # == attempts.id
    status: SessionStatus
    title: str = "Untitled Session"
    # Ownership: a signed-in user OR an anonymous guest token (exactly one set)
    user_id: Optional[str] = None
    guest_token: Optional[str] = None
    question_id: Optional[str] = None
    words: list[WordTimestamp] = Field(default_factory=list)
    fillers: list[FillerOccurrence] = Field(default_factory=list)
    pauses: list[PauseOccurrence] = Field(default_factory=list)
    metrics: SessionMetrics = Field(default_factory=SessionMetrics)
    transcript_text: str = ""
    live_transcript: Optional[str] = None
    audio_url: Optional[str] = None
    audio_path: Optional[str] = None  # storage object key, not a signed URL
    created_at: Optional[str] = None
    error: Optional[str] = None
    # Recording budget for this attempt (seconds). 180 behavioral/coding, 300 design/project.
    max_duration_sec: Optional[int] = None


class DimensionScore(BaseModel):
    """Score-only slice of a rubric dimension, for history listings."""

    dimension: str
    score: float = 0.0


class AttemptSummary(BaseModel):
    """Lightweight row for history listings and the progress dashboard."""

    session_id: str
    title: str
    status: SessionStatus
    created_at: Optional[str] = None
    total_fillers: int = 0
    duration_sec: float = 0.0
    fillers_per_minute: float = 0.0
    words_per_minute: float = 0.0
    overall_score: Optional[float] = None
    dimensions: list[DimensionScore] = Field(default_factory=list)
    bucket: Optional[str] = None  # behavioral bucket or technical track
    qtype: Optional[str] = None
    rubric: Optional[str] = None


class BudgetStatus(BaseModel):
    cap_usd: float
    spent_usd: float
    remaining_usd: float
    budget_exceeded: bool


class Profile(BaseModel):
    user_id: str
    email: Optional[str] = None
    target_role: str = "Software Engineer"
    seniority: str = "mid"


class ProfileUpdate(BaseModel):
    target_role: Optional[str] = None
    seniority: Optional[str] = None


# --- Interview questions & scorecards ---------------------------------------

class QuestionExample(BaseModel):
    input: str
    output: str
    explanation: str = ""


class Question(BaseModel):
    id: str
    qtype: str  # "behavioral" | "technical"
    prompt: str
    source: Literal["mock", "generated", "pasted"] = "generated"
    fallback_reason: Optional[str] = None
    constraints: Optional[str] = None  # technical: input size, ranges, edge conditions
    examples: list[QuestionExample] = Field(default_factory=list)  # technical: worked I/O
    meta: dict = Field(default_factory=dict)  # role, seniority, difficulty, topic
    owner_user_id: Optional[str] = None
    created_at: Optional[str] = None

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, value: object) -> str:
        """Keep legacy stored rows readable without ever overstating unknown provenance."""
        source = str(value or "").strip().lower()
        if source in {"generated", "pasted", "mock"}:
            return source
        if source == "user":
            return "pasted"
        if source == "bank":
            return "mock"
        # Old `followup` rows did not preserve whether they were live or bank-backed.
        # Label them conservatively instead of claiming live generation.
        return "mock"


class GenerateQuestionRequest(BaseModel):
    qtype: str = "behavioral"
    role: str = "Software Engineer"
    seniority: str = "mid"  # intern | new-grad | mid | senior
    difficulty: Optional[str] = None  # technical coding only: easy | medium | hard
    topic: Optional[str] = None
    track: Optional[str] = None  # technical only: coding | project


class CustomQuestionRequest(BaseModel):
    qtype: str = "behavioral"
    prompt: str
    meta: dict = Field(default_factory=dict)


class ScoreDimension(BaseModel):
    dimension: str
    score: float  # 1–5
    rationale: str = ""
    evidence: str = ""  # short quote / timestamp from the answer
    suggestion: str = ""


class ScoreSource(BaseModel):
    """A KB chunk actually retrieved while grading (never model-generated)."""

    id: str
    title: str
    url: Optional[str] = None
    snippet: str = ""


class DimensionDefinition(BaseModel):
    name: str
    description: str


class Scorecard(BaseModel):
    attempt_id: str
    rubric: str  # "star" | "technical"
    overall_score: float = 0.0  # 1–5
    overall_summary: str = ""
    dimensions: list[ScoreDimension] = Field(default_factory=list)
    sources: list[ScoreSource] = Field(default_factory=list)
    dimension_definitions: list[DimensionDefinition] = Field(default_factory=list)
    created_at: Optional[str] = None


class ScoreRequest(BaseModel):
    pseudocode: Optional[str] = None  # candidate's scratchpad notes (technical)


class ModelAnswer(BaseModel):
    rubric: str  # "star" | "technical"
    approach: str = ""    # technical: the optimal approach
    complexity: str = ""  # technical: time/space Big-O
    outline: str = ""     # behavioral: strong-answer outline
    key_points: list[str] = Field(default_factory=list)


# --- Mock interview (multi-question guided session with dynamic follow-ups) ----

class InterviewMainSpec(BaseModel):
    """An immutable spec for one planned MAIN question in an interview.

    The plan is built up front; each spec is realized into a Question when reached.
    ``followup_cap`` bounds how many dynamic follow-ups this main question can spawn.
    """
    qtype: str  # "behavioral" | "technical"
    track: Optional[str] = None  # technical: coding | system_design | project
    bucket: Optional[str] = None  # behavioral: experience | introspection | learning
    competency: Optional[str] = None  # experience bucket only
    difficulty: Optional[str] = None  # coding: easy | medium | hard
    followup_cap: int = 2
    focus: Optional[str] = None  # weakest content dimension; copied to question.meta.focus


class InterviewTurn(BaseModel):
    """One turn in an interview — a main question or a follow-up. Append-only log entry.

    Each turn points at a Question and (once the candidate answers) an attempt. All
    session cursors are DERIVED from this log, so no mutable counters are stored.
    """
    turn_id: str
    plan_index: int  # which InterviewMainSpec this turn belongs to
    is_followup: bool = False
    parent_turn_id: Optional[str] = None  # the main turn a follow-up hangs off
    question_id: str
    attempt_id: Optional[str] = None  # set when the candidate starts answering
    answered: bool = False


class InterviewReportTurn(BaseModel):
    """A turn listed in the final report. Its per-question scorecard is fetched on demand
    (via the attempt), not scored up front — the report leads with a general rubric."""
    turn_id: str
    question: str
    is_followup: bool
    attempt_id: Optional[str] = None  # to score this single question on demand
    rubric: str = ""
    overall_score: float = 0.0
    scorecard: Optional[Scorecard] = None


class InterviewReport(BaseModel):
    overall_score: float = 0.0  # 1–5, from the general rubric
    verdict: str = ""  # e.g. strong / mixed / needs work
    summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    followup_handling: str = ""  # how the candidate held up under probing
    # One generalized rubric for the whole interview (behavioral vs technical).
    general_scorecard: Optional[Scorecard] = None
    # Aggregate delivery across every answer in the interview
    total_fillers: int = 0
    avg_words_per_minute: float = 0.0
    total_pauses: int = 0
    turns: list[InterviewReportTurn] = Field(default_factory=list)


class InterviewSession(BaseModel):
    session_id: str
    status: str = "active"  # active | complete | abandoned
    mode: str = "behavioral"  # behavioral | technical
    user_id: Optional[str] = None
    guest_token: Optional[str] = None
    config: dict = Field(default_factory=dict)  # role, seniority, section
    plan: list[InterviewMainSpec] = Field(default_factory=list)
    turns: list[InterviewTurn] = Field(default_factory=list)
    report: Optional[InterviewReport] = None
    # Main questions realized AHEAD of time (plan_index -> question_id) so a transition
    # to the next main question doesn't block on generation. Populated by a background
    # prefetch after each turn; in-memory only (single worker), rebuilt lazily on restart.
    prefetched: dict[int, str] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StartInterviewRequest(BaseModel):
    mode: str = "behavioral"  # behavioral | technical
    section: Optional[str] = None  # technical only: coding | system_design | project
    role: str = "Software Engineer"
    seniority: str = "mid"  # intern | new-grad | mid | senior
    num_behavioral: int = 3  # behavioral only: how many main questions


class AdvanceInterviewRequest(BaseModel):
    attempt_id: str  # the just-finished answer's attempt
    turn_id: Optional[str] = None  # the turn that attempt answered (defaults to current)
    # Client-provided live transcript (browser speech-to-text). When present, the
    # follow-up decision uses it immediately instead of waiting for the server-side
    # Whisper transcript to finish persisting, lets /advance run in parallel with
    # answer analysis. Falls back to the persisted attempt transcript when blank.
    transcript: Optional[str] = None


class InterviewQuestionResponse(BaseModel):
    """Returned by start/advance: the next question to ask, or done."""
    done: bool = False
    session_id: str
    turn_id: Optional[str] = None
    question: Optional[Question] = None
    is_followup: bool = False
    progress: str = ""  # e.g. "Question 2 of 3" / "Follow-up"


class KBDocument(BaseModel):
    """A chunk of reference coaching material for RAG (one row of kb_documents)."""
    id: str
    kind: str = "behavioral_guidance"  # e.g. behavioral_guidance
    ref: Optional[str] = None  # source filename / topic key
    content: str
    embedding: list[float] = Field(default_factory=list)  # 768-dim; omitted in API responses
    meta: dict = Field(default_factory=dict)  # source, bucket, chunk index
    created_at: Optional[str] = None


# Recording budgets. Behavioral and coding answers: 3 min. Project / system design: 5 min.
ANSWER_CAP_BEHAVIORAL_SEC = 180
ANSWER_CAP_CODING_SEC = 180
ANSWER_CAP_DESIGN_SEC = 300


def answer_cap_sec(qtype: Optional[str] = None, track: Optional[str] = None) -> int:
    """Seconds allowed for one spoken answer, from question type and technical track."""
    if track in ("system_design", "project"):
        return ANSWER_CAP_DESIGN_SEC
    if qtype == "technical":
        return ANSWER_CAP_CODING_SEC
    return ANSWER_CAP_BEHAVIORAL_SEC
