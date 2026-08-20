"""Tests for LLM output parsing."""

import json

import pytest

from candidate_intelligence.llm.parsers import (
    CandidateParsingError,
    parse_candidate_understanding,
)


def test_parse_candidate_understanding_valid_json() -> None:
    """Verify valid LLM JSON output parses into a Candidate."""
    raw_json = json.dumps(
        {
            "full_name": "Nikhil Chamle",
            "email": "nikhil@example.com",
            "phone": None,
            "total_experience_years": 5.5,
            "skills": ["Python", "FastAPI"],
            "education": [
                {"degree": "B.Tech", "institution": "XYZ University", "year": "2018"}
            ],
            "work_experience": [
                {
                    "title": "Software Engineer",
                    "company": "Acme Corp",
                    "duration": "2018-2023",
                    "description": "Built backend systems.",
                }
            ],
            "summary": "Experienced backend engineer.",
        }
    )

    candidate = parse_candidate_understanding("candidate-1", raw_json)

    assert candidate.candidate_id == "candidate-1"
    assert candidate.full_name == "Nikhil Chamle"
    assert candidate.skills == ["Python", "FastAPI"]
    assert candidate.education[0].degree == "B.Tech"


def test_parse_candidate_understanding_invalid_json_raises() -> None:
    """Verify malformed JSON raises CandidateParsingError."""
    with pytest.raises(CandidateParsingError, match="not valid JSON"):
        parse_candidate_understanding("candidate-1", "not json")


def test_parse_candidate_understanding_non_object_json_raises() -> None:
    """Verify JSON that is not an object raises CandidateParsingError."""
    with pytest.raises(CandidateParsingError, match="not an object"):
        parse_candidate_understanding("candidate-1", "[1, 2, 3]")


def test_parse_candidate_understanding_schema_mismatch_raises() -> None:
    """Verify JSON that does not match the candidate schema raises an error."""
    raw_json = json.dumps({"skills": "not-a-list"})

    with pytest.raises(CandidateParsingError, match="did not match"):
        parse_candidate_understanding("candidate-1", raw_json)
