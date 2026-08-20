"""Tests for the candidate profile builder."""

import json
from unittest.mock import MagicMock

from candidate_intelligence.ingestion.candidate.profile_builder import (
    build_candidate_profile,
)


def test_build_candidate_profile_returns_parsed_candidate() -> None:
    """Verify the profile builder calls the LLM and parses the result."""
    llm_client = MagicMock()
    llm_client.generate_json.return_value = json.dumps(
        {
            "full_name": "Nikhil Chamle",
            "skills": ["Python"],
        }
    )

    candidate = build_candidate_profile(
        llm_client, candidate_id="candidate-1", resume_text="resume text here"
    )

    assert candidate.candidate_id == "candidate-1"
    assert candidate.full_name == "Nikhil Chamle"
    assert candidate.skills == ["Python"]
    llm_client.generate_json.assert_called_once()
