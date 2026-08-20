"""Tests for the candidate narrative builder."""

from candidate_intelligence.domain.candidate import (
    Candidate,
    EducationEntry,
    WorkExperienceEntry,
)
from candidate_intelligence.ingestion.candidate.narrative_builder import (
    build_candidate_narrative,
)


def test_build_candidate_narrative_with_minimal_fields() -> None:
    """Verify narrative building handles a candidate with only an id."""
    candidate = Candidate(candidate_id="candidate-1")

    narrative = build_candidate_narrative(candidate)

    assert narrative == ""


def test_build_candidate_narrative_includes_all_sections() -> None:
    """Verify narrative building composes all populated fields."""
    candidate = Candidate(
        candidate_id="candidate-1",
        full_name="Nikhil Chamle",
        total_experience_years=5.5,
        skills=["Python", "FastAPI"],
        work_experience=[
            WorkExperienceEntry(
                title="Software Engineer",
                company="Acme Corp",
                duration="2018-2023",
                description="Built backend systems.",
            )
        ],
        education=[
            EducationEntry(degree="B.Tech", institution="XYZ University", year="2018")
        ],
        summary="Experienced backend engineer.",
    )

    narrative = build_candidate_narrative(candidate)

    assert "Candidate: Nikhil Chamle." in narrative
    assert "Total experience: 5.5 years." in narrative
    assert "Skills: Python, FastAPI." in narrative
    assert (
        "Software Engineer at Acme Corp (2018-2023): Built backend systems."
        in narrative
    )
    assert "B.Tech from XYZ University (2018)" in narrative
    assert "Summary: Experienced backend engineer." in narrative


def test_build_candidate_narrative_omits_missing_optional_fields() -> None:
    """Verify narrative building skips fields that are not present."""
    candidate = Candidate(candidate_id="candidate-1", skills=["Python"])

    narrative = build_candidate_narrative(candidate)

    assert narrative == "Skills: Python."
    assert "Candidate:" not in narrative
    assert "Education:" not in narrative
