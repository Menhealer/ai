from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
import httpx

from src.config.settings import settings
from src.pipeline.extract import ExtractedContext

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "relationship_v1,md"

def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def _build_user_payload(ctx: ExtractedContext) -> str:
    payload = {
        "text": ctx.situation,
        "goal": ctx.goal,
        "tone": ctx.tone,
        "friend_alias": ctx.friend_alias,
        "signals": {
            "feelings_guess": ctx.friend_alias,
            "needs_guess": ctx.needs,
            "issues_guess": ctx.issues
        }
    }
    return json.dumps(payload, ensure_ascii=False)

async def call_llm_generate(ctx: ExtractedContext) -> str:
    system_prompt = _load_prompt()
    user_content = _build_user_payload(ctx)
    
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