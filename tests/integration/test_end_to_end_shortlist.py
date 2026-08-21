"""Integration test for the end-to-end candidate shortlist workflow."""

from __future__ import annotations

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.matching.pipeline import MatchingPipeline
from candidate_intelligence.ranking.llm_ranker import LLMFinalRanker


class FakeRetrievalResult:
    """Deterministic retrieval result for integration testing."""

    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id


class FakeCandidateRetriever:
    """Returns a predefined set of shortlisted candidate ids."""

    def retrieve(
        self, job: JobDescription, limit: int = 10
    ) -> list[FakeRetrievalResult]:
        del job
        return [
            FakeRetrievalResult("candidate-1"),
            FakeRetrievalResult("candidate-2"),
        ][:limit]


class FakeCandidateRepository:
    """In-memory candidate repository for integration testing."""

    def __init__(self, candidates: dict[str, Candidate]) -> None:
        self._candidates = candidates

    def get(self, candidate_id: str) -> Candidate | None:
        return self._candidates.get(candidate_id)


class FakeMatchRepository:
    """In-memory match repository for integration testing."""

    def __init__(self) -> None:
        self.saved: list[MatchResult] = []

    def save(self, match: MatchResult) -> None:
        self.saved.append(match)


class FakeRulesScorer:
    """Deterministic rules scorer."""

    def score(self, candidate: Candidate, job: JobDescription) -> float:
        del job
        return 90.0 if candidate.candidate_id == "candidate-1" else 70.0


class FakeEvidenceScorer:
    """Deterministic evidence scorer."""

    def score(self, candidate: Candidate, job: JobDescription) -> float:
        del job
        return 80.0 if candidate.candidate_id == "candidate-1" else 60.0


class FakeLLMClient:
    """Deterministic LLM substitute for final ranking."""

    def generate_json(self, prompt: str) -> str:
        del prompt
        return """
        {
          "rankings": [
            {
              "candidate_id": "candidate-1",
              "rank": 1,
              "final_score": 92.0,
              "rationale": "Strongest overall match."
            },
            {
              "candidate_id": "candidate-2",
              "rank": 2,
              "final_score": 68.0,
              "rationale": "Good match but less aligned."
            }
          ]
        }
        """


def test_end_to_end_shortlist_flow() -> None:
    """Verify retrieval, scoring, deterministic ranking, and LLM ranking."""

    job = JobDescription(
        job_id="job-1",
        title="Python Developer",
        required_skills=["Python", "FastAPI"],
        min_experience_years=3,
    )

    candidates = {
        "candidate-1": Candidate(
            candidate_id="candidate-1",
            full_name="Candidate One",
            skills=["Python", "FastAPI"],
            total_experience_years=5,
        ),
        "candidate-2": Candidate(
            candidate_id="candidate-2",
            full_name="Candidate Two",
            skills=["Python"],
            total_experience_years=4,
        ),
    }

    match_repository = FakeMatchRepository()

    pipeline = MatchingPipeline(
        retriever=FakeCandidateRetriever(),
        candidate_repository=FakeCandidateRepository(candidates),
        match_repository=match_repository,
        rules_scorer=FakeRulesScorer(),
        evidence_scorer=FakeEvidenceScorer(),
    )

    deterministic_matches = pipeline.match(job, limit=10)

    assert len(deterministic_matches) == 2
    assert deterministic_matches[0].candidate_id == "candidate-1"
    assert deterministic_matches[0].rank == 1
    assert deterministic_matches[0].final_score == 85.0

    assert deterministic_matches[1].candidate_id == "candidate-2"
    assert deterministic_matches[1].rank == 2
    assert deterministic_matches[1].final_score == 65.0

    assert len(match_repository.saved) == 2

    ranker = LLMFinalRanker(FakeLLMClient())
    final_matches = ranker.rank(
        job,
        list(candidates.values()),
        deterministic_matches,
    )

    assert len(final_matches) == 2
    assert final_matches[0].candidate_id == "candidate-1"
    assert final_matches[0].rank == 1
    assert final_matches[0].rationale == "Strongest overall match."

    assert final_matches[1].candidate_id == "candidate-2"
    assert final_matches[1].rank == 2
    assert final_matches[1].rationale == "Good match but less aligned."
