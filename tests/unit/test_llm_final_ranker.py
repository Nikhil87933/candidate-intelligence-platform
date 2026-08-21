"""Tests for LLM-based final candidate ranking."""

from unittest.mock import MagicMock

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.ranking.llm_ranker import LLMFinalRanker


def test_rank_returns_empty_list_without_matches() -> None:
    """Verify the LLM is not called when there are no matches."""
    llm_client = MagicMock()
    ranker = LLMFinalRanker(llm_client)

    results = ranker.rank(
        job=JobDescription(job_id="job-1"),
        candidates=[],
        matches=[],
    )

    assert results == []
    llm_client.generate_json.assert_not_called()


def test_rank_updates_matches_from_llm_response() -> None:
    """Verify LLM ranking updates rank, score, and rationale."""
    llm_client = MagicMock()
    llm_client.generate_json.return_value = """
    {
        "rankings": [
            {
                "candidate_id": "candidate-2",
                "rank": 1,
                "final_score": 95,
                "rationale": "Best overall match."
            },
            {
                "candidate_id": "candidate-1",
                "rank": 2,
                "final_score": 88,
                "rationale": "Strong candidate with fewer matching skills."
            }
        ]
    }
    """

    ranker = LLMFinalRanker(llm_client)

    job = JobDescription(
        job_id="job-1",
        title="Python Developer",
        required_skills=["Python", "FastAPI"],
    )

    candidates = [
        Candidate(
            candidate_id="candidate-1",
            full_name="Candidate One",
            skills=["Python"],
        ),
        Candidate(
            candidate_id="candidate-2",
            full_name="Candidate Two",
            skills=["Python", "FastAPI"],
        ),
    ]

    matches = [
        MatchResult(
            job_id="job-1",
            candidate_id="candidate-1",
            final_score=70,
        ),
        MatchResult(
            job_id="job-1",
            candidate_id="candidate-2",
            final_score=90,
        ),
    ]

    results = ranker.rank(
        job=job,
        candidates=candidates,
        matches=matches,
    )

    assert [result.candidate_id for result in results] == [
        "candidate-2",
        "candidate-1",
    ]

    assert results[0].rank == 1
    assert results[0].final_score == 95
    assert results[0].rationale == "Best overall match."

    assert results[1].rank == 2
    assert results[1].final_score == 88
    assert results[1].rationale == ("Strong candidate with fewer matching skills.")

    llm_client.generate_json.assert_called_once()


def test_build_prompt_contains_job_and_candidate_data() -> None:
    """Verify the LLM prompt contains the ranking context."""
    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
        required_skills=["Python", "SQL", "Spark"],
    )

    candidate = Candidate(
        candidate_id="candidate-1",
        full_name="Jane Doe",
        total_experience_years=5,
        skills=["Python", "SQL"],
        summary="Data engineering professional.",
    )

    match = MatchResult(
        job_id="job-1",
        candidate_id="candidate-1",
        rules_score=80,
        evidence_score=90,
        final_score=85,
    )

    prompt = LLMFinalRanker._build_prompt(
        job=job,
        candidates=[candidate],
        matches=[match],
    )

    assert "Data Engineer" in prompt
    assert "Python" in prompt
    assert "SQL" in prompt
    assert "Spark" in prompt
    assert "candidate-1" in prompt
    assert "Jane Doe" in prompt
    assert "85" in prompt
