import json
import re
from datetime import date, datetime
from typing import Any, Optional

from groq import Groq

from app.config import settings


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


LOG_INTERACTION_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system. Extract interaction details from the user's natural language description of a meeting with a Healthcare Professional (HCP).

Extract the following fields into a JSON object. Use ONLY information explicitly or implicitly present in the text. Be precise:
- hcp_name: Full name of the HCP (string)
- interaction_type: One of "Call", "Email", "Meeting", "Other"
- interaction_date: Date in YYYY-MM-DD format. Default to today if not specified.
- duration_minutes: Integer of duration in minutes, or null
- sentiment: One of "Positive", "Neutral", "Negative", or ""
- specialty: HCP's medical specialty (string, or "")
- region: City/region (string, or "")
- products_discussed: Comma-separated list of products (string, or "")
- key_discussion_points: Summary of what was discussed (string, or "")
- action_items: Next steps/action items (string, or "")
- follow_up_date: Follow-up date YYYY-MM-DD (string, or "")
- additional_notes: Any other relevant info (string, or "")

Return ONLY a valid JSON object with these fields. Do not include any other text."""


def log_interaction_tool(user_message: str, current_interaction: Optional[dict] = None) -> dict:
    context = ""
    if current_interaction and any(v for v in current_interaction.values()):
        context = f"\nCurrent interaction data: {json.dumps(current_interaction)}"

    result = _call_llm(
        LOG_INTERACTION_SYSTEM_PROMPT,
        f"Extract interaction details from this message: \"{user_message}\"{context}"
    )

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
        else:
            parsed = {}

    clean = {
        "hcp_name": parsed.get("hcp_name", ""),
        "interaction_type": parsed.get("interaction_type", ""),
        "interaction_date": parsed.get("interaction_date", date.today().isoformat()),
        "duration_minutes": parsed.get("duration_minutes"),
        "sentiment": parsed.get("sentiment", ""),
        "specialty": parsed.get("specialty", ""),
        "region": parsed.get("region", ""),
        "products_discussed": parsed.get("products_discussed", ""),
        "key_discussion_points": parsed.get("key_discussion_points", ""),
        "action_items": parsed.get("action_items", ""),
        "follow_up_date": parsed.get("follow_up_date", ""),
        "additional_notes": parsed.get("additional_notes", ""),
    }

    if current_interaction:
        for key in clean:
            if clean[key] and not current_interaction.get(key):
                current_interaction[key] = clean[key]
            elif clean[key] and current_interaction.get(key):
                current_interaction[key] = clean[key]
        return current_interaction

    return clean


EDIT_INTERACTION_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system. Update interaction fields based on user instructions.

The user wants to edit specific fields of an existing interaction record. Given the current interaction data and the user's edit request, update ONLY the fields that are being changed.

Return a JSON object with the following fields (only include fields that are being updated):
- hcp_name: string
- interaction_type: one of "Call", "Email", "Meeting", "Other"
- interaction_date: YYYY-MM-DD
- duration_minutes: integer or null
- sentiment: "Positive", "Neutral", "Negative", or ""
- specialty: string
- region: string
- products_discussed: string
- key_discussion_points: string
- action_items: string
- follow_up_date: YYYY-MM-DD or ""
- additional_notes: string

Return ONLY a valid JSON object. Include ONLY the fields being updated."""


def edit_interaction_tool(user_message: str, current_interaction: dict) -> dict:
    result = _call_llm(
        EDIT_INTERACTION_SYSTEM_PROMPT,
        f"Current interaction: {json.dumps(current_interaction)}\n\nUser edit request: \"{user_message}\"\n\nReturn the fields to update."
    )

    try:
        updates = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        updates = json.loads(match.group()) if match else {}

    updated = dict(current_interaction)
    for key, value in updates.items():
        if key in updated and value is not None and value != "":
            updated[key] = value

    return updated


SEARCH_HCP_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system. Based on the user query, extract HCP search parameters.

Return a JSON object with:
- name: HCP name or partial name to search (string, or "")
- specialty: Medical specialty to filter by — USE THE STANDARD SPECIALTY NAME (e.g. "Cardiology" not "cardiologist", "Dentistry" not "dentist") (string, or "")
- region: Region/location to filter by (string, or "")

Return ONLY a valid JSON object."""


def search_hcp_tool(user_message: str) -> dict:
    result = _call_llm(
        SEARCH_HCP_SYSTEM_PROMPT,
        f"Extract search parameters from: \"{user_message}\""
    )

    try:
        params = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        params = json.loads(match.group()) if match else {}

    return {
        "search_params": {
            "name": params.get("name", ""),
            "specialty": params.get("specialty", ""),
            "region": params.get("region", ""),
        },
        "results": _generate_mock_hcp_results(params),
    }


def _generate_mock_hcp_results(params: dict) -> list[dict]:
    mock_hcps = [
        {"name": "Dr. Sarah Chen", "specialty": "Cardiology", "region": "San Francisco", "last_interaction": "2026-06-15"},
        {"name": "Dr. James Rodriguez", "specialty": "Oncology", "region": "New York", "last_interaction": "2026-06-28"},
        {"name": "Dr. Emily Patel", "specialty": "Neurology", "region": "Chicago", "last_interaction": "2026-07-01"},
        {"name": "Dr. Michael Thompson", "specialty": "Cardiology", "region": "Boston", "last_interaction": "2026-05-20"},
        {"name": "Dr. Lisa Kim", "specialty": "Endocrinology", "region": "San Francisco", "last_interaction": "2026-07-05"},
        {"name": "Dr. Robert Garcia", "specialty": "Dentistry", "region": "Los Angeles", "last_interaction": "2026-07-02"},
        {"name": "Dr. Amanda Lee", "specialty": "Dentistry", "region": "San Francisco", "last_interaction": "2026-06-20"},
        {"name": "Dr. David Wilson", "specialty": "General Practice", "region": "Chicago", "last_interaction": "2026-07-03"},
    ]

    results = mock_hcps
    if params.get("name"):
        name_q = params["name"].lower()
        results = [h for h in results if name_q in h["name"].lower() or h["name"].lower() in name_q]
    if params.get("specialty"):
        spec = params["specialty"].lower()
        results = [h for h in results if
                   spec in h["specialty"].lower() or
                   h["specialty"].lower() in spec or
                   spec[:6] in h["specialty"].lower() or
                   h["specialty"].lower()[:6] in spec]
    if params.get("region"):
        region = params["region"].lower()
        results = [h for h in results if
                   region in h["region"].lower() or
                   h["region"].lower() in region]

    return results


SUGGEST_NEXT_STEPS_SYSTEM_PROMPT = """You are an AI sales strategist for a pharmaceutical company. Based on the interaction data provided, suggest strategic next steps for the field sales representative to follow up with the Healthcare Professional (HCP).

Consider:
1. Follow-up meeting or call timing and purpose
2. Clinical data or educational materials to share
3. Product samples or demonstration opportunities
4. Relationship-building based on the interaction sentiment
5. Key decision-maker engagement within the HCP's practice

The suggestions should be specific to the HCP and products mentioned in the interaction data.
Do NOT suggest generic CRM onboarding steps. Focus on pharmaceutical sales activities.

Return a JSON object with an array called "suggestions" containing objects with:
- suggestion: The specific next step suggestion (string, 10-20 words)
- priority: "High", "Medium", or "Low"
- timeframe: When this should be done (string, e.g. "Within 1 week", "Next month")

Return ONLY valid JSON."""


def suggest_next_steps_tool(interaction: dict) -> dict:
    has_data = any(v for v in interaction.values() if v)
    if not has_data:
        return {"suggestions": []}

    result = _call_llm(
        SUGGEST_NEXT_STEPS_SYSTEM_PROMPT,
        f"Interaction data: {json.dumps(interaction)}\n\nSuggest next steps based on this interaction."
    )

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        parsed = json.loads(match.group()) if match else {"suggestions": []}

    return {"suggestions": parsed.get("suggestions", [])}


VALIDATE_INTERACTION_SYSTEM_PROMPT = """You are a data quality analyst for a pharmaceutical CRM system. Validate the interaction data and check for completeness.

Required fields for a valid interaction:
- hcp_name: Must be a real person's name
- interaction_type: Must be one of Call, Email, Meeting, Other
- interaction_date: Must be a valid date
- key_discussion_points: Should have meaningful content

Optional but recommended:
- sentiment, specialty, region, action_items, follow_up_date

Return a JSON object with:
- is_valid: boolean
- missing_fields: array of field names that are empty/insufficient
- suggestions: array of helpful suggestions to improve the record

Return ONLY valid JSON."""


def validate_interaction_tool(interaction: dict) -> dict:
    result = _call_llm(
        VALIDATE_INTERACTION_SYSTEM_PROMPT,
        f"Validate this interaction data: {json.dumps(interaction)}"
    )

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        parsed = json.loads(match.group()) if match else {}

    return {
        "is_valid": parsed.get("is_valid", False),
        "missing_fields": parsed.get("missing_fields", []),
        "suggestions": parsed.get("suggestions", []),
    }
