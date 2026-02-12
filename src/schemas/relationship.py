from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, List, Optional
from pydantic import BaseModel, Field, ConfigDict

ToneType = Literal["warm"]
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
    situation_summary: str = Field(..., min_length=10, max_length=800, description="상황 요약(사실 중심)")

# solution
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
    solution_text: str = Field(..., min_length=20, max_length=800, description="관계 솔루션 본문")

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
    summaries: List["SettlementSummaryItem"] = Field(..., min_length=1, max_length=50, description="친구별 월간 요약 리스트")
    context_hint: Optional[str] = Field(default=None, max_length=500, description="전체 힌트(선택)")

class SettlementFriendMonthlySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: str = Field(..., min_length=1, max_length=40)
    summary: str = Field(..., min_length=10, max_length=800)
    bullets: List[str] = Field(default_factory=list, max_length=6)
    solution: str = Field(..., min_length=10, max_length=800)
    direction: str = Field(..., min_length=5, max_length=120)

class SettlementMonthlyText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    month: str = Field(..., min_length=7, max_length=7, description="YYYY-MM")
    summary_text: str = Field(..., min_length=5, max_length=800)

class SettlementSummaryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: str = Field(..., min_length=1, max_length=40)
    summaries: List[SettlementMonthlyText] = Field(..., min_length=1, max_length=12, description="친구별 월간 요약 텍스트 리스트")

class SettlementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-settlement")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quarter_summary: str = Field(..., min_length=20, max_length=1200)
    quarter_solution: str = Field(..., min_length=20, max_length=1200)
    quarter_direction: str = Field(..., min_length=10, max_length=200, description="분기 방향성 한 줄")
    quarter_bullets: List[str] = Field(..., min_length=1, max_length=6, description="분기 핵심 요약 불릿")
    best_friend: Optional[str] = Field(default=None, max_length=40)
    worst_friend: Optional[str] = Field(default=None, max_length=40)
    recommendation_friend: Optional[str] = Field(default=None, max_length=40)
    recommendation_title: str = Field(..., min_length=5, max_length=80)
    recommendation_body: str = Field(..., min_length=20, max_length=1200)
    recommendation_points: List[str] = Field(..., min_length=1, max_length=5, description="추천 근거 포인트")
    caution_friend: Optional[str] = Field(default=None, max_length=40)
    caution_title: str = Field(..., min_length=5, max_length=80)
    caution_body: str = Field(..., min_length=20, max_length=1200)
    caution_points: List[str] = Field(..., min_length=1, max_length=5, description="주의/워스트 근거 포인트")
    safety: SafetyResult = Field(default_factory=SafetyResult)

# best/worst
class BestWorstFriendInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: str = Field(..., min_length=1, max_length=40)
    summaries: List[SettlementMonthlyText] = Field(..., min_length=1, max_length=12)
    meetings: int = Field(..., ge=0, le=200, description="만남 횟수")
    rating_avg: float = Field(..., ge=0, le=5, description="평균 평가 점수(0~5)")
    gift_given: int = Field(..., ge=0, le=200)
    gift_received: int = Field(..., ge=0, le=200)

class BestWorstRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friends: List[BestWorstFriendInput] = Field(..., min_length=1, max_length=100)

class BestWorstItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    friend_alias: str = Field(..., min_length=1, max_length=40)
    reason: str = Field(..., min_length=5, max_length=300)
    suggestion: str = Field(..., min_length=5, max_length=120)

class BestWorstResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-friend-best-worst")
    best_list: List[BestWorstItem] = Field(..., min_length=1)
    worst_list: List[BestWorstItem] = Field(..., min_length=1)
