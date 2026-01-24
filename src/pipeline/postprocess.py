from __future__ import annotations

import json, re
from typing import Any, Dict
from pydantic import ValidationError

from src.schemas.relationship import FriendSummaryResponse, FriendSolutionResponse

def _extract_json_lbject(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.find("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM output.")
    return text[start : end + 1]

def _basic_repair(s: str) -> str:
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    s = re.sub(r",\s*", "}", s)
    s = re.sub(r",\s*", "]", s)
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    return s

def parse_summary(raw: str) -> FriendSummaryResponse:
    json_text = _extract_json_lbject(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return FriendSummaryResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return FriendSummaryResponse.model_validate(data2)

def parse_solution(raw: str) -> FriendSolutionResponse:
    json_text = _extract_json_lbject(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return FriendSolutionResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return FriendSolutionResponse.model_validate(data2)