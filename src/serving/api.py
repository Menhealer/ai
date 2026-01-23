from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.schemas.relationship import FriendSolveRequest, FriendSolveResponse
from src.safety.rules import check_safety
from src.safety.escalation import build_escalation_response
from src.pipeline.extract import extract_context
from src.pipeline.generate_advice import call_llm_generate
from src.pipeline.postprocess import parse_and_validate

app = FastAPI(title="Relog AI")

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/solve", response_model=FriendSolveResponse)
async def solve(req: FriendSolveRequest) -> FriendSolveResponse:
    safety = check_safety(req.text)
    if safety.flagged:
        return build_escalation_response(req, safety)
    
    try:
        ctx = extract_context(req)
        raw = await call_llm_generate(ctx)
        result = parse_and_validate(raw)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI solve failed: {e}")