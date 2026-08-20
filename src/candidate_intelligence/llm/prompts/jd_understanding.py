"""Prompt template for extracting structured job requirements from JD text."""

JD_UNDERSTANDING_PROMPT_TEMPLATE = """\
You are an expert technical recruiter. Extract structured information from \
the job description text below and return ONLY a valid JSON object, with \
no additional commentary.

The JSON object must have exactly these keys:
- "title": string or null
- "company": string or null
- "required_skills": array of strings
- "min_experience_years": number or null
- "responsibilities": array of strings
- "qualifications": array of strings
- "summary": a short 2-3 sentence summary of the role, or null

If a field cannot be determined from the job description text, use null \
(or an empty array for list fields). Do not invent information that is \
not present in the job description text.

Job description text:
\"\"\"
{jd_text}
\"\"\"
"""


def build_jd_understanding_prompt(jd_text: str) -> str:
    """Build the LLM prompt for extracting structured job requirements."""
    return JD_UNDERSTANDING_PROMPT_TEMPLATE.format(jd_text=jd_text)
