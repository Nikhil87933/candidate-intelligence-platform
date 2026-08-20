"""Prompt template for extracting structured candidate data from resume text."""

CANDIDATE_UNDERSTANDING_PROMPT_TEMPLATE = """\
You are an expert technical recruiter. Extract structured information from \
the resume text below and return ONLY a valid JSON object, with no \
additional commentary.

The JSON object must have exactly these keys:
- "full_name": string or null
- "email": string or null
- "phone": string or null
- "total_experience_years": number or null
- "skills": array of strings
- "education": array of objects, each with "degree", "institution", "year" \
(year may be null)
- "work_experience": array of objects, each with "title", "company", \
"duration", "description" (duration and description may be null)
- "summary": a short 2-3 sentence professional summary of the candidate, \
or null

If a field cannot be determined from the resume text, use null (or an \
empty array for list fields). Do not invent information that is not \
present in the resume text.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""


def build_candidate_understanding_prompt(resume_text: str) -> str:
    """Build the LLM prompt for extracting structured candidate data."""
    return CANDIDATE_UNDERSTANDING_PROMPT_TEMPLATE.format(resume_text=resume_text)
