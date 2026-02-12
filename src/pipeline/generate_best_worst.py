from __future__ import annotations
import json, httpx
from pathlib import Path
from typing import Any, Dict
from dataclasses import asdict, is_dataclass

from src.config.settings import settings

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "friend_best_worst_v1.md"

def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def _to_payload(obj: Any) -> Dict[str, Any]:
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"Unsupported payload type: {type(obj)}")

async def call_llm_best_worst(ctx: Dict[str, Any]) -> str:
    system_prompt = _load_prompt()
    payload = _to_payload(ctx)
    user_content = json.dumps(payload, ensure_ascii=False)

    # url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/api/chat"
    body: Dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SEC) as client:
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()
    return data["message"]["content"]
