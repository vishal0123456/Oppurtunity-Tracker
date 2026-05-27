"""
AI Extraction Pipeline — uses Google Gemini (free tier) to extract structured
opportunity data from raw scraped web page text.

Model: gemini-2.0-flash  (free, 15 req/min, 1500 req/day via Google AI Studio)

Design:
- Primary extraction: structured JSON via Gemini
- Fallback: regex-based heuristics if LLM fails or returns invalid JSON
- All failures are logged, never crash the pipeline
"""
import json
import logging
import re
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini client once at module load
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=genai.GenerationConfig(
        temperature=0.1,
        response_mime_type="application/json",  # Forces JSON output
    ),
)

EXTRACTION_PROMPT = """You are an expert opportunity data extractor.
Extract structured data from this opportunity page text and return as JSON.

Required JSON fields:
- title: string (program/opportunity name)
- organization: string (offering organization/company)
- country: array of strings (target countries, e.g. ["India", "USA", "Global"])
- deadline: string in YYYY-MM-DD format or null
- eligibility: string (who can apply)
- funding_amount: string (e.g. "$10,000", "Fully funded", "Stipend provided") or null
- category: one of exactly: scholarship | fellowship | accelerator | vc_program | grant | competition | conference | exhibition | exchange_program | travel_program | government_scheme | giveaway | other
- description: string (2-3 sentence summary of what this opportunity is)
- is_remote: boolean (true if remote/online participation is possible)
- women_friendly: boolean (true if specifically targets or welcomes women founders/applicants)
- india_eligible: boolean (true if Indian applicants are eligible)
- student_eligible: boolean (true if students can apply)
- age_limit: string (e.g. "Under 35", "18-30") or null
- application_fee: string (e.g. "Free", "$50") or null
- tags: array of strings chosen ONLY from: [AI, Startup, Women, Research, Design, MBA, Engineering, Climate, Travel, Social Impact, Hackathon, Student, Founder, Grant, Fellowship, Scholarship, Tech, Health, Education, Finance, Arts, Sports, Leadership, Government]

Page text (truncated):
{text}

Return ONLY valid JSON, no markdown fences, no explanation."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=3, max=15),
)
async def extract_opportunity_with_llm(raw_text: str) -> Optional[dict]:
    """
    Call Gemini to extract structured opportunity data from raw text.
    Returns a dict or None if extraction fails.
    """
    truncated_text = raw_text[:4000]

    try:
        response = await _model.generate_content_async(
            EXTRACTION_PROMPT.format(text=truncated_text)
        )

        raw_json = response.text.strip()

        # Strip markdown fences if Gemini adds them despite the mime type
        if raw_json.startswith("```"):
            raw_json = re.sub(r"^```(?:json)?\n?", "", raw_json)
            raw_json = re.sub(r"\n?```$", "", raw_json)

        data = json.loads(raw_json)
        logger.debug(f"Gemini extraction succeeded: {data.get('title', 'unknown')}")
        return data

    except json.JSONDecodeError as e:
        logger.warning(f"Gemini returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        return None


def extract_with_fallback_heuristics(raw_text: str, url: str) -> dict:
    """
    Regex/heuristic fallback when LLM extraction fails.
    Extracts minimal fields to still create a useful record.
    """
    # Guard against None input
    if not raw_text:
        return {
            "title": "Unknown Opportunity",
            "organization": None,
            "country": [],
            "deadline": None,
            "eligibility": None,
            "funding_amount": None,
            "category": "other",
            "description": None,
            "is_remote": False,
            "women_friendly": False,
            "india_eligible": False,
            "student_eligible": False,
            "age_limit": None,
            "application_fee": None,
            "tags": [],
            "_extraction_method": "fallback",
        }

    deadline = None
    date_patterns = [
        r"deadline[:\s]+(\w+ \d{1,2},?\s*\d{4})",
        r"apply by[:\s]+(\w+ \d{1,2},?\s*\d{4})",
        r"closing date[:\s]+(\w+ \d{1,2},?\s*\d{4})",
        r"(\d{4}-\d{2}-\d{2})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            deadline = match.group(1)
            break

    lines = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 20]
    title = lines[0][:300] if lines else "Unknown Opportunity"

    text_lower = raw_text.lower()
    category = "other"
    category_keywords = {
        "scholarship": ["scholarship", "tuition", "academic award"],
        "fellowship": ["fellowship", "fellow program"],
        "accelerator": ["accelerator", "acceleration program", "cohort"],
        "grant": ["grant", "funding opportunity", "seed fund"],
        "competition": ["competition", "contest", "challenge", "hackathon"],
        "conference": ["conference", "summit", "symposium"],
        "exchange_program": ["exchange program", "study abroad"],
        "travel_program": ["travel grant", "travel fellowship", "travel award"],
        "government_scheme": ["government", "ministry", "federal", "national scheme"],
    }
    for cat, keywords in category_keywords.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break

    return {
        "title": title,
        "organization": None,
        "country": [],
        "deadline": deadline,
        "eligibility": None,
        "funding_amount": None,
        "category": category,
        "description": raw_text[:500] if raw_text else None,
        "is_remote": False,
        "women_friendly": any(w in text_lower for w in ["women", "female", "girl"]),
        "india_eligible": any(w in text_lower for w in ["india", "indian"]),
        "student_eligible": any(w in text_lower for w in ["student", "undergraduate", "graduate"]),
        "age_limit": None,
        "application_fee": None,
        "tags": [],
        "_extraction_method": "fallback",
    }


async def extract_opportunity(raw_text: str, url: str) -> dict:
    """
    Main extraction entry point.
    Tries Gemini first, falls back to heuristics.
    Always returns a dict (never raises).
    """
    if not raw_text or len(raw_text.strip()) < 100:
        logger.warning(f"Skipping extraction — text too short for URL: {url}")
        return extract_with_fallback_heuristics(raw_text or "", url)

    result = await extract_opportunity_with_llm(raw_text)

    if result and result.get("title"):
        result["_extraction_method"] = "llm"
        return result

    logger.warning(f"Gemini extraction failed for {url}, using heuristic fallback")
    return extract_with_fallback_heuristics(raw_text, url)
