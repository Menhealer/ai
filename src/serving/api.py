from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
import logging, uuid
from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware

from src.safety.rules import check_safety
from src.safety.escalation_summary import build_summary_escalation
from src.safety.escalation_solution import build_solution_escalation
from src.pipeline.extract import extract_summary, extract_solution
from src.schemas.relationship import FriendSolutionResponse, FriendSolutionRequest, FriendSummaryRequest, FriendSummaryResponse
from src.pipeline.generate_summary import call_llm_summary
from src.pipeline.generate_solution import call_llm_solution
from src.pipeline.postprocess import parse_solution, parse_summary

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

@app.post("/summarize", response_model=FriendSummaryResponse)
async def summarize(req: FriendSummaryRequest, request: Request) -> FriendSummaryResponse:
    rid = request.state.request_id
    logger.info("summarize called", extra={"request_id": rid})

    safety = check_safety(req.text)
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_summary_escalation(req, safety)
    
    try:
        ctx = extract_summary(req)
        logger.info("extracted context", extra={"request_id": rid})

        if hasattr(ctx, "model_dump"):
            ctx = ctx.model_dump()

        raw = await call_llm_summary(ctx)
        logger.info("llm response received", extra={"request_id": rid})

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

    safety = check_safety(req.text)
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_solution_escalation(req, safety)
    
    try:
        ctx = extract_solution(req)
        logger.info("extracted context", extra={"request_id": rid})

        if hasattr(ctx, "model_dump"):
            ctx = ctx.model_dump()

        raw = await call_llm_solution(ctx)
        logger.info("llm response received", extra={"request_id": rid})

        result = parse_solution(raw)
        result.safety = safety
        logger.info("response validated", extra={"request_id": rid})
        return result
    except Exception as e:
        logger.exception("solution failed", extra={"request_id": rid})
        raise HTTPException(status_code=500, detail=f"AI solution failed: {e}")