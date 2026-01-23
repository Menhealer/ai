from __future__ import annotations

import re
from typing import List, Tuple

from src.schemas.relationship import SafetyResult

_RULES: List[Tuple[str, List[str]]] = [
    ("self_harm", [
        r"죽고\s*싶",
        r"자살",
        r"극단적\s*선택",
        r"자해",
        r"목숨",
        r"살\s*기\s*싫",
    ]),
    ("violence", [
        r"죽여",
        r"폭행",
        r"때려",
        r"칼",
        r"협박",
        r"해코지",
    ]),
    ("stalking", [
        r"미행",
        r"스토킹",
        r"집\s*앞",
        r"따라가",
        r"잠복",
        r"몰래\s*따라",
    ]),
    ("illegal", [
        r"불법",
        r"해킹",
        r"계정\s*털",
        r"협박\s*문자",
        r"개인정보\s*유출",
    ])
]

_COMPILED = [(cat, [re.compile(p) for p in patterns]) for cat, patterns in _RULES]

def check_safety(text: str) -> SafetyResult:
    t = (text or "").strip()
    categories: List[str] = []
    for cat, patterns in _COMPILED:
        if any(p.search(t) for p in patterns):
            categories.append(cat)

    flagged = len(categories) > 0
    note = None

    if flagged:
        note = "민감/위험 신호가 감지되어 일반적인 관계 조언 대신 안전 중심 안내로 전환합니다."
    return SafetyResult(flagged=flagged, categories=categories, note=note)