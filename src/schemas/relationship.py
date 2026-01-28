from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, List, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, conlist

ToneType = Literal["warm", "neutral", "direct"]
GoalType = Literal["understand", "resolve", "distance", "reconnect", "other"]

class SafetyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    flagged: bool = Field(default=False)
    categories: List[str] = Field(default_factory=list)
    note: Optional[str] = Field(default=None, max_length=300)

# summary
class FriendSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=5, max_length=5000, description="사용자가 작성한 친구 관계 생각/상황")
    tone: ToneType = Field(default="warm", description="정리 말투")
    friend_alias: Optional[str] = Field(default=None, max_length=30)
    context_hint: Optional[str] = Field(default=None, max_length=500)

class FriendSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    version: str = Field(default="v1-friend-summary")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    one_line_summary: str = Field(..., min_length=5, max_length=120, description="한 줄 핵심")
    situation_summary: str = Field(..., min_length=10, max_length=500, description="상황 요약(사실 중심)")
    facts: List[str] = Field(default_factory=list, description="관찰 가능한 사실/사건")
    my_interpretations: List[str] = Field(default_factory=list, description="내 해석/생각(단정X, 내 관점)")
    feelings: List[str] = Field(default_factory=list, description="감정 단어")
    needs: List[str] = Field(default_factory=list, description="욕구/가치")
    uncertainties: List[str] = Field(default_factory=list, description="모르는 부분/확인 필요")
    reflection_questions: List[str] = Field(default_factory=list, description="내가 스스로에게 던질 질문(3개 권장)")
    safety: SafetyResult = Field(default_factory=SafetyResult)

# solution
class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=2, max_length=60)
    description: str = Field(..., min_length=5, max_length=300)
    intensity: Literal["low", "medium", "high"] = Field(default="low")
    why_this: Optional[str] = Field(default=None, max_length=200)

class MessageTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    situation: str = Field(..., min_length=2, max_length=40)
    text: str = Field(..., min_length=5, max_length=400)

class FriendSolutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=5, max_length=5000)
    goal: GoalType = Field(default="resolve")
    tone: ToneType = Field(default="warm")
    friend_alias: Optional[str] = Field(default=None, max_length=30)
    context_hint: Optional[str] = Field(default=None, max_length=500)
    summary: Optional[FriendSummaryResponse] = Field(default=None, description="(선택) /summarize 결과")

class FriendSolutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-friend-solution")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    goal: GoalType = Field(default="resolve")
    top_strategy: str = Field(..., min_length=5, max_length=200, description="핵심 전략 한 줄")
    actions: Annotated[list[ActionItem], conlist(ActionItem, min_length=1, max_length=6)]
    message_templates: Annotated[list[MessageTemplate], conlist(MessageTemplate, min_length=0, max_length=5)] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list, description="부작용/주의")
    if_no_change: List[str] = Field(default_factory=list, description="반복될 때 플랜B")
    safety: SafetyResult = Field(default_factory=SafetyResult)