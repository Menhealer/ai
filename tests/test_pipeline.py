import pytest

from src.schemas.relationship import FriendSummaryRequest, FriendSolutionRequest
from src.pipeline.extract import extract_summary, extract_solution
from src.pipeline.generate_summary import call_llm_summary
from src.pipeline.generate_solution import call_llm_solution
from src.pipeline.postprocess import parse_summary, parse_solution


@pytest.mark.asyncio
async def test_pipeline_smoke():
    text = "친구가 요즘 답장을 너무 늦게 해서 서운해. 내가 부담 주는 건가 싶어서 말도 못하겠어."

    # summarize
    sreq = FriendSummaryRequest(text=text, tone="warm", friend_alias="민수")
    sctx = extract_summary(sreq)
    sraw = await call_llm_summary(sctx)
    sres = parse_summary(sraw)

    assert sres is not None

    # solution
    solreq = FriendSolutionRequest(text=text, goal="resolve", tone="warm", friend_alias="민수", summary=sres)
    solctx = extract_solution(solreq)
    solraw = await call_llm_solution(solctx)
    solres = parse_solution(solraw)

    assert solres is not None