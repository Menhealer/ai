from __future__ import annotations
import json, httpx
from pathlib import Path
from typing import Any, Dict
from dataclasses import asdict, is_dataclass
from datetime import datetime, date

from src.config.settings import settings

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "friend_solution_v1.md"

def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def _to_payload(obj: Any) -> Dict[str, Any]:
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj

def _json_safe(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if is_dataclass(obj):
        return {k: _json_safe(v) for k, v in asdict(obj).items()}
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj

def _looks_truncated(s: str) -> bool:
    s = (s or "").strip()
    if not s:
        return True
    if "{" in s and s.count("{") > s.count("}"):
        return True
    if s.endswith("..."):
        return True
    return False

async def call_llm_solution(ctx: Dict[str, Any]) -> str:
    system_prompt = _load_prompt()
    payload = _to_payload(ctx)
    user_content = json.dumps(payload, ensure_ascii=False)
    
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}"}
    body: Dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "messages":[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SEC) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        if _looks_truncated(content):
            resp2 = await client.post(url, headers=headers, json=body)
            resp2.raise_for_status()
            data2 = resp2.json()
            content2 = data2["choices"][0]["message"]["content"]
            if _looks_truncated(content2):
                raise ValueError("LLM output seems truncated twice.")
            content = content2

    return content