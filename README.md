# Portfolio

A static portfolio site generator: write projects as Markdown files with
YAML front matter, get a static HTML site out. Built for a Data Science /
UI-UX portfolio, but the category system is generic — add a new
`content/<type>/` folder and it shows up on the homepage automatically.

## Quick start

```bash
pip install -r requirements.txt
python main.py build
python -m http.server -d static 8000
```

Open `http://localhost:8000`.

## How it works

```
content/<type>/*.md  →  parser.py  →  loader.py  →  builder.py  →  static/
   (Markdown +           (front matter    (validates into        (renders
    front matter)         + body → HTML)   Project objects,        templates,
                                            groups by category)     copies assets)
```

1. **`content/`** — one Markdown file per project, one folder per category
   (`data/`, `uiux/`, or any folder name you add).
2. **`src/parser.py`** — splits a file into YAML front matter + Markdown
   body, renders the body to HTML.
3. **`src/loader.py`** — walks `content/`, validates each file's front
   matter into a `Project` (via `src/models.py`), skips anything invalid
   or marked `draft: true`, sorts, and groups by category.
4. **`src/builder.py`** — renders `templates/index.html` and
   `templates/project.html` (one output per project) with Jinja2, copies
   `assets/` into `static/`.
5. **`main.py`** — CLI entry point (`python main.py build`) and the
   site-wide copy (hero text, about section, footer links) that isn't
   per-project content.

## Writing a project

Add a Markdown file under `content/<type>/`. The filename (minus `.md`)
becomes the URL slug, e.g. `content/data/my-project.md` builds to
`static/my-project/index.html`.

```markdown
---
title: Project Title
summary: One or two sentences — shown on the homepage card.
tagline: MACHINE LEARNING       # optional, overrides the category label
technologies: [Python, Pandas, Scikit-learn]
featured: true                  # featured projects sort first
order: 1                        # tiebreaker within featured/non-featured
draft: false                    # true = built but excluded from output
cover_image: images/my-project/cover.png   # optional, path under assets/
links:
  - label: GitHub
    url: https://github.com/you/my-project
  - label: Dataset
    url: https://example.com/dataset
---

## Overview

Regular Markdown from here down — headings, paragraphs, ```code fences```,
tables, and images all work and get styled to match the design.

Place an image exactly where it belongs in the write-up with `[[path]]`,
where `path` is relative to `assets/` (same convention as `cover_image`):

[[images/my-project/screen-1.png|Optional caption shown under the image]]

The caption after `|` is optional — `[[images/my-project/screen-1.png]]`
alone works too, falling back to the filename as alt text. Put it on its
own line with a blank line before and after, same as any other block.
```

See `content/data/app-rating-prediction.md` and
`content/uiux/internship-project.md` for full working examples.

### Front matter fields

| Field          | Required | Notes                                              |
|----------------|----------|-----------------------------------------------------|
| `title`        | yes      |                                                       |
| `summary`      | yes      | short — used on the homepage card                    |
| `technologies` | no       | list of tags shown as pills                          |
| `tagline`      | no       | defaults to the category label (e.g. "DATA & ANALYTICS") |
| `featured`     | no       | default `false` — featured projects sort first       |
| `order`        | no       | default `0` — lower sorts first, within the same featured/draft group |
| `draft`        | no       | default `false` — `true` excludes it from the build   |
| `cover_image`  | no       | path under `assets/`, shown on the homepage card      |
| `image_label`  | no       | fallback text on the card if there's no `cover_image` |
| `links`        | no       | list of `{label, url}` — buttons on the project page  |

There is no `gallery` field — place images inline in the body with
`[[path]]` / `[[path|caption]]` instead (see above). This puts each
image next to the text it illustrates rather than pinned to a fixed
spot on the page.

Malformed front matter (wrong type, missing required field) is skipped
with a printed warning at build time rather than crashing the whole build
— check the console output after `python main.py build`.

## Editing site-wide copy

Hero headline, about section, and footer links aren't per-project
content, so they live as plain dicts at the top of `main.py`
(`SITE`, `HOME`, `WORK`, `INTERSECTION`, `ABOUT`) — edit them directly.

## Project structure

```
portfolio/
├── content/            Source content — Markdown + front matter
│   ├── data/
│   └── uiux/
├── templates/           Jinja2 templates (base, index, project)
├── assets/               Source assets — copied into static/assets/ on build
│   ├── css/
│   ├── images/
│   └── js/
├── static/               Generated output — do not edit directly, do not commit
├── src/                  Build logic
│   ├── models.py         Pydantic Project/Link
│   ├── parser.py         Front matter + Markdown → HTML, inline [[image]] syntax
│   ├── loader.py         Discovers and validates content/ into Projects
│   ├── builder.py        Renders templates, writes static/
│   └── utils.py          Shared asset_url() path helper
├── main.py               Site copy + CLI
└── requirements.txt
```

## Known gaps / not yet built

- No `serve --watch` dev command — rebuild manually after content changes.
- No syntax-highlighting theme — `codehilite` classes are in the output
  HTML but need a Pygments CSS theme appended to `style.css`
  (`pygmentize -S <style> -f html -a .codehilite`).
- No Jupyter notebook loader yet — Markdown only for now.
- No deployment config (GitHub Actions / Netlify / Vercel) — `static/` is
  built locally and would need to be uploaded or wired to CI.
- `assets/js/` and `assets/images/` exist but are currently empty.
- The `.gallery` grid CSS class (side-by-side image layout) is still in
  `style.css` but unused by any template now — it's a manual escape hatch
  if you ever want two images side by side: wrap raw HTML directly in a
  Markdown file, e.g. `<div class="gallery">...`. Not documented as a
  first-class feature since it breaks the plain-Markdown authoring flow.

## Requirements

- Python 3.10+
- `jinja2`, `markdown`, `pyyaml`, `pydantic` (see `requirements.txt`)
