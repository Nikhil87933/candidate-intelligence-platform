"""Builds embedding-ready narrative text from a structured candidate profile."""

from __future__ import annotations

from candidate_intelligence.domain.candidate import Candidate


def build_candidate_narrative(candidate: Candidate) -> str:
    """Compose a dense narrative paragraph from a structured Candidate.

    The output is intended to be used as the text passed to the embedding
    model, so it favors concrete, information-rich phrasing over prose
    style.
    """
    parts: list[str] = []

    if candidate.full_name:
        parts.append(f"Candidate: {candidate.full_name}.")

    if candidate.total_experience_years is not None:
        parts.append(f"Total experience: {candidate.total_experience_years} years.")

    if candidate.skills:
        parts.append(f"Skills: {', '.join(candidate.skills)}.")

    if candidate.work_experience:
        experience_parts = []
        for entry in candidate.work_experience:
            segment = f"{entry.title} at {entry.company}"
            if entry.duration:
                segment += f" ({entry.duration})"
            if entry.description:
                segment += f": {entry.description}"
            experience_parts.append(segment)
        parts.append("Work experience: " + " | ".join(experience_parts) + ".")

    if candidate.education:
        education_parts = []
        for education_entry in candidate.education:
            segment = f"{education_entry.degree} from {education_entry.institution}"
            if education_entry.year:
                segment += f" ({education_entry.year})"
            education_parts.append(segment)
        parts.append("Education: " + " | ".join(education_parts) + ".")

    if candidate.summary:
        parts.append(f"Summary: {candidate.summary}")

    return " ".join(parts)
