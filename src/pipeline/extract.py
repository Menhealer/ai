from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.schemas.relationship import (
    FriendSolutionRequest,
    FriendSummaryRequest,
    SettlementRequest,
)

@dataclass
class SummaryContext:
    situation: str
    feelings: List[str]
    needs: List[str]
    issues: List[str]
    friend_alias: Optional[str]
    tone: str
    context_hint: Optional[str] = None
    month_text: str = ""
    entries_count: int = 0

@dataclass
class SolutionContext:
    situation: str
    feelings: List[str]
    needs: List[str]
    issues: List[str]
    friend_alias: Optional[str]
    goal: str
    tone: str
    context_hint: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    month_text: str = ""
    entries_count: int = 0

@dataclass
class SettlementPeriodCtx:
    period_label: str
    month_text: str
    entries_count: int
    context_hint: Optional[str]

@dataclass
class SettlementFriendCtx:
    friend_alias: str
    month_text: str
    entries_count: int
    context_hint: Optional[str]

@dataclass
class SettlementContext:
    tone: str
    month: SettlementPeriodCtx
    quarter: SettlementPeriodCtx
    friends: List[SettlementFriendCtx]
    context_hint: Optional[str]

def _join_entries(req) -> str:
    lines: List[str] = []
    for e in req.entries:
        dt = e.created_at.isoformat()
        tag_part = f" [tags: {', '.join(e.tags)}]" if e.tags else ""
        lines.append(f"- ({dt}) {e.text}{tag_part}")
    return "\n".join(lines)

def _extract_common(month_text: str):
    text = (month_text or "").strip()
    situation = re.sub(r"\s+", " ", text)
    if len(situation) > 800:
        situation = situation[:800] + "..."

    feelings: List[str] = []
    needs: List[str] = []
    issue_keywords = ["무시", "연락", "약속", "오해", "말투", "거리", "부담", "서운", "화", "차단", "피하"]
    sentences = re.split(r"[.!?\n]+", text)
    issues: List[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if any(k in s for k in issue_keywords):
            issues.append(s)
    if not issues:
        issues = ["핵심 이슈를 더 추가해주세요."]
    return situation, feelings, needs, issues[:7]

def extract_summary(req: FriendSummaryRequest) -> SummaryContext:
    month_text = _join_entries(req)
    situation, feelings, needs, issues = _extract_common(month_text)

    return SummaryContext(
        friend_alias=req.friend_alias,
        tone=req.tone,
        context_hint=req.context_hint,
        month_text=month_text,
        situation=situation,
        feelings=feelings,
        needs=needs,
        issues=issues,
        entries_count=len(req.entries),
    )

def extract_solution(req: FriendSolutionRequest) -> SolutionContext:
    month_text = _join_entries(req)
    situation, feelings, needs, issues = _extract_common(month_text)

    return SolutionContext(
        friend_alias=req.friend_alias,
        goal=req.goal,
        tone=req.tone,
        context_hint=req.context_hint,
        month_text=month_text,
        situation=situation,
        feelings=feelings,
        needs=needs,
        issues=issues,
        entries_count=len(req.entries),
        summary=req.summary.model_dump(mode="json") if req.summary else None,
    )

def _period_ctx(period) -> SettlementPeriodCtx:
    month_text = _join_entries(period)
    return SettlementPeriodCtx(
        period_label=period.period_label,
        month_text=month_text,
        entries_count=len(period.entries),
        context_hint=period.context_hint,
    )

def _friend_ctx(f) -> SettlementFriendCtx:
    month_text = _join_entries(f)
    return SettlementFriendCtx(
        friend_alias=f.friend_alias,
        month_text=month_text,
        entries_count=len(f.entries),
        context_hint=f.context_hint,
    )

def extract_settlement(req: SettlementRequest) -> SettlementContext:
    month = _period_ctx(req.month)
    quarter = _period_ctx(req.quarter)
    friends = [_friend_ctx(f) for f in req.friends]
    return SettlementContext(
        tone=req.tone,
        month=month,
        quarter=quarter,
        friends=friends,
        context_hint=req.context_hint,
    )
