"""Idea transition analysis via configured LLM provider."""

import json
import re
from concurrent.futures import ThreadPoolExecutor

from app.config import settings
from app.models import WordTimestamp
from app.services.budget import check_budget, cost_of_call, record_cost
from app.services.llm_client import chat_completion, get_provider, is_configured


def _segment_transcript(words: list[WordTimestamp], segment_duration: float = 45.0) -> list[dict]:
    if not words:
        return []

    segments: list[dict] = []
    current_words: list[WordTimestamp] = []
    segment_start = words[0].start

    for w in words:
        if w.start - segment_start > segment_duration and current_words:
            segments.append(
                {
                    "start": segment_start,
                    "end": current_words[-1].end,
                    "text": " ".join(cw.word for cw in current_words),
                    "word_indices": [cw.index for cw in current_words],
                }
            )
            current_words = [w]
            segment_start = w.start
        else:
            current_words.append(w)

    if current_words:
        segments.append(
            {
                "start": segment_start,
                "end": current_words[-1].end,
                "text": " ".join(cw.word for cw in current_words),
                "word_indices": [cw.index for cw in current_words],
            }
        )

    return segments


def analyze_transitions(words: list[WordTimestamp], fillers: list) -> set[int]:
    if not is_configured():
        return set()

    try:
        check_budget()
    except Exception:
        return set()

    segments = _segment_transcript(words)
    if not segments:
        return set()

    filler_by_index = {f.index: f for f in fillers}
    transition_indices: set[int] = set()

    for seg in segments:
        seg_fillers = [f for f in fillers if f.index in seg["word_indices"]]
        if not seg_fillers:
            continue

        filler_list = ", ".join(
            f'"{f.word}" at index {f.index}' for f in seg_fillers
        )

        prompt = f"""Analyze this speech transcript segment for idea transitions.

Transcript segment:
"{seg['text']}"

Filler words in this segment: {filler_list}

Determine which filler words occur during or near an idea transition (when the speaker shifts from one concept to another).

Known transition signals: next, however, furthermore, moving on, in contrast, secondly, on the other hand, additionally, first, second, finally.

Respond ONLY with valid JSON in this exact format:
{{
  "transition_filler_indices": [list of filler word indices that occur during idea transitions],
  "transition_phrases_found": ["list of transition phrases detected in the segment"]
}}"""

        try:
            result = chat_completion(prompt)
            text = result.text
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for idx in data.get("transition_filler_indices", []):
                    if idx in filler_by_index:
                        transition_indices.add(idx)

            cost = cost_of_call(result, prompt)
            record_cost(
                get_provider().value,
                f"Transition analysis segment {seg['start']:.0f}s",
                cost,
            )
        except Exception:
            continue

    return transition_indices


def analyze_transitions_mock(words: list[WordTimestamp], fillers: list) -> set[int]:
    return set()


# ---------------------------------------------------------------------------
# Discourse-marker disambiguation
#
# Words like "like", "actually", "basically", "literally" are fillers in some
# contexts and meaningful in others. A regex can't tell them apart, so each
# candidate occurrence is judged in context by the LLM.
# ---------------------------------------------------------------------------

def classify_discourse_fillers(
    words: list[WordTimestamp], candidate_indices: list[int]
) -> set[int]:
    """Return the subset of candidate indices that are genuine fillers, judged in context.

    ``candidate_indices`` are positions of discourse markers (like/actually/...) found by
    ``filler_detect.discourse_candidates``. Falls back to an empty set on any failure so
    the caller can apply its own heuristic.
    """
    if not is_configured() or not candidate_indices:
        return set()

    try:
        check_budget()
    except Exception:
        return set()

    candidate_set = set(candidate_indices)
    segments = _segment_transcript(words)

    def _process(seg) -> set[int]:
        seg_cands = [i for i in seg["word_indices"] if i in candidate_set]
        if not seg_cands:
            return set()

        listing = "\n".join(f'- index {i}: "{words[i].word}"' for i in seg_cands)

        prompt = f"""You are a precise speech analyst. For each listed word in the segment,
decide whether it is used as a FILLER (a discourse marker / verbal tic that adds no
meaning and could be deleted without changing the sentence) or as a MEANINGFUL word.

Default to FILLER unless the word clearly carries meaning. In casual and interview
speech, "like" is a filler far more often than not — do not miss these.

Rules for "like":
- FILLER (the common case) — discourse marker, hedge, quotative, or approximator:
  "it's, like, really fast", "we should like refactor it", "I was like done",
  "she's like nope", "we had like three options", "it's like the main bottleneck",
  "like, I think the issue is...", "you can just, like, cache it".
  A reliable test: if you can delete "like" and the sentence still means the same thing,
  it is a FILLER.
- NOT a filler ONLY when it is a real verb ("I like this approach", "users would like
  that", "people like clean code") or a genuine comparison/example that carries meaning
  and cannot be deleted ("it behaves like a hash map", "sounds like rain", "languages
  like Python and Go").

Rules for "actually", "basically", "literally":
- FILLER: reflexive emphasis that could be removed with no loss
  ("it's basically just a loop", "I literally just return it", "so actually, um...").
- NOT a filler: when it carries real contrast or meaning
  ("it actually returns null, not zero", "literally" meaning not-figuratively).

Transcript segment:
"{seg['text']}"

Words to judge:
{listing}

Respond ONLY with valid JSON in this exact format:
{{"filler_indices": [list of indices, from the list above, that are FILLERS]}}"""

        out: set[int] = set()
        try:
            result = chat_completion(prompt)
            text = result.text
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                seg_word_set = set(seg["word_indices"])
                for idx in data.get("filler_indices", []):
                    if idx in candidate_set and idx in seg_word_set:
                        out.add(idx)

            cost = cost_of_call(result, prompt)
            record_cost(
                get_provider().value,
                f"Discourse-filler disambiguation segment {seg['start']:.0f}s",
                cost,
            )
        except Exception:
            return set()
        return out

    # Segments are independent, judge them concurrently.
    confirmed: set[int] = set()
    with ThreadPoolExecutor(max_workers=min(4, max(1, len(segments)))) as ex:
        for seg_result in ex.map(_process, segments):
            confirmed |= seg_result
    return confirmed


# ---------------------------------------------------------------------------
# Contextual filler tagging
#
# Classifies *why* each filler occurred. Generalizes the transition analysis
# above into descriptive, per-filler tags surfaced to the user.
# ---------------------------------------------------------------------------

VALID_TAGS = {"idea_transition", "topic_mention", "hesitation"}


def tag_fillers(words: list[WordTimestamp], fillers: list) -> dict[int, dict]:
    """Tag each filler with why it occurred, via the configured LLM provider.

    Returns a mapping of filler word index -> {"tag", "reason", "topic"}.
    Fillers the model classifies as "none" are simply omitted from the map.
    """
    if not is_configured():
        return tag_fillers_mock(words, fillers)

    try:
        check_budget()
    except Exception:
        return {}

    segments = _segment_transcript(words)
    if not segments:
        return {}

    def _process(seg) -> dict[int, dict]:
        seg_fillers = [f for f in fillers if f.index in seg["word_indices"]]
        if not seg_fillers:
            return {}

        filler_list = "\n".join(
            f'- index {f.index}: "{f.word}"' for f in seg_fillers
        )

        prompt = f"""You are a speech coach analyzing why a speaker used filler words.

Transcript segment:
"{seg['text']}"

Filler words used in this segment (with their indices):
{filler_list}

For EACH filler word above, classify why it most likely occurred into exactly one category:
- "idea_transition": the speaker is shifting from one point or section to the next.
- "topic_mention": the filler clusters around a specific subject/concept the speaker is introducing or struggling to name.
- "hesitation": the speaker is searching for a word or recalling a fact (a stall), not tied to a transition or topic.
- "none": no clear pattern; an unconscious habit.

Respond ONLY with valid JSON in this exact format:
{{
  "tags": [
    {{"index": <filler index>, "tag": "idea_transition|topic_mention|hesitation|none", "reason": "<short one-line explanation>", "topic": "<subject if tag is topic_mention, else empty string>"}}
  ]
}}"""

        seg_tags: dict[int, dict] = {}
        try:
            result = chat_completion(prompt)
            text = result.text
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for item in data.get("tags", []):
                    idx = item.get("index")
                    tag = item.get("tag")
                    if idx is None or tag not in VALID_TAGS:
                        continue
                    if not any(f.index == idx for f in seg_fillers):
                        continue
                    topic = (item.get("topic") or "").strip()
                    seg_tags[idx] = {
                        "tag": tag,
                        "reason": (item.get("reason") or "").strip(),
                        "topic": topic if tag == "topic_mention" and topic else None,
                    }

            cost = cost_of_call(result, prompt)
            record_cost(
                get_provider().value,
                f"Filler tagging segment {seg['start']:.0f}s",
                cost,
            )
        except Exception:
            return {}
        return seg_tags

    # Segments are independent, tag them concurrently, then merge.
    tags: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=min(4, max(1, len(segments)))) as ex:
        for seg_result in ex.map(_process, segments):
            tags.update(seg_result)
    return tags


def tag_fillers_mock(words: list[WordTimestamp], fillers: list) -> dict[int, dict]:
    """Heuristic tagging for demo mode — marks fillers near transition phrases."""
    from app.services.filler_detect import mark_transition_fillers

    marked = mark_transition_fillers(words, list(fillers))
    transition_indices = {f.index for f in marked if f.is_transition_related}
    return {
        idx: {
            "tag": "idea_transition",
            "reason": "Occurs near an idea-transition phrase.",
            "topic": None,
        }
        for idx in transition_indices
    }
