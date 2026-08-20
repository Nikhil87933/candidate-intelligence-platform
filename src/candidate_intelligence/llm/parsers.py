"""Parsers for converting raw LLM output into domain models."""

from __future__ import annotations

import json

from candidate_intelligence.domain.candidate import Candidate


class CandidateParsingError(ValueError):
    """Raised when LLM output cannot be parsed into a Candidate."""


def parse_candidate_understanding(candidate_id: str, raw_json: str) -> Candidate:
    """Parse raw LLM JSON output into a structured Candidate object."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise CandidateParsingError(f"LLM response was not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise CandidateParsingError("LLM response JSON was not an object.")

    data["candidate_id"] = candidate_id

    try:
        return Candidate.model_validate(data)
    except Exception as exc:
        raise CandidateParsingError(
            f"LLM response JSON did not match the expected candidate schema: {exc}"
        ) from exc
