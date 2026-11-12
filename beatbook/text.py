from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
BY_RE = re.compile(r"^\s*(?:by|written by|words by)\s+", re.I)
TRAILING_ROLE = re.compile(r"\s*[,\-–|]\s*(?:staff|senior|chief|political|correspondent|editor|reporter|writer|columnist).*$", re.I)

# Framing markers. Indicative only: a lexicon counts words, it does not read a story.
NEGATIVE = (
    "fail", "failed", "failing", "crisis", "collapse", "scandal", "slam", "slammed",
    "criticise", "criticised", "criticize", "criticized", "blasted", "row", "backlash",
    "probe", "investigation", "delay", "delayed", "cuts", "cut", "shortfall", "gap",
    "warn", "warned", "risk", "threat", "concern", "concerns", "dispute", "unclear",
    "stalled", "stall", "rejected", "shrink", "shrank", "slump", "paused", "halted",
)
POSITIVE = (
    "agreement", "agreed", "deal", "progress", "boost", "record", "landmark", "welcome",
    "welcomed", "approve", "approved", "funding", "pledge", "pledged", "support",
    "partnership", "launch", "launched", "deliver", "delivered", "milestone", "growth",
)


def strip_html(text: str) -> str:
    return SPACE_RE.sub(" ", TAG_RE.sub(" ", text or "")).strip()


def clean_byline(raw: str) -> str:
    """Normalise a byline without inventing anyone.

    Handles what feeds actually publish: "By Jane Doe", "JANE DOE",
    "Jane Doe, Senior Correspondent", "jane.doe@example.org (Jane Doe)".
    Multiple authors collapse to the first: one story, one accountable byline.
    """
    if not raw:
        return ""
    text = strip_html(raw)
    text = BY_RE.sub("", text)
    if "<" in text:                        # "Jane Doe <jane@example.org>"
        text = text.split("<")[0]
    text = TRAILING_ROLE.sub("", text)
    text = re.split(r"\s+(?:and|&)\s+|;|/", text)[0]
    text = re.sub(r"\s+", " ", text).strip(" ,.-")
    if not text or "@" in text or len(text) > 60:
        return ""
    return text.title() if text.isupper() else text


def name_key(name: str) -> str:
    return re.sub(r"[^a-z ]", "", name.lower()).strip()


def themes_in(text: str, themes: Iterable[Dict[str, Any]]) -> List[str]:
    low = (text or "").lower()
    found = []
    for theme in themes:
        for keyword in theme.get("keywords", []):
            if keyword and re.search(r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)", low):
                found.append(theme.get("name", theme.get("id", "")))
                break
    return found


def framing(text: str) -> Dict[str, int]:
    words = re.findall(r"[a-z']+", (text or "").lower())
    counts = {"negative": 0, "positive": 0}
    for word in words:
        if word in NEGATIVE:
            counts["negative"] += 1
        elif word in POSITIVE:
            counts["positive"] += 1
    return counts


def tendency(negative: int, positive: int) -> str:
    total = negative + positive
    if total == 0:
        return "neutral sample"
    share = negative / total
    if share >= 0.7:
        return "consistently critical"
    if share >= 0.55:
        return "leans critical"
    if share <= 0.3:
        return "leans favourable"
    return "mixed"
