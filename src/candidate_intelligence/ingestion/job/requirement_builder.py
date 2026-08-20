"""Builds structured job requirements from raw JD text using the LLM."""

from __future__ import annotations

from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.llm.client import OllamaClient
from candidate_intelligence.llm.parsers import parse_jd_understanding
from candidate_intelligence.llm.prompts.jd_understanding import (
    build_jd_understanding_prompt,
)


def build_job_requirements(
    llm_client: OllamaClient, job_id: str, jd_text: str
) -> JobDescription:
    """Build a structured JobDescription from raw job description text.

    Sends the JD text to the LLM for understanding and parses the response
    into a structured JobDescription domain object.
    """
    prompt = build_jd_understanding_prompt(jd_text)
    raw_json = llm_client.generate_json(prompt)
    return parse_jd_understanding(job_id, raw_json)
