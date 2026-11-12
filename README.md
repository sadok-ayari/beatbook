# beatbook

Who covers your beat, how often, and how they framed it last time.

```
$ beatbook run --articles out/articles.json
2026-11-12 · 6 pieces, 5 with bylines, 3 journalists, 6 new · report: out/beatbook.md
```

## Why

A briefing packs a minister with talking points and a list of outlets. It almost never says who will write the story, what they have written before, or how they treated the last announcement. That knowledge lives in one person's head and leaves when they do.

Beatbook builds it from bylines and text. Per named reporter: outlets, count of pieces, the themes they actually cover, a framing tendency from a visible lexicon, and their last two headlines. Plus the theme-by-reporter matrix and the gap that matters: **themes with one named reporter**.

## What it does

- **Byline hygiene.** Cleans what feeds publish: `By Jane Doe`, `JANE DOE`, `Jane Doe, Senior Correspondent`, `Jane Doe <jane@example.org>`. Multiple authors collapse to the first: one story, one accountable name.
- **Beat attribution.** Keyword themes from `config/themes.json`, matched word-bounded.
- **Framing tendency.** Counts critical and favourable markers. `consistently critical` at 70%+, `leans critical` at 55%, `leans favourable` at 30% or below, otherwise `mixed`. Indicative only, and labelled as such.
- **Relationship gaps.** Any theme carried by fewer than two named reporters: one departure removes your access.
- **Archive.** SQLite, deduplicated by URL. Run it weekly and the beat builds itself.

## Install

Python 3.9+. No dependencies, no keys, no model.

```bash
git clone https://github.com/sadok-ayari/beatbook.git
cd beatbook
python -m beatbook run --articles tests/fixtures/articles.json
```

```bash
pip install -e . && beatbook show "Aisha"
```

## Configuration

`config/themes.json`: the themes you care about, and the words that mark them. Same shape as a watchlist: adding a theme is a config block, not code.

```json
{"themes": [{"id": "climate-finance", "name": "climate finance",
             "keywords": ["climate finance", "green bond", "concessional"]}]}
```

## Inputs

Any JSON list of `{title, author, outlet, url, published, summary}`. It also reads a coverage-radar `stories.json` if the byline is present there, so collect, cluster and beat-tracking can share one pipeline.

## Output

`out/beatbook.md`: the reporters ranked by volume, their beat, framing and last headlines; who covers what per theme; relationship gaps. `--json` for a scheduler. `beatbook show <name>` for one record.

## How this lands in a working week

- **Ritual:** briefing prep. One page joins the talking points: who is likely to write it and what they wrote last time.
- **Trigger:** monthly, or the morning a big announcement goes out.
- **Format:** names first, themes second. Reporters are read in the order a minister would meet them.
- **Owner:** whoever owns media relations, not the analyst.
- **Fail state:** a theme with one named reporter is a standing risk item. Track it until it has two.

## Honest limits

- **Feeds are bad at bylines.** Roughly half of what RSS returns carries no author. The report states the byline rate at the top: if it is under 50%, it says so rather than pretending to know the beat.
- **A lexicon counts words, not intent.** "Critical of the delay" and "critical funding gap" both count as critical. Use the tendency as a prompt to read the last three pieces, never as a rating of a person.
- **No contact details, no scraping, no profiles.** Bylines and text only. Contact data has its own legal and ethical rules and this tool stays out of them.
- **Attribution is first-author only.** Genuine co-bylines are rare in feeds and the simplification is stated in the output.

## Tests

```bash
python -m unittest discover -s tests   # 23 tests, offline
```

## Licence

MIT. See [LICENSE](LICENSE).
