from __future__ import annotations
from src.schemas.relationship import FriendSummaryRequest, FriendSummaryResponse, SafetyResult

def build_summary_escalation(req: FriendSummaryRequest, safety: SafetyResult) -> FriendSummaryResponse:
    return FriendSummaryResponse(
        version="v1-friend-summary",
        situation_summary="일반적인 관계 정리보다 먼저, 현재 안전을 확보하는 것이 최우선이에요.",
    )
