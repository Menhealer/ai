from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
import logging, uuid
from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware

from src.schemas.relationship import FriendSolveRequest, FriendSolveResponse
from src.safety.rules import check_safety
from src.safety.escalation import build_escalation_response
from src.pipeline.extract import extract_context
from src.pipeline.generate_advice import call_llm_generate
from src.pipeline.postprocess import parse_and_validate

from src.config.settings import settings
from src.utils.logging import setup_logging, attack_request_id_filter

app = FastAPI(title="Relog AI")

logger = logging.getLogger("Relog.ai")

@app.on_event("startup")
async def on_startup():
    setup_logging(settings.LOG_DIR, settings.LOG_FILE, settings.LOG_LEVEL)
    attack_request_id_filter()
    logger.info("AI server started", extra={"request_id": "-"})

class RequestIDMiddleware(BaseHTTPMiddleware):
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

app.add_middleware(RequestIDMiddleware)

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/solve", response_model=FriendSolveResponse)
async def solve(req: FriendSolveRequest, request: Request) -> FriendSolveResponse:
    rid = request.state.request_id
    logger.info("solve called", extra={"request_id": rid})

    safety = check_safety(req.text)
    if safety.flagged:
        logger.warning(f"safety flagged: {safety.categories}", extra={"request_id": rid})
        return build_escalation_response(req, safety)
    
    try:
        ctx = extract_context(req)
        logger.info("extracted context", extra={"request_id": rid})

        raw = await call_llm_generate(ctx)
        logger.info("llm response received", extra={"request_id": rid})

        result = parse_and_validate(raw)
        logger.info("response validated", extra={"request_id": rid})
        return result
    except Exception as e:
        logger.exception("solve failed", extra={"request_id": rid})
        raise HTTPException(status_code=500, detail=f"AI solve failed: {e}")