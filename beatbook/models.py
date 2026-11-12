from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Piece:
    title: str
    outlet: str = ""
    author: str = ""
    url: str = ""
    published: Optional[str] = None
    themes: List[str] = field(default_factory=list)
    negative: int = 0
    positive: int = 0

    @property
    def key(self) -> str:
        return self.url or f"{self.outlet}|{self.title}".lower()


@dataclass
class Journalist:
    name: str
    outlets: Dict[str, int] = field(default_factory=dict)
    pieces: int = 0
    themes: Dict[str, int] = field(default_factory=dict)
    negative: int = 0
    positive: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    latest_titles: List[str] = field(default_factory=list)

    @property
    def outlet(self) -> str:
        ranked = sorted(self.outlets.items(), key=lambda kv: (-kv[1], kv[0]))
        if not ranked:
            return ""
        names = [name for name, _ in ranked[:2]]
        return ", ".join(names) + (" and others" if len(ranked) > 2 else "")

    @property
    def beat(self) -> List[str]:
        ranked = sorted(self.themes.items(), key=lambda kv: (-kv[1], kv[0]))
        return [name for name, _ in ranked[:3]]


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def rows_from(path: str) -> List[Dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, list):
        return payload
    if "articles" in payload:
        return list(payload["articles"])
    if "stories" in payload:
        return [
            {"title": s.get("lead_title", ""), "url": s.get("url", ""),
             "outlet": (s.get("outlets") or [""])[0], "published": s.get("published"),
             "author": s.get("author", ""), "summary": s.get("summary", "")}
            for s in payload["stories"]
        ]
    return []
