from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, List, Optional
from pydantic import BaseModel, Field, ConfigDict

ToneType = Literal["warm", "neutral", "direct"]
GoalType = Literal["understand", "resolve", "distance", "reconnect", "other"]

class SafetyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    flagged: bool = Field(default=False)
    categories: List[str] = Field(default_factory=list)
    note: Optional[str] = Field(default=None, max_length=800)

# 1건 요약
class FriendEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    text: str = Field(..., min_length=1, max_length=300, description="해당 날의 관계 기록/생각")

# 한달 요약
class FriendMonthlyBaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: Optional[str] = Field(default=None, description="친구 별칭(표시용)")
    tone: ToneType = Field(default="warm")
    entries: List[FriendEntry] = Field(..., min_length=1, max_length=300, description="한 달치 기록 리스트")
    context_hint: Optional[str] = Field(default=None, max_length=500, description="추가 힌트(선택)")

# summary
class FriendSummaryRequest(FriendMonthlyBaseRequest):
    pass

class FriendSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    version: str = Field(default="v1-friend-summary")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    one_line_summary: str = Field(..., min_length=5, max_length=120, description="한 줄 핵심")
    situation_summary: str = Field(..., min_length=10, max_length=800, description="상황 요약(사실 중심)")
    period_label: str = Field(default="최근 3개월 기준", min_length=2, max_length=40, description="요약 기준 기간 라벨")
    relationship_status_percent: int = Field(default=50, ge=0, le=100, description="관계 상태 게이지(0~100)")
    relationship_status_label: str = Field(default="보통", min_length=1, max_length=20, description="관계 상태 라벨(예: 긍정적/보통/부정적)")
    meeting_continuity: str = Field(default="", max_length=60, description="만남 지속/빈도 요약(짧은 문장)")
    post_meeting_satisfaction: str = Field(default="", max_length=60, description="만남 이후 만족도 요약(짧은 문장)")
    emotion_pattern: str = Field(default="", max_length=80, description="감정 패턴 요약(짧은 문장)")
    gift_balance: str = Field(default="", max_length=80, description="선물/호의 주고받음 균형 요약")
    initiative_balance: str = Field(default="", max_length=80, description="먼저 연락/제안한 쪽 요약")
    facts: List[str] = Field(default_factory=list, description="관찰 가능한 사실/사건")
    my_interpretations: List[str] = Field(default_factory=list, description="내 해석/생각(단정X, 내 관점)")
    uncertainties: List[str] = Field(default_factory=list, description="모르는 부분/확인 필요")
    reflection_questions: List[str] = Field(default_factory=list, description="내가 스스로에게 던질 질문(3개 권장)")
    safety: SafetyResult = Field(default_factory=SafetyResult)

# solution
class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=2, max_length=60)
    description: str = Field(..., min_length=5, max_length=800)
    intensity: Literal["low", "medium", "high"] = Field(default="low")
    why_this: Optional[str] = Field(default=None, max_length=300)

class MessageTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    situation: str = Field(..., min_length=2, max_length=400)
    text: str = Field(..., min_length=5, max_length=600)

class FriendSolutionRequest(FriendMonthlyBaseRequest):
    goal: GoalType = Field(default="resolve")
    summary: Optional[FriendSummaryResponse] = Field(default=None, description="(선택) /summarize 결과를 그대로 넣기")

class FriendSolutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-friend-solution")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    goal: GoalType = Field(..., description="요청 목표")
    top_strategy: str = Field(..., min_length=5, max_length=200, description="핵심 전략 한 줄")
    direction_suggestion: str = Field(default="", max_length=120, description="관계 방향성 제안 한 줄")
    actions: List[ActionItem] = Field(..., min_length=1, max_length=6)
    message_templates: List[MessageTemplate] = Field(default_factory=list, max_length=5)
    risks: List[str] = Field(default_factory=list, max_length=8, description="부작용/주의")
    if_no_change: List[str] = Field(default_factory=list, max_length=6, description="반복될 때 플랜B")
    safety: SafetyResult = Field(default_factory=SafetyResult)

# settlement
class SettlementPeriodContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period_label: str = Field(default="이번 달", min_length=2, max_length=20)
    entries: List[FriendEntry] = Field(..., min_length=1, max_length=300)
    context_hint: Optional[str] = Field(default=None, max_length=500)

class SettlementFriendContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: str = Field(..., min_length=1, max_length=40)
    entries: List[FriendEntry] = Field(..., min_length=1, max_length=300)
    context_hint: Optional[str] = Field(default=None, max_length=500)

class SettlementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tone: ToneType = Field(default="warm")
    month: SettlementPeriodContext
    quarter: SettlementPeriodContext
    friends: List[SettlementFriendContext] = Field(default_factory=list, max_length=50)
    context_hint: Optional[str] = Field(default=None, max_length=500, description="전체 힌트(선택)")

class SettlementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-settlement")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    month_summary: str = Field(..., min_length=20, max_length=1200)
    month_solution: str = Field(..., min_length=20, max_length=1200)
    quarter_summary: str = Field(..., min_length=20, max_length=1200)
    quarter_bullets: List[str] = Field(..., min_length=1, max_length=6, description="1분기 핵심 요약 불릿")
    best_friend: Optional[str] = Field(default=None, max_length=40)
    worst_friend: Optional[str] = Field(default=None, max_length=40)
    recommendation_title: str = Field(..., min_length=5, max_length=80)
    recommendation_body: str = Field(..., min_length=20, max_length=1200)
    safety: SafetyResult = Field(default_factory=SafetyResult)
