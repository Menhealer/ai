from __future__ import annotations

from datetime import datetime, timezone

from src.schemas.relationship import SettlementRequest, SettlementResponse, SafetyResult

def build_settlement_escalation(req: SettlementRequest, safety: SafetyResult) -> SettlementResponse:
    return SettlementResponse(
        version="v1-settlement",
        created_at=datetime.now(timezone.utc),
        month_summary="민감/위험 신호가 감지되어 일반적인 정산보다 안전을 우선 안내합니다.",
        month_solution="지금은 관계 분석보다 안전을 먼저 확보하는 것이 중요해요. 가까운 도움을 요청하세요.",
        quarter_summary="현재는 관계 정리보다 안전이 최우선입니다.",
        quarter_bullets=[
            "안전을 확보한 뒤에 관계 문제를 다루는 것이 좋아요.",
            "혼자 감당하기 어렵다면 신뢰할 수 있는 도움을 요청하세요.",
        ],
        best_friend=None,
        worst_friend=None,
        recommendation_title="안전 우선 안내",
        recommendation_body="감정이 격해졌다면 잠시 거리를 두고, 필요한 경우 주변의 도움을 받는 것을 권장해요.",
        safety=safety,
    )
