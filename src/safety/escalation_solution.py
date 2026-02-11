from __future__ import annotations

from datetime import datetime, timezone
from src.schemas.relationship import (
    FriendSolutionRequest,
    FriendSolutionResponse,
    SafetyResult
)

def build_solution_escalation(req: FriendSolutionRequest, safety: SafetyResult) -> FriendSolutionResponse:
    return FriendSolutionResponse(
        version="v1-friend-solution",
        created_at=datetime.now(timezone.utc),
        goal=req.goal,
        top_strategy="위험 신호가 감지되어 관계 솔루션보다 안전 확보와 도움 요청을 우선합니다.",
        direction_suggestion="지금은 안전 확보와 도움 요청을 우선하세요.",
        solution_text="현재 관계는 안전이 최우선인 상태예요. 지금은 관계 조언보다 안전 확보와 도움 요청이 필요해 보여요. 감정이 격해졌다면 즉시 도움을 요청하는 것이 좋아 보여요. 👉 관계 상태 제안: 안전 확보 최우선",
    )
