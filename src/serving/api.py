from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
import logging, uuid, re
from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from src.safety.rules import check_safety
from src.safety.escalation_summary import build_summary_escalation
from src.safety.escalation_solution import build_solution_escalation
from src.safety.escalation_settlement import build_settlement_escalation
from src.pipeline.extract import extract_summary, extract_solution, extract_settlement
from src.pipeline.generate_summary import call_llm_summary
from src.pipeline.generate_solution import call_llm_solution
from src.pipeline.generate_settlement import call_llm_settlement
from src.pipeline.postprocess import parse_solution, parse_summary, parse_settlement
from src.schemas.relationship import (
    FriendSolutionResponse,
    FriendSolutionRequest,
    FriendSummaryRequest,
    FriendSummaryResponse,
    SettlementRequest,
    SettlementResponse,
)

from src.config.settings import settings
from src.utils.logging import setup_logging, attach_request_id_filter

app = FastAPI(title="Relog AI")

logger = logging.getLogger("Relog.ai")

@app.on_event("startup")
async def on_startup():
    setup_logging(settings.LOG_DIR, settings.LOG_FILE, settings.LOG_LEVEL)
    attach_request_id_filter()
    logger.info("AI server started", extra={"request_id": "-"})

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = perf_counter()
        try:
            response = await call_next(request)
        finally:
            elapsed_ms = int((perf_counter() - start) * 1000)
        
        response.headers["x-request-id"] = request_id
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms}ms)",
            extra={"request_id": request_id},
        )
        return response

app.add_middleware(RequestIdMiddleware)

@app.get("/health")
async def health():
    return {"ok": True}

def _entries_text(req) -> str:
    return "\n".join([e.text for e in req.entries])

def _settlement_entries_text(req: SettlementRequest) -> str:
    parts = []
    if req.context_hint:
        parts.append(req.context_hint)
    for m in req.summaries:
        parts.append(m.friend_alias)
        for s in m.summaries:
            parts.append(s.month)
            parts.append(s.summary_text)
    return "\n".join(p for p in parts if p)

def _replace_aliases(text: str, aliases: list[str], repl: str) -> str:
    if not text or not aliases:
        return text
    uniq = sorted(set(a for a in aliases if a), key=len, reverse=True)
    if not uniq:
        return text
    pattern = re.compile("|".join(re.escape(a) for a in uniq))
    return pattern.sub(repl, text)

@app.post("/summarize", response_model=FriendSummaryResponse)
async def summarize(req: FriendSummaryRequest, request: Request) -> FriendSummaryResponse:
    rid = request.state.request_id
    logger.info("summarize called", extra={"request_id": rid})

    safety = check_safety(_entries_text(req))
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_summary_escalation(req, safety)
    
    try:
        ctx = extract_summary(req)
        logger.info("extracted context", extra={"request_id": rid})

        raw = await call_llm_summary(ctx)
        logger.info("llm response received", extra={"request_id": rid})

        # summary 로그 확인
        # logger.info(f"llm raw tail (summary): {raw[-300:]}", extra={"request_id": rid})
        # Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
        # Path(f"{settings.LOG_DIR}/last_summary_raw.txt").write_text(raw, encoding="utf-8")

        result = parse_summary(raw)
        result.safety = safety
        logger.info("response validated", extra={"request_id": rid})
        return result
    except Exception as e:
        logger.exception("summarize failed", extra={"request_id": rid})
        raise HTTPException(status_code=500, detail=f"AI summarize failed: {e}")

@app.post("/solution", response_model=FriendSolutionResponse)
async def solution(req: FriendSolutionRequest, request: Request) -> FriendSolutionResponse:
    rid = request.state.request_id
    logger.info("solution called", extra={"request_id": rid})

    safety = check_safety(_entries_text(req))
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_solution_escalation(req, safety)
    
    try:
        ctx = extract_solution(req)
        logger.info("extracted context", extra={"request_id": rid})

        raw = await call_llm_solution(ctx)
        logger.info("llm response received", extra={"request_id": rid})
        
        # solution 로그 확인
        # logger.info(f"llm raw tail (solution): {raw[-300:]}", extra={"request_id": rid})
        # Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
        # Path(f"{settings.LOG_DIR}/last_solution_raw.txt").write_text(raw, encoding="utf-8")

        result = parse_solution(raw)
        result.safety = safety
        logger.info("response validated", extra={"request_id": rid})
        return result
    except Exception as e:
        logger.exception("solution failed", extra={"request_id": rid})
        raise HTTPException(status_code=500, detail=f"AI solution failed: {e}")

@app.post("/settlement", response_model=SettlementResponse)
async def settlement(req: SettlementRequest, request: Request) -> SettlementResponse:
    rid = request.state.request_id
    logger.info("settlement called", extra={"request_id": rid})

    safety = check_safety(_settlement_entries_text(req))
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_settlement_escalation(req, safety)

    try:
        ctx = extract_settlement(req)
        logger.info("extracted context", extra={"request_id": rid})

        raw = await call_llm_settlement(ctx)
        logger.info("llm response received", extra={"request_id": rid})

        result = parse_settlement(raw)
        
        aliases = [s.friend_alias for s in req.summaries if s.friend_alias]
        result.quarter_summary = _replace_aliases(result.quarter_summary, aliases, "상대")
        result.quarter_solution = _replace_aliases(result.quarter_solution, aliases, "상대")
        result.quarter_direction = _replace_aliases(result.quarter_direction, aliases, "관계")
        if result.quarter_bullets:
            result.quarter_bullets = [_replace_aliases(b, aliases, "상대") for b in result.quarter_bullets]
        
        result.safety = safety
        logger.info("response validated", extra={"request_id": rid})
        return result
    except Exception as e:
        logger.exception("settlement failed", extra={"request_id": rid})
        raise HTTPException(status_code=500, detail=f"AI settlement failed: {e}")
