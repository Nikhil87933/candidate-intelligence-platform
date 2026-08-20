"""Builds structured candidate profiles from extracted resume text using the LLM."""

from __future__ import annotations

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.llm.client import OllamaClient
from candidate_intelligence.llm.parsers import parse_candidate_understanding
from candidate_intelligence.llm.prompts.candidate_understanding import (
    build_candidate_understanding_prompt,
)


def build_candidate_profile(
    llm_client: OllamaClient, candidate_id: str, resume_text: str
) -> Candidate:
    """Build a structured Candidate profile from extracted resume text.

    Sends the resume text to the LLM for understanding and parses the
    response into a structured Candidate domain object.
    """
    prompt = build_candidate_understanding_prompt(resume_text)
    raw_json = llm_client.generate_json(prompt)
    return parse_candidate_understanding(candidate_id, raw_json)
