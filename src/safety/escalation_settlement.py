from __future__ import annotations

from datetime import datetime, timezone

from src.schemas.relationship import SettlementRequest, SettlementResponse, SafetyResult

def build_settlement_escalation(_req: SettlementRequest, safety: SafetyResult) -> SettlementResponse:
    return SettlementResponse(
        version="v1-settlement",
        created_at=datetime.now(timezone.utc),
        month_summary="민감/위험 신호가 감지되어 일반적인 정산보다 안전을 우선 안내합니다.",
        month_bullets=[
            "안전을 우선해야 하는 신호가 감지되었어요.",
            "관계 분석은 안전 확보 이후로 미루는 것이 좋아요.",
        ],
        month_solution="지금은 관계 분석보다 안전을 먼저 확보하는 것이 중요해요. 가까운 도움을 요청하세요.",
        month_direction="지금은 관계 분석보다 안전 확보를 우선하세요.",
        month_friend_summaries=[],
        quarter_summary="현재는 관계 정리보다 안전이 최우선입니다.",
        quarter_solution="안전이 확보된 뒤에 관계 문제를 단계적으로 다루는 것이 좋아요.",
        quarter_direction="안전 확보 후 관계를 재정리하세요.",
        quarter_bullets=[
            "안전을 확보한 뒤에 관계 문제를 다루는 것이 좋아요.",
            "혼자 감당하기 어렵다면 신뢰할 수 있는 도움을 요청하세요.",
        ],
        best_friend=None,
        worst_friend=None,
        recommendation_friend=None,
        recommendation_title="안전 우선 안내",
        recommendation_body="감정이 격해졌다면 잠시 거리를 두고, 필요한 경우 주변의 도움을 받는 것을 권장해요.",
        recommendation_points=[
            "현재는 안전 확보가 최우선이에요.",
            "도움을 요청하는 것이 회복에 도움이 돼요.",
        ],
        caution_friend=None,
        caution_title="주의 안내",
        caution_body="지금은 관계 판단보다 안전 확보가 중요해요. 위험 신호가 느껴지면 도움을 요청하세요.",
        caution_points=[
            "안전이 확보되지 않으면 관계 판단은 보류하세요.",
            "필요시 주변 또는 전문가 도움을 요청하세요.",
        ],
        safety=safety,
    )
