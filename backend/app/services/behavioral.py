"""Interview rubric definitions — behavioral buckets + the technical "project" track.

Three behavioral buckets (experience/STAR, introspection, learning), each with its own
scoring lens so a "what are your strengths" answer isn't graded on the STAR
(Situation/Task/Action/Result) rubric meant for a "tell me about a time" story.
``generate_question`` picks one bucket at random; a typed (bring-your-own) question is
classified into a bucket by the LLM.

A project deep-dive ("walk me through your hardest project") is a *technical* conversation,
not behavioral, so it lives here as ``PROJECT_TRACK`` — one of the two technical categories
(coding vs project) — and is consumed by the technical scoring path, reusing the same Bucket
shape. Both ``questions.py`` and ``scoring.py`` read from here so each rubric is defined once.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Bucket:
    key: str
    label: str
    gen_guidance: str  # how to phrase a question in this bucket
    dimensions: list[tuple[str, str]]  # (dimension name, what it measures)
    answer_hint: str  # how a model answer should be framed
    scoring_intro: str = ""  # technical tracks: the framing line for the scoring prompt


# Shared tail dimensions on every behavioral answer, keeps delivery-grounded
# credibility consistent across all four buckets.
_CONCISE = ("Conciseness", "tight and structured vs rambling (use the delivery stats)")
_DELIVERY = ("Delivery", "spoken fluency and confidence given the filler/pace stats")

BUCKETS: dict[str, Bucket] = {
    "experience": Bucket(
        key="experience",
        label="experience story (STAR)",
        gen_guidance=(
            "A 'tell me about a time...' question inviting a STAR story — conflict, "
            "failure, ownership, teamwork, leadership, or handling ambiguity/pressure."
        ),
        dimensions=[
            ("Situation", "did they set clear, concise context?"),
            ("Task", "was their specific responsibility / goal clear?"),
            ("Action", "did they describe specific actions THEY took (watch 'I' vs 'we')?"),
            ("Result", "a concrete, ideally quantified outcome?"),
            ("Relevance", "did the story actually answer the question asked?"),
            ("Specificity", "concrete details and metrics vs vague generalities?"),
            _CONCISE,
            _DELIVERY,
        ],
        answer_hint="Outline how to structure a strong STAR answer: Situation, Task, Action, Result.",
    ),
    "introspection": Bucket(
        key="introspection",
        label="self-reflection & fit",
        gen_guidance=(
            "A candid self-assessment or motivation question — a key strength, a real "
            "weakness they're improving, feedback they acted on, or why they're drawn to engineering."
        ),
        dimensions=[
            ("Self-awareness", "honest and specific, not a humble-brag or canned answer?"),
            ("Evidence", "did they back the claim with a concrete example?"),
            ("Growth mindset", "for a weakness/feedback — what are they actively doing about it?"),
            ("Authenticity & motivation", "does it read as genuine rather than rehearsed?"),
            ("Relevance", "did they actually answer what was asked?"),
            _CONCISE,
            _DELIVERY,
        ],
        answer_hint=(
            "Outline a strong answer: a specific, honest claim -> a concrete example that "
            "proves it -> what they're actively doing to grow (for weaknesses/feedback)."
        ),
    ),
    "learning": Bucket(
        key="learning",
        label="learning & curiosity",
        gen_guidance=(
            "A question about how they learn — a technical concept they genuinely enjoyed "
            "learning, ramping up on something hard fast, or how they stay current."
        ),
        dimensions=[
            ("Understanding", "do they actually understand the concept they chose, not just name it?"),
            ("Curiosity & passion", "genuine enthusiasm and intellectual curiosity?"),
            ("Clarity of explanation", "could a listener follow it — can they teach it?"),
            ("Learning approach", "did they show how they learn (resources, practice, first principles)?"),
            ("Relevance", "did they answer the question asked?"),
            _CONCISE,
            _DELIVERY,
        ],
        answer_hint=(
            "Outline a strong answer: pick one concrete concept -> explain it clearly and "
            "simply -> convey genuine curiosity and how they learned it."
        ),
    ),
}

BUCKET_KEYS = list(BUCKETS.keys())
DEFAULT_BUCKET = "experience"

# Competencies probed by the "experience" (STAR) bucket. These are TAGS, not separate
# rubrics: every experience answer is scored on the same STAR dimensions above. The
# competency just steers what a generated question asks about and what evidence the
# scorer should reward. Only meaningful for the experience bucket; other buckets ignore it.
# Easy to extend (e.g. "pressure", "influence", "mentorship"), just add an entry.
EXPERIENCE_COMPETENCIES: dict[str, str] = {
    "conflict": "a disagreement with a teammate, manager, or stakeholder — how they navigated it to a resolution",
    "failure": "a mistake, bug, outage, or project that went wrong that they owned — and what they learned",
    "ownership": "taking initiative or end-to-end responsibility for something beyond their assigned role",
    "teamwork": "collaborating with or helping others — cross-functional work, unblocking a teammate, building consensus",
    "leadership": "leading without formal authority — driving a project or decision, mentoring, or rallying a team",
    "ambiguity": "making progress under unclear, shifting, or under-specified requirements",
}
EXPERIENCE_COMPETENCY_KEYS = list(EXPERIENCE_COMPETENCIES.keys())


def get_competency_guidance(key: str | None) -> str | None:
    """Resolve an experience-bucket competency to its phrasing guidance, or None."""
    return EXPERIENCE_COMPETENCIES.get((key or "").strip().lower())

# Technical tracks beyond plain coding. Same Bucket shape, but consumed by the technical
# scoring/generation path (not part of the behavioral BUCKETS above). "coding" stays special
# (constraints/examples/pseudocode + TECHNICAL_DIMENSIONS in scoring.py) and is not here.
PROJECT_TRACK = Bucket(
    key="project",
    label="project deep-dive",
    gen_guidance=(
        "Ask the candidate to walk through a specific project — the one they're proudest of, "
        "the most technically challenging, or the most impactful — and their personal role in "
        "it. This is a spoken project deep-dive, NOT a coding problem: no algorithm, constraints, "
        "or test cases."
    ),
    dimensions=[
        ("Context", "did they explain the problem and why it mattered, briefly?"),
        ("Your contribution", "is THEIR specific role and what they personally built clear ('I' vs 'we')?"),
        ("Technical depth", "did they surface real decisions, trade-offs, and challenges?"),
        ("Impact", "a concrete outcome or result — users, performance, what shipped?"),
        ("Relevance", "did they pick a project that genuinely showcases their ability?"),
        _CONCISE,
        _DELIVERY,
    ],
    answer_hint=(
        "Outline how to walk through a project: the problem -> their specific role -> "
        "key technical decisions and trade-offs -> the impact."
    ),
    scoring_intro=(
        "scoring a candidate's spoken PROJECT DEEP-DIVE — they are walking through a project they "
        "worked on (not solving a coding problem). Judge how well they communicate the work and "
        "their role"
    ),
)

SYSTEM_DESIGN_TRACK = Bucket(
    key="system_design",
    label="system design",
    gen_guidance=(
        "Ask a classic system-design question — design a well-known system or feature and reason "
        "about scale and trade-offs (e.g. 'Design Uber's surge pricing', 'Design a URL shortener', "
        "'Design a news feed', 'Design a rate limiter'). This is a spoken architecture discussion, "
        "NOT a coding problem: no algorithm puzzle, constraints, or test cases."
    ),
    dimensions=[
        ("Requirements & scope", "did they clarify functional/non-functional requirements and estimate scale (users, QPS, data)?"),
        ("High-level design", "coherent core components, APIs, and data flow?"),
        ("Data model & deep dive", "sound storage choices and a real deep-dive into the key mechanism (e.g. the surge-pricing calc)?"),
        ("Scalability & bottlenecks", "did they find and address what breaks at scale — sharding, caching, load balancing?"),
        ("Trade-offs", "are choices justified (e.g. consistency vs availability) with alternatives weighed?"),
        ("Communication", "structured, clear walkthrough a listener can follow?"),
        _DELIVERY,
    ],
    answer_hint=(
        "Outline how to approach system design: clarify requirements & scale -> sketch the "
        "high-level components and data flow -> deep-dive the key mechanism -> address scaling "
        "bottlenecks and trade-offs."
    ),
    scoring_intro=(
        "scoring a candidate's spoken SYSTEM DESIGN answer — they are talking through how they "
        "would architect a system at scale (not writing code). Judge the soundness of the design "
        "and how well they reason about scale and trade-offs"
    ),
)

# Non-coding technical tracks, keyed by meta.track.
TECHNICAL_TRACKS: dict[str, Bucket] = {
    PROJECT_TRACK.key: PROJECT_TRACK,
    SYSTEM_DESIGN_TRACK.key: SYSTEM_DESIGN_TRACK,
}


def get_technical_track(key: str | None) -> Bucket | None:
    """Resolve a non-coding technical track (project/system_design), or None for coding."""
    return TECHNICAL_TRACKS.get((key or "").strip().lower())


def get_bucket(key: str | None) -> Bucket:
    """Resolve a bucket key, falling back to the classic STAR experience bucket."""
    return BUCKETS.get((key or "").strip().lower(), BUCKETS[DEFAULT_BUCKET])


# Seniority calibration, the "something personal depending on who it is" the user
# asked for. Scales expectations so an intern isn't graded against senior-level scope.
_SENIORITY_CALIBRATION = {
    "intern": (
        "This is an INTERN candidate — expect examples from coursework, personal projects, "
        "hackathons, or a first internship. Don't expect industry leadership or large-scale "
        "ownership; reward initiative, curiosity, and learning."
    ),
    "new-grad": (
        "This is a NEW-GRAD candidate — expect examples from internships, capstone/academic "
        "projects, and side projects. Reward clear thinking and growth; don't expect senior scope."
    ),
    "mid": (
        "This is a MID-LEVEL engineer — expect concrete professional examples with real "
        "ownership and measurable impact."
    ),
    "senior": (
        "This is a SENIOR engineer — expect leadership, cross-team influence, mentoring, and "
        "significant, quantified impact; hold them to a high bar."
    ),
}


def seniority_note(seniority: str | None) -> str:
    return _SENIORITY_CALIBRATION.get((seniority or "").strip().lower(), "")


# Concrete per-level score anchors for BEHAVIORAL grading. Same questions across levels;
# what changes is the BAR. These tell the scorer what a 5 vs 3 vs 1–2 looks like at each
# level so the same story is graded appropriately (an intern isn't held to senior scope,
# and a small-scope story doesn't score high at the senior bar).
_SENIORITY_GRADING_ANCHORS = {
    "intern": (
        "Grade at an INTERN bar. 5 = a specific story from coursework, a personal/hackathon "
        "project, or a first internship, with clear ownership of THEIR part, concrete details, "
        "and genuine reflection/learning. 3 = relevant but vague on specifics or their exact role. "
        "1–2 = generic, no concrete example, or doesn't answer. Do NOT penalize small scope or "
        "lack of industry/leadership experience — reward initiative, curiosity, and coachability."
    ),
    "new-grad": (
        "Grade at a NEW-GRAD bar. 5 = a specific example from an internship, capstone, or serious "
        "side project with clear individual contribution, a concrete outcome, and thoughtful "
        "reflection. 3 = relevant but light on impact or specifics. 1–2 = vague or generic. "
        "Don't expect large-scale ownership or leadership."
    ),
    "mid": (
        "Grade at a MID-LEVEL bar. 5 = a professional example with real end-to-end ownership, "
        "measurable impact, and clear trade-off reasoning. 3 = solid but limited scope, fuzzy "
        "impact, or more 'we' than 'I'. 1–2 = generic or lacking ownership/results. Expect concrete "
        "metrics and clear individual contribution."
    ),
    "senior": (
        "Grade at a SENIOR bar — hold to a high standard. 5 = leadership or cross-team influence, "
        "significant QUANTIFIED impact, mentoring, and driving decisions under ambiguity. 3 = good "
        "individual work but limited scope/influence for the level. 1–2 = no leadership/scope or "
        "vague results. Small-scope, individual-only stories should NOT score high."
    ),
}


def seniority_grading_anchor(seniority: str | None) -> str:
    """Level-specific score anchors for behavioral grading (empty if unknown)."""
    return _SENIORITY_GRADING_ANCHORS.get((seniority or "").strip().lower(), "")
