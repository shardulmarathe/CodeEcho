"""Filler word detection with whitelist heuristics."""

import re
from typing import Optional

from app.models import FillerOccurrence, WordTimestamp

# Non-lexical fillers, unambiguous, always counted. No real word collides with these,
# so they need no context to decide.
CLASSIC_FILLERS = {
    "um", "umm", "uhm", "uh", "uhh", "er", "err", "ah", "ahh",
    "hmm", "hm", "mhm", "eh", "mm",
}

# Bigram fillers
BIGRAM_FILLERS = [("you", "know")]

# Discourse markers that are *sometimes* a verbal tic and sometimes a meaningful word.
# These are never counted blindly, every occurrence is gathered as a CANDIDATE and
# judged in context (LLM when configured, heuristic fallback otherwise).
DISCOURSE_MARKERS = {"like", "actually", "basically", "literally"}

# Heuristic fallback only (used when no LLM): "like" preceded by one of these reads as a
# real verb / comparison, not a filler, e.g. "I like", "would like", "looks like rain".
LIKE_REAL_PRECEDING = {
    "i", "you", "we", "they", "he", "she", "who", "to", "would", "wouldn't",
    "do", "don't", "does", "doesn't", "did", "didn't", "really", "also", "not",
    "might", "may", "should", "'d", "'ll", "will", "people", "users", "everyone",
    "looks", "look", "looked", "feels", "feel", "felt", "seems", "seem", "seemed",
    "sounds", "sound", "sounded", "tastes", "smells",
}

# Words that, when they immediately precede "like", make it a quotative discourse marker
# ("I was like done", "she's like really fast", "they were like nope"). This is *always*
# a filler, there is no verb/comparison reading, so it overrides LIKE_REAL_PRECEDING.
LIKE_QUOTATIVE_PRECEDING = {"was", "were", "is", "am", "are", "be", "been", "m", "re", "s"}

# Fixed transition phrases
TRANSITION_PHRASES = [
    "next",
    "another reason",
    "furthermore",
    "however",
    "moving on",
    "in contrast",
    "secondly",
    "on the other hand",
    "additionally",
    "first",
    "second",
    "finally",
    "in addition",
    "moreover",
    "meanwhile",
    "that said",
    "to summarize",
]

TRANSITION_WINDOW_SEC = 3.0
LONG_PAUSE_THRESHOLD_SEC = 0.8


def _normalize(word: str) -> str:
    return re.sub(r"[^\w']", "", word.lower())


def _get_context(words: list[WordTimestamp], index: int, radius: int = 8) -> str:
    start = max(0, index - radius)
    end = min(len(words), index + radius + 1)
    return " ".join(w.word for w in words[start:end])


def discourse_candidates(words: list[WordTimestamp]) -> list[int]:
    """Indices of words that *might* be filler discourse markers (like/actually/...).

    These are decided in context downstream, not here — see
    ``classify_discourse_fillers`` (LLM) and ``heuristic_discourse_fillers`` (fallback).
    """
    return [i for i, w in enumerate(words) if _normalize(w.word) in DISCOURSE_MARKERS]


def _ends_with_comma(word: str) -> bool:
    return word.strip().endswith(",")


def _is_quotative_like(words: list[WordTimestamp], index: int) -> bool:
    """True when "like" reads as a quotative tic — "I was like", "she's like"."""
    if index == 0:
        return False
    prev = _normalize(words[index - 1].word)
    if prev in LIKE_QUOTATIVE_PRECEDING:
        return True
    # Be-contractions keep their apostrophe after normalization: "i'm", "she's", "we're".
    return prev.endswith("'m") or prev.endswith("'re") or prev.endswith("'s")


def like_is_high_confidence_filler(words: list[WordTimestamp], index: int) -> bool:
    """Unambiguous "like"-as-filler signals that need no LLM and have no verb reading.

    These are used as a safety floor in the LLM path so obvious fillers are never missed:
    - quotative use — "I was like", "she's like";
    - comma-wrapped discourse marker — "it's, like, fast" (the transcriber brackets it).
    """
    if _normalize(words[index].word) != "like":
        return False
    if _is_quotative_like(words, index):
        return True
    # Comma immediately before or after marks a parenthetical discourse marker.
    if _ends_with_comma(words[index].word):
        return True
    if index > 0 and _ends_with_comma(words[index - 1].word):
        return True
    return False


def _like_is_filler_heuristic(words: list[WordTimestamp], index: int) -> bool:
    """Best-effort, LLM-free decision for a single 'like'. Used only offline/mock.

    Defaults to *filler* (the common case in casual speech) and only bows out when the
    preceding word makes it a clear verb or comparison — "I like", "looks like rain".
    """
    if like_is_high_confidence_filler(words, index):
        return True
    prev_word = _normalize(words[index - 1].word) if index > 0 else ""
    return prev_word not in LIKE_REAL_PRECEDING


def high_confidence_discourse_fillers(
    words: list[WordTimestamp], candidates: list[int]
) -> set[int]:
    """Subset of candidates that are unambiguous fillers regardless of LLM judgment.

    Currently only the strong "like" signals (quotative / comma-wrapped); the other
    markers (actually/basically/literally) are left entirely to the LLM in that path.
    """
    return {
        i
        for i in candidates
        if _normalize(words[i].word) == "like" and like_is_high_confidence_filler(words, i)
    }


def heuristic_discourse_fillers(
    words: list[WordTimestamp], candidates: list[int]
) -> set[int]:
    """Offline fallback: decide discourse-marker candidates without an LLM."""
    confirmed: set[int] = set()
    for i in candidates:
        word = _normalize(words[i].word)
        if word == "like":
            if _like_is_filler_heuristic(words, i):
                confirmed.add(i)
        else:
            # actually / basically / literally, default to filler when no context.
            confirmed.add(i)
    return confirmed


def make_filler(
    words: list[WordTimestamp], index: int, label: Optional[str] = None
) -> FillerOccurrence:
    """Build a FillerOccurrence for the word at ``index``.

    ``label`` is the displayed filler word; defaults to the normalized token.
    """
    w = words[index]
    return FillerOccurrence(
        word=label or _normalize(w.word),
        start=w.start,
        end=w.end,
        index=index,
        context=_get_context(words, index),
        sentence_position="middle",  # filled later
        is_transition_related=False,
    )


def _is_you_know_filler(words: list[WordTimestamp], index: int) -> bool:
    if index >= len(words) - 1:
        return False
    if _normalize(words[index].word) != "you":
        return False
    if _normalize(words[index + 1].word) != "know":
        return False

    # Skip fixed phrases
    if index + 2 < len(words):
        third = _normalize(words[index + 2].word)
        if third in ("what", "it", "how", "if", "when", "where", "who"):
            return False

    return True


def detect_fillers(words: list[WordTimestamp]) -> list[FillerOccurrence]:
    """Deterministic pass: unambiguous non-lexical fillers + the "you know" bigram.

    Ambiguous discourse markers (like/actually/...) are intentionally NOT decided here —
    they are gathered via ``discourse_candidates`` and judged in context by the pipeline.
    """
    fillers: list[FillerOccurrence] = []
    skip_indices: set[int] = set()

    for i, w in enumerate(words):
        if i in skip_indices:
            continue

        normalized = _normalize(w.word)

        if normalized in CLASSIC_FILLERS:
            fillers.append(make_filler(words, i, normalized))
        elif _is_you_know_filler(words, i):
            fillers.append(make_filler(words, i, "you know"))
            skip_indices.add(i + 1)

    return fillers


def classify_sentence_positions(
    words: list[WordTimestamp], fillers: list[FillerOccurrence]
) -> list[FillerOccurrence]:
    """Classify filler position within sentence using punctuation boundaries."""
    if not words:
        return fillers

    # Build sentence boundaries from punctuation in transcript
    sentence_starts: list[int] = [0]
    sentence_ends: list[int] = []

    for i, w in enumerate(words):
        if re.search(r"[.!?]$", w.word.strip()):
            sentence_ends.append(i)
            if i + 1 < len(words):
                sentence_starts.append(i + 1)

    if not sentence_ends or sentence_ends[-1] != len(words) - 1:
        sentence_ends.append(len(words) - 1)

    def position_for_index(idx: int) -> str:
        for s_start, s_end in zip(sentence_starts, sentence_ends):
            if s_start <= idx <= s_end:
                span = s_end - s_start
                if span == 0:
                    return "beginning"
                rel = (idx - s_start) / span
                if rel <= 0.2:
                    return "beginning"
                if rel >= 0.8:
                    return "end"
                return "middle"
        return "middle"

    for filler in fillers:
        filler.sentence_position = position_for_index(filler.index)

    return fillers


def mark_transition_fillers(
    words: list[WordTimestamp],
    fillers: list[FillerOccurrence],
    gemini_transition_indices: Optional[set[int]] = None,
) -> list[FillerOccurrence]:
    """Mark fillers near transition phrases (rule-based + optional Gemini hits)."""
    gemini_transition_indices = gemini_transition_indices or set()

    # Find transition phrase timestamps in transcript
    full_text = " ".join(w.word for w in words).lower()
    transition_times: list[float] = []

    for phrase in TRANSITION_PHRASES:
        idx = 0
        while True:
            pos = full_text.find(phrase, idx)
            if pos == -1:
                break
            # Approximate word index from char position
            char_count = 0
            for wi, w in enumerate(words):
                if char_count >= pos:
                    transition_times.append(w.start)
                    break
                char_count += len(w.word) + 1
            idx = pos + len(phrase)

    for filler in fillers:
        if filler.index in gemini_transition_indices:
            filler.is_transition_related = True
            continue
        for t_time in transition_times:
            if abs(filler.start - t_time) <= TRANSITION_WINDOW_SEC:
                filler.is_transition_related = True
                break

    return fillers
