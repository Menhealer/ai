from __future__ import annotations
import json, httpx
from pathlib import Path
from typing import Any, Dict

from src.config.settings import settings

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "friend_summary_v1.md"

def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

async def call_llm_summary(payload: Dict[str, Any]) -> str:
    system_prompt = _load_prompt()
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
    
    return data["choices"][0]["message"]["content"]