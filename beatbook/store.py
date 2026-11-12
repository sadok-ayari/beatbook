from __future__ import annotations

import os
import sqlite3
from typing import Dict, List

from .models import Journalist, Piece

SCHEMA = """
CREATE TABLE IF NOT EXISTS pieces (
    key      TEXT PRIMARY KEY,
    day      TEXT,
    author   TEXT,
    outlet   TEXT,
    title    TEXT,
    url      TEXT,
    themes   TEXT,
    negative INTEGER DEFAULT 0,
    positive INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS pieces_author ON pieces(author);
"""


class Store:
    def __init__(self, path: str = "beatbook.db"):
        directory = os.path.dirname(os.path.abspath(path))
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def save(self, pieces: List[Piece]) -> int:
        new = 0
        for piece in pieces:
            if self.conn.execute("SELECT 1 FROM pieces WHERE key = ?", (piece.key,)).fetchone():
                continue
            day = (piece.published or "")[:10]
            self.conn.execute(
                "INSERT OR REPLACE INTO pieces (key, day, author, outlet, title, url, themes, negative, positive) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (piece.key, day, piece.author, piece.outlet, piece.title, piece.url,
                 ",".join(piece.themes), piece.negative, piece.positive))
            new += 1
        self.conn.commit()
        return new

    def journalists(self) -> Dict[str, Journalist]:
        rows = self.conn.execute(
            "SELECT author, outlet, title, themes, negative, positive, day FROM pieces "
            "WHERE author <> '' ORDER BY day").fetchall()
        out: Dict[str, Journalist] = {}
        for author, outlet, title, themes, negative, positive, day in rows:
            record = out.setdefault(author, Journalist(name=author))
            record.pieces += 1
            if outlet:
                record.outlets[outlet] = record.outlets.get(outlet, 0) + 1
            record.negative += negative
            record.positive += positive
            if day:
                record.first_seen = record.first_seen or day
                record.last_seen = day
            for theme in [t for t in (themes or "").split(",") if t]:
                record.themes[theme] = record.themes.get(theme, 0) + 1
            record.latest_titles.append(title)
        for record in out.values():
            record.latest_titles = record.latest_titles[-3:]
        return out

    def theme_matrix(self) -> Dict[str, Dict[str, int]]:
        rows = self.conn.execute("SELECT themes, author FROM pieces WHERE author <> ''").fetchall()
        matrix: Dict[str, Dict[str, int]] = {}
        for themes, author in rows:
            for theme in [t for t in (themes or "").split(",") if t]:
                matrix.setdefault(theme, {})
                matrix[theme][author] = matrix[theme].get(author, 0) + 1
        return matrix

    def close(self) -> None:
        self.conn.close()
