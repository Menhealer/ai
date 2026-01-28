from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.schemas.relationship import FriendSolutionRequest, FriendSummaryRequest

@dataclass
class SummaryContext:
    situation: str
    feelings: List[str]
    needs: List[str]
    issues: List[str]
    friend_alias: Optional[str]
    tone: str

@dataclass
class SolutionContext:
    situation: str
    feelings: List[str]
    needs: List[str]
    issues: List[str]
    friend_alias: Optional[str]
    goal: str
    tone: str
    summary: Optional[Dict[str, Any]] = None

_FEELING_HINTS = [
    ("서운", "서운함"),
    ("불안", "불안함"),
    ("화", "화남"),
    ("짜증", "짜증남"),
    ("답답", "답답함"),
    ("속상", "속상함"),
    ("미안", "미안함"),
    ("걱정", "걱정됨"),
]

_NEED_HINTS = [
    ("존중", "존중"),
    ("배려", "배려"),
    ("소통", "명확한 소통"),
    ("사과", "사과/인정"),
    ("시간", "시간/거리"),
    ("신뢰", "신뢰"),
]

def _guess_list(text: str, hints) -> List[str]:
    found = []
    for needle, label in hints:
        if needle in text:
            found.append(label)
    return list(dict.fromkeys(found))

def _extract_common(text: str):
    text = text.strip()
    situation = re.sub(r"\s+", " ", text)
    if len(situation) > 350:
        situation = situation[:350] + "..."

    feelings = _guess_list(text, _FEELING_HINTS)
    needs = _guess_list(text, _NEED_HINTS)
    issue_keywords = ["무시", "연락", "약속", "오해", "말투", "거리", "부담", "서운", "화", "차단", "피하"]
    sentences = re.split(r"[.!?\n]+", text)
    issues = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if any(k in s for k in issue_keywords):
            issues.append(s)

    if not issues:
        issues = ["핵심 이슈를 더 추가해주세요."]

    return situation, feelings, needs, issues[:5]

def extract_solution(req: FriendSolutionRequest) -> SolutionContext:
    situation, feelings, needs, issues = _extract_common(req.text)

    return SolutionContext(
        situation=situation,
        feelings=feelings,
        needs=needs,
        issues=issues,
        friend_alias=req.friend_alias,
        goal=req.goal,
        tone=req.tone,
        summary=req.summary.model_dump() if getattr(req, "summary", None) else None,
    )

def extract_summary(req: FriendSummaryRequest) -> SummaryContext:
    situation, feelings, needs, issues = _extract_common(req.text)

    return SummaryContext(
        situation=situation,
        feelings=feelings,
        needs=needs,
        issues=issues,
        friend_alias=req.friend_alias,
        tone=req.tone,
    )