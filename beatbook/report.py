from __future__ import annotations

from typing import Dict, List

from .models import Journalist
from .text import tendency


def _plural(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def render(journalists: Dict[str, Journalist], matrix: Dict[str, Dict[str, int]],
           day: str, total_pieces: int, with_byline: int, themes: List[str]) -> str:
    out = [f"# Beat book — {day}", ""]
    out.append(f"**{len(journalists)} named journalists across "
               f"{len({j.outlet for j in journalists.values() if j.outlet})} outlets. "
               f"{with_byline} of {total_pieces} pieces carried a usable byline.**")
    if total_pieces and with_byline / total_pieces < 0.5:
        out += ["", "> Half the sample has no byline. Feed bylines are unreliable; treat the "
                    "names below as the reporters you can see, not the beat in full."]

    ranked = sorted(journalists.values(), key=lambda j: (-j.pieces, j.name))
    out += ["", "## The people", ""]
    if not ranked:
        out.append("_No usable bylines in this window._")
    for person in ranked:
        framing = tendency(person.negative, person.positive)
        span = f"{person.first_seen} to {person.last_seen}" if person.first_seen else "undated"
        out.append(f"- **{person.name}** — {person.outlet or 'outlet unknown'}, "
                   f"{_plural(person.pieces, 'piece', 'pieces')}, {span}")
        if person.beat:
            out.append(f"  - beat: {', '.join(person.beat)}")
        out.append(f"  - framing: {framing} ({person.negative} critical markers, "
                   f"{person.positive} favourable)")
        for title in person.latest_titles[-2:]:
            out.append(f"  - last: {title}")

    out += ["", "## Who covers what", ""]
    for theme in themes:
        people = matrix.get(theme, {})
        if not people:
            out.append(f"- **{theme}:** no named byline in this window")
            continue
        top = sorted(people.items(), key=lambda kv: (-kv[1], kv[0]))
        named = ", ".join(f"{name} ({count})" for name, count in top[:5])
        out.append(f"- **{theme}:** {named}")
        if len(top) < 2:
            out.append("  - thin: one reporter carries this theme")

    thin = [t for t in themes if len(matrix.get(t, {})) < 2]
    if thin:
        out += ["", "## Relationship gaps", "",
                "_Themes with fewer than two named reporters. One departure removes your access._"]
        for theme in thin:
            out.append(f"- {theme}")

    out += ["", "---", "",
            "_Built from bylines only. No scraping of contact details, no profiles, "
            "no inference beyond the words in the sample._"]
    return "\n".join(out) + "\n"
