from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.schemas.relationship import (
    FriendSolutionRequest,
    FriendSummaryRequest,
    SettlementRequest,
    SettlementSummaryItem,
)

@dataclass
class SummaryContext:
    situation: str
    issues: List[str]
    friend_alias: Optional[str]
    tone: str
    context_hint: Optional[str] = None
    month_text: str = ""
    entries_count: int = 0

@dataclass
class SolutionContext:
    situation: str
    issues: List[str]
    friend_alias: Optional[str]
    goal: str
    tone: str
    context_hint: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    month_text: str = ""
    entries_count: int = 0

@dataclass
class SettlementContext:
    tone: str
    summaries: List[dict]
    context_hint: Optional[str]

def _join_entries(req) -> str:
    lines: List[str] = []
    for e in req.entries:
        dt = e.created_at.isoformat()
        lines.append(f"- ({dt}) {e.text}")
    return "\n".join(lines)

def _extract_common(month_text: str):
    text = (month_text or "").strip()
    situation = re.sub(r"\s+", " ", text)
    if len(situation) > 800:
        situation = situation[:800] + "..."
    issues: List[str] = []
    return situation, issues[:7]

def extract_summary(req: FriendSummaryRequest) -> SummaryContext:
    month_text = _join_entries(req)
    situation, issues = _extract_common(month_text)

    return SummaryContext(
        friend_alias=req.friend_alias,
        tone=req.tone,
        context_hint=req.context_hint,
        month_text=month_text,
        situation=situation,
        issues=issues,
        entries_count=len(req.entries),
    )

def extract_solution(req: FriendSolutionRequest) -> SolutionContext:
    month_text = _join_entries(req)
    situation, issues = _extract_common(month_text)

    return SolutionContext(
        friend_alias=req.friend_alias,
        goal=req.goal,
        tone=req.tone,
        context_hint=req.context_hint,
        month_text=month_text,
        situation=situation,
        issues=issues,
        entries_count=len(req.entries),
        summary=req.summary.model_dump(mode="json") if req.summary else None,
    )

def extract_settlement(req: SettlementRequest) -> SettlementContext:
    summaries: List[dict] = []
    for m in req.summaries:
        if isinstance(m, SettlementSummaryItem):
            summaries.append({
                "friend_alias": m.friend_alias,
                "summaries": [s.model_dump(mode="json") for s in m.summaries],
            })
        else:
            summaries.append(m)
    return SettlementContext(
        tone=req.tone,
        summaries=summaries,
        context_hint=req.context_hint,
    )
