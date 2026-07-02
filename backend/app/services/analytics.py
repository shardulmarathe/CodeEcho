"""Compute speech analytics metrics from transcript and fillers."""

from app.models import (
    FillerOccurrence,
    PauseOccurrence,
    PositionBreakdown,
    SessionMetrics,
    WordTimestamp,
)
from app.services.filler_detect import LONG_PAUSE_THRESHOLD_SEC


def compute_metrics(
    words: list[WordTimestamp],
    fillers: list[FillerOccurrence],
    duration_sec: float | None = None,
    pauses: list[PauseOccurrence] | None = None,
) -> SessionMetrics:
    if not words:
        return SessionMetrics()

    # Prefer explicit audio duration (from file); fall back to word timestamps
    words_end = words[-1].end if words else 0.0
    if duration_sec and duration_sec > 0:
        total_duration = duration_sec
    elif words_end > 0:
        total_duration = words_end
    else:
        total_duration = max(words[-1].end - words[0].start, 1.0)

    pauses = pauses or []
    total_fillers = len(fillers)
    minutes = total_duration / 60.0
    fpm = total_fillers / minutes if minutes > 0 else 0.0
    # WPM: all transcribed words over total audio duration (standard speech rate)
    wpm = len(words) / minutes if minutes > 0 else 0.0

    # Pause analysis — all inter-word gaps (incl. small ones) for the average.
    # The structured ``pauses`` list (passed in) holds only the larger surfaced gaps.
    gaps: list[float] = []
    for i in range(1, len(words)):
        gap = words[i].start - words[i - 1].end
        if gap > 0.05:  # ignore micro-gaps
            gaps.append(gap)

    avg_pause = sum(gaps) / len(gaps) if gaps else 0.0

    pauses_before_filler: list[float] = []
    pauses_elsewhere: list[float] = []
    long_pause_fillers = 0

    filler_indices = {f.index for f in fillers}
    for i in range(1, len(words)):
        gap = words[i].start - words[i - 1].end
        if gap <= 0.05:
            continue
        if i in filler_indices:
            pauses_before_filler.append(gap)
            if gap > LONG_PAUSE_THRESHOLD_SEC:
                long_pause_fillers += 1
        else:
            pauses_elsewhere.append(gap)

    avg_pause_before = (
        sum(pauses_before_filler) / len(pauses_before_filler)
        if pauses_before_filler
        else 0.0
    )
    avg_pause_elsewhere = (
        sum(pauses_elsewhere) / len(pauses_elsewhere) if pauses_elsewhere else 0.0
    )
    long_pause_pct = (
        (long_pause_fillers / total_fillers * 100) if total_fillers > 0 else 0.0
    )

    # Position breakdown
    positions = {"beginning": 0, "middle": 0, "end": 0}
    for f in fillers:
        positions[f.sentence_position] = positions.get(f.sentence_position, 0) + 1

    total_pos = sum(positions.values()) or 1
    position_breakdown = PositionBreakdown(
        beginning=round(positions["beginning"] / total_pos * 100, 1),
        middle=round(positions["middle"] / total_pos * 100, 1),
        end=round(positions["end"] / total_pos * 100, 1),
    )

    # Filler type breakdown
    filler_breakdown: dict[str, int] = {}
    for f in fillers:
        filler_breakdown[f.word] = filler_breakdown.get(f.word, 0) + 1

    # Tag breakdown — why fillers occurred (idea_transition / topic_mention / hesitation)
    tag_breakdown: dict[str, int] = {}
    for f in fillers:
        if f.tag:
            tag_breakdown[f.tag] = tag_breakdown.get(f.tag, 0) + 1

    transition_count = tag_breakdown.get("idea_transition", 0)
    transition_pct = (
        (transition_count / total_fillers * 100) if total_fillers > 0 else 0.0
    )

    # Pause counts (surfaced gaps, from pause_detect)
    total_pauses = len(pauses)
    long_pauses = sum(1 for p in pauses if p.is_long)
    total_pause_sec = sum(p.duration for p in pauses)
    ppm = total_pauses / minutes if minutes > 0 else 0.0

    return SessionMetrics(
        duration_sec=round(total_duration, 2),
        total_fillers=total_fillers,
        fillers_per_minute=round(fpm, 2),
        words_per_minute=round(wpm, 1),
        avg_pause_sec=round(avg_pause, 2),
        avg_pause_before_filler_sec=round(avg_pause_before, 2),
        avg_pause_elsewhere_sec=round(avg_pause_elsewhere, 2),
        total_pauses=total_pauses,
        long_pauses=long_pauses,
        pauses_per_minute=round(ppm, 2),
        total_pause_sec=round(total_pause_sec, 1),
        long_pause_filler_pct=round(long_pause_pct, 1),
        transition_filler_pct=round(transition_pct, 1),
        position_breakdown=position_breakdown,
        filler_breakdown=filler_breakdown,
        tag_breakdown=tag_breakdown,
    )
