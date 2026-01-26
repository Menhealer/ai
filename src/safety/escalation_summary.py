from __future__ import annotations
from datetime import timezone, datetime

from src.schemas.relationship import FriendSummaryRequest, FriendSummaryResponse, SafetyResult

def build_summary_escalation(req: FriendSummaryRequest, safety: SafetyResult) -> FriendSummaryResponse:
    return FriendSummaryResponse(
        version="v1-friend-summary",
        created_at=datetime.now(timezone.utc),
        one_line_summary="민감/위험 신호가 감지되어 안전을 우선 안내합니다.",
        situation_summary="일반적인 관계 정리보다 먼저, 현재 안전을 확보하는 것이 최우선이에요.",
        facts=[],
        my_interpretations=[],
        feelings=[],
        needs=[],
        uncertainties=["지금 당장 본인 또는 타인의 안전이 위협받고 있는지 확인이 필요해요."],
        reflection_questions=[
            "지금 내가 안전한 곳에 있나?",
            "혼자 감당하기 어렵다면 도움을 요청할 수 있나?",
            "즉각적인 위험이면 지역의 긴급 도움을 이용할 수 있나?"
        ],
        safety=safety
    )