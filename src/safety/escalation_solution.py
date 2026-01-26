from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from src.schemas.relationship import (
    FriendSolutionRequest,
    FriendSolutionResponse,
    ActionItem,
    MessageTemplate,
    SafetyResult
)

def build_solution_escalation(req: FriendSolutionRequest, safety: SafetyResult) -> FriendSolutionResponse:
    actions: List[ActionItem] = [
        ActionItem(
            title="지금은 안전을 먼저 확보하기",
            description="감정이 격해졌다면 잠시 자리를 이동하거나 주변에 사람을 두고, 즉시 행동으로 옮기기 전에 숨을 고르세요.",
            intensity="low",
            why_this="위험 신호가 보일 때는 관계 조언보다 안전이 우선이에요.",
        ),
        ActionItem(
            title="신뢰할 수 있는 사람/전문 도움에 연결하기",
            description="혼자 감당하기 어렵다면 가까운 지인, 학교/직장 상담 창구, 지역 상담 서비스를 통해 도움을 요청하세요.",
            intensity="medium",
            why_this="지원이 있으면 충동적 선택을 줄이고 상황을 정리하기 쉬워요.",
        ),
        ActionItem(
            title="즉각적인 위험이면 긴급 도움을 요청하기",
            description="지금 당장 자신이나 타인의 안전이 위협받는 상황이면 지역의 긴급 도움(응급/경찰/핫라인 등)을 이용하세요.",
            intensity="high",
            why_this="긴급 상황은 즉시 대응이 필요해요.",
        )
    ]

    templates: List[MessageTemplate] = [
        MessageTemplate(
            situation="도움 요청",
            text="지금 감정이 너무 벅차서 혼자 해결하기 어려워. 잠깐 통화하거나 같이 있어줄 수 있을까?",
        ),
        MessageTemplate(
            situation="거리두기",
            text="지금은 감정이 격해져서 대화를 이어가기 어렵다. 안전하게 진정한 뒤에 다시 이야기하고 싶어.",
        )
    ]

    return FriendSolutionResponse(
        version="v1-friend-solution",
        created_at=datetime.now(timezone.utc),
        goal=req.goal,
        top_strategy="위험 신호가 감지되어 관계 솔루션보다 안전 확보와 도움 요청을 우선합니다.",
        actions=actions,
        message_templates=templates,
        risks=[
            "상대에게 해를 주거나 스스로를 해치는 행동은 절대 하지 않기",
            "상대를 추적/위협하는 행동은 상황을 악화시키고 법적 문제로 이어질 수 있어요",
        ],
        if_no_change=[
            "안전이 확보되지 않으면 전문가/긴급 도움을 우선 이용하세요.",
            "상황이 진정된 뒤에 관계 문제를 단계적으로 다루는 게 좋아요.",
        ],
        safety=safety,
    )