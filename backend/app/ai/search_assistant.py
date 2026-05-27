"""
AI Search Assistant — converts natural language queries into structured DB filters
using Google Gemini (free tier).

Example: "Women founder grants in Europe" →
  { category: "grant", women_friendly: true, country: ["Europe"] }
"""
import json
import logging
import re

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
_search_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=genai.GenerationConfig(
        temperature=0.0,
        response_mime_type="application/json",
    ),
)

SEARCH_PROMPT = """You are a search query parser for an opportunity tracker platform.
Convert this natural language search query into structured filter JSON.

Query: "{query}"

Return JSON with these optional fields (only include fields clearly implied by the query):
- category: one of: scholarship | fellowship | accelerator | vc_program | grant | competition | conference | exhibition | exchange_program | travel_program | government_scheme | giveaway
- country: array of country/region strings
- tags: array from: [AI, Startup, Women, Research, Design, MBA, Engineering, Climate, Travel, Social Impact, Hackathon, Student, Founder, Grant, Fellowship, Scholarship, Tech, Health, Education, Finance, Arts, Sports, Leadership, Government]
- women_friendly: boolean
- india_eligible: boolean
- student_eligible: boolean
- is_remote: boolean
- keyword: string (remaining search terms for text search)

Examples:
- "Women founder grants in Europe" → {{"category": "grant", "women_friendly": true, "country": ["Europe"], "tags": ["Women", "Founder", "Grant"]}}
- "Fully funded fellowships for Indian students" → {{"category": "fellowship", "india_eligible": true, "student_eligible": true, "tags": ["Fellowship", "Student"]}}
- "AI startup accelerators in Singapore" → {{"category": "accelerator", "country": ["Singapore"], "tags": ["AI", "Startup"]}}

Return ONLY valid JSON, no markdown, no explanation."""


async def parse_search_query(query: str) -> dict:
    """
    Use Gemini to parse a natural language query into structured filters.
    Falls back to simple keyword search if LLM fails.
    """
    if not query or len(query.strip()) < 2:
        return {"keyword": query}

    try:
        response = await _search_model.generate_content_async(
            SEARCH_PROMPT.format(query=query)
        )

        raw_json = response.text.strip()
        if raw_json.startswith("```"):
            raw_json = re.sub(r"^```(?:json)?\n?", "", raw_json)
            raw_json = re.sub(r"\n?```$", "", raw_json)

        filters = json.loads(raw_json)
        logger.info(f"Search query '{query}' parsed to filters: {filters}")
        return filters

    except Exception as e:
        logger.warning(f"Search query parsing failed: {e}, falling back to keyword search")
        return {"keyword": query}
