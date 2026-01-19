from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, List, Optional
from pydantic import BaseModel, Field, ConfigDict

ToneType = Literal["warm", "neutral", "direct"]
GoalType = Literal["understand", "resolve", "distance", "reconnect", "other"]

class FriendSolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=5, max_length=5000, description="사용자가 작성한 친구 관계 생각/상황")
    goal: GoalType = Field(default="resolve", description="원하는 방향")
    tone: ToneType = Field(default="warm", description="답변 톤")

class ActionItme(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=2, max_length=60)
    description: str = Field(..., min_length=5, max_length=300)
    intensity: Literal["low", "medium", "high"] = Field(default="low")
    why_this: Optional[str] = Field(default=None, max_length=200)

class MessageTemplete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    situration: str = Field(..., min_length=2, max_length=40)
    text: str = Field(..., min_length=5, max_length=400)

class SafetyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    flagged: bool = Field(default=False)
    categories: List[str] = Field(default_factory=list)
    note: Optional[str] = Field(default=None, max_length=300)

class FriendSolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(default="v1-friend")
    created_at: datetime = Field(default_factory=datetime.datetime.now(timezone.utc))
    summary: str = Field(..., min_length=10, max_length=500)
    feelings: List[str] = Field(default_factory=list)
    needs: List[str] = Field(default_factory=list)
    possible_interpretations: List[str] = Field(default_factory=list)
    actions: List[ActionItme] = Field(..., min_items=1, max_items=6)
    message_templates: List[MessageTemplete] = Field(default_factory=list, max_items=5)
    cautions: List[str] = Field(default_factory=list)
    safety: SafetyResult = Field(default_factory=SafetyResult)
