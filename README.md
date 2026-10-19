# Portfolio

A static portfolio site generator: write projects as Markdown files with
YAML front matter, get a static HTML site out. Built for a Data Science /
UI-UX portfolio, but the category system is generic — add a new
`content/<type>/` folder and it shows up on the homepage automatically.

## Quick start

```bash
pip install -r requirements.txt
python main.py serve
```

Open `http://localhost:8000`.

## How to use

### Development server (Live-reload)

Run the dev server with automatic rebuilding and browser live-reload:

```bash
python main.py serve
```

Any changes to Markdown files and site copy (`content/`), Jinja templates (`templates/`), or static assets (`assets/`) will automatically trigger an incremental in-process rebuild and refresh connected browser tabs. Changes to `src/` will automatically restart the server process.

**Options:**
- `--port`, `-p`: Port to serve on (default: `8000`)
  ```bash
  python main.py serve -p 8080
  ```
- `--host`: Host address to bind to (default: `127.0.0.1`)
  ```bash
  python main.py serve --host 0.0.0.0
  ```
- `--base-url`: Base URL prefix for testing subpath routing
  ```bash
  python main.py serve --base-url /Portfolio
  ```
- `--open`: Open the site in your default browser automatically on start
  ```bash
  python main.py serve --open
  ```
- `--no-watch`: Serve the `static/` folder statically without file watching or live-reload
  ```bash
  python main.py serve --no-watch
  ```

### Building static output

Generate the static HTML files directly into `static/` without running the server:

```bash
python main.py build
```

**Options:**
- `--base-url`: Prefix all internal and asset links with a base path (useful for GitHub Pages project sites like `https://username.github.io/repo-name`)
  ```bash
  python main.py build --base-url /Portfolio
  ```
- `--strict`: Fail with exit code 1 if any content front matter is invalid or malformed (recommended for CI pipelines)
  ```bash
  python main.py build --strict
  ```

The output in `static/` is ready to be deployed to any static hosting service (GitHub Pages, Cloudflare Pages, Netlify, Vercel, etc.). A GitHub Actions workflow is also provided at `.github/workflows/deploy.yml`.

## How it works

```
content/<type>/*.md  →  parser.py  →  loader.py  →  images.py  →  builder.py  →  static/
   (Markdown +           (front matter    (validates into  (WebP optimize,   (renders templates,
    front matter)         + body → HTML)   Project objects, unreferenced      outputs 404, sitemap)
                                           groups category) assets pruned)
```

1. **`content/`** — one Markdown file per project, one folder per category
   (`data/`, `uiux/`, or any folder name you add), and `_site.yaml` for site-wide copy.
2. **`src/parser.py`** — splits a file into YAML front matter + Markdown
   body, parses inline `![[image]]` tags with dimensions and lazy loading, renders the body to HTML with code syntax highlighting tokens.
3. **`src/loader.py`** — walks `content/`, loads `content/_site.yaml`, validates each file's front
   matter into a `Project` (via `src/models.py`), skips anything invalid
   or marked `draft: true`, sorts, and groups by category.
4. **`src/images.py`** — optimizes referenced images to WebP, resizes large screenshots, caches output via mtime, syncs non-image assets incrementally, prunes unreferenced images, and auto-generates the Pygments code syntax highlighting CSS.
5. **`src/builder.py`** — renders `templates/index.html`, `templates/project.html`, `templates/404.html`, and `sitemap.xml` with Jinja2.
6. **`src/server.py`** — dev server with live-reload using `livereload`, watching source folders with incremental rebuilds and process restarting on `src/` changes.
7. **`main.py`** — CLI entry point (`build`, `serve`).

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
draft: false                    # true = excluded from output
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

Place an image exactly where it belongs in the write-up with `![[path]]`
(Obsidian-style embed syntax), where `path` is relative to `assets/`
(same convention as `cover_image`):

![[images/my-project/screen-1.png|Optional caption shown under the image]]

The caption after `|` is optional — `![[images/my-project/screen-1.png]]`
alone works too, falling back to the filename as alt text. Put it on its
own line with a blank line before and after, same as any other block.
```

See `content/data/app-rating-prediction.md` and
`content/uiux/Internship Project.md` for full working examples.

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

Malformed front matter (wrong type, missing required field) is reported with a printed warning at build time (or fails the build if `--strict` is enabled).

## Editing site-wide copy

Hero headline, about section, resume link, base URL, and footer links live in `content/_site.yaml` — edit them directly without touching Python code.

## Project structure

```
portfolio/
├── .github/workflows/  GitHub Actions CI/CD deployment
│   └── deploy.yml
├── content/            Source content — Markdown + front matter
│   ├── _site.yaml      Global site copy and configuration
│   ├── data/
│   └── uiux/
├── templates/          Jinja2 templates (base, index, project, 404)
├── assets/             Source assets (css, images, etc.)
│   ├── css/style.css
│   └── images/
├── static/             Generated output (WebP images, HTML, sitemap.xml)
├── src/                Build logic
│   ├── models.py       Pydantic Project/Link definitions
│   ├── parser.py       Front matter + Markdown → HTML, inline [[image]] syntax
│   ├── loader.py       Discovers content & loads _site.yaml into Projects
│   ├── images.py       WebP optimization, asset sync, syntax.css generation
│   ├── builder.py      Incremental site renderer, sitemap, 404
│   ├── server.py       Dev server with live-reload
│   └── utils.py        asset_url() and url_for() path helpers
├── main.py             CLI entry point
└── requirements.txt
```

## Requirements

- Python 3.10+
- `jinja2`, `markdown`, `pyyaml`, `pydantic`, `livereload`, `pillow`, `pygments` (see `requirements.txt`)
