from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from . import __version__, report
from .models import Piece, load_json, rows_from
from .store import Store
from .text import clean_byline, framing, themes_in


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beatbook",
                                     description="Track who covers your beat, and how they framed it.")
    parser.add_argument("--version", action="version", version=f"beatbook {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="ingest articles and render the beat book")
    run.add_argument("--articles", required=True)
    run.add_argument("--config", default="config/themes.json")
    run.add_argument("--out", default="out")
    run.add_argument("--db", default="beatbook.db")
    run.add_argument("--day", default=None)
    run.add_argument("--json", action="store_true")

    show = sub.add_parser("show", help="one journalist's record")
    show.add_argument("name")
    show.add_argument("--db", default="beatbook.db")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "show":
        store = Store(args.db)
        people = store.journalists()
        key = args.name.lower()
        match = [j for name, j in people.items() if name.lower() == key] or \
                [j for name, j in people.items() if key in name.lower()]
        store.close()
        if not match:
            print(f"no byline matching {args.name!r} in the archive", file=sys.stderr)
            return 1
        for person in match:
            print(f"{person.name} — {person.outlet or 'outlet unknown'}, {person.pieces} pieces, "
                  f"{person.first_seen} to {person.last_seen}")
            print(f"  beat: {', '.join(person.beat) or 'unknown'}")
            print(f"  framing: {person.negative} critical / {person.positive} favourable markers")
            for title in person.latest_titles:
                print(f"  · {title}")
        return 0

    try:
        config = load_json(args.config)
        rows = rows_from(args.articles)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    themes = config.get("themes", [])
    pieces = []
    for row in rows:
        title = row.get("title") or row.get("lead_title") or ""
        if not title:
            continue
        author = clean_byline(row.get("author") or row.get("byline") or row.get("creator") or "")
        text = " ".join([title, row.get("summary") or ""])
        counts = framing(text)
        pieces.append(Piece(title=title, outlet=row.get("outlet", ""), author=author,
                            url=row.get("url", ""), published=row.get("published"),
                            themes=themes_in(text, themes),
                            negative=counts["negative"], positive=counts["positive"]))

    store = Store(args.db)
    new = store.save(pieces)
    people = store.journalists()
    matrix = store.theme_matrix()
    store.close()

    day = args.day or today()
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "beatbook.md")
    named = sum(1 for p in pieces if p.author)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(report.render(people, matrix, day, len(pieces), named,
                                   [t.get("name", t.get("id", "")) for t in themes]))

    if args.json:
        print(json.dumps({
            "day": day, "pieces": len(pieces), "with_byline": named, "new": new,
            "journalists": {p.name: {"outlet": p.outlet, "pieces": p.pieces,
                                     "beat": p.beat, "negative": p.negative,
                                     "positive": p.positive} for p in people.values()},
            "report": path,
        }, indent=2))
    else:
        print(f"{day} · {len(pieces)} pieces, {named} with bylines, {len(people)} journalists, "
              f"{new} new · report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
