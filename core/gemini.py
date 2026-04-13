import os
import json
import streamlit as st
import google.generativeai as genai
from core.schema import RequirementRecord, REQ_TYPES, PRIORITIES

_PROMPT_TEMPLATE = """\
Extract all requirements from the engineering text below.
Return a JSON array only — no explanation, no markdown fences.
Each item must have exactly these keys:
  "text"          — a clear, atomic requirement statement
  "type"          — one of: Functional, Non-Functional, Constraint
  "priority"      — one of: High, Medium, Low
  "source_phrase" — the short phrase from the input that this came from

TEXT:
{input_text}
"""


def _get_api_key() -> str | None:
    try:
        val = st.secrets.get("GEMINI_API_KEY")
        if val:
            return val
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")


def extract(text: str) -> dict:
    """Call Gemini and return a result dict.

    Always returns:
        {"ok": bool, "records": list[RequirementRecord], "error": str, "raw_response": str | None}
    """
    key = _get_api_key()
    if not key:
        return {
            "ok": False,
            "records": [],
            "error": "GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml or set the environment variable.",
            "raw_response": None,
        }

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.5-flash")


    # Use JSON mime type if the SDK supports it — more reliable than parsing free text
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
    )

    try:
        response = model.generate_content(
            _PROMPT_TEMPLATE.format(input_text=text.strip()),
            generation_config=generation_config,
        )
        raw = response.text.strip() if response.text else ""
    except Exception as e:
        return {"ok": False, "records": [], "error": str(e), "raw_response": None}

    if not raw:
        return {"ok": False, "records": [], "error": "Model returned an empty response.", "raw_response": raw}

    try:
        items = json.loads(raw)
        if not isinstance(items, list):
            raise ValueError("Expected a JSON array at the top level.")
    except (json.JSONDecodeError, ValueError) as e:
        return {"ok": False, "records": [], "error": f"Could not parse model output: {e}", "raw_response": raw}

    records = []
    for item in items:
        if not isinstance(item, dict):
            continue
        req_type = item.get("type", "Functional")
        if req_type not in REQ_TYPES:
            req_type = "Functional"
        priority = item.get("priority", "Medium")
        if priority not in PRIORITIES:
            priority = "Medium"
        records.append(
            RequirementRecord(
                text=str(item.get("text", "")).strip(),
                req_type=req_type,
                priority=priority,
                source_phrase=str(item.get("source_phrase", "")).strip(),
            )
        )

    return {"ok": True, "records": records, "error": "", "raw_response": raw}
