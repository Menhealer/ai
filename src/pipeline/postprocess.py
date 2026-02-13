from __future__ import annotations

import json, re
from typing import Any, Dict
from pydantic import ValidationError

from src.schemas.relationship import FriendSummaryResponse, FriendSolutionResponse, SettlementResponse, BestWorstResponse

def _extract_json_object(text: str) -> str:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty LLM output.")
    if "```" in text:
        parts = text.split("```")
        candidates = [p.strip() for p in parts if "{" in p and "}" in p]
        if candidates:
            text = candidates[0]
            if text.lower().startswith("json"):
                text = text[4:].strip()

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM output.")
    depth = 0
    in_str = False
    esc = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
    if end is None:
        raise ValueError("JSON object not closed properly.")
    return text[start : end + 1]

def _basic_repair(s: str) -> str:
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s

def parse_summary(raw: str) -> FriendSummaryResponse:
    json_text = _extract_json_object(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return FriendSummaryResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return FriendSummaryResponse.model_validate(data2)

def parse_solution(raw: str) -> FriendSolutionResponse:
    json_text = _extract_json_object(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return FriendSolutionResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return FriendSolutionResponse.model_validate(data2)

def parse_settlement(raw: str) -> SettlementResponse:
    json_text = _extract_json_object(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return SettlementResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return SettlementResponse.model_validate(data2)

def parse_best_worst(raw: str) -> BestWorstResponse:
    json_text = _extract_json_object(raw)
    try:
        data: Dict[str, Any] = json.loads(json_text)
        return BestWorstResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        repaired = _basic_repair(json_text)
        data2: Dict[str, Any] = json.loads(repaired)
        return BestWorstResponse.model_validate(data2)
